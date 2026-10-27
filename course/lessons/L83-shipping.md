---
id: L83
phase: 8
title: "Shipping it - docs, versioning and the public repo"
minutes: 30
concepts: [shipping, versioning, public-evidence, reproducibility]
prereqs: [L73, L60]
paths: [beginner, provider-live]
exercise_file: docs/notes/L83-shipping.md
quiz: L83
---

# L83 - Shipping it: docs, versioning and the public repo

## Why this matters

A measurement that nobody can re-run is a rumour. This repo's whole claim is
that a third party can check it: "run this one command, it costs under a
dollar, and here is every raw call it made". Shipping is the moment that
claim becomes true - and shipping is mostly *packaging*, not code. A reader
who cannot find the command, cannot tell which model version answered, or
cannot see the raw file, will conclude that you made the number up. That
conclusion is usually correct.

## The naive story

You finish the experiment. You write a README. You push it to a public
repository. You tweet the finding.

The naive story assumes that shipping is the last step, after the work is
done. In this repo it is the opposite: the packaging decisions - what gets
committed, what gets versioned, what gets written down as a decision - are
what make the *work* trustworthy in the first place. The raw evidence is
committed because of a shipping rule, not because of a measurement rule.

## What breaks

**Break 1 - the public repo has no evidence in it.** A public repo with only
mock output invites exactly the misreading the mock banner exists to
prevent. The repo's own decision log records the decision: *"The repo starts
private and flips public on Day 5"* - and the reason: *"A public repo with
only mock output invites the exact misreading the mock banner exists to
prevent. A public repo with a real run against a real model is a different
artifact."* Shipping order matters. Evidence first, then the public flip.

**Break 2 - "latest" is not a version.** `JevProvider` defaults to
`model="jev-latest"`, and its docstring lists the pinnable ids `jev-latest |
jev-1.14.0 | jev-1.13.0`. `jev-latest` is a **moving target** - the same
string can answer differently next month, and then your finding is a
comparison between two different models. A finding that cannot name the model
version that produced it cannot be checked. Pin the version; if you must use
`latest`, say so in the write-up and date it.

**Break 3 - the number outlived the artifact.** You publish "accuracy 92%".
Then you edit the case file, then the metric formula. The number now
describes a battery that no longer exists, and the raw file behind it is
useless because you cannot tell which questions produced which answers. The
battery hash in `meta.json` is what makes this detectable - but only if the
run file is committed. Un-committed evidence is not evidence; it is a memory.

**Break 4 - the credential is in the diff.** The most common way a
measurement project dies is not a wrong number - it is a key. This repo's
rule 5 is absolute: credentials come from **environment variables only**,
`.env.example` lists the names with empty values, and the filled `.env` is
never committed. A public repository is a permanent, searchable place; a
leaked key is a bill in someone else's name.

**Break 5 - the decisions evaporate.** Six months from now, a reader (or
you) will want to know *why* the repo is stdlib-only, why the mock ships, why
the raw files are committed, why the repo went public on a particular day.
If the answer only lives in chat history, it is gone. `docs/decision-log.md`
exists for exactly this, and its format is fixed: **date · decision · why ·
what it cost · what would change our mind**. The fourth field is the one
people skip and the one that makes the log useful.

## The story

A reader on the other side of the world is going to decide whether to
believe your number. They have no reason to trust that you ran anything at
all.

So you cannot just send the number. You send a parcel, and inside it there
are four things.

The **repo** - pure standard library, nothing to install. The **command**:
one line to type, the name of the key it wants, and what it will cost before
they spend anything. A check that costs $40 gets the tab closed; a check
that costs well under a dollar gets re-run.

Then the **raw evidence**. Every call you made, one line per call, with the
slip beside it saying which model answered, which questions were asked, and
what it all cost.

And last, the **one finding**: a single sentence somebody else can check,
with the numbers in it and the condition under which you would withdraw it.

Two small things ride along. A **version** - "latest" is a moving target, so
pin it or date it. And the **decision log**: the date, the choice, the reason,
and what would change your mind, written down at the time rather than
remembered later.

Ship the parcel. Let them open it.

## The real thing

**Shipping** this repo means four things, and all four are in the repo
already:

1. **A command a stranger can run.** One line, on a bare Python, no install
   step. `README.md` says it plainly: *"Pure Python standard library. No `pip
   install`, no virtualenv, no dependencies."* And: *"A full battery sweep
   costs **well under $1**. That is the whole point: the experiment is cheap
   enough to re-run on every model release."* A reader must be able to see
   the cost *before* they spend it - which is why `cmd_run()` prints
   `price : $X/Mtok` before the first call.
2. **The raw evidence, committed.** `runs/` holds `<run_id>.jsonl` (one line
   per call), `<run_id>.meta.json` (the provenance: provider, price, cases,
   repeats, battery hash, timestamps, cost, spend cap, uuid) and `<run_id>.md`
   (the derived report). The decision log has an entry for this: *"Raw run
   files are committed"*, with the reason *"The claim of this repo is that
   evidence should travel with the number. A benchmark table without its raw
   calls is marketing."*
3. **An explicit statement of what is not evidence.** `AGENTS.md` hard rule 4:
   *"The mock is not evidence. `MockProvider` is an offline simulator for
   testing the harness. Its numbers must never be published as a model
   evaluation."* The same rule shows up in three more places - the mock
   banner at the top of every mock report, the `note` column in the
   `providers` table, and the `mock-is-not-evidence` entry in
   `AI-CONTEXT.md`'s `verified_facts`. Four restatements of one rule is not
   redundancy; it is the price of a public claim.
4. **A decision log.** `docs/decision-log.md`, with one entry per
   significant choice, in the format **date · decision · why · what it cost ·
   what would change our mind**. The "what would change our mind" field is
   what makes a decision falsifiable instead of a preference.

**Versioning** in this repo means three different things, and you need all
three:

- **Code version.** `AI-CONTEXT.md` carries `version: 0.1.0`,
  `license: Apache-2.0`, `python_requires: ">=3.9"` and `dependencies: []`.
  The licence matters for a public repo: Apache-2.0 matches the models it
  measures, so a reader can reuse the harness without a legal question.
- **Model version.** Pin the provider spec: `jev:jev-1.14.0` is a different
  provider from `jev:jev-latest`, and the provider name lands in
  `meta.json` and in every report header as `jev:<model>`. Your finding
  names one of these.
- **Evidence version.** Every run has a run id of the form
  `<YYYYMMDD>-<HHMMSS>-<label>`, a 12-character `battery_hash`, and a
  `uuid`. The hash says *which questions* were run; the uuid says *which
  run*; the timestamp says *when*. A finding cites all three.

**Public evidence** is the whole product. The contract is: *the repo, the
command, the raw evidence, and the one finding*. `AI-CONTEXT.md` shows the
pattern for how a fact is recorded - `id`, `claim`, `evidence`,
`verified_on` - and the `evidence` field always points at a **file**, not at
a memory:

```
- id: mock-is-not-evidence
  claim: "MockProvider output is a harness test, never a model evaluation."
  evidence: "decisionarena/providers.py"
  verified_on: 2026-10-25
```

**Reproducibility** is the test of shipping: a reader, on a different
machine, with their own key, must land in the same place. Three things make
that possible, and all three are already in the harness:

- **stdlib only** - no dependency matrix, no version drift (decision log
  entry: *"A dependency is a failure mode with a licence, a CVE feed and a
  version matrix."*);
- **a fixed wire protocol** - `noul` / `choice` / `score`, normalised at the
  adapter boundary, so the metrics never know which vendor they are looking
  at;
- **the spend cap** - `--spend-cap`, default `0.25`, so a reader who forgets
  to think cannot spend much by accident.

And one rule about the raw files that is easy to miss: `AI-CONTEXT.md` lists
`runs/*.jsonl — committed raw evidence, append-only` under `do_not_touch`.
**Append-only.** Never edit a raw file to tidy it, never delete one. The
repo never deletes.

## In this repo

- `README.md` - the reader's entry point: "Zero-install", the pure-stdlib
  promise, the four commands table, the batteries table, the output contract
  ("Commit the raw evidence. A number without its raw calls behind it is
  marketing"), the live-credentials section (env vars only) and the
  `Apache-2.0` licence.
- `AGENTS.md` - the eight hard rules: stdlib only; never delete; evidence
  before claims; the mock is not evidence; never log or commit secrets; one
  writer per file; update `AI-CONTEXT.md` in the same change; the learner
  writes the exercise code; and the course gate.
- `docs/decision-log.md` - the decision log itself, with the format line
  "date · decision · why · what it cost · what would change our mind", and
  the entries for stdlib-only, the labelled mock, the canonical answer
  shape, committing raw runs, one-client-three-providers, the Laya venv, and
  the private-then-public flip.
- `AI-CONTEXT.md` - the machine-readable current state: `version`,
  `license`, `python_requires`, `dependencies: []`, the `verified_facts`
  list (each with `claim`, `evidence` file path and `verified_on` date), and
  the `do_not_touch` list that includes `runs/*.jsonl — committed raw
  evidence, append-only`.
- `runs/` - the committed evidence: `<run_id>.jsonl`, `<run_id>.meta.json`,
  `<run_id>.md` and `swap-report.md`, with run ids like
  `20261025-040448-mock`.
- `runs/20261025-040448-mock.meta.json` - the provenance record:
  `"provider": "mock"`, `"price_per_mtok": 0.042`, `"cases": 5`,
  `"repeats": 1`, `"battery_hash": "fd9fb7c25685"`, `"cost_usd": 3.28e-05`,
  `"spend_cap_usd": 0.25`, `"uuid": "3dfd4c41-2b90-4eb7-88d3-1345c63feaf0"`.
- `decisionarena/report.py` - `run_report()` puts the SIMULATED RUN banner on
  every mock report, so the warning travels with the artifact even if the
  report is copied out of the repo on its own.
- `decisionarena/harness.py` - `run_battery()` writes the `.jsonl` and the
  `.meta.json` before the report is ever rendered.
- `decisionarena/cli.py` - `cmd_run()` prints the price before the run, and
  prints the path of the raw evidence after it:
  `raw evidence: runs/<run_id>.jsonl`.
- `.env.example` - every credential name, with empty values.
- `tools/course_check.py` - the gate that keeps a broken lesson from
  reaching a learner; the same idea, applied to teaching material.

## Your turn

Write a file `docs/notes/L83-shipping.md`. It is the shipping checklist for
this repo as a **public, checkable artifact** - the thing you would hand to a
stranger with a laptop and a key.

It must contain:

- a section `## The one command a stranger runs` - the exact command (with
  the provider spec and battery), what it prints, and what it costs, with the
  cost taken from a run you made or from the price in the code
- a section `## What lands on disk` - the three files a run writes and which
  one is derived, plus the actual `battery_hash` and `run_id` from one run
- a section `## What is evidence and what is not` - one sentence each on (a)
  the committed raw runs, (b) the mock, quoting the rule from `AGENTS.md` in
  your own words, (c) the vendor benchmark tables
- a section `## Versioning` - how a reader knows which model answered (the
  pinnable provider specs), which code version this is, and which three
  identifiers from `meta.json` your finding must quote
- a section `## Decisions` - **one new entry in the format of
  `docs/decision-log.md`**: date · decision · why · what it cost · what would
  change our mind. It must be about a choice *you* made while doing this
  phase (which battery, which thresholds, which provider, how many repeats)
  and it must be honest about the cost
- a section `## Reviewer's checklist` - six or fewer bullets a reviewer can
  run through in five minutes, each one checkable: for example "the run id
  in the finding exists in `runs/`", "the `battery_hash` in the finding
  matches the `.meta.json`", "no file in the diff contains a credential"

Inputs: the repo's `README.md`, `AGENTS.md`, `docs/decision-log.md`,
`AI-CONTEXT.md`, and one run you made yourself.

Expected output: the six sections above, about 500 words, with every
identifier in it copied from a real file - not invented.

**Hint:** every fact a reviewer needs is already written down somewhere in
this repo; shipping is mostly *copying the right lines into the right
place*. The decision-log entry is the only part you have to author.

**Do not** include any API key, account id or token anywhere in this file,
and check that none of the files you list contains one.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. What are the four things a public, checkable artifact of this repo has to
   contain, and where in the repo does each one already live?
2. Why does `jev-latest` make a finding harder to check than
   `jev:jev-1.14.0`, even though both are "the same provider"?
3. Why does the decision log have a "what would change our mind" field, and
   why does the "what it cost" field matter as much?
4. What is the difference between a report in `runs/` and a raw `.jsonl` in
   `runs/`, when a reader wants to check your number?

## Artifact

The artifact **is** `docs/notes/L83-shipping.md` - the six sections above.
Before you commit it, do the reviewer's checklist yourself against your own
file: open every file you named, confirm every identifier you quoted, and
confirm there is no credential in the text.

Then commit it. The artifact is the proof that this repo can be picked up by
a stranger, not the proof that you read the README.
