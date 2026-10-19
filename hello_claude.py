"""Hello-world call to the Claude API. Proves the key, the SDK, and the network all work."""

import anthropic
from dotenv import load_dotenv

MODEL = "claude-opus-5-5"

load_dotenv()  # copies the settings in .env into environment variables
client = anthropic.Anthropic()  # finds ANTHROPIC_API_KEY in the environment

try:
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,  # a ceiling on the reply length, not a target
        messages=[{"role": "user", "content": "Say hello in one short sentence."}],
    )
except anthropic.AuthenticationError:
    raise SystemExit("The API key was rejected. Check the value in .env.")
except anthropic.APIStatusError as e:
    raise SystemExit(f"The API returned an error ({e.status_code}): {e.message}")
except anthropic.APIConnectionError:
    raise SystemExit("Could not reach the API. Check your internet connection.")

# The reply is a list of content blocks, and not every block is text.
for block in response.content:
    if block.type == "text":
        print(block.text)

print(f"model: {response.model}")
print(f"stop_reason: {response.stop_reason}")
print(f"tokens in: {response.usage.input_tokens}, out: {response.usage.output_tokens}")
