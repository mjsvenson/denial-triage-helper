# Denial Triage Helper

A small command-line learning project that triages invented insurance claim denial notes with an LLM.

**Status: in progress.** Only the items under "What works so far" exist. Everything else is a plan.

## Planned

1. Classify the denial reason into a category (structured JSON output) (working, see below)
2. Retrieve the most relevant snippet from a small set of invented payer policy notes
3. Draft a suggested next step, using one tool call (for example, looking up an invented payer's appeal deadline)
4. Evaluate against a handful of test cases and report how many it gets right (started, see below)

Stack: Python, the Anthropic API, command line.

## What works so far

- `classify.py` sends one denial note to Claude and gets back a validated category and a short explanation. The output is checked against a Pydantic model, so the category is always one of the seven in [docs/denial-categories.md](docs/denial-categories.md).
- `eval_classify.py` runs the classifier on labeled notes and reports how many it gets right. Latest run: 14 of 14 on `data/denial_notes.json` with `claude-opus-5-5`. Those notes were written alongside the prompt, so treat that score as optimistic. A held-out test set written separately is still to come.
- Synthetic data in `data/`: 14 labeled denial notes and 9 invented payer policy snippets.

## Try it

Requires Python 3.11 or later and an Anthropic API key.

```
python -m venv .venv
.venv\Scripts\activate            (Windows; on macOS or Linux: source .venv/bin/activate)
pip install -r requirements.txt
cp .env.example .env              (then put your API key in .env)
python classify.py "No prior authorization on file for this procedure."
python eval_classify.py
```

## Data

All data is synthetic. No real patient, payer, or employer data is used.

## How it was built

Built with AI assistance. Claude (Anthropic) is used as a coding assistant, working in small steps where I make the design decisions. Commits that Claude helped write include a `Co-Authored-By` line. No frameworks such as LangChain or LlamaIndex are used unless this README says otherwise.

## License

MIT. See [LICENSE](LICENSE).
