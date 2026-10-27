---
id: L33
phase: 3
title: "Calibration - when a confident model is wrong"
minutes: 35
concepts: [calibration, overconfidence, reliability, ece-intro]
prereqs: [L32, L12]
paths: [beginner, foundations]
exercise_file: exercises/L33_calibration.py
quiz: L33
---

# L33 - Calibration: when a confident model is wrong

## Why this matters

A decision model that is right 80% of the time can still be *dangerous*. If
its wrong 20% of the time it is confident about, it will occasionally tell a
customer their refund is approved, or tell a security team an attack is
benign, with total conviction. Accuracy measures how often the model is
right. **Calibration** measures something else: when the model says 90%,
is it right 90% of the time?

This is the metric the whole repo is built around, and the reason
`decisionarena/metrics.py` has `_ece()` and `reliability_bins()` next to the
accuracy function. If you can only measure one thing about a decision model,
measure its calibration.

## The naive story

A model says "billing, 72%". You check: of all the tickets the model gave
72% to, how many actually went to billing? If the answer is about 72%, the
model is **calibrated**. If the answer is 95%, the model is **overconfident**:
it says 72% and then is right 95% of the time, which sounds like a good
thing and is not - it means you cannot trust the 28% case, which is exactly
where you needed to know.

The naive story says this is a property of the model. It is not. It is a
property of the model **plus the data it was measured on**.

## What breaks

**Break 1 - "calibration" is a relationship, not a number.** You cannot ask
"is this model calibrated?" in isolation. You can only ask: *when this model
says X%, is it right X% of the time, on this workload?* A model trained on
clean English tickets and tested on messy ones is calibrated on the first and
overconfident on the second. The dataset is half of the claim.

**Break 2 - one confidence level is not the whole story.** A model can be
perfectly calibrated at 0.9 and badly calibrated at 0.2. Calibration has to
be checked *per confidence level*, which means grouping the predictions into
buckets and comparing the average confidence in each bucket with the
accuracy in that bucket. That is the **reliability** table.

**Break 3 - the deployment changes the data.** This is the trap this repo
exists to catch. The routing battery measures the model on the tickets *you*
fed it. In production, the tickets that reach the model are the ones your
rules let through - which are not a random sample of all tickets. If you
route only the *hard* tickets to the model, the model's confidence on those
will be systematically different from its confidence on the battery. A model
that was calibrated on your test set can be badly miscalibrated in
production, with nothing changing inside the model at all.

**Break 4 - calibration and accuracy are independent.** A model can be
accurate and miscalibrated (right for the wrong reasons - it says 0.99 and
0.51 both times and happens to be right 80% of the time), or calibrated and
inaccurate (it says 50% and is right 50% of the time - useless, but honest).
You need both numbers. The harness reports both: `score_case()` returns
`accuracy`, `brier` and `ece` together.

## The real thing

**Calibration** is the property that the model's stated probability matches
its observed frequency of being right.

**Reliability** is the table that shows it, bucket by bucket. Group the
predictions by their confidence, then for each bucket compare:

```
average stated confidence   vs   observed accuracy
```

- If the two match, the model is **calibrated** in that bucket.
- If observed accuracy is *higher* than stated confidence, the model is
  **underconfident** - hedging more than it needs to.
- If observed accuracy is *lower*, the model is **overconfident**. This is
  the dangerous direction, and it is the common one.

A worked example. Suppose you take every ticket the model gave a
probability of `0.9` or higher to "billing", and find that only 60% of them
actually went to billing:

```
stated confidence : 0.90
observed accuracy : 0.60
gap               : 0.30
```

That model is badly overconfident. If you set your routing threshold at
`0.9` and the model is right only 60% of the time above that threshold, then
**four in ten of the tickets it confidently routed to billing did not belong
there**. That is the trap, stated in plain numbers.

**ECE** - expected calibration error - is the single number that summarises
the reliability table. The idea:

```
1. bucket every prediction by confidence (0.0-0.1, 0.1-0.2, ..., 0.9-1.0)
2. for each bucket, compute |average confidence - accuracy|
3. weight each bucket's gap by how many predictions landed in it
4. average the weighted gaps
```

The result is one number between 0 and 1. **0 means perfectly calibrated.**
0.3 means, on average, the model's stated confidence is off by about 30
percentage points in the buckets people actually use.

The repo implements exactly this in `decisionarena/metrics.py`:

- `_ece(probs, outcomes, bins=10)` - buckets with
  `b = min(int(p * bins), bins - 1)`, computes mean confidence and mean
  accuracy per bucket, and adds
  `(len(bucket) / total) * abs(conf - acc)` for each bucket.
- `reliability_bins(probs, outcomes, bins=10)` - the raw table: for each
  bucket, the range, the count `n`, the mean `confidence` and the mean
  `accuracy`.

Read `_ece()` once and you will never need a textbook again. The
`abs(conf - acc)` is the gap per bucket, and the
`(len(bucket) / total)` is the weight that makes a bucket with three
predictions count much less than a bucket with three hundred.

**A worked ECE by hand.** Suppose you have 10 predictions, all with confidence
`0.9`, and 6 of them are correct. They all land in one bucket:

```
conf = 0.9,  acc = 0.6,  gap = 0.3,  weight = 10/10 = 1
ECE = 1 * 0.3 = 0.3
```

Now suppose instead you had 5 predictions at confidence `0.9` (3 correct) and
5 at confidence `0.5` (3 correct):

```
bucket 0.9-1.0: conf=0.9, acc=0.6, gap=0.3, weight=0.5  -> 0.150
bucket 0.5-0.6: conf=0.5, acc=0.6, gap=0.1, weight=0.5  -> 0.050
ECE = 0.200
```

Same accuracy (60%), better ECE - because the gap is now spread over buckets
and the badly-calibrated bucket only holds half the predictions. This is why
ECE is a *weighted* average and not a plain one.

**What to do about bad calibration.** In order of cost:

1. **Temperature.** Flatten the distribution (raise `T`). The ranking does
   not change, the confidence does. `examples/02_temperature.py` is the
   dial, and it is a deployment-time fix - no retraining.
2. **More data, or data that matches production.** Calibration is measured
   on a distribution; fix the distribution.
3. **Retraining.** The expensive fix, and the one you should try last.

**And the limit of this lesson.** You will not compute ECE here. The
measurement itself - with the right bins, the right confidence source, and
enough predictions to make the estimate stable - is phase 5's job
(`decisionarena/metrics.py` is already written; you will use it against real
runs). What you are learning now is what the number *means* and why a
decision model that is wrong with confidence is a different kind of problem
from one that is simply wrong.

## In this repo

- `decisionarena/metrics.py` - `_ece(probs, outcomes, bins=10)` is the
  expected calibration error, exactly as described above. The docstring
  says it in one line: "mean |confidence - accuracy| weighted by bucket
  size."
- `decisionarena/metrics.py` - `reliability_bins(probs, outcomes, bins=10)`
  returns the table: `{"bin", "n", "confidence", "accuracy"}` per bucket.
  This is the reliability diagram's data.
- `decisionarena/metrics.py` - `collect_scored()` builds the `(probability,
  outcome)` pairs both of them consume. For a `choice` answer the
  probability is the one the model gave the *gold* option, so the ECE asks:
  "when the model says this probability for the correct answer, is it
  right that often?"
- `decisionarena/metrics.py` - `score_case()` returns `accuracy`, `brier`
  and `ece` in one dict, and `aggregate()` rolls them up as `mean_ece` and
  `mean_brier`. Accuracy alone is never reported in this repo without its
  calibration number next to it.
- `decisionarena/providers.py` - `MockProvider.decide()` is where
  overconfidence gets manufactured in the simulator: for a `choice` answer
  it sets `"confidence": round(min(0.99, probs[top] + 0.05), 4)` - the
  confidence is *always* a bit above the top probability. The simulator is
  built to produce a miscalibrated model so the metrics have something to
  measure. (Its numbers are never evidence about a real model.)
- `cases/routing.json` - the `gold` labels are what make calibration
  measurable at all. Without a label there is no outcome, and no outcome
  means no accuracy, no Brier and no ECE - only friction and injection
  measurements, which look at the output alone.
- `examples/02_temperature.py` - the fix. The closing block explains the
  deployment-dial argument: temperature is "a deployment-time dial, not a
  retraining project - which is exactly why a decision-model API exposing
  probabilities instead of a hard label is worth paying for."
- `examples/03_train_linear.py` - where overconfidence comes from. Training
  drives the loss down by pushing probabilities towards 0 and 1, which is
  exactly what an overconfident model does. The closing block's advice:
  "When you see bad calibration, temperature is the cheap fix; retraining is
  the expensive one."

## Your turn

Write a file `exercises/L33_calibration.py` that contains:

- a function `bucket(p: float, bins: int = 10) -> int` that returns the
  bucket index for a probability: `min(int(p * bins), bins - 1)`
- a function `reliability(probs: list[float], outcomes: list[int], bins:
  int = 10) -> list[dict]` that returns one dict per non-empty bucket with
  the keys `bin` (a string like `"0.9-1.0"`), `n`, `confidence` (the mean
  probability in the bucket) and `accuracy` (the mean outcome in the bucket)
- a function `ece(probs: list[float], outcomes: list[int], bins: int = 10) ->
  float` that returns the weighted average of `|confidence - accuracy|` over
  the buckets, weighting each bucket by `n / total`
- a function `overconfidence(probs: list[float], outcomes: list[int]) ->
  float` that returns the mean of `confidence - accuracy` over only the
  predictions whose probability is at least `0.9` - the "what happens to the
  confident ones" number
- a `main()` that:
  - uses this list of (probability, outcome) pairs:
    `[(0.95, 1), (0.92, 1), (0.94, 0), (0.91, 1), (0.93, 0), (0.55, 1),
    (0.60, 1), (0.58, 0), (0.52, 0)]`
  - prints the reliability table, one bucket per line, with `n`,
    `confidence` and `accuracy` to four decimal places
  - prints the ECE with four decimal places
  - prints the overconfidence number with four decimal places
  - prints a line `confident_bucket_wrong_ratio=<number>` - of the
    predictions with probability at least `0.9`, the fraction that were
    wrong, with four decimal places

Inputs: the nine pairs above. Expected output: the high-confidence bucket
holds five predictions with average confidence around 0.93 and accuracy 0.60,
the ECE is clearly above zero, and the confident bucket is wrong roughly
40% of the time.

**Hint:** the bucket index is `min(int(p * bins), bins - 1)` - the `min` is
there so a probability of exactly 1.0 does not fall off the end. And the ECE
weighting is `n / total` per bucket, not a plain average over the buckets.

**Do not** smooth or round anything before the final print. The whole point
of the exercise is that the numbers are what they are - a bucket that is
60% accurate while claiming 93% is the finding.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. A model says 0.99 and is wrong 60% of the time. Is it calibrated, and if
   not, what is it called?
2. Why is calibration a property of the data and the deployment as well as
   of the model? Give one concrete scenario.
3. What does ECE measure, in one sentence, and what does a value of 0 mean?
4. Give the two ways to fix bad calibration in order of cost, and say which
   one is a deployment-time dial.

## Artifact

Write `docs/notes/L33-calibration.md` - under 200 words, aimed at a smart
friend who has never heard of calibration. It must contain:

- one sentence defining calibration
- the ECE and the overconfidence number from your own run
- one sentence on why a model that is right 80% of the time can still be
  dangerous

Then commit it. The artifact is the proof that you understood it, not the
proof that you ran the code.
