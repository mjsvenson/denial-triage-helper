"""Run the classifier on labeled denial notes and report how many it gets right.

Usage: python eval_classify.py [path to notes JSON]   (default: data/denial_notes.json)
"""

import json
import sys
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
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/denial_notes.json")
    notes = json.loads(path.read_text(encoding="utf-8"))

    load_dotenv()
    client = anthropic.Anthropic()

    correct = 0
    misses = []
    tokens_in = tokens_out = 0
    for note in notes:
        try:
            result, usage = classify(client, note["text"])
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

    print(f"\n{correct} of {len(notes)} correct ({MODEL}, {path})")

    for note, result in misses:
        print(f"\n{note['id']}: {note['text']}")
        if result is None:
            print("  model gave no valid answer")
        else:
            print(f"  model said {result.category}: {result.explanation}")
        print(f"  label is {note['expected_category']}: {note.get('label_reason', '(no reason given)')}")

    price_in, price_out = PRICES.get(MODEL, (0.0, 0.0))
    cost = (tokens_in * price_in + tokens_out * price_out) / 1_000_000
    print(f"\ntokens in: {tokens_in}, out: {tokens_out}, estimated cost: ${cost:.4f}")


if __name__ == "__main__":
    main()
