---
id: L82
phase: 8
title: "The escape hatch - abstention, thresholds and hysteresis"
minutes: 35
concepts: [abstention, hysteresis, thresholds, escalation]
prereqs: [L54]
paths: [beginner, provider-live]
exercise_file: exercises/L82_abstention.py
quiz: L82
---

# L82 - The escape hatch: abstention, thresholds and hysteresis

## Why this matters

Everything so far assumed the model always answers, and that you act on what
it says. That assumption is what turns a decision model into a liability. A
system that can only ever say "yes" or "no" has no way to say *"I am not sure,
and this ticket needs a human"*. The escape hatch is the route by which a
decision model declines to decide - and it is the bridge between this repo's
measurement work and a system you could actually put in front of customers.
Without it, every probability you measured is a probability you are forced to
act on.

## The naive story

Picture a junior triage clerk at a hospital. A patient walks in, and the
clinic's rulebook says the clerk must pick exactly one of four departments
from the list - no "I am not sure", no "someone else should look". The clerk
learns quickly that "not sure" is not on the form, so the clerk stops being
unsure. They pick the most plausible department for every single patient.

Sounds like a design flaw, but consider the alternative rule: "if you are less
than 60% confident, send the patient to a senior clerk." Now the clerk is
allowed to be unsure - and, crucially, you get to *count* how often they are.
The second rule is not a weaker version of the first. It is the rule that
makes the first safe, because a rule you cannot decline is a rule that will
be applied confidently to the cases you are least sure about.

That second rule is **abstention**, and this lesson is about building it
properly.

## What breaks

**Break 1 - a model that must answer always answers.** These are decision
models, not chat models: the wire protocol has a `noul` (yes/no), a `choice`
and a `score`. There is no "refuse" answer type in the protocol. So if your
product has no escape hatch, the probability itself becomes your escape
hatch - and a probability is not a policy. A model at 0.51 on "is this
destructive?" has effectively said *yes* if your only rule is "act on the
answer".

**Break 2 - one global threshold is wrong for every question.** Look at the
thresholds this repo actually ships, in `cases/routing.json`:

```
"thresholds": {"is_billing": 0.5, "team": 0.6, "severity": 0.5}
```

Three questions, two different thresholds. `is_billing` is a clean yes/no and
0.5 is the natural line. `team` needs **0.6**, because auto-routing a ticket
to the wrong team costs more than escalating it to a human. A single global
threshold - "0.6 everywhere" or "0.5 everywhere" - is a policy decision
pretending to be a technical one. And the thresholds live **with the cases**,
not in the code, because they are a product decision (that was the point of
lesson L54).

**Break 3 - a threshold with no margin is a switch that flickers.** Take a
probability that hovers at 0.50 because the ticket is genuinely borderline -
"cancel my plan and get last month refunded, also move the invoice to a
different company name" is `routing-004`, a case the battery itself classes
as `"borderline"`. If your rule is "act when the probability is 0.5 or
above", then a probability of 0.49 and a probability of 0.51 produce
**different actions from the same situation**, and a value that wobbles by a
hundredth between two identical calls flips the ticket back and forth. The
fix is a **band** around the threshold: two lines instead of one, with a zone
in between where the system keeps whatever it was doing. That is
**hysteresis**, and you met it in lesson L54.

**Break 4 - abstention is not free.** Every escalated ticket is a human's
time. If your escape hatch is wired too tightly, you have built a system that
escalates everything - accurate, safe, useless. The number to watch is the
**escalation rate**: what fraction of tickets went to a human instead of being
decided automatically. A good threshold policy is a *balance*, and it is
different for every product. There is no threshold that is right in general.

## The real thing

There are **two** escape hatches, at two different levels, and a real product
needs both.

**Abstention inside the model.** Look at the `criteria` of the `team` question
in `cases/routing.json`:

```
"billing": "Charges, invoices, subscriptions and refunds",
"technical": "Errors, outages, integrations and configuration",
"sales": "Plans, pricing, upgrades and procurement",
"other": "None of the above - needs human triage"
```

That fourth option **is** an escape hatch, built into the question's
vocabulary. The model can say "other" - and the harness treats `other` as a
perfectly good answer, scoring it like any other label. The routing battery
uses it deliberately: `routing-005` is a spam ticket whose gold answer is
exactly `"other"`. So abstention can be a *first-class answer*, not a failure.

**Abstention at the system level.** When the model's top probability is below
the threshold for that question, the system does not act - it **escalates**.
This is the same rule the harness measures, from the other side:
`metrics.action_change_rate()` treats a question as "acted on" when the
value (for a `noul`) or the top probability (for a `choice`) is `>= threshold`.
Below the threshold, the honest reading is "not confident enough to act".

**Per-class thresholds.** The thresholds dict is keyed by **question id**, so
each question gets its own line:

| question | threshold | what it means in the routing battery |
|---|---|---|
| `is_billing` | 0.5 | a plain yes/no - the natural line is halfway |
| `team` | 0.6 | auto-route only when fairly sure; otherwise escalate |
| `severity` | 0.5 | a plain scale |

And `cases/injection.json` carries the same idea with its own question ids -
`{"contains_pii": 0.5, "is_destructive": 0.5, "severity": 0.5}` on the PII
case, and `{"is_destructive": 0.5, "team": 0.6, "severity": 0.5}` on the
other two. A PII question and a routing question do not deserve the same
confidence bar, and the data structure lets you say so per question.

**Hysteresis.** With one threshold, the action is `act if p >= t`. With
hysteresis you use two:

- act when `p >= t + margin`
- stop acting (escalate) when `p < t - margin`
- **inside the band** - that is, when `t - margin <= p < t + margin` - keep
  the previous action.

The band is a "do not change your mind" zone. Take `t = 0.5` and
`margin = 0.05`: the system starts acting at 0.55 and only stops acting below
0.45. A probability wobbling between 0.48 and 0.52 no longer flips anything.
Lesson L54 measured exactly this: a 0.04 difference between two providers
produced one action change under a single threshold and **zero** action
changes under a 0.05 margin.

What you give up for it: **latency near the threshold**. The system takes
longer to react in the band - it is deliberately sticky. That is a product
trade-off, and like every threshold in this repo it belongs to whoever owns
the consequence (a support manager, a risk owner), not to the engineer alone.

**One thing the harness does not do, and you should know.** `metrics.py`
records a `noul` answer as **correct** when it lands on the same side of 0.5
as the gold label - `abs(p - o) < 0.5`, where `o` is 1 for a true gold label
and 0 for a false one. So a model that abstains at 0.4 on a question whose gold
answer is `true` is counted as **wrong** by the metric. That is deliberate: an
abstention is not a correct answer. But it means your accuracy number and your
escalation rate must be read together - a policy that escalates a lot will
show a lower accuracy, and that is not a bug, it is the cost of the escape
hatch showing up in the metric.

## In this repo

- `cases/routing.json` - the thresholds dict
  `{"is_billing": 0.5, "team": 0.6, "severity": 0.5}` on every case, and the
  `team` question's `criteria` with its `"other"` option, described as
  "None of the above - needs human triage".
- `cases/routing.json` - `routing-005` is a spam ticket whose gold `team`
  answer is `"other"`, and `routing-004` is the `"class": "borderline"` case -
  the ticket the harness itself says is genuinely ambiguous.
- `cases/injection.json` - thresholds keyed by the injection battery's own
  question ids (`contains_pii`, `is_destructive`, `team`, `severity`).
- `decisionarena/metrics.py` - `action_change_rate(a, b, thresholds)` is the
  rule, written out: for a `noul`, act when `float(aa["value"]) >= thr`; for
  anything else, act when the top probability is `>= thr`. Below the
  threshold is where escalation lives.
- `decisionarena/metrics.py` - `collect_scored()` scores a `noul` as correct
  only when `abs(p - o) < 0.5`, i.e. when it falls on the same side of 0.5 as
  the gold label. An abstention is not counted as a correct answer.
- `decisionarena/metrics.py` - `label_agreement()` compares `noul` answers by
  the side of 0.5 they fall on, the same line the action rule uses.
- `decisionarena/cli.py` - `cmd_swap()` picks the thresholds out of the cases
  and passes them to `action_change_rate()`, so the thresholds are read from
  the data, not hard-coded.
- `decisionarena/report.py` - `swap_report()` prints the "Decisions that
  would change" table with `a_acts` and `b_acts` - the two columns where an
  escalation would appear.
- `decisionarena/harness.py` - `run_battery()` records the raw `answers` for
  every call, so an escalation rate can be recomputed from the raw file
  later, under different thresholds, without spending another cent.
- `runs/20261025-040448-mock.jsonl` - the committed evidence you can
  recompute an escalation rate from today: five routing cases, each with
  `is_billing`, `team` and `severity` answers.

## Your turn

Write a file `exercises/L82_abstention.py`. It must run offline, with no API
key and no network.

It must contain:

- a function `decide_action(prob: float, threshold: float) -> str` that
  returns `"act"` when the probability is at or above the threshold and
  `"escalate"` when it is below
- a function `decide_action_hysteresis(prob: float, threshold: float,
  margin: float, previous: str) -> str` that applies the three-part band rule
  described in "The real thing": act above `threshold + margin`, escalate
  below `threshold - margin`, and keep `previous` inside the band
- a function `escalation_rate(records: list, thresholds: dict) -> dict` that
  takes the **raw records** from a run (the list of dicts that
  `harness.run_battery()` puts in `RunResult.records`) and returns, per
  question id, the fraction of records whose answer would escalate under
  `decide_action`, plus an overall rate across all questions
- a `main()` that:
  - runs the `routing` battery offline with the mock provider and
    `harness.run_battery(..., repeats=3, out_dir="runs/l82-exercise")`
  - prints the per-question escalation rate under the **real** thresholds
    from `cases/routing.json` (read them out of the case file - do not
    retype them), and the overall rate
  - prints a second block: a fixed, hand-written sequence of probabilities
    that wobbles around 0.5 (for example 0.49, 0.51, 0.48, 0.52, 0.50), and
    for that sequence counts how many times the action **changes** (a) under
    a single 0.5 threshold and (b) under a 0.5 threshold with a 0.05 margin
  - prints the `other`-answer count for the `team` question - how many of the
    mock's routing answers chose `"other"`, the model-level abstention
- a self-check section using `assert` that fails loudly if:
  - the per-question escalation rate for any question is outside `[0.0, 1.0]`
  - the single-threshold run changes its action **more often** than the
    hysteresis run on the same sequence
  - the overall escalation rate equals the per-question rate for at least
    one question (the overall rate is not simply a copy of one question's
    rate)
  - the number of records you scored equals the number of cases times the
    number of repeats

Inputs: the `routing` battery, its `thresholds` dict, and the probabilities
you choose for the wobble sequence.

Expected output: the per-question escalation rates, the overall rate, the two
action-change counts, and the `other`-answer count.

**Hint:** the rule is "the question's own threshold decides", and the
thresholds are *in the case file*, keyed by question id - so one loop over
`thresholds` covers every question without hard-coding a single number.
For the wobble, the only thing that matters is where each probability sits
relative to the threshold and to the band.

**Do not** modify `cases/routing.json` to add your own thresholds for this
exercise - the point is to use the ones the repo ships. If you want to try
other thresholds later, do it in the artifact, and say that you did.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. What is the difference between the `"other"` option in the `team` question
   and a threshold below which you escalate? Which one is inside the model's
   control, and which one is yours?
2. Why does the `team` question carry a threshold of 0.6 while `is_billing`
   carries 0.5? Who should decide that number?
3. A probability sits at 0.51 on one call and 0.49 on the next, on the same
   ticket. What does a single threshold do, what does a 0.05 margin do, and
   what do you give up by using the margin?
4. Your accuracy drops when you turn abstention on. Why is that the expected
   behaviour, and what number should you look at next to it?

## Artifact

Write `docs/notes/L82-abstention.md` - under 300 words, for a reader who has
never heard of a threshold. It must contain:

- the two escape hatches, one line each
- your per-question escalation rates, with the thresholds you used and where
  they came from
- the two action-change counts from the wobble sequence, and what the
  difference tells you
- one sentence naming who should own the threshold numbers in a real product,
  and why

Then commit it. The artifact is the proof that you can design a way out for
the model, not the proof that you ran the code.
