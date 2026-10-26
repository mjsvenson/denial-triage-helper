"""Run the classifier on labeled denial notes and report how many it gets right.

Usage: python eval_classify.py [notes JSON path] [--model MODEL_ID]
"""

import argparse
import json
import time
from pathlib import Path
from typing import get_args

import anthropic
from dotenv import load_dotenv

from classify import MODEL, Category, classify

REQUIRED_FIELDS = ("id", "text", "expected_category")

# Dollars per million tokens (input, output), from Anthropic's published pricing.
PRICES = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-5-5": (0.10, 0.50),
}


def check_notes(notes):
    """Return a list of problems with the notes file. An empty list means it is safe to run."""
    if not isinstance(notes, list):
        return ["the file must contain a JSON array of notes"]
    allowed = get_args(Category)
    problems = []
    seen_ids = set()
    for position, note in enumerate(notes, start=1):
        if not isinstance(note, dict):
            problems.append(f"item {position}: not a JSON object")
            continue
        name = str(note.get("id", f"item {position}"))
        for field in REQUIRED_FIELDS:
            if not note.get(field):
                problems.append(f"{name}: missing or empty '{field}'")
        if name in seen_ids:
            problems.append(f"{name}: duplicate id")
        seen_ids.add(name)
        category = note.get("expected_category")
        if category and category not in allowed:
            problems.append(f"{name}: unknown expected_category '{category}'")
    return problems


def main():
    parser = argparse.ArgumentParser(description="Score the classifier on a labeled notes file.")
    parser.add_argument("notes", nargs="?", default="data/denial_notes.json", help="path to a notes JSON file")
    parser.add_argument("--model", default=MODEL, choices=sorted(PRICES), help=f"Claude model ID (default: {MODEL})")
    args = parser.parse_args()

    path = Path(args.notes)
    try:
        # utf-8-sig also accepts files saved with a byte order mark, which some Windows editors add.
        raw = path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        raise SystemExit(f"File not found: {path}")
    try:
        notes = json.loads(raw)
    except json.JSONDecodeError as e:
        # AI chat answers often wrap JSON in Markdown code fences.
        hint = " (remove the ``` lines around the JSON)" if raw.lstrip().startswith("```") else ""
        raise SystemExit(f"{path} is not valid JSON: {e}{hint}")

    problems = check_notes(notes)
    if problems:
        print(f"{path} has {len(problems)} problem(s), so no API calls were made:")
        for problem in problems:
            print(f"  - {problem}")
        raise SystemExit(1)

    load_dotenv()
    client = anthropic.Anthropic()

    correct = 0
    misses = []
    tokens_in = tokens_out = 0
    start = time.perf_counter()
    for note in notes:
        try:
            result, usage = classify(client, note["text"], args.model)
        except ValueError as e:
            # One failed answer should not hide the results for the other notes.
            print(f"FAIL {note['id']}: {e}")
            misses.append((note, None))
            continue
        tokens_in += usage.input_tokens
        tokens_out += usage.output_tokens
        ok = result.category == note["expected_category"]
        correct += ok
        status = "OK  " if ok else "MISS"
        print(f"{status} {note['id']}: expected {note['expected_category']}, got {result.category}")
        if not ok:
            misses.append((note, result))
    elapsed = time.perf_counter() - start

    print(f"\n{correct} of {len(notes)} correct ({args.model}, {path})")

    for note, result in misses:
        print(f"\n{note['id']}: {note['text']}")
        if result is None:
            print("  model gave no valid answer")
        else:
            print(f"  model said {result.category}: {result.explanation}")
        print(f"  label is {note['expected_category']}: {note.get('label_reason', '(no reason given)')}")

    price_in, price_out = PRICES[args.model]
    cost = (tokens_in * price_in + tokens_out * price_out) / 1_000_000
    print(f"\ntokens in: {tokens_in}, out: {tokens_out}, estimated cost: ${cost:.4f}, time: {elapsed:.0f}s")


if __name__ == "__main__":
    main()
