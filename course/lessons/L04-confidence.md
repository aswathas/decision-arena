---
id: L04
phase: 0
order: 6
title: "Confidence is not probability - the first trap"
minutes: 30
concepts: [confidence-vs-probability, calibration, overconfidence]
prereqs: [L03]
paths: [beginner, provider-live]
exercise_file: exercises/L04_confidence.py
quiz: L04
---

# L04 - Confidence is not probability - the first trap

## Why this matters

This is the trap that catches people who have used an LLM for an afternoon and
nothing else. A model will hand you two different numbers - one for "how
likely is this outcome" and one for "how sure am I" - and they are **not** the
same thing. A model can be 95% confident and 50% accurate. If you wire the
wrong one into your threshold, you will build a system that is confidently
wrong, which is the most expensive kind of wrong.

## The naive story

You ask someone: "Is this email about billing?" They answer "yes, I'm quite
sure - I'd say 90% sure."

Now you ask a second person the same email. They answer "yes, I'm *very*
sure." Is that second person more likely to be right than the first? Usually
yes - and that is exactly the intuition that breaks on models.

The problem is that a model's two numbers come from two different places:

- the **probability** is about the *world*: "this email has a 0.9 chance of
  being a billing email".
- the **confidence** is about the *model*: "I am 0.9 sure about what I just
  said".

A model can be extremely sure of a wrong answer. A model can also be
moderately sure and right. Nothing forces the two numbers to line up - and
the gap between them is a *measurable* thing.

## What breaks

**Break 1 - confidence is not calibrated.** If a model says "90% sure" on 100
questions and is right 70 times, its confidence is a lie. If it says "60% sure"
on 100 questions and is right 60 times, its confidence is honest - even though
the first model *sounds* more impressive. This repo measures the honesty, not
the volume.

**Break 2 - the two numbers measure different failures.** A wrong probability
means "the model does not know how often it is right". A wrong confidence
means something worse: "the model does not know what it does not know". Only
the second one is dangerous, because a miscalibrated probability still
degrades gracefully - at 0.55 you act less often - while miscalibrated
confidence makes you act *harder* when you are wrong.

**Break 3 - some providers send one and not the other.** In this repo the
answer shape has both fields, but they are optional. The `MockProvider`
docstring states it: "`noul` carries no confidence, `choice`/`score` do". So a
`noul` answer in a run file can have `confidence: null`, and a `choice` answer
usually does not. Any code that reads confidence has to handle `None`.

**Break 4 - the mock is deliberately over-confident, and that is a gift.** In
`decisionarena/providers.py`, `MockProvider` builds its `choice` answers with
`"confidence": round(min(0.99, probs[top] + 0.05), 4)` - the top probability
plus five points, capped at 0.99. That is a *built-in* example of "confidence
slightly above probability": the model is always a bit more sure of itself
than its own distribution supports. You can measure that gap on day one
without spending money.

## The story

Picture two people answering the same question, and two notebooks.

The first notebook is the world. Every time someone says yes to the billing
question, a mark goes in a column labelled "correct". Count the marks against
the number they claimed and you can see whether they are honest - a
forecaster who writes 0.9 and is right nine times in ten is calibrated.

The second notebook is the person. Every time someone answers, they also
write down how sure they are. This column can disagree with the first.

Someone writes 0.9 on a hundred questions and is right seventy times. Their
confidence is overstated by 0.2 on every question. Someone else writes 0.6
and is right sixty times - honest, and unimpressive.

The trouble starts when a rule is built on the wrong notebook. Suppose a
support desk only escalates a ticket when the number crosses 0.6. If the
rule reads the first notebook, a shaky answer of 0.55 simply does not
escalate - the system gets cautious. If it reads the second notebook, the
person who claims 0.9 while being right 70% of the time escalates
everywhere, including the thirty times they were wrong. The first failure
slows the system down. The second makes it act hardest exactly when it
should have stayed quiet.

## The real thing

Two numbers, two meanings, two failure modes.

| | probability | confidence |
|---|---|---|
| claim about | the outcome (the world) | the model (its own answer) |
| lives in | `probabilities` dict / `noul` value | the `confidence` field |
| wrong means | the model is not as good as it thinks | the model is *misled about itself* |
| can it be `None`? | yes, when a provider sends no distribution | yes - `noul` answers usually have none |

**Calibration** - the property that a probability means what it says. Formally:
among all the cases where the model said `p`, the fraction that turned out to
be correct should be `p`. The repo measures it two ways:

- **ECE** (expected calibration error), in `decisionarena/metrics.py`:
  `_ece(probs, outcomes, bins=10)`. The pairs are bucketed by probability
  into 10 bins. For each bin it computes the mean confidence and the
  accuracy, takes the absolute difference, and averages those differences
  weighted by how many cases each bin holds. **0.0 is perfect. Bigger is
  worse.**
- **Reliability bins**, `reliability_bins()`: the same bucketing, but it
  returns the rows so you can *see* it - each row has the bin range, how many
  cases landed in it, the mean confidence and the accuracy. A well-calibrated
  model has `confidence` and `accuracy` close together in every row.

**Overconfidence** - the specific, common failure: the confidence is
systematically *above* the accuracy. The gap is `confidence - accuracy`. A
model that is wrong 30% of the time while claiming 90% confidence is
overconfident by 0.2 on every case, and its ECE will be around 0.2.

**The threshold is where the trap pays out.** In this repo the decision is
made by comparing a **probability** to a threshold (`action_change_rate()` in
`decisionarena/metrics.py` compares `max(probabilities)` against the
threshold). So the consequence of confusing the two numbers is concrete: if
you threshold on *confidence* instead of probability, an overconfident model
crosses your 0.6 bar on cases where the probability is only 0.3, and your
system acts on garbage.

**How to tell the two apart from a single answer.** The `noul` value *is* the
probability - it is the number that gets thresholded. The `confidence` field
is a separate, extra number that this repo carries but does not threshold on.
If a provider sends `confidence` but no probabilities, you have a vibe, not a
decision.

## In this repo

- `decisionarena/providers.py` - `normalise_answers()` returns both
  `probabilities` and `confidence` as separate keys, each defaulting to `{}`
  or `None` when absent.
- `decisionarena/providers.py` - `MockProvider.decide()`: `noul` answers get
  no confidence at all, while `choice` answers get
  `confidence = min(0.99, probs[top] + 0.05)` and `score` answers get a flat
  `confidence = 0.8`. Two different kinds of made-up confidence, on purpose.
- `decisionarena/metrics.py` - `_ece()` and `reliability_bins()` are the
  calibration machinery; `collect_scored()` is what produces the
  `(probs, outcomes)` pairs they consume.
- `decisionarena/metrics.py` - `action_change_rate()` thresholds the
  **probability** (`max(probabilities)`), never the confidence.
- `decisionarena/report.py` - `run_report()` prints `mean ECE` in the headline
  table, next to accuracy.
- `cases/routing.json` - the thresholds (`0.5`, `0.6`, `0.5`) that the
  probabilities are compared against.

## Your turn

Write a file `exercises/L04_confidence.py` that contains:

- a function `overconfidence_gap(confidence: float, accuracy: float) -> float`
  that returns `confidence - accuracy`. A positive number means the model is
  claiming to be more sure than the evidence supports.
- a function `calibration_error(pairs: list[tuple[float, int]], bins: int = 10)
  -> float` that returns the expected calibration error of a list of
  `(confidence, outcome)` pairs: bucket the pairs by confidence into `bins`
  ranges, compute each bucket's mean confidence and accuracy, take the
  absolute difference in each bucket, and average those differences weighted
  by the number of pairs in each bucket.
- a function `bin_report(pairs: list[tuple[float, int]], bins: int = 10) ->
  list[dict]` that returns one dict per non-empty bucket with the keys
  `"lo"`, `"hi"`, `"n"`, `"confidence"` and `"accuracy"`.
- a `main()` that uses this hand-made dataset of `(confidence, outcome)`
  pairs, where the model claims 0.9 ten times but is right only seven times:

  ```
  [(0.9, 1)] * 7 + [(0.9, 0)] * 3 + [(0.6, 1)] * 8 + [(0.6, 0)] * 2
  ```

  and prints:
  - the bin report, one row per bucket
  - the calibration error, to four decimal places
  - the overconfidence gap for the 0.9 bucket, to four decimal places
  - a verdict line that reads `OVERCONFIDENT` when the gap is above `0.05`
    and `CALIBRATED` otherwise
- a self-check section using `assert` that fails loudly if:
  - the calibration error of the dataset above is not greater than `0.05`
  - the calibration error is not between 0 and 1
  - the overconfidence gap for the 0.9 bucket is not greater than zero

Inputs: the 20 pairs above. Expected output: two bucket rows (the 0.5-0.6
bucket and the 0.9 bucket), a calibration error above 0.05, a positive gap for
the 0.9 bucket, and the verdict `OVERCONFIDENT`.

**Hint:** a bucket is a *range* of confidence values, and the error of a
bucket is the gap between what the model claimed there and how often it was
right there. The weight of a bucket is how many cases it holds - a bucket
with one case should not count as much as a bucket with ten.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. A model answers a `choice` question with `probabilities {"billing": 0.4,
   "other": 0.6}` and `confidence: 0.95`. What is each number claiming, and
   which one does this repo threshold on?
2. What does an ECE of 0.0 mean, and what does an ECE of 0.3 mean about a
   model?
3. Why is overconfident confidence more dangerous than a miscalibrated
   probability?

## Artifact

Write `docs/notes/L04-confidence.md` - under 250 words, for a smart friend who
has only ever used a chatbot. It must contain:

- one sentence saying what a probability claims and one saying what a
  confidence claims
- one sentence defining calibration
- one concrete number from your own run of your own code - the calibration
  error, or the gap, with the dataset it came from

Then commit it. The artifact is the proof that you can tell the two numbers
apart on sight.
