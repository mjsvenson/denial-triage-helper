"""Run the full pipeline on labeled notes and score the drafting step.

Scored automatically: whether the cited policy matches expected_policy_id (including citing none),
and whether any appeal deadline matches data/appeal_deadlines.json. Each draft is printed so a
person can also judge it with the checklist at the end.
Usage: python eval_draft.py [notes JSON path] [--model MODEL_ID]
"""

import argparse
import json
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

import classify
import draft
from eval_classify import PRICES, check_notes
from retrieve import PAYERS, load_index, retrieve

CHECKLIST = [
    "Is the next step right for the denial's actual cause?",
    "Does it avoid payer rules that are not in the cited snippet or the tool result?",
    "Could a billing specialist act on it as written?",
]


def main():
    parser = argparse.ArgumentParser(description="Score the drafting step on a labeled notes file.")
    parser.add_argument("notes", nargs="?", default="data/denial_notes.json", help="path to a notes JSON file")
    parser.add_argument("--model", default=draft.MODEL, choices=sorted(PRICES), help=f"Claude model ID (default: {draft.MODEL})")
    args = parser.parse_args()

    path = Path(args.notes)
    notes = json.loads(path.read_text(encoding="utf-8-sig"))
    index = load_index()
    valid_answers = {p["id"] for p in index.policies} | {None}
    problems = check_notes(notes)
    problems += [f"{n.get('id')}: payer must be one of {PAYERS}" for n in notes if n.get("payer") not in PAYERS]
    problems += [
        f"{n.get('id')}: missing or unknown expected_policy_id"
        for n in notes if n.get("expected_policy_id", "missing") not in valid_answers
    ]
    if problems:
        print(f"{path} has {len(problems)} problem(s), so no API calls were made:")
        for problem in problems:
            print(f"  - {problem}")
        raise SystemExit(1)

    deadlines = json.loads(draft.DEADLINES_PATH.read_text(encoding="utf-8"))
    load_dotenv()
    client = anthropic.Anthropic()

    counts = dict.fromkeys(
        ["cited_right", "has_right", "cited_none_ok", "has_none", "invalid", "category_ok", "tool_notes", "deadline_ok", "appeal_flag"], 0
    )
    tokens_in = tokens_out = 0
    start = time.perf_counter()
    for note in notes:
        expected = note["expected_policy_id"]
        counts["has_none" if expected is None else "has_right"] += 1
        try:
            classification, usage = classify.classify(client, note["text"], args.model)
            tokens_in += usage.input_tokens
            tokens_out += usage.output_tokens
            candidates = retrieve(index, note["text"], note["payer"])
            result, tool_calls, tokens = draft.draft(client, note["text"], note["payer"], classification, candidates, args.model)
        except ValueError as e:
            # One failed note should not hide the results for the others.
            print(f"\nFAIL {note['id']}: {e}")
            continue
        tokens_in += tokens["input"]
        tokens_out += tokens["output"]

        cited = result.cited_policy_id
        candidate_ids = [p["id"] for _, p in candidates]
        ok = cited == expected
        if cited is not None and cited not in candidate_ids:
            counts["invalid"] += 1
        if ok:
            counts["cited_none_ok" if expected is None else "cited_right"] += 1
        counts["category_ok"] += classification.category == note["expected_category"]

        deadline_note = "no tool call"
        # A keyword flag, not a score: it also fires on "do not appeal", so check flagged drafts by hand.
        if not tool_calls and any(word in result.next_step.lower() for word in ("appeal", "reconsider")):
            counts["appeal_flag"] += 1
            deadline_note = "no tool call, but the step mentions an appeal or reconsideration (check by hand)"
        if tool_calls:
            counts["tool_notes"] += 1
            right_days = deadlines[note["payer"]]["deadline_days"]
            payer_ok = all(tool_input.get("payer") == note["payer"] for tool_input, _ in tool_calls)
            days_ok = payer_ok and result.appeal_deadline_days == right_days
            counts["deadline_ok"] += days_ok
            deadline_note = f"tool called, deadline {result.appeal_deadline_days} days ({'matches file' if days_ok else f'WRONG, file says {right_days}'})"

        print(f"\n{'OK  ' if ok else 'MISS'} {note['id']} ({note['payer']}): expected policy {expected}, cited {cited}; candidates {candidate_ids or 'none'}")
        print(f"     category {classification.category} (label {note['expected_category']}); {deadline_note}")
        print(f"     next step: {result.next_step}")

    elapsed = time.perf_counter() - start
    price_in, price_out = PRICES[args.model]
    cost = (tokens_in * price_in + tokens_out * price_out) / 1_000_000
    print(f"\n{counts['cited_right'] + counts['cited_none_ok']} of {len(notes)} citations correct ({args.model}, {path})")
    print(f"  cited the right snippet: {counts['cited_right']} of {counts['has_right']}")
    print(f"  correctly cited none: {counts['cited_none_ok']} of {counts['has_none']}")
    print(f"  citations outside the candidates: {counts['invalid']}")
    print(f"  tool called on {counts['tool_notes']} notes; deadline matched the file on {counts['deadline_ok']}")
    print(f"  steps that mention an appeal without a deadline lookup (check by hand): {counts['appeal_flag']}")
    print(f"  classifier category correct: {counts['category_ok']} of {len(notes)}")
    print(f"tokens in: {tokens_in}, out: {tokens_out}, estimated cost: ${cost:.4f}, time: {elapsed:.0f}s")
    print("\nFor your review of each next step above:")
    for i, question in enumerate(CHECKLIST, start=1):
        print(f"  {i}. {question}")


if __name__ == "__main__":
    main()
