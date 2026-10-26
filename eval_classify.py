"""Run the classifier on labeled denial notes and report how many it gets right.

Usage: python eval_classify.py [notes JSON path] [--model MODEL_ID]
"""

import argparse
import json
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from classify import MODEL, classify

# Dollars per million tokens (input, output), from Anthropic's published pricing.
PRICES = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-5-5": (0.10, 0.50),
}


def main():
    parser = argparse.ArgumentParser(description="Score the classifier on a labeled notes file.")
    parser.add_argument("notes", nargs="?", default="data/denial_notes.json", help="path to a notes JSON file")
    parser.add_argument("--model", default=MODEL, choices=sorted(PRICES), help=f"Claude model ID (default: {MODEL})")
    args = parser.parse_args()

    path = Path(args.notes)
    notes = json.loads(path.read_text(encoding="utf-8"))

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
