"""Draft a next step for a denied claim from its policy candidates, with one tool for appeal deadlines."""

import json
from pathlib import Path

import anthropic
from pydantic import BaseModel

from retrieve import PAYERS

MODEL = "claude-haiku-5-5"
DEADLINES_PATH = Path(__file__).parent / "data" / "appeal_deadlines.json"
MAX_TOOL_ROUNDS = 3  # a safety limit, so a confused model cannot keep calling tools forever


class Draft(BaseModel):
    next_step: str
    cited_policy_id: str | None
    appeal_deadline_days: int | None


# What Claude sees: the tool's name, when to use it, and the exact input it must send.
DEADLINE_TOOL = {
    "name": "get_appeal_deadline",
    "description": (
        "Look up how many days a payer allows for an appeal or reconsideration request after a denial, "
        "and how to submit it. Use it whenever the next step involves an appeal or reconsideration."
    ),
    "strict": True,  # the API guarantees the input matches this schema
    "input_schema": {
        "type": "object",
        "properties": {"payer": {"type": "string", "enum": PAYERS}},
        "required": ["payer"],
        "additionalProperties": False,
    },
}

SYSTEM_PROMPT = """You draft the next step for a denied insurance claim, for a medical billing specialist.

You receive the denial note, the claim's payer, the denial category chosen by a classifier, and up to two candidate policy snippets from that payer. The candidates come from keyword search, so they can be wrong: a snippet may share words with the note without applying to it, for example when the note mentions a topic only to say it is not the cause.

Rules:
- Cite a candidate only if it applies to the actual cause of this denial. A candidate that covers this type of denial counts as applying even when its rules lead to taking no action. If neither applies, set cited_policy_id to null.
- State payer rules only if they come from the cited snippet or from a tool result. Do not invent deadlines, limits, or requirements.
- If next_step mentions an appeal or a reconsideration request at all, even as a fallback, call get_appeal_deadline for the claim's payer and put the number of days in appeal_deadline_days. Otherwise, do not call the tool and set appeal_deadline_days to null.
- Write next_step as two or three specific, actionable sentences."""


def get_appeal_deadline(payer):
    """The tool's real work, done by our code, not by Claude: read the payer's rules from the data file."""
    deadlines = json.loads(DEADLINES_PATH.read_text(encoding="utf-8"))
    if payer not in deadlines:
        return {"error": f"no appeal deadline on file for {payer}"}
    return {"payer": payer, **deadlines[payer]}


def run_tool(name, tool_input):
    if name == "get_appeal_deadline":
        return get_appeal_deadline(tool_input["payer"])
    return {"error": f"unknown tool {name}"}


def build_request(note_text, payer, classification, candidates):
    """Put each input in its own tags, so Claude can tell the note, the labels, and the snippets apart."""
    parts = [
        f"<note>\n{note_text}\n</note>",
        f"<payer>{payer}</payer>",
        f"<category>{classification.category}</category>",
        f"<category_explanation>{classification.explanation}</category_explanation>",
    ]
    for _, policy in candidates:
        parts.append(f'<candidate id="{policy["id"]}" topic="{policy["topic"]}">\n{policy["text"]}\n</candidate>')
    if not candidates:
        parts.append("<candidates>none found</candidates>")
    return "\n\n".join(parts)


def draft(client: anthropic.Anthropic, note_text, payer, classification, candidates, model: str = MODEL):
    """Run the tool loop. Return (Draft, tool_calls, tokens) or raise ValueError if no valid draft came back.

    tool_calls is a list of (input, output) pairs, one per get_appeal_deadline call.
    """
    messages = [{"role": "user", "content": build_request(note_text, payer, classification, candidates)}]
    tool_calls = []
    tokens = {"input": 0, "output": 0}
    for _ in range(MAX_TOOL_ROUNDS + 1):
        response = client.messages.parse(
            model=model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=[DEADLINE_TOOL],
            messages=messages,
            output_format=Draft,
        )
        tokens["input"] += response.usage.input_tokens
        tokens["output"] += response.usage.output_tokens

        if response.stop_reason != "tool_use":
            if response.stop_reason == "end_turn" and response.parsed_output is not None:
                return response.parsed_output, tool_calls, tokens
            raise ValueError(f"no valid draft (stop_reason: {response.stop_reason})")

        # Claude asked to use the tool. Keep its turn as is, run the tool ourselves,
        # and send the result back so Claude can finish the draft.
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type == "tool_use":
                output = run_tool(block.name, block.input)
                tool_calls.append((block.input, output))
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,  # ties this result to the request it answers
                    "content": json.dumps(output),
                    "is_error": "error" in output,
                })
        messages.append({"role": "user", "content": results})

    raise ValueError(f"no draft after {MAX_TOOL_ROUNDS} tool rounds")
