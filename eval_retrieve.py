"""Score retrieval: is each note's expected policy among the top candidates (recall at k)?

Notes whose expected_policy_id is null have no right snippet. Deciding that no candidate applies
is the drafting step's job, so those notes are listed here but scored there.
This makes no API calls, so it is free and gives the same result every run.
Usage: python eval_retrieve.py [notes JSON path] [--k N]
"""

import argparse
import json
from pathlib import Path

from retrieve import PAYERS, TOP_K, load_index, retrieve


def main():
    parser = argparse.ArgumentParser(description="Score policy retrieval on a labeled notes file.")
    parser.add_argument("notes", nargs="?", default="data/denial_notes.json", help="path to a notes JSON file")
    parser.add_argument("--k", type=int, default=TOP_K, help=f"how many candidates count (default: {TOP_K})")
    args = parser.parse_args()

    path = Path(args.notes)
    notes = json.loads(path.read_text(encoding="utf-8-sig"))
    index = load_index()

    valid_answers = {p["id"] for p in index.policies} | {None}
    problems = []
    for n in notes:
        if n.get("payer") not in PAYERS:
            problems.append(f"{n.get('id')}: payer must be one of {PAYERS}")
        if "expected_policy_id" not in n:
            problems.append(f"{n.get('id')}: missing expected_policy_id")
        elif n["expected_policy_id"] not in valid_answers:
            problems.append(f"{n.get('id')}: unknown expected_policy_id '{n['expected_policy_id']}'")
    if problems:
        print(f"{path} has {len(problems)} problem(s):")
        for problem in problems:
            print(f"  - {problem}")
        raise SystemExit(1)

    hits = with_answer = no_answer = 0
    for note in notes:
        candidates = retrieve(index, note["text"], note["payer"], args.k)
        shown = ", ".join(f"{p['id']} {score:.3f}" for score, p in candidates) or "none"
        expected = note["expected_policy_id"]
        if expected is None:
            no_answer += 1
            print(f"--   {note['id']}: no right snippet; candidates passed on: {shown}")
            continue
        with_answer += 1
        ok = expected in [p["id"] for _, p in candidates]
        hits += ok
        print(f"{'OK  ' if ok else 'MISS'} {note['id']}: expected {expected} in top {args.k}; got {shown}")

    print(f"\nright snippet in the top {args.k}: {hits} of {with_answer} ({path})")
    print(f"notes with no right snippet: {no_answer} (scored in the drafting step, which decides if a candidate applies)")


if __name__ == "__main__":
    main()
