"""Score retrieval against each note's expected_policy_id.

This makes no API calls, so it is free and gives the same result every run.
Usage: python eval_retrieve.py [notes JSON path] [--min-score N]
"""

import argparse
import json
from pathlib import Path

from retrieve import MIN_SCORE, load_index, retrieve


def main():
    parser = argparse.ArgumentParser(description="Score policy retrieval on a labeled notes file.")
    parser.add_argument("notes", nargs="?", default="data/denial_notes.json", help="path to a notes JSON file")
    parser.add_argument("--min-score", type=float, default=MIN_SCORE, help=f"minimum similarity (default: {MIN_SCORE})")
    args = parser.parse_args()

    path = Path(args.notes)
    notes = json.loads(path.read_text(encoding="utf-8-sig"))
    index = load_index()

    valid_answers = {p["id"] for p in index.policies} | {None}
    problems = [f"{n.get('id')}: missing expected_policy_id" for n in notes if "expected_policy_id" not in n]
    problems += [
        f"{n['id']}: unknown expected_policy_id '{n['expected_policy_id']}'"
        for n in notes if "expected_policy_id" in n and n["expected_policy_id"] not in valid_answers
    ]
    if problems:
        print(f"{path} has {len(problems)} problem(s):")
        for problem in problems:
            print(f"  - {problem}")
        raise SystemExit(1)

    found = should_find = empty_ok = should_be_empty = 0
    for note in notes:
        policy, ranked = retrieve(index, note["text"], args.min_score)
        got = policy["id"] if policy else None
        expected = note["expected_policy_id"]
        ok = got == expected
        best = f"{ranked[0][1]['id']} at {ranked[0][0]:.3f}" if ranked else "no candidates"
        print(f"{'OK  ' if ok else 'MISS'} {note['id']}: expected {expected}, got {got}   (top candidate: {best})")
        if expected is None:
            should_be_empty += 1
            empty_ok += ok
        else:
            should_find += 1
            found += ok

    print(f"\n{found + empty_ok} of {len(notes)} correct ({path}, min score {args.min_score})")
    print(f"  found the right snippet: {found} of {should_find}")
    print(f"  correctly returned no policy: {empty_ok} of {should_be_empty}")


if __name__ == "__main__":
    main()
