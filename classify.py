"""Classify a denial note into one of the categories in docs/denial-categories.md."""

import sys
from typing import Literal

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel

MODEL = "claude-opus-5-5"

# Keep in sync with docs/denial-categories.md.
Category = Literal[
    "billing_or_coding_error",
    "authorization_issue",
    "medical_necessity",
    "eligibility_or_coverage",
    "timely_filing",
    "duplicate_claim",
    "other_or_unclear",
]


class Classification(BaseModel):
    category: Category
    explanation: str


SYSTEM_PROMPT = """You classify insurance claim denial notes for a medical billing team.

Choose exactly one category for the main reason the claim was denied:

- billing_or_coding_error: the claim has missing or wrong data, or a code or modifier problem.
- authorization_issue: required prior approval is absent or was exceeded.
- medical_necessity: the payer says the service was not medically necessary.
- eligibility_or_coverage: the patient was not covered on the date of service, could not be identified as insured, or the payer is not the responsible one.
- timely_filing: the filing deadline passed.
- duplicate_claim: the payer believes it already received this claim.
- other_or_unclear: the note does not clearly fit any category above.

Rules:
- Choose by the cause stated in the note. Do not assume causes the note does not mention.
- If the note does not clearly fit a category, choose other_or_unclear instead of guessing.
- In the explanation, use one or two sentences to point to the words in the note that support the category."""


def classify(client: anthropic.Anthropic, note_text: str):
    """Return (Classification, usage) for one note, or raise ValueError if no valid answer came back."""
    response = client.messages.parse(
        model=MODEL,
        max_tokens=4096,  # room for the model's thinking plus the short JSON answer
        system=SYSTEM_PROMPT,
        # The tags mark where the note starts and ends, so its text is read as data.
        messages=[{"role": "user", "content": f"<note>\n{note_text}\n</note>"}],
        output_format=Classification,
    )
    if response.stop_reason != "end_turn" or response.parsed_output is None:
        raise ValueError(f"no valid classification (stop_reason: {response.stop_reason})")
    return response.parsed_output, response.usage


def main():
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python classify.py "denial note text"')
    load_dotenv()
    client = anthropic.Anthropic()
    try:
        result, usage = classify(client, sys.argv[1])
    except anthropic.APIError as e:
        raise SystemExit(f"API error: {e}")
    print(result.model_dump_json(indent=2))
    print(f"tokens in: {usage.input_tokens}, out: {usage.output_tokens}")


if __name__ == "__main__":
    main()
