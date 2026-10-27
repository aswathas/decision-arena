---
id: L70
phase: 7
title: "Designing cases - state, questions, gold and thresholds"
minutes: 35
concepts: [case-design, gold-labels, thresholds, question-set]
prereqs: [L01, L60]
paths: [beginner, provider-live]
exercise_file: cases/routing.json
quiz: L70
---

# L70 - Designing cases: state, questions, gold and thresholds

## Why this matters

Everything the harness measures comes from the case files. A case is the
*experiment*: the situation, the questions asked about it, the right answers,
and the point at which a decision counts as taken. If your cases are bad,
every number the harness produces is bad - with total confidence, which is
the dangerous part. This lesson is about writing a case.

## The naive story

A case is a question with an answer. You write the question, you write the
answer, you put them in a list, and the harness does the rest.

That is true, and it hides the four things that actually decide what you
measured. Think of a case as a small experiment with five moving parts:
the **state** (the world you put in front of the model), the **questions**
(what you ask about it), the **gold** (what the right answers are), the
**thresholds** (when a probability becomes an action), and the **class** (a
label you use later to slice the results). Change any one of them and you
have run a different experiment.

## What breaks

**Break 1 - a question with no stable answer.** If two careful humans would
answer your question differently, you have not created a case - you have
created an argument. Every accuracy number computed from it is noise, and
noise looks like signal if you do not have enough cases.

**Break 2 - one question per case hides the point.** If you ask only "which
team?", a model that always says "billing" scores 60% on a billing-heavy
battery and looks fine. You need *several* questions per case, in different
formats, so that a model cannot pass by guessing one way.

**Break 3 - thresholds that are wrong move the goalposts.** The threshold
decides when a probability *acts*. Set it at 0.99 and almost nothing acts, so
the action-change rate is 0% and everything looks safe. Set it at 0.1 and
everything acts, so the rate is 100% and everything looks broken. The
threshold is a *policy decision*, and it has to be written down in the case
so that every run uses the same one.

**Break 4 - a battery with no failures in it teaches you nothing.** If every
case is obvious, every model scores 100% and you learn nothing about where
the edges are.

## The story

Imagine a laboratory bench. Before you switch anything on, you lay out five
things.

The **state**: the ticket itself, the whole world the model will see.
Nothing else goes on the bench. If you leave a stray note there, the note is
part of what you measured.

The **questions**: several, of different kinds - a yes/no judgement, a
categorical choice, an ordered level. If you ask only one, a model that
always answers "billing" walks away with a good score and you have learned
nothing about it.

The **gold**: the right answers, written down. For the choice question that
means every option, including "other, needs human triage", so a ticket
belonging to none of them still has a correct answer instead of being forced
into a wrong bucket.

The **thresholds**: the line where a probability stops being a number and
starts being an action. These live in the case, not in the code, because they
are a policy decision.

And the **class**: clear-cut, borderline, spam - the label you slice the
results by later, so you can see the model that scores 100% on the easy pile
and 30% on the hard one.

Five cards on a bench. Change any one of them and you have run a different
experiment.

## The real thing

Here is the anatomy of a case, using the real fields in
`cases/routing.json`.

**`id`** - a unique string. It is written into every JSONL line as
`case_id`, so it is how you find the evidence for one case in a run file.
The existing ids look like `routing-001`.

**`group`** - a coarse bucket, `"routing"` for all the cases in that file.
`run_report()` groups the per-case scores by `group` and prints a `## By
group` table. Groups let you say "accuracy on the routing group", and later
you can add a second group to compare.

**`class`** - the finer slice, and the one that tells you *what kind of
case this is*. The three in `cases/routing.json` are:

- `clear-cut` - the answer is obvious. `routing-001` is a double charge;
  it is billing, no debate.
- `borderline` - the answer is arguable. `routing-004` asks to cancel
  *and* to move an invoice to a different company; it is mostly billing but
  it could go either way.
- `spam` - the input is not a real request at all. `routing-005` is a
  lottery scam, and the gold answer is `"other"` - none of the above,
  needs human triage.

Why does `class` matter? Because the results get sliced by it. A model that
scores 100% on `clear-cut` and 30% on `borderline` is a different model from
one that scores 60% and 60%. The class is how you see the difference. It is
also how you spot a **degenerate** model - one that always answers the most
common class, and looks fine on a battery that is mostly easy.

**`state`** - the world. One string in `cases/routing.json` (the whole
ticket). In `cases/format_variants.json` it is a `variants` dict instead,
because that battery needs three shapes of the same content.

**`questions`** - a dict of question id to question. The three question
types, now from the *author's* side:

- `noul` - a yes/no judgement, with a probability. From the author's side:
  the question must be **binary and answerable from the state alone**, and
  its `instructions` must name the boundary. `"Is this message about a
  payment, invoice or refund?"` is a good one. `"Is this message
  problematic?"` is not - it is not binary.
- `choice` - pick one option from a `criteria` dict, where the key is the
  option and the value is a description of it. The criteria must be
  **mutually exclusive and collectively exhaustive** - that is why every
  case in this file has an `other` option meaning "none of the above -
  needs human triage". Without it, a correct answer can be forced into a
  wrong bucket, and you are measuring your taxonomy instead of the model.
- `score` - a level on an ordered scale, where `criteria` is a **list** of
  level strings: `["No impact", "Minor", "Major", "Critical"]`. The list
  order is the order. The gold for a score question is the *index* - `0`
  for "No impact", `3` for "Critical" - not the string.

**`gold`** - the right answers, as a dict of question id to right answer:
`{"is_billing": true, "team": "billing", "severity": 1}`. Note the types:
`true` for a `noul` question, the **option key** (`"billing"`) for a
`choice` question, and the **index** (`1`) for a `score` question.
`metrics.collect_scored()` is where that mapping is interpreted, and it
accepts exactly these three shapes. A question with no gold entry is simply
not scored - it can still be asked, but it does not move accuracy.

**`thresholds`** - a dict of question id to the probability at which the
question acts: `{"is_billing": 0.5, "team": 0.6, "severity": 0.5}`. The
`choice` threshold is higher (0.6) because you want to be more than merely
undecided before you auto-route a ticket to a team. `action_change_rate()`
uses these to decide whether the decision changed between two providers.

**The design discipline.** A good case set has: several questions per case,
in different formats; a mix of `class` values including genuinely hard
ones; a `criteria` set with a catch-all; and a threshold set that matches
your real policy. And the whole set is small enough that you can read every
case yourself - if you cannot read all 5 cases of a battery, you do not know
what you measured.

## In this repo

- `cases/routing.json` - five cases: `routing-001`, `routing-002`,
  `routing-003` (`clear-cut`), `routing-004` (`borderline`), `routing-005`
  (`spam`). Each has `id`, `group`, `class`, `state`, `questions`, `gold`,
  `thresholds`.
- `cases/routing.json` - the `criteria` block is identical across all five
  cases: `billing`, `technical`, `sales`, `other`. The same vocabulary for
  every case is what makes the results comparable.
- `decisionarena/harness.py` - `load_cases(path)` reads the file: it accepts
  a `.json` file with a `cases` key (or a bare array) and a `.jsonl` file
  with one case per line.
- `decisionarena/harness.py` - `run_battery()` reads `case["state"]`,
  `case["questions"]`, `case.get("gold")` and `case.get("class")` - the
  four fields the runner actually uses. `case["state"]` and
  `case["questions"]` are required; `gold` and `class` are optional.
- `decisionarena/metrics.py` - `collect_scored(answers_by_qid, gold)`
  interprets the gold: `bool` for `noul`, the option key for `choice`, the
  index for `score`. `score_case()` rolls it into accuracy, Brier and ECE.
- `decisionarena/metrics.py` - `action_change_rate(a, b, thresholds)` is the
  only consumer of `thresholds`.
- `decisionarena/cli.py` - `_load_battery(name)` maps the `--battery` name
  to a file: `routing` -> `routing.json`, `injection` -> `injection.json`,
  `format` -> `format_variants.json`, `all` -> routing + injection.

## Your turn

Edit `cases/routing.json` and add **one new case**. Do not modify the five
existing cases - they are committed evidence.

Your new case must have:

- `id` starting with `routing-` and ending with a number that does not
  clash with `001`-`005`, e.g. `routing-006`
- `group` - `"routing"`
- `class` - one of `"clear-cut"`, `"borderline"`, `"spam"`. Pick honestly:
  if you are not sure whether it is borderline, it is borderline.
- `state` - one realistic ticket string, in the voice of a customer. Do not
  paste a template that makes the class obvious.
- `questions` - **all three** question types, using **the same question ids
  and the same `criteria` as the existing cases**: `is_billing` (noul),
  `team` (choice, with the same four criteria: billing, technical, sales,
  other), and `severity` (score, with the same four level strings).
  Reusing the vocabulary is not laziness - it is what makes the numbers
  comparable across cases.
- `gold` - the right answer for each of the three questions: a bool for
  `is_billing`, the option key for `team`, the **index** for `severity`.
- `thresholds` - the same three ids with the same values as the existing
  cases: `is_billing` 0.5, `team` 0.6, `severity` 0.5.

Then run:

```
python -m decisionarena run --provider mock --battery routing
```

Inputs: your own ticket. Expected output: the run completes, the report's
`## By group` table now includes your case, and the JSONL file contains a
line with your `case_id` whose `gold` field holds your three labels.

**Hint:** the `severity` gold is the position of the level in the `criteria`
list, counted from zero - so the *first* level in the list is `0`, not `1`.
Check that against `routing-002` before you write yours.

**Then check your own case honestly:** read it again after writing it. If a
colleague could argue with your gold label, either change the label or move
the case to `"borderline"`.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. What are the seven fields of a case in this repo, and which two does the
   runner require?
2. Why does every `choice` question in `cases/routing.json` include an
   `other` option, and what happens to your accuracy numbers if it is
   missing?
3. What does the `class` field let you do to the results that `group` alone
   cannot?

## Artifact

Write `docs/notes/L70-case-design.md` - under 250 words, for a reader who
has never designed a case. It must contain:

- the seven fields and one line each
- your new case's `id`, `class`, and the three gold labels
- one sentence on why you chose that `class`

Then commit it. The artifact is the proof you can design an experiment, not
the proof you ran the code.
