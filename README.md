# Denial Triage Helper

A small command-line learning project that triages invented insurance claim denial notes with an LLM.

**Status: in progress.** Only the items under "What works so far" exist. Everything else is a plan.

## Planned

1. Classify the denial reason into a category (structured JSON output)
2. Retrieve the most relevant snippet from a small set of invented payer policy notes
3. Draft a suggested next step, using one tool call (for example, looking up an invented payer's appeal deadline)
4. Evaluate against a handful of test cases and report how many it gets right

Stack: Python, the Anthropic API, command line.

## What works so far

Nothing yet. Project setup only.

## Data

All data is synthetic. No real patient, payer, or employer data is used.

## How it was built

Built with AI assistance. Claude (Anthropic) is used as a coding assistant, working in small steps where I make the design decisions. Commits that Claude helped write include a `Co-Authored-By` line. No frameworks such as LangChain or LlamaIndex are used unless this README says otherwise.
