---
id: L50
phase: 5
title: "Accuracy and why it is not enough"
minutes: 30
concepts: [accuracy, base-rate, class-imbalance, precision-recall]
prereqs: [L40, L10]
paths: [beginner, foundations, provider-live]
exercise_file: exercises/L50_accuracy.py
quiz: L50
---

# L50 - Accuracy and why it is not enough

## Why this matters

Accuracy is the first number anyone reports about a classifier, and it is the
number most easily made to look impressive without the model doing anything
useful. This repo reports accuracy - but the whole reason it also measures
the Brier score, ECE and the action-change rate is that accuracy alone will
happily hide a broken model.

## The naive story

You are sorting 100 support tickets into four teams. You want to know how
often your sorter puts a ticket in the right bucket. So you count the right
answers and divide by 100. That fraction is **accuracy**. Simple, intuitive,
one number.

Now imagine a second sorter: one that never sorts at all. It always puts
every ticket in the biggest bucket. If 80 of your 100 tickets really are
billing tickets, that sorter scores 80 out of 100 - **80 % accuracy** - and it
has learned nothing whatsoever.

## What breaks

**Break 1 - the majority-class baseline.** The sorter that always guesses the
most common class has an accuracy equal to the **base rate**: the fraction of
your workload made up of that class. Any model you evaluate must be compared
against that number. If your model's accuracy is close to the base rate, your
model is worth about as much as always guessing. In this repo's
`cases/routing.json` the gold team labels are `billing`, `technical`, `sales`
and `other` - one each - so the *routing* battery is balanced, but your own
real workload will not be. Real support traffic is heavily skewed towards one
or two teams.

**Break 2 - class imbalance hides the failure.** If 99 % of tickets are
billing, a model that gets every single *technical* ticket wrong still scores
99 % accuracy. Accuracy is an average over all cases, so the rare case - the
one that actually hurt a customer - is diluted into invisibility. And note
that the repo's `aggregate()` computes accuracy as the **mean of the
per-case accuracies**, so a case with three questions counts as much as a
case with thirty.

**Break 3 - accuracy cannot see confidence.** Accuracy only asks "was the
answer right?". It says nothing about *how sure* the model was. A model that
is right 80 % of the time with 51 % confidence and a model that is right 80 %
of the time with 99 % confidence score identically on accuracy - and they are
completely different products. That gap is what the Brier score (L51) and
ECE (L52) measure.

## The story

Picture a sorting bench at a support desk, with four bins. A hundred tickets
arrive. You want one number: how often did a ticket land in the right bin?
Count the right ones, divide by a hundred, and you have accuracy.

Now imagine a second sorter that never sorts. It puts every ticket in the
fullest bin. If eighty of your hundred tickets really are billing tickets,
that sorter scores eighty out of a hundred - eighty percent accuracy - and it
learned nothing at all.

That number is the base rate, and it is the floor every model has to beat. A
model at eighty percent is worth exactly as much as always guessing. Worse,
the failure hides: accuracy is an average over all the tickets, so if
ninety-nine percent of your traffic is one kind, a model that gets every one
of the rare cases wrong still scores ninety-nine percent. The customer who was
hurt is diluted into the average.

And accuracy cannot see how sure the model was. Two sorters, both right eighty
percent of the time, one confident every time and one barely confident, score
identically - and they are completely different products. That gap is what the
next two lessons measure.

## The real thing

Work with four counts over a set of questions. For a binary yes/no question,
let:

- **TP** - true positives: said yes, and it really was yes.
- **FP** - false positives: said yes, but it really was no.
- **FN** - false negatives: said no, but it really was yes.
- **TN** - true negatives: said no, and it really was no.

Then:

```
accuracy  = (TP + TN) / (TP + FP + FN + TN)
precision = TP / (TP + FP)        "of the tickets I flagged, how many were real?"
recall    = TP / (TP + FN)        "of the real cases, how many did I catch?"
```

**Precision** is about not crying wolf. **Recall** is about not missing
anything. They trade off against each other: a more cautious model catches
more real cases (higher recall) and flags more innocent ones (lower
precision). The example that makes this concrete:

| predictor | TP | FP | FN | TN | accuracy | precision | recall |
|---|---|---|---|---|---|---|---|
| always "billing" (the majority class) | 80 | 0 | 0 | 20 | 80 % | 80 % | 100 % |
| a model that flags 90 tickets as billing, 70 correctly | 70 | 20 | 10 | 0 | 70 % | 78 % | 88 % |

Look at the first row. The do-nothing predictor gets **80 % accuracy, 100 %
recall** - and it still misses the 10 real technical tickets, because it
never looks at the ticket at all. Accuracy alone would have called the two
rows comparable. The second row is genuinely better at the job *and* it
scores lower on accuracy.

For a multi-class question (the `team` question with four options), the
same idea applies per class: precision for "billing" is "of the tickets I
routed to billing, how many really were billing"; recall for "billing" is "of
the real billing tickets, how many did I route to billing". Averaging over
the classes gives the familiar macro averages.

**How the repo computes accuracy.** In `decisionarena/metrics.py`,
`collect_scored()` turns each answer into an **outcome** (1 or 0) plus the
probability it gave the correct answer, and `score_case()` returns
`accuracy = sum(outcomes) / len(outcomes)`. The rules per answer type are
worth knowing:

- `noul` (yes/no): the outcome is 1 when the probability is on the right side
  of 0.5 - `abs(p - gold) < 0.5`.
- `choice`: the outcome is 1 when the chosen option equals the gold option.
- `score`: the outcome is 1 when the chosen level is within half a level of
  the gold level.

Then `aggregate()` rolls the per-case accuracies into one number.

## In this repo

- `decisionarena/metrics.py` - `collect_scored()` (turns answers into
  outcomes and rows), `score_case()` (`accuracy`, `brier`, `ece`), and
  `aggregate()` (mean of the per-case accuracies).
- `decisionarena/metrics.py` - `fmt_pct()`, the helper that renders an
  accuracy as a percentage in the reports.
- `decisionarena/report.py` - `run_report()`, whose "Headline" table prints
  accuracy, mean ECE and mean Brier - accuracy first, but never alone.
- `cases/routing.json` - the gold labels (`"team": "billing"`, `"is_billing":
  true`, `"severity": 1`) and the case classes `clear-cut`, `borderline` and
  `spam`. The spam case is deliberately a different kind of row.
- `cases/injection.json` - cases with **no** gold labels at all, so accuracy
  is not computable there. That is the point of that battery: it measures
  whether a decision *held*, not whether it was right.

## Your turn

Write a file `exercises/L50_accuracy.py` that contains:

- a function `confusion(gold, predicted) -> dict` that takes two lists of
  `True`/`False` labels of equal length and returns a dict with the four
  counts `tp`, `fp`, `fn`, `tn`
- a function `accuracy(c) -> float`, `precision(c) -> float` and
  `recall(c) -> float` that compute the three rates from that dict.
  `precision` must return `0.0` when there are no predicted positives
  (nothing was flagged, so nothing can be right) and `recall` must return
  `0.0` when there are no actual positives
- a function `majority_baseline(labels) -> float` that returns the base
  rate: the fraction of the most common label
- a `main()` that uses a concrete dataset of 100 tickets - 80 billing, 20
  technical - and prints:
  - the base rate
  - the accuracy, precision and recall of the **always-billing** predictor
  - the accuracy, precision and recall of a **second** predictor that flags
    90 tickets as billing, 70 of them correctly
  - the number of real technical tickets the always-billing predictor missed
- a self-check section using `assert` that fails loudly if:
  - the always-billing predictor's accuracy equals the base rate
  - the second predictor's accuracy is greater than the always-billing
    predictor's accuracy (it should be *lower*, which is the lesson)
  - the always-billing predictor's recall is not `1.0`

Inputs: the 100-ticket dataset described above. Expected output: a base rate
of `0.8`, an accuracy of `0.8` for the trivial predictor with a recall of
`1.0`, and a *lower* accuracy of `0.7` for the better predictor.

**Hint:** the whole lesson is in one sentence - the trivial predictor's
accuracy equals the base rate by construction, so build the base rate first
and compare.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. Your workload is 95 % billing tickets. A model scores 93 % accuracy. What
   does that tell you, and what would you want to measure instead?
2. Why can precision and recall not both be maximised at the same time?
3. In `cases/injection.json` there are no gold labels. What does that mean
   for the accuracy of a run over that battery, and what does that battery
   measure instead?

## Artifact

Write `docs/notes/L50-accuracy.md` - under 250 words, for a smart friend who
has only heard of accuracy. It must contain:

- the accuracy of the always-guess-the-majority-class predictor on your
  dataset, and why that number is the floor every model must beat
- the accuracy, precision and recall of your second predictor, with the
  sentence "the better model scored *lower* accuracy" if that is what your
  numbers show
- one sentence on why `aggregate()` averaging per-case accuracies is a
  choice worth knowing about

Then commit it.
