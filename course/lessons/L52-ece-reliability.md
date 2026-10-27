---
id: L52
phase: 5
title: "ECE and the reliability curve"
minutes: 40
concepts: [ece, reliability-curve, calibration-error, binning]
prereqs: [L51, L33]
paths: [beginner, foundations, provider-live]
exercise_file: exercises/L52_ece.py
quiz: L52
---

# L52 - ECE and the reliability curve

## Why this matters

The Brier score (L51) mixes every question into one average. Sometimes you
need to see *where* a model is wrong. The **reliability curve** shows it: it
sorts predictions by confidence and asks "when the model said 80 %, how
often was it right?". **ECE** - expected calibration error - compresses that
curve into a single number you can put in a table and compare across
providers. This repo reports ECE in every run.

## The naive story

Imagine a weather forecaster who keeps a **scorecard of promises**. Every
time she says "70 % chance", she writes it in a column. Every time it rains,
she writes "rained" in a column next to it.

At the end of the month she sorts her scorecard into drawers by the number
she promised: the "said 70 %" drawer, the "said 40 %" drawer, and so on.
Then she checks each drawer: *in the drawer where she promised 70 %, how
often did it actually rain?*

- If in that drawer it rained about 70 % of the time, her promises are
  **honest**.
- If it rained only 40 % of the time when she promised 70 %, she is
  **overconfident** - she promised more than she could deliver.
- If it rained 90 % of the time when she promised 70 %, she is
  **underconfident** - she undersold herself.

Plot one point per drawer: *what she promised* on the horizontal axis, *what
actually happened* on the vertical axis. The honest forecaster's points lie
on the diagonal line. That picture is the **reliability diagram**. Drawing
one diagonal line per model on the same axes is the **reliability curve**.

The drawers are the **bins**.

## What breaks

**Break 1 - one number hides the interesting part.** ECE is a single scalar
like the mean absolute gap between promise and outcome, averaged across
drawers. A model can have a good ECE and still be badly broken in one
drawer - because a drawer with two entries barely moves the average. If you
only publish ECE, you will never know which drawer is the problem, and the
drawer is where the fix lives.

**Break 2 - ECE depends on the number of bins.** Ten bins and five bins
produce different numbers for the same predictions, because binning decides
which promises get compared with which. There is no "true" ECE; there is an
ECE *at a given binning*. When you compare two providers you must use the
same binning, or you are comparing apples to oranges.

**Break 3 - ECE is not a measure of sharpness.** ECE says nothing about how
decisive the model is. A model that says "50 %" about everything has a
perfect ECE of 0 - perfectly calibrated, and completely useless. Good
calibration and good discrimination are two different properties, and a
useful model needs both.

## The real thing

**The diagram.** For each bin, you compute two numbers:

- **confidence** - the average probability the model stated in that bin;
- **accuracy** - the fraction of questions in that bin that actually came out
  the way the model said.

The signed gap `confidence - accuracy` says which way the model is off. With
the convention used here - **confidence on the horizontal axis, accuracy on
the vertical axis** - the diagonal is the line where the two are equal:

- gap > 0 (confidence above accuracy) -> **overconfident**: the point sits
  *below* the diagonal, because the model promised more than it delivered;
- gap < 0 -> **underconfident**: the point sits *above* the diagonal, because
  it delivered more than it promised;
- gap = 0 -> calibrated in that bin.

**The number.** ECE is the average of the absolute gaps across bins, weighted
by how many questions are in each bin:

```
ECE = sum over bins of (n_bin / N) * |confidence_bin - accuracy_bin|
```

The weighting matters: a bin holding 60 % of the questions counts for 60 %
of the ECE. Unweighted averaging would let a bin with one question swing the
number as much as a bin with a hundred.

**The code.** In `decisionarena/metrics.py`:

- `_ece(probs, outcomes, bins=10)` puts each prediction into bucket
  `min(int(p * bins), bins - 1)`, computes each bucket's mean probability and
  mean outcome, and accumulates
  `(len(bucket) / total) * abs(conf - acc)`.
- `reliability_bins(probs, outcomes, bins=10)` produces the rows of the
  diagram: for each non-empty bucket a dict with `"bin"` (the label
  `"0.6-0.7"`), `"n"` (how many), `"confidence"` and `"accuracy"`, both
  rounded to four decimals.

So the repo has both halves: the curve (`reliability_bins`) and the number
(`_ece`). `score_case()` returns the number; `report.py` prints it as
`mean ECE`.

**A worked example.** Suppose you have eight questions: three answered with
0.95 (all three right), one answered with 0.85 (wrong), one with 0.55
(right), one with 0.45 (wrong), and two with 0.05 (both right).

With ten bins, bucket 0.9-1.0 holds the three 0.95s: confidence 0.95,
accuracy 1.0, gap -0.05, and it holds 3 of 8 questions. Bucket 0.8-0.9 holds
the single 0.85: confidence 0.85, accuracy 0.0, gap +0.85, holding 1 of 8.
Bucket 0.5-0.6 holds the 0.55: confidence 0.55, accuracy 1.0, gap -0.45.
Bucket 0.4-0.5 holds the 0.45: confidence 0.45, accuracy 0.0, gap +0.45.
Bucket 0.0-0.1 holds the two 0.05s: confidence 0.05, accuracy 1.0, gap
-0.95.

ECE = (3/8)(0.05) + (1/8)(0.85) + (1/8)(0.45) + (1/8)(0.45) + (2/8)(0.95)
= 0.01875 + 0.10625 + 0.05625 + 0.05625 + 0.2375 = **0.475**.

Read that number with the diagram beside you: the model is very well
calibrated where it is confident (the 0.95 bucket) and *catastrophically*
wrong in the 0.8-0.9 bucket. The ECE of 0.475 is real, but the shape of the
curve is what tells you where to act.

**Why ECE is in the report.** `laya-lab/README.md` records the upstream
numbers: ECE 0.466 out of the box, improving to 0.081 after a temperature
fit. A 0.466 means "on average, my probabilities are off by nearly half" -
and the fix was a single knob, not a retraining project. That is the kind of
thing you can only see with a calibration metric.

## In this repo

- `decisionarena/metrics.py` - `_ece()`, the weighted mean absolute gap
  across buckets, default `bins=10`.
- `decisionarena/metrics.py` - `reliability_bins()`, which returns the rows
  of the diagram: `bin`, `n`, `confidence`, `accuracy`.
- `decisionarena/metrics.py` - `collect_scored()`, which produces the
  `probs`/`outcomes` pairs both functions consume; `score_case()`, which
  returns `"ece"`; `aggregate()`, which averages it into `"mean_ece"`.
- `decisionarena/report.py` - `run_report()`, whose Headline table prints
  `mean ECE` next to accuracy and mean Brier.
- `examples/02_temperature.py` - the deployment-time fix for a bad ECE:
  raising T flattens an overconfident distribution.

## Your turn

Write a file `exercises/L52_ece.py` that contains:

- a function `bin_index(p: float, bins: int = 10) -> int` that returns which
  bucket a probability belongs to. It must handle `p = 1.0` without falling
  off the end - think about what a probability of exactly 1.0 means for the
  last bucket
- a function `reliability(probs: list[float], outcomes: list[int], bins: int = 10) -> list[dict]`
  that returns one dict per non-empty bucket with the keys `"bin"`, `"n"`,
  `"confidence"`, `"accuracy"` and `"gap"` (the signed
  `confidence - accuracy`)
- a function `ece(probs, outcomes, bins=10) -> float` that computes the
  weighted mean absolute gap
- a `main()` that:
  - uses the eight-question worked example from "The real thing"
    (`probs = [0.95, 0.95, 0.95, 0.85, 0.55, 0.45, 0.05, 0.05]`,
    `outcomes = [1, 1, 1, 0, 1, 0, 1, 1]`)
  - prints the reliability table: one row per bucket with the bin label, `n`,
    `confidence`, `accuracy` and the signed `gap`
  - prints your ECE and the ECE that `metrics._ece()` computes on the same
    inputs, so they can be compared
  - prints the row of `metrics.reliability_bins()` for the bucket your table
    says is most overconfident, so the two implementations can be checked
    against each other
- a self-check section using `assert` that fails loudly if:
  - your ECE and `metrics._ece(...)` differ by more than `1e-9`
  - `bin_index(1.0)` is not the last bucket index
  - the bucket with the largest **positive** gap (the most overconfident one)
    is not the 0.8-0.9 bucket - in this example that bucket promised 0.85 and
    was wrong, so its gap is positive and large. If your table says
    otherwise, your gap sign or your accuracy computation is inverted. (Note
    that the *largest* absolute gap in this example is a different bucket -
    the 0.0-0.1 one, which under-confident. Keep the two apart.)

Inputs: the eight probabilities and outcomes above. Expected output: five
bucket rows, an ECE of about `0.475`, and a matching ECE from
`metrics._ece`.

**Hint:** the bucket index is derived from the probability's position in
`[0, 1]`, and a probability of exactly 1.0 belongs to the last bucket - so
clamp it rather than letting it fall outside.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. In the worked example, the model is well calibrated in the 0.9-1.0
   bucket and disastrous in the 0.8-0.9 bucket. What does the reliability
   diagram tell you that the single ECE number does not?
2. Why does ECE weight each bucket by its size instead of averaging the
   bucket gaps equally?
3. A model that answers "50 %" about everything has ECE 0. Why is that not a
   recommendation?

## Artifact

Write `docs/notes/L52-ece.md` - under 300 words, for a smart friend who has
never seen a calibration plot. It must contain:

- the reliability-diagram idea in your own words (promise on one axis, what
  happened on the other, the diagonal is honesty)
- your worked example's ECE, computed by your own code, and the ECE that
  `metrics._ece` computed
- the bucket that was most overconfident, with its confidence, accuracy and
  gap - the three numbers that show *where* the model is wrong
- one sentence on why a single ECE number is not enough on its own

Then commit it.
