---
id: L00
phase: 0
order: 1
title: "What this repo is - and what a decision model is not"
minutes: 25
concepts: [decision-model, evaluation, evidence]
prereqs: []
paths: [beginner, provider-live]
exercise_file: docs/notes/L00-what-is-a-decision-model.md
quiz: L00
---

# L00 - What this repo is - and what a decision model is not

## Why this matters

You are about to spend the next few weeks of your life reading a harness that
measures other people's models. If you do not know what the thing under
measurement *is*, every number it prints will be a black box with a decimal
point in it. So we start by clearing away the wrong mental models - the
chatbot, the writer, the clever agent - before we meet the right one.

## The naive story

Your first guess at "an AI model" is probably a chat window. You type a
question, it types an answer back, prose and all. That picture is so common
that it feels like a definition. It is not.

Here is the picture this repo actually uses. You are a support desk. A customer
sends a message. Your job is **not** to reply to the customer. Your job is to
decide three things:

1. Is this about a payment? (yes / no)
2. Which team should handle it? (billing / technical / sales / other)
3. How severe is it? (no impact / minor / major / critical)

That is a **decision**. There is a fixed list of answers, and the model's job is
to say which one and how sure it is. Nobody is reading an essay.

## What breaks

**Break 1 - if you think of it as a chatbot, you will grade it like one.** You
will read the output for tone, for length, for "did it explain itself". None of
that is measured here. This repo grades *decisions*: was the team right, was
the probability honest, did the action change when we swapped the model.

**Break 2 - if you think of it as a writer, you will expect one answer.** A
writer picks one option and forgets the rest. A decision model does not: it
returns a **distribution** - a number for every option - and lets the caller
decide what to do. The repo's own thresholds (0.5 for a yes/no, 0.6 for the
team) are the caller deciding.

**Break 3 - if you think of it as a reasoning agent, you will expect it to
think.** There is no plan here, no tool loop, no multi-step scratchpad. One
state in, one set of answers out. That is deliberate: it keeps the measurement
honest. Once a model is allowed to take six steps and call three tools, you can
no longer tell whether the decision came from the model or from the scaffolding
around it.

**Break 4 - and the one that actually bites: every vendor publishes a benchmark
where they win.** TypeSafe publishes a table saying Jev wins. Cloudflare
publishes a table saying Clef wins. The two tables disagree with each other.
This repo exists so that *a third party* can run the same battery against
several models and publish the raw evidence.

## The story

Imagine a support desk on a busy morning. A customer message arrives: a
subscription was charged twice. The person at the desk does not write a
reply. They decide three things: is this about a payment, which team takes
it, how severe is it.

There are fixed boards for each answer: a yes-or-no flag for the payment
question, a set of team bays, a ladder of four rungs for severity. A pointer
is set on each answer and left there.

Now put a machine on the desk. It reads the customer message and moves the
same pointers. It does not talk to the customer, it does not plan, and it
does not think out loud. It puts a number beside each pointer instead.

That is the whole job. One situation in, a fixed set of answers out, a number
on every answer.

And the numbers belong to the machine, not to the world. Swap the machine and
the pointers move even though the customer message did not. That is why this
repo sends the same questions to several models and writes down what each one
did.

The pointer is not the verdict either. Where it ends up is a policy the desk
sets after the model has answered.

## The real thing

**One sentence, and it is the whole brief:**

> `decision-arena` runs the **same battery** against multiple decision models
> (TypeSafe Jev, Cloudflare Clef, OpenAI-compatible gateways, local Laya) and
> measures **accuracy, calibration, cost, latency, determinism, injection
> resistance, and swap safety** - because every vendor publishes a benchmark
> where they win.

Read those seven words as seven things you can check:

| what is measured | plain meaning |
|---|---|
| accuracy | how often the decision was right |
| calibration | when it says 80%, was it right 80% of the time? |
| cost | how many US dollars the answers cost, with the token counts beside it |
| latency | how long the answer took, in seconds |
| determinism | ask twice, get the same answer? |
| injection resistance | does a nasty instruction inside the input change the decision? |
| swap safety | if I swap the model, how often does my *action* change? |

**Evidence.** In this repo, a number is not a fact until the raw run file is
behind it. Every run writes `runs/<run_id>.jsonl` - one line per call, with the
raw provider answer, the latency, the token usage, the cost and any error. If
you cite a number, you cite that file. A number without its raw evidence behind
it is marketing.

**And the hardest rule in this repo, which you must know before you touch
anything:** *the mock is not evidence.* `MockProvider` is an offline simulator
whose only job is to prove the harness works without spending money. Its
numbers are **never** a measurement of any model, and the report says so in
loud letters at the top of every mock run.

## In this repo

- `README.md` - the whole point in two paragraphs: "every vendor published a
  benchmark table where they win, and the two headline tables disagree with
  each other."
- `AGENTS.md` - the seven hard rules. Rule 4 is the mock rule: "`MockProvider`
  is an offline simulator for testing the harness. Its numbers must never be
  published as a model evaluation."
- `decisionarena/providers.py` - `MockProvider`, whose docstring says
  "Deterministic offline simulator - for testing the HARNESS, not the models",
  and `available_providers()`, whose note reads "offline simulator - tests the
  harness, proves nothing about real models".
- `decisionarena/report.py` - `run_report()` checks
  `result.provider.startswith("mock")` and prints a `SIMULATED RUN` banner
  telling the reader the numbers must never be quoted as evidence.
- `decisionarena/cli.py` - `cmd_providers()` prints that same warning next to
  the `mock` entry, before you spend a cent.
- `decisionarena/harness.py` - `run_battery()` writes the `.jsonl` evidence file
  and the `meta.json` before any report exists.

## Your turn

Write the file `docs/notes/L00-what-is-a-decision-model.md`. It is a note to
yourself, written in your own words, in this order:

1. A section **"What a decision model is not"** with exactly three bullets:
   not a chatbot, not a writer, not a reasoning agent - each bullet one
   sentence saying why that picture does not fit this repo.
2. A section **"What it is"** with one sentence in the form: *a decision model
   takes a state and returns a distribution over a fixed set of options, and
   the caller decides what to do with it.*
3. A section **"The seven things this repo measures"** - the seven words from
   the brief, each with a half-line explanation in your own words.
4. A section **"The rule I must not break"** - one sentence that says the mock
   is not evidence and why.
5. One concrete number you saw yourself, taken from running
   `python -m decisionarena run --provider mock --battery routing --dry-run`
   (it prints the number of cases in the routing battery), or by counting the
   rows `python -m decisionarena providers` prints - one row per known
   provider. Write the number, the command you ran, and - if the number came
   from a `mock` run - say explicitly that it is a harness number and not a
   model measurement.

Expected output: a markdown file of roughly 300-450 words containing those
five sections, with at least one real number in it that you can trace back to
a command you ran.

**Hint:** the vocabulary you need is in `AGENTS.md` under "Hard rules" (rule 4
is the mock rule) and in the brief at the top of that file. The seven
measurements are listed there in the same order as the table above.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. A friend asks you what this repo does. Give them a one-sentence answer that
   does not use the word "chatbot".
2. Why is it a problem that every vendor publishes a benchmark where they win?
   What does this repo do differently?
3. You run the harness with the mock provider and get an accuracy of 90%. What
   can and cannot you conclude from that number?

## Artifact

Publish `docs/notes/L00-what-is-a-decision-model.md` - the note you just
wrote. It is the proof that you can say what this repo is without reading it
back. Do not include any number from a mock run without labelling it as a
harness number.
