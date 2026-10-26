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
- `eval_classify.py` runs the classifier on labeled notes and reports how many it gets right, along with token usage, estimated cost, and run time. `--model` picks which Claude model to test. Latest runs: 14 of 14 on `data/denial_notes.json` with each of `claude-haiku-5-5`, `claude-sonnet-5-5`, and `claude-opus-5-5`. Those notes were written alongside the prompt, so treat that score as optimistic. A held-out test set written separately is still to come.
- Synthetic data in `data/`: 14 labeled denial notes and 9 invented payer policy snippets.

## Try it

You need Python (tested with 3.11) and an Anthropic API key. The commands below call the virtual environment's own Python by its path, so there is no need to activate the environment first.

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

macOS or Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

Then open `.env` and replace `your-key-here` with your API key. `.env` is git-ignored, so the key stays on your machine.

Classify one note (on macOS or Linux, use `.venv/bin/python` in place of `.venv\Scripts\python.exe`):

```powershell
.venv\Scripts\python.exe classify.py "No prior authorization on file for this procedure."
```

Run the evaluation on the labeled notes:

```powershell
.venv\Scripts\python.exe eval_classify.py
```

Both scripts take `--model` to choose the Claude model (default `claude-opus-5-5`), for example `--model claude-haiku-5-5`. `eval_classify.py` also accepts a path to a different notes file. Run either script with `--help` to see all options.

## Data

All data is synthetic. No real patient, payer, or employer data is used.

## How it was built

Built with AI assistance. Claude (Anthropic) is used as a coding assistant, working in small steps where I make the design decisions. Commits that Claude helped write include a `Co-Authored-By` line. No frameworks such as LangChain or LlamaIndex are used unless this README says otherwise.

## License

MIT. See [LICENSE](LICENSE).
