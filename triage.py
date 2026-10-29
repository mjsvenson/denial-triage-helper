"""Triage one denial note end to end: classify it, retrieve policy candidates, and draft a next step."""

import argparse

import anthropic
from dotenv import load_dotenv

import classify
import draft
from retrieve import PAYERS, find_payer, load_index, retrieve


def main():
    parser = argparse.ArgumentParser(description="Triage one denial note end to end.")
    parser.add_argument("text", help="the denial note text, in quotes")
    parser.add_argument("--payer", choices=PAYERS, help="payer from the claim record (default: look for a payer name in the text)")
    parser.add_argument("--model", default=draft.MODEL, help=f"Claude model ID for both steps (default: {draft.MODEL})")
    args = parser.parse_args()

    payer = args.payer or find_payer(args.text)
    if payer is None:
        raise SystemExit("Could not tell the payer from the note text. Pass --payer.")

    load_dotenv()
    client = anthropic.Anthropic()
    try:
        classification, _ = classify.classify(client, args.text, args.model)
        candidates = retrieve(load_index(), args.text, payer)
        result, tool_calls, _ = draft.draft(client, args.text, payer, classification, candidates, args.model)
    except (anthropic.APIError, ValueError) as e:
        raise SystemExit(f"Triage failed: {e}")

    print(f"payer:       {payer}")
    print(f"category:    {classification.category}")
    print(f"             {classification.explanation}")
    print(f"candidates:  {', '.join(p['id'] for _, p in candidates) or 'none'}")

    cited = next((p for _, p in candidates if p["id"] == result.cited_policy_id), None)
    if result.cited_policy_id is None:
        print("cited:       none of the candidates applies")
    elif cited:
        print(f"cited:       {cited['id']}: {cited['text']}")
    else:
        print(f"cited:       {result.cited_policy_id} (WARNING: not one of the candidates)")

    for tool_input, output in tool_calls:
        print(f"tool call:   get_appeal_deadline({tool_input}) returned {output}")
    if not tool_calls:
        print("tool call:   none")

    print(f"\nnext step:   {result.next_step}")
    if result.appeal_deadline_days is not None:
        print(f"deadline:    {result.appeal_deadline_days} days")


if __name__ == "__main__":
    main()
