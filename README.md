# Denial Triage Helper

A small command-line learning project that triages invented insurance claim denial notes with an LLM.

**Status: in progress.** Only the items under "What works so far" exist. Everything else is a plan.

## Planned

1. Classify the denial reason into a category (structured JSON output) (working, see below)
2. Retrieve the most relevant snippet from a small set of invented payer policy notes (second version, see below)
3. Draft a suggested next step, using one tool call (for example, looking up an invented payer's appeal deadline) (working, see below)
4. Evaluate against a handful of test cases and report how many it gets right (working, see below)

Stack: Python, the Anthropic API, command line.

## What works so far

- `classify.py` sends one denial note to Claude and gets back a validated category and a short explanation. The output is checked against a Pydantic model, so the category is always one of the seven in [docs/denial-categories.md](docs/denial-categories.md).
- `eval_classify.py` runs the classifier on labeled notes and reports how many it gets right, along with token usage, estimated cost, and run time. `--model` picks which Claude model to test. It checks the notes file for missing fields and unknown labels before making any API calls.
- `retrieve.py` ranks the payer policy snippets against a note using TF-IDF keyword search written by hand (no search library). It searches only the claim's payer, which comes from the claim record rather than the note text, and returns the top 2 candidates. Deciding which candidate applies, if any, is left to the next step.
- `eval_retrieve.py` checks whether each note's `expected_policy_id` is among the candidates (recall at 2). It makes no API calls, so it is free and gives the same result every run.
- `draft.py` drafts the next step. It gives Claude the note, the classifier's category, and the retrieval candidates, and offers one tool, `get_appeal_deadline`, which our own code answers from `data/appeal_deadlines.json`. Claude must say which candidate it cites, or that none applies, and may state payer rules only from the cited snippet or the tool result. The tool loop is written by hand, so each step of tool use is visible in the code.
- `triage.py` runs the whole pipeline on one note and prints the category, the candidates, the cited policy, any tool call, and the next step.
- `eval_draft.py` runs the pipeline on labeled notes, scores the citations and deadlines automatically, flags steps that mention an appeal without a deadline lookup, and prints each draft for a person to check.
- Synthetic data in `data/`: 14 labeled development notes (`denial_notes.json`), 9 held-out notes (`heldout_notes.json`), 8 fresh notes scored once after every prompt was frozen (`fresh_notes.json`), 9 invented payer policy snippets (`payer_policies.json`), and invented appeal deadlines for each payer (`appeal_deadlines.json`).

## Evaluation results

### Classifier

| | Haiku 5.5 | Sonnet 5.5 | Opus 5.5 |
|---|---|---|---|
| Development set (14 notes, written alongside the prompt) | 14 of 14 | 14 of 14 | 14 of 14 |
| Held-out set (9 notes) | 9 of 9 | 9 of 9 | 9 of 9 |
| Fresh set (8 notes, scored as part of the drafting run below) | 8 of 8 | 8 of 8 | 8 of 8 |
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

### Drafting (development runs, before the prompt freeze)

| | Development (14 notes) | Earlier held-out, now development (9 notes) |
|---|---|---|
| Citation correct overall | 14 of 14 | 9 of 9 |
| Cited the right snippet | 12 of 12 | 4 of 4 |
| Correctly cited no policy | 2 of 2 | 5 of 5 |
| Deadline matched the data file, when the tool was called | 6 of 6 | 3 of 3 |

- On holdout-07, keyword search ranked the prior authorization snippet first, but the drafting step cited the corrected-claims snippet because the note says the authorization was approved. That is the case the first version of retrieval missed.
- The first run missed note-11, a true duplicate of a claim already paid: the draft said to take no action but cited no policy. Two prompt clarifications, made on this development data, fixed it. A policy that covers this type of denial now counts as applying even when the step is to take no action, and any mention of an appeal or reconsideration requires a deadline lookup.
- The appeal-without-lookup flag is keyword based, so it also fires on phrases like "rather than appealing". The one flag in this run was that kind of false positive, which is why flagged drafts are checked by hand.
- Both sets were used during development, so these numbers are optimistic.

### Drafting (fresh notes, scored once after the freeze)

The classifier prompt, retrieval, and the drafting prompt were all frozen before this run. Like the held-out notes, the fresh notes were drafted and first labeled with a separate AI tool, then reviewed by me.

| | Haiku 5.5 | Sonnet 5.5 | Opus 5.5 |
|---|---|---|---|
| Citation correct (all 8 were "no policy applies") | 8 of 8 | 8 of 8 | 8 of 8 |
| Classifier category correct | 8 of 8 | 8 of 8 | 8 of 8 |
| Deadline matched the data file, when the tool was called | 3 of 3 | 4 of 4 | 4 of 4 |
| Cost of the run | $0.0052 | $0.0990 | $0.1901 |

- Every fresh note turned out to be a case where the payer has no policy on that topic. The request used to generate them asked for at least 3 such notes, and those were the only payer and topic combinations it named. So this run tested rejecting candidates that do not apply, not picking the right one. Evidence for picking the right snippet comes only from the development runs above.
- The rejections were not trivial. Most notes contain a misleading keyword, and on fresh-06 a Quillfield duplicate came with Quillfield's corrected-claims policy as a candidate while the note itself mentions the corrected-claim process. All three models still cited no policy, and none borrowed another payer's rules.
- By the rule set before the run (use the cheapest model that ties the best citation score), `claude-haiku-5-5` stays the default.
- Reading the drafts turned up differences the automatic scores miss. On fresh-08, where the denial reason is still unknown, Sonnet and Opus said to watch the 45-day appeal window while waiting for the payer's written determination, and Haiku did not. Haiku's fresh-06 draft also ends with a muddled sentence.
- Every draft from this run, for all three models, is in [results/fresh-notes-run.md](results/fresh-notes-run.md).

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

Triage one note end to end (two or three API calls), then score the drafting step on the labeled notes:

```powershell
.venv\Scripts\python.exe triage.py "Claim received after the filing limit. CARC 29." --payer "Bramblecrest Insurance"
```

```powershell
.venv\Scripts\python.exe eval_draft.py
```

The scripts that call Claude (`classify.py`, `triage.py`, `eval_classify.py`, and `eval_draft.py`) take `--model` to choose the model (default `claude-haiku-5-5`), for example `--model claude-opus-5-5`. The eval scripts accept a path to a different notes file, and the retrieval scripts take `--k` to change how many candidates are returned. Run any script with `--help` to see all options.

## Data

All data is synthetic. No real patient, payer, or employer data is used.

## How it was built

Built with AI assistance. Claude (Anthropic) is used as a coding assistant, working in small steps where I make the design decisions. Commits that Claude helped write include a `Co-Authored-By` line. No frameworks such as LangChain or LlamaIndex are used unless this README says otherwise.

## License

MIT. See [LICENSE](LICENSE).
