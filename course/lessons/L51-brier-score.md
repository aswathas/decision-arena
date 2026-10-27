---
id: L51
phase: 5
title: "The Brier score - probability quality"
minutes: 35
concepts: [brier-score, probability-quality, squared-error]
prereqs: [L50, L12]
paths: [beginner, foundations, provider-live]
exercise_file: decisionarena/metrics.py
quiz: L51
---

# L51 - The Brier score: probability quality

## Why this matters

Lesson L50 showed that accuracy cannot see confidence. The Brier score is the
simplest metric that can. It asks one question: *how close was the number you
said to the number that happened?* A model that says 0.9 and is right deserves
credit; a model that says 0.9 and is wrong should be punished hard. That is
the whole idea, and it is why this repo prints Brier next to accuracy in every
report.

## The naive story

You are a weather forecaster. Every morning you say "70 % chance of rain".
Over a hundred days:

- on 70 of those days it rained - and on those days you were right;
- on 30 of those days it did not rain - and on those days you were wrong.

How well did you do? A score that only counted right/wrong would treat you
exactly like a forecaster who said "50 % chance of rain" every morning and got
the same 70/30 split. But you should get **more** credit than that, because
your 70 % was a good, specific claim: of all the days you called at 70 %, 70 %
were real. Your forecast was *sharp* and *honest*.

That extra credit is the Brier score.

## What breaks

**Break 1 - a score that only counts right and wrong cannot see overconfidence.**
Consider two forecasters over the same hundred days. Both are right 70 % of
the time. The first says "70 %" every morning. The second says "95 %" every
morning and "45 %" every morning on the days it was wrong. Accuracy is
identical. The second forecaster is *worse* - when it says 95 %, it is right
only 70 % of the time, and that gap is exactly what a user gets hurt by. The
Brier score sees the gap; accuracy cannot.

**Break 2 - squared error punishes the confident wrong more than the
uncertain wrong.** With a probability `p` and an outcome `o` (1 for "it
happened", 0 for "it did not"), the error is `(p - o)`. Square it and the
size of the mistake is what matters. A claim of 0.95 when the truth is 0 is
an error of 0.95; a claim of 0.45 when the truth is 0 is an error of 0.45.
Squares make the big blunders hurt more - which is the behaviour you want
when a wrong confident answer triggers an irreversible action.

**Break 3 - you must compare the number to the *outcome*, not to the label.**
The Brier score needs a probability *and* what actually happened. A model
that is right but says 0.51 has a small error; a model that is right and says
0.99 has a big one, because 0.99 was not justified. This is why the repo's
`collect_scored()` produces two parallel lists - `probs` and `outcomes` -
before any calibration metric runs.

## The story

Picture a forecaster who says, every morning, "seventy percent chance of
rain". Over a hundred days it rained on seventy.

A score that only counted right and wrong would treat her like someone who
says "fifty percent" every morning and gets the same split. But she deserves
more credit, because her number was specific: of the days she called at
seventy percent, seventy percent were real. That extra credit is the Brier
score.

The number itself is a distance. Take what she said, take what happened - one
for rain, zero for dry - and look at the gap. Square that gap, and average the
squares. Zero is perfect, one the worst possible.

Squaring is what makes it bite. A day she called ninety-five percent that
stayed dry leaves a square of 0.9025; a day she called forty-five percent and
stayed dry leaves 0.2025. The big confident mistake costs far more, which is
what you want when a wrong confident answer triggers something irreversible.

Here is the part that makes the metric worth having. A forecaster who says
"fifty percent" about everything scores 0.25 - and that beats the
overconfident forecast's 0.325, with the very same accuracy. Saying nothing
useful is a milder failure than saying something confidently wrong, and only
this metric says so.

## The real thing

**The definition.** The Brier score is the **average squared distance between
what you said and what happened**:

```
brier = (1/N) * sum over i of (p_i - o_i)^2
```

Lower is better. `0` is perfect - every probability exactly matched its
outcome. `1` is the worst possible - every probability was exactly wrong.

**A hand-computed example.** Two questions. For each one, `p` is the
probability the model gave to the correct answer and `o` is 1 if it was
right, 0 if it was wrong:

| question | p (said) | o (happened) | (p - o)^2 |
|---|---|---|---|
| Q1 | 0.9 | 1 | (0.9 - 1)^2 = 0.01 |
| Q2 | 0.8 | 0 | (0.8 - 0)^2 = 0.64 |

```
brier = (0.01 + 0.64) / 2 = 0.325
```

Now the honest version of the same model, which was less sure:

| question | p (said) | o (happened) | (p - o)^2 |
|---|---|---|---|
| Q1 | 0.6 | 1 | (0.6 - 1)^2 = 0.16 |
| Q2 | 0.4 | 0 | (0.4 - 0)^2 = 0.16 |

```
brier = (0.16 + 0.16) / 2 = 0.16
```

Same accuracy (50 % in both cases - one right, one wrong). The honest model
has **half** the Brier score. That is the metric doing its job.

And now the punchline. A model that says "50 %" about everything:

```
brier = ((0.5 - 1)^2 + (0.5 - 0)^2) / 2 = (0.25 + 0.25) / 2 = 0.25
```

`0.25` - **better than the 0.325 of the overconfident model**, with exactly
the same accuracy. Being uninformative is a milder failure than being
confidently wrong, and the Brier score says so out loud. Accuracy cannot
even tell the two apart.

**What the repo actually computes.** `_brier()` in
`decisionarena/metrics.py`:

```
def _brier(probs, outcomes):
    if not probs:
        return None
    return sum((p - o) ** 2 for p, o in zip(probs, outcomes)) / len(probs)
```

Three things to know about it:

1. It is the **mean** over questions, so it is comparable across batteries of
   different sizes.
2. The inputs are produced by `collect_scored()`: for a `noul` question,
   `probs` gets the probability of *yes* and `outcomes` gets 1 if the gold
   answer was yes; for a `choice` question, `probs` gets the probability the
   model gave to the **gold option** (`p_gold`) and `outcomes` gets 1 if the
   chosen option was the gold one; for a `score` question, `probs` gets the
   probability of the gold level.
3. That last point is worth being precise about: for `choice` questions this
   repo computes the **one-vs-rest form** of the Brier score - it scores only
   the probability of the correct option, not a sum over every option. The
   strict multi-class Brier would add the errors on all the other options
   too. The one-vs-rest form is what `collect_scored()` makes available, and
   it is the form the reports show.

**Where it appears.** `score_case()` returns it as `"brier"`, `aggregate()`
averages it as `"mean_brier"`, and `report.py`'s Headline table prints it
beside accuracy and mean ECE. Money is never involved here, but the
convention is the same as everywhere else in this repo: the number is always
reported next to the counts it came from.

## In this repo

- `decisionarena/metrics.py` - `_brier()`, the function above; it is the
  only Brier implementation in the repo.
- `decisionarena/metrics.py` - `collect_scored()`, which builds the
  `probs` and `outcomes` lists that `_brier` and `_ece` both consume, and
  `score_case()`, which returns `brier` rounded to four decimals.
- `decisionarena/metrics.py` - `aggregate()`, which averages the per-case
  Brier into `mean_brier`.
- `decisionarena/report.py` - `run_report()`, whose Headline table prints
  `mean Brier`.
- `examples/02_temperature.py` - the temperature knob is the deployment-time
  way to fix a bad Brier score: raising T flattens an overconfident
  distribution and pulls it back toward the truth.

## Your turn

You will edit an existing repo file: **`decisionarena/metrics.py`**. Add
**one new public function** and change nothing else.

Add `brier_detail(probs: list[float], outcomes: list[int]) -> float` to
`decisionarena/metrics.py`, placed after `_brier()`. It must:

- print one line per prediction, in the form
  `q1 p=0.9000 o=1 err=0.0100` (index or 1-based position, the probability
  to four decimals, the outcome, and the squared error to four decimals)
- print a final summary line `brier = 0.3250` (the mean squared error to
  four decimals)
- **return** the same float it printed, so the value can be used in an
  assertion

Do not modify `_brier()`, `collect_scored()`, `score_case()`, `aggregate()`
or anything else in the file. Keep the module's existing style: a docstring
that says what the function does and what it returns, and
`from __future__ import annotations` already at the top of the file - leave
that line alone.

Then write `exercises/L51_brier.py` (a new file) that:

- imports `decisionarena.metrics` and calls your new `brier_detail` on the
  hand-computed example from this lesson: `probs = [0.9, 0.8]`,
  `outcomes = [1, 0]`
- prints the Brier score of the honest model `[0.6, 0.4]` and of the
  always-50 %-model `[0.5, 0.5]` for comparison
- contains a self-check section using `assert` that fails loudly if:
  - `brier_detail([0.9, 0.8], [1, 0])` returns a value that differs from
    `metrics._brier([0.9, 0.8], [1, 0])` by more than `1e-9`
  - the overconfident model's Brier score is **lower** than the always-50 %
    model's (it must be higher - that is the lesson)

Inputs: the two probability lists above. Expected output: two printed detail
blocks, a Brier of `0.3250` for the overconfident model, `0.1600` for the
honest one and `0.2500` for the always-50 % one.

**Hint:** the squared error of one prediction is the distance between the
probability and the outcome, squared - the same arithmetic for every row, so
compute it once per row and average the results.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. Why does the Brier score punish a wrong-but-confident answer more than a
   wrong-and-uncertain one? Give the arithmetic for a claim of 0.95 that turns
   out false.
2. The always-50 % model scored 0.25 and the overconfident model scored
   0.325, with identical accuracy. Which model is better for a user, and
   what does that tell you about which metric to look at first?
3. For a `choice` question, this repo's Brier score uses the probability of
   the gold option only. What is different about the strict multi-class
   Brier score, and why does it matter that you know which one you are
   reading?

## Artifact

Write `docs/notes/L51-brier.md` - under 250 words, for a smart friend who
has never heard of a Brier score. It must contain:

- the definition in your own words ("the average squared distance between
  what you said and what happened" is a fine start)
- your hand-computed example: the overconfident model's Brier, the honest
  model's Brier, and the always-50 % model's Brier, with the numbers
- one sentence on why the always-50 % model beating the overconfident one is
  the most useful thing in this lesson

Then commit it.
