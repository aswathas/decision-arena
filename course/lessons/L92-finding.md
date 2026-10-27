---
id: L92
phase: 9
title: "Writing a finding other people can check"
minutes: 35
concepts: [finding, reproducibility, claim-status, limitations]
prereqs: [L91, L73]
paths: [beginner, provider-live]
exercise_file: docs/notes/L92-finding.md
quiz: L92
---

# L92 - Writing a finding other people can check

## Why this matters

A run produces numbers. A **finding** is a claim about the world that those
numbers support, written so that somebody else - on another machine, with
their own key, in their own time - can decide whether you are right. The
difference between the two is not style. It is that a finding states its own
weaknesses before somebody else finds them, and points at the file where the
evidence lives.

## The naive story

The run is done. The mean spread was 0.42 with 4 flips out of 9 questions.
You write: "**Format friction is a serious problem.** Models are heavily
influenced by the serialisation of their input state, and benchmarks that use
a single format are measuring the benchmark author's taste."

Every sentence in that paragraph is unfalsifiable, and one of them is
probably wrong. "Serious" is not a number. "Heavily influenced" is not a
number. "Benchmarks" is not a number - *which* benchmarks, measured how? And
"the models" is plural: you measured one model, on one battery, on one day.
The paragraph reads like a finding and behaves like a poster.

## What breaks

**Break 1 - the claim is not a single checkable sentence.** "Format friction
is a serious problem" cannot be checked, because "serious" has no number and
no comparison. A checkable sentence names the measurement, the number and the
boundary: *on this battery, with this provider, the probability moved by this
much, and this many questions changed side.* Somebody can then open the run
file and count.

**Break 2 - the evidence is not pointed at.** The paragraph mentions no run
id, no file, no date. A reader who wants to check it has nowhere to start,
and a claim with nowhere to start is a claim, not a measurement. This repo's
rule is blunt: *a number without its raw `runs/*.jsonl` behind it is
marketing.* The number in the finding and the file in the repo must be
linked by an identifier - the run id - and the raw file must be committed.

**Break 3 - the model version is missing.** "The model" is not a subject.
`jev-latest` and `jev:jev-1.14.0` are different subjects and they are
recorded differently: the provider name in `meta.json` is `jev:<model>`, and
the run id carries the provider name too. A finding that names the provider
but not the model version cannot be re-checked in six months.

**Break 4 - the limitations are missing, so they get found for you.** Every
result has boundaries, and the ones you did not state will be stated by
somebody else, less kindly. The published prior work in this field shows how
it is done: the independent harness's injection result is recorded as
**VERIFIED (two probes only)** - verified, and immediately bounded. Its
labelled accuracy of 96% / 92% -> 83% / 79% is flagged **VERIFIED but
small-n**, because it came from 24 author-labelled cases. Those parenthetical
labels are the difference between a result and a claim.

**Break 5 - measurement and inference are mixed together.** "The model is
sensitive to input shape" is an *inference* - a generalisation beyond the
cases you ran. "The `noul` probability for `is_urgent` moved 0.9271 ->
0.3278 -> 0.0 across the three serialisations of `fmt-001-refund`" is a
*measurement*. Put them in the same paragraph and the reader cannot tell
which parts are checkable. Worse, the inference inherits the credibility of
the measurement without earning it.

## The story

A measurement is a number in a file. A finding is a sentence somebody
else can disagree with - and that means the sentence has to carry its own
instructions for checking it.

So the sentence comes first, and it is a single sentence. Not "format
friction is a serious problem", because "serious" has no number in it.
Instead: on this battery, with this many cases and this many questions, this
metric came out at this value, and this many questions changed side.

Next, the evidence, and the evidence is always a file. The run id, the
battery hash that proves the cases were the same ones, the provider and the
model version - "the model" is not a subject, and `jev-latest` and
`jev:jev-1.14.0` are two different subjects.

Then the part that makes it useful to a stranger: how to check it. The
command, the key it needs, what it costs, and which number to look at when
it finishes.

Then draw a line between two lists: what you measured, and what you
inferred. The second list is where you are allowed to be interesting. It
just has to be labelled.

Then your own limits, and the status word.

## The real thing

A finding in this repo has six parts. Here is the shape, with the real
identifiers from a committed run:

**1. The claim, in one checkable sentence.**

> On `cases/format_variants.json` (3 cases, 9 questions), the mock provider's
> `noul` answers moved by a mean spread of 0.42 across the prose / flat /
> nested serialisations of the same content, and 4 of 9 questions changed
> side of 0.5.

That sentence names the battery, the denominators, the metric, the numbers
and the boundary. A reader can decide whether it is true. Note that it says
"the mock provider" - because that is what was measured. If it were a live
provider, the sentence would name the model version instead.

**2. The evidence, with identifiers.** Take them from the committed files:
the `run_id` (`20261025-040448-friction-mock`), the `battery_hash` from the
matching `meta.json`, the provider name, the model version, the date, the
number of cases, the number of repeats, the cost, and the path of the raw
file. `AI-CONTEXT.md` shows the house style for exactly this - each fact
carries `claim`, `evidence` (a **file path**) and `verified_on` (a date).
The evidence field is always a file. Never "I ran it last week".

**3. How to check it.** The command, the cost, and what to look at when it
runs. Something like: `python -m decisionarena friction --provider
<spec>` - it needs `<ENV_VAR>` set on your machine, it costs about
`$0.0001` on this battery, and the number to look at is `flips_at_0.5` in
`runs/<run_id>.json`. This is the part that makes the finding
**reproducible** rather than merely true.

**4. What you measured, and what you inferred.** Two separate lists, never
mixed. Measured: the numbers in the raw file. Inferred: everything else -
the mechanism you think caused them, the claim about other models, the claim
about your production system. The second list is where you are allowed to be
interesting; it just has to be labelled.

**5. The limitations, stated by you.** At least three, and each one specific
enough to be useful:
- the **n**: three cases and nine questions is a small denominator; the
  published prior work flags its own 24-case accuracy as small-n for the same
  reason;
- the **battery**: `cases/format_variants.json` says in its own description
  that it has no labels, so it measures movement and *not* correctness;
- the **subject**: one provider, one model version, one day, one question
  style (`noul`); the published result also holds only on `noul`, with
  `choice` and `score` stable;
- the **probes**: two injection probes held; that is two probes, not a
  guarantee.

**6. The status label.** This repo's learning vault keeps a status key in
`Learning/Decision Models/Research/Claims Ledger.md`, and it is worth using
because it forces you to say where you got the claim from:

- **VERIFIED** - confirmed in a primary source read directly (official
  docs, a model card, a licence file, or a reproducible third-party run with
  committed raw evidence);
- **CLAIM** - asserted by a vendor, blog post or announcement, not
  independently checked;
- **UNCERTAIN** - contested, ambiguous, or not confirmable from a primary
  source;
- **CONFLICT** - two sources disagree; both are listed.

Your own finding is normally **VERIFIED** in the narrow sense that *you* ran
it and the raw evidence is committed - and that is a statement about your
measurement, not about the world. When you quote a vendor's benchmark, that
number is a **CLAIM**. When you quote the prior harness's 0.90 / 0.86 / 0.09,
it is **VERIFIED** for them and a **CLAIM** for you until you have read
their raw file. Labelling is not hedging; it tells the reader exactly how
much weight to put on each sentence.

**The one-sentence test.** Read your finding aloud to somebody who has not
seen the repo. If they cannot say (a) what was measured, (b) where the
evidence is, and (c) what would make you change your mind, it is not
finished.

## In this repo

- `runs/20261025-040448-friction-mock.md` - a real report to read as a
  model: run id, cases, questions measured, `mean spread 0.42`, `max spread
  0.9271`, `questions whose side of 0.5 flips across formats: 4`, and a
  per-question table.
- `runs/20261025-040448-friction-mock.json` - the machine-readable form of
  the same run: `rows` with `values` per format, `spread` and `flips_at_0.5`
  per question.
- `runs/20261025-040448-mock.meta.json` - the provenance block to copy from:
  `run_id`, `provider`, `price_per_mtok`, `cases`, `repeats`,
  `battery_hash`, `dry_run`, `started_at`, `finished_at`, `duration_s`,
  `cost_usd`, `spend_cap_usd`, `uuid`.
- `runs/20261025-040448-mock.jsonl` - the raw file, one JSON object per line,
  each with `run_id`, `case_id`, `group`, `case_class`, `repeat`, `ts`,
  `latency_s`, `usage`, `cost_usd`, `error`, `answers` and `gold`.
- `decisionarena/harness.py` - `run_format_friction()` computes `spread`,
  `flips_at_0.5`, `mean_spread` and `max_spread`; `run_battery()` produces
  the `meta` dict with the identifiers a finding quotes.
- `decisionarena/report.py` - `friction_report()` and `run_report()` are the
  two report shapes a finding can be derived from; `run_report()` also
  prepends the SIMULATED RUN banner for mock providers, which a finding must
  acknowledge.
- `decisionarena/providers.py` - `MockProvider.FORMAT_SHIFT` is the designed-in
  shift; quoting the mock's friction number without saying so would be
  exactly the mistake this lesson is about.
- `AI-CONTEXT.md` - `verified_facts` is the house style for a recorded fact:
  `id`, `claim`, `evidence`, `verified_on`. The `evidence` field is always a
  file path.
- `AGENTS.md` - hard rule 3: *"Evidence before claims. A number without its
  raw `runs/*.jsonl` behind it is marketing."*
- `docs/decision-log.md` - where a choice that shaped the finding gets
  recorded, with its date, why, cost and what would change your mind.
- The vault's `Learning/Decision Models/Research/Claims Ledger.md` - the
  status key (VERIFIED / CLAIM / UNCERTAIN / CONFLICT) and the worked
  examples of how the prior work is labelled.

## Your turn

Write a file `docs/notes/L92-finding.md`. It is the finding you would
publish, written as if a reviewer had the run files open next to it.

It must contain these sections, in this order:

- `## Finding` - **one sentence**, checkable, with the battery, the
  denominators, the metric and the numbers in it
- `## Evidence` - a list of the identifiers, each one copied from a real
  file you have read: the `run_id`, the `battery_hash`, the provider (and
  model version, if the provider has one), the number of cases, the number of
  repeats, the cost, the date, and the path of the raw file
- `## How to check it` - the exact command a reader would run, what it needs
  (environment variable names only - never a value), what it costs, and which
  number in the output they should look at
- `## Measured` - three or four bullets, each one a number you can find in
  the raw file
- `## Inferred` - two or three bullets, each one clearly a conclusion you
  drew rather than a number you read
- `## Limitations` - at least three specific limitations: the size of the
  case set, what the battery does and does not measure, how many providers
  and model versions you covered, and what your probes did not cover
- `## Status` - one label from the vault's status key
  (VERIFIED / CLAIM / UNCERTAIN / CONFLICT) for your own finding, plus one
  label for the prior work you are comparing against, and one sentence for
  each saying why
- `## What would change my mind` - the result that would make you withdraw or
  revise the finding

Inputs: a run you made yourself (or the committed mock run in `runs/`, if you
have not run a live provider yet), the vault's status key, and the report and
`meta.json` files in `runs/`.

Expected output: the eight sections above, 400-700 words, with every
identifier copied from a file rather than remembered.

**Hint:** the identifiers a finding needs are all in the `meta.json` of the
run, and the raw numbers are all in the `.jsonl` or in the friction `.json`.
If you cannot point at a file for a number, that number does not go in the
finding yet.

**Do not** present a mock number as a measurement of a real model. If your
run was a mock run, say so in the first sentence - the status label depends
on it.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. What is the difference between a measurement and an inference, and why does
   mixing them cost you credibility?
2. Which four identifiers must a finding quote so that a reader can find the
   evidence, and where does each one live?
3. The prior harness's injection result is recorded as "VERIFIED (two probes
   only)". What is that parenthetical doing, and why should your finding
   have a similar parenthetical?
4. Why does a null result still count as a published finding?

## Artifact

The artifact **is** `docs/notes/L92-finding.md`. Before you commit it, run
the one-sentence test on it: read the `## Finding` sentence aloud to someone
who has never seen the repo, and check that they could answer - what was
measured, where the evidence is, and what would change your mind.

Then commit it. The artifact is the proof that you can write a claim somebody
else can check, not the proof that the claim is true.
