# Denial Triage Helper

A small command-line learning project that triages invented insurance claim denial notes with an LLM.

**Status: in progress.** Only the items under "What works so far" exist. Everything else is a plan.

## Planned

1. Classify the denial reason into a category (structured JSON output) (working, see below)
2. Retrieve the most relevant snippet from a small set of invented payer policy notes (second version, see below)
3. Draft a suggested next step, using one tool call (for example, looking up an invented payer's appeal deadline)
4. Evaluate against a handful of test cases and report how many it gets right (working, see below)

Stack: Python, the Anthropic API, command line.

## What works so far

- `classify.py` sends one denial note to Claude and gets back a validated category and a short explanation. The output is checked against a Pydantic model, so the category is always one of the seven in [docs/denial-categories.md](docs/denial-categories.md).
- `eval_classify.py` runs the classifier on labeled notes and reports how many it gets right, along with token usage, estimated cost, and run time. `--model` picks which Claude model to test. It checks the notes file for missing fields and unknown labels before making any API calls.
- `retrieve.py` ranks the payer policy snippets against a note using TF-IDF keyword search written by hand (no search library). It searches only the claim's payer, which comes from the claim record rather than the note text, and returns the top 2 candidates. Deciding which candidate applies, if any, is left to the next step.
- `eval_retrieve.py` checks whether each note's `expected_policy_id` is among the candidates (recall at 2). It makes no API calls, so it is free and gives the same result every run.
- Synthetic data in `data/`: 14 labeled development notes (`denial_notes.json`), 9 held-out notes (`heldout_notes.json`), and 9 invented payer policy snippets (`payer_policies.json`).

## Evaluation results

### Classifier

| | Haiku 5.5 | Sonnet 5.5 | Opus 5.5 |
|---|---|---|---|
| Development set (14 notes, written alongside the prompt) | 14 of 14 | 14 of 14 | 14 of 14 |
| Held-out set (9 notes) | 9 of 9 | 9 of 9 | 9 of 9 |
| Cost of the held-out run | $0.0013 | $0.0243 | $0.0483 |

- The held-out notes were drafted and first labeled with a separate AI tool, then reviewed by me. They were scored only after the classifier prompt was frozen. They are now public in `data/heldout_notes.json`, so any future prompt change needs a fresh held-out set to be scored fairly.
- One held-out note was dropped before final scoring as ambiguous: its text described bundling while its label said duplicate.
- The default model is `claude-haiku-5-5`. The rule was set before scoring: use Haiku if it ties the best held-out score. It did, at about 1/37 of the cost of Opus on this run.
- Limits: both sets are small and cleanly worded, and the held-out set has no `other_or_unclear` notes. Treat these scores as a sanity check, not a measure of real-world accuracy.

### Retrieval (first version)

| | Development (14 notes) | Held-out (9 notes) |
|---|---|---|
| Correct overall | 14 of 14 | 4 of 9 |
| Found the right snippet | 12 of 12 | 3 of 4 |
| Correctly returned no policy | 2 of 2 | 1 of 5 |

- The held-out retrieval labels were committed before any retrieval code existed. The 0.16 cutoff was set from the development notes before the single held-out run, so the development score is optimistic.
- Why the held-out run missed:
  - Six of the nine held-out notes never name their payer, only a claim number, so the payer filter could not run. Three of those notes matched another payer's policy. (Every development note names its payer, so this never showed up there.)
  - Keyword search cannot read negation or context. holdout-03 says the denial is "not due to eligibility" and matched the eligibility policy. holdout-07 mentions an approved authorization and matched the prior authorization policy instead of corrected claims. The classifier got both notes right.
  - The development notes had no case where a payer simply has no policy on the topic, so the cutoff never learned that case.
- Any fix chosen after seeing these misses has to be measured on fresh notes, not on this held-out set.

### Retrieval (second version)

Changes made in response to the first version's misses:

- The payer comes from the claim record (each note's `payer` field), not from the note text.
- Retrieval returns the top 2 candidates instead of one answer or none. The drafting step, which uses an LLM that can read negation and context, will decide which candidate applies or that none does.

| | Development (14 notes) | Held-out (9 notes) |
|---|---|---|
| Right snippet in the top 2 | 12 of 12 | 4 of 4 |
| Notes with no right snippet (scored in the drafting step) | 2 | 5 |

- The held-out result is not a clean measure, because these changes were chosen after seeing the held-out misses. Fresh notes are needed for that.
- Each payer has only 3 snippets, so finding the right one in the top 2 is easy. The harder test is whether the drafting step picks the right candidate, or correctly rejects both.

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

Run the evaluation on the development notes, then on the held-out notes:

```powershell
.venv\Scripts\python.exe eval_classify.py
```

```powershell
.venv\Scripts\python.exe eval_classify.py data/heldout_notes.json
```

Find the candidate policy snippets for one note, then score retrieval (both are free, with no API calls):

```powershell
.venv\Scripts\python.exe retrieve.py "The claim arrived after the filing limit." --payer "Bramblecrest Insurance"
```

```powershell
.venv\Scripts\python.exe eval_retrieve.py data/heldout_notes.json
```

`classify.py` and `eval_classify.py` take `--model` to choose the Claude model (default `claude-haiku-5-5`), for example `--model claude-opus-5-5`. Both eval scripts accept a path to a different notes file, and the retrieval scripts take `--k` to change how many candidates are returned. Run any script with `--help` to see all options.

## Data

All data is synthetic. No real patient, payer, or employer data is used.

## How it was built

Built with AI assistance. Claude (Anthropic) is used as a coding assistant, working in small steps where I make the design decisions. Commits that Claude helped write include a `Co-Authored-By` line. No frameworks such as LangChain or LlamaIndex are used unless this README says otherwise.

## License

MIT. See [LICENSE](LICENSE).
