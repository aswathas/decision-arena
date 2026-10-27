---
id: L61
phase: 6
title: "Format friction - the cheapest experiment in the field"
minutes: 40
concepts: [format-friction, serialisation, state-shape, hypothesis]
prereqs: [L60]
paths: [beginner, provider-live]
exercise_file: cases/format_variants.json
quiz: L61
---

# L61 - Format friction: the cheapest experiment in the field

## Why this matters

This is the lesson that produces the repo's publishable finding. The question
it asks is embarrassingly simple: *if I send the model the same information
in a different shape, does its decision change?* If the answer is yes, then
every benchmark table in this field is partly measuring the author's
favourite serialisation - not the model's ability. And unlike almost every
other experiment in AI/ML, this one needs **no labels at all**.

## The naive story

You write a support ticket into a system. The ticket arrives as a blob of
text. You decide to be tidy, so you wrap it in JSON:

```
{"message": "I was charged twice...", "subject": "Double charge"}
```

Same information. Same ticket. Same customer. But you now have a decision
model that reads JSON, and JSON has keys, and keys carry emphasis. The model
may read `{"refund_requested": true}` as stronger evidence than "please
refund". The *content* is identical. The *shape* is not.

Now imagine your production system: Monday the tickets arrive as prose.
Someone on the team adds a parser on Tuesday, and now the same tickets arrive
as nested JSON with metadata. Nobody changed the model. Nobody changed the
customer. But if the model's decisions quietly moved, your routing metrics
moved with them, and your dashboard is now measuring the parser, not the
model.

## What breaks

**Break 1 - you cannot tell "the model is wrong" from "the model is
shaped".** A model scores 0.9 on a ticket. Is it right? You need a label to
know. Without labels you cannot score anything - which is exactly why most
people stop here.

**Break 2 - the shape of the data is invisible in the report.** If you
change your serialiser, your accuracy might move and your dashboard will
show "model got worse". You will blame the model. You will ship a rollback.
You will be wrong.

**Break 3 - averages hide the decision.** Suppose the probability moves by
0.03 on average across your battery. On some questions it moves 0.00, on one
question it moves 0.9. The mean is a comfortable, ignorable number; the one
question that flipped from "no" to "yes" is a customer who got the wrong
team. The mean is not the story. The **flip** is the story.

## The story

Picture a support ticket. On Monday it arrives as a blob of text. On Tuesday
someone adds a parser, and the same ticket arrives as a nested structure with
metadata wrapped in keys. Nobody changed the customer or the model. But the
model reads keys, and keys carry emphasis - a field named for a refund may
read as stronger evidence than the words please refund. Same facts, different
bytes, possibly a different decision.

And you can measure that without knowing the right answer. Send the same
content in a few shapes, watch how far the probability travels, and you have a
measurement of the friction between model and serialiser. No human labelled
anything. That is why this is the cheapest experiment in the field: the
expensive part of an accuracy study is the gold set, and this one does without
it.

Here is the discipline. The average movement tells you how far the probability
usually moves - but a probability going from 0.41 to 0.49 changed no decision.
What you must count is flips: the answer crossing the line where the system
acts. A battery whose probabilities barely move but where one question of nine
flips is a product bug waiting for a customer; one where everything moves a
lot but nothing ever crosses is boring.

## The real thing

**Serialisation** is the exact text or structure you hand to the model. Same
facts, different bytes.

**Format friction** is the measurable amount a decision *moves* when only the
serialisation changes and nothing else does. It is a property of the pair
(model, serialiser), and it is measurable without knowing the right answer.

**State shape** is the structural form of the state: prose (one string),
flat JSON (one level of keys), nested JSON (keys inside keys).

The experiment has exactly three moves:

1. Take one piece of content.
2. Write it out in N shapes, changing nothing else - not the wording, not
   the questions, not the order of the questions.
3. Send each shape to the model and watch the probability move.

The harness calls this **the cheapest experiment in the field** and the
docstring in `run_format_friction()` says why: *requires no labels*. Here is
the arithmetic. A labelled experiment needs you to (a) write cases, (b) pay
humans to label the outcomes, (c) argue about the labels, (d) run the
battery. The format experiment needs (a) write the same content twice, (b)
call the model. One API call per shape - three per case, for prose, flat and
nested - and **not one label**.

**The numbers that matter.** `run_format_friction()` writes one row per
question per case, containing the probability under each format, the
**spread** (`max - min` across the formats), and a boolean
`flips_at_0.5` - true when the formats do not all fall on the same side of
0.5. Here is the discipline:

- `mean_spread` tells you the *typical* amount of movement. Useful as a
  smell test.
- `flips_at_0.5` tells you how often the **decision** changed, not the
  number. A probability moving from 0.41 to 0.49 changed no decision. A
  probability moving from 0.49 to 0.51 changed one.

So: **`flips_at_0.5` is the number that matters, not the mean spread.** A
battery with mean spread 0.42 and zero flips is a boring result. A battery
with mean spread 0.05 and one flip out of nine questions is a product bug
waiting for a customer.

**What the state of the world is.** The independent harness
`rmax-ai/jev-vs-clef` reported a **0.90 / 0.86 / 0.09** spread across
exactly this axis - prose, flat, nested - on `noul` questions: the model
answered "yes" with 0.90 confidence on the prose version and 0.09 on the
nested version of the *same content*. `AI-CONTEXT.md` records this as the
finding to reproduce.

**And now the honest part.** `MockProvider` in `decisionarena/providers.py`
has a `FORMAT_SHIFT` of `{"prose": 0.0, "flat": -0.04, "nested": -0.81}` -
it is *built* to reproduce the shape of that finding so the pipeline can be
exercised offline. So when you run the friction battery against the mock,
you will see a large spread and several flips, and **that proves the harness
works, not that any real model is sensitive to shape**. The mock is not
evidence. To claim anything about a real model you must run
`--provider clef:clef-flash` or `--provider jev` and cite the run file.

**Hypothesis.** A format-friction result is a claim about a mechanism, and a
good one states what it predicts: *if a model's decisions move when only the
serialisation changes, then the same model will disagree with itself across
two teams' pipelines - and a benchmark that uses one shape is measuring the
benchmark author's taste.* That prediction is what makes it a hypothesis
rather than an anecdote. You can test it: run the same battery with two
different providers and see whether the flips land on the same questions.

## In this repo

- `decisionarena/harness.py` - `FORMAT_BUILDERS` is the dict of the three
  shapes: `"prose"` takes `payload["prose"]`, `"flat"` takes `payload["flat"]`,
  `"nested"` takes `payload["nested"]`. Each value is a one-argument lambda.
- `decisionarena/harness.py` - `run_format_friction(provider, cases, formats,
  out_dir)` is the whole experiment. It loops over cases, builds each state
  with `FORMAT_BUILDERS[fmt](variants)`, calls `provider.decide(state,
  case["questions"])`, then computes `spread` and `flips_at_0.5` per
  question and writes `runs/<run_id>.json`.
- `decisionarena/harness.py` - `run_format_friction()` has no `gold` lookup
  anywhere in it. That is the point: no labels are involved.
- `cases/format_variants.json` - the battery. Each case has `variants` (the
  three shapes of the same content), a `group` of `"format"`, a `class` of
  `"format-variant"`, and `questions` - for example `fmt-001-refund` has
  `is_urgent` and `is_refund` (both `noul`) plus `team` (a `choice`).
  Notice there is **no `gold` key** anywhere in this file.
- `decisionarena/report.py` - `friction_report(report)` renders the table
  with the prose / flat / nested columns and the `flips@0.5` column.
- `decisionarena/cli.py` - `cmd_friction()` wires it up; the CLI command is
  `python -m decisionarena friction --provider mock`.
- `runs/20261025-040448-friction-mock.md` - a real (mock) report: mean
  spread 0.42, max spread 0.9271, **4 of 9 questions flipped** at 0.5, and
  `fmt-001-refund / is_urgent` moving 0.9271 -> 0.3278 -> 0.0.
- `decisionarena/providers.py` - `MockProvider.FORMAT_SHIFT` is the honest
  label on the mock's numbers: the shift is *designed in*.

## Your turn

Edit `cases/format_variants.json` and add **one new case**. Do not touch the
three existing cases - they are the committed evidence the mock report above
was measured on.

Your new case must:

- have an `id` that starts with `fmt-0` and ends with a short slug naming
  the situation, e.g. `fmt-004-<slug>`
- have `"group": "format"` and `"class": "format-variant"`
- have a `variants` dict with **all three** keys `prose`, `flat` and
  `nested`, where all three carry the **same content**: the identical core
  message, and the same extra facts, just arranged differently. The nested
  version must genuinely nest (an object inside an object), not just be a
  flat object with a different name.
- have a `questions` dict with **one `noul` question and one `choice`
  question**. The `choice` question needs `criteria` with at least three
  options, each option a string describing the option.
- have **no `gold` key**. Format cases are scored by how far the
  probability moves, not by whether the answer was right, so a gold label
  would be a mistake here.

Use a piece of content you actually have to hand: a real support ticket, a
form submission, a bug report. Then run:

```
python -m decisionarena friction --provider mock
```

Inputs: your own content, in three shapes. Expected output: a report row for
your case id, with a `spread` and a `flips@0.5` column, and a new
`runs/<run_id>.json`.

**Hint:** the three shapes have to be *the same facts*, so write the core
message once and then only decide where it sits. If the `nested` version is
just the `flat` version with an extra layer of empty keys, you have measured
nothing.

**Do not** add a `gold` key even though every case in `cases/routing.json`
has one. Ask yourself what a gold label would even mean for a case whose
whole point is that there is no single right answer shape.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. Why does the format experiment need no labels, and what exactly does it
   measure instead?
2. A battery has mean spread 0.03 and zero flips. Another has mean spread
   0.05 and one flip in nine questions. Which one should make you look
   harder, and why?
3. Your friction run against the mock shows a huge spread. What have you
   actually learned - and what would you have to do to turn that into a claim
   about a real model?

## Artifact

Write `docs/notes/L61-format-friction.md` - under 250 words, for a reader
who has never heard of this repo. It must contain:

- your hypothesis, in one sentence, stated so it could be wrong
- the three shapes you used, in one line each
- the `flips_at_0.5` count from your own run, with the run id
- one sentence saying explicitly that the mock's numbers are not evidence

Then commit it. The artifact is the proof you understood the experiment, not
the proof you ran the code.
