---
id: L12
phase: 1
title: "Softmax - from raw scores to probabilities"
minutes: 30
concepts: [logits, softmax, normalisation, numerical-stability]
prereqs: [L10, L11]
paths: [beginner, foundations]
exercise_file: exercises/L12_softmax.py
quiz: L12
---

# L12 - Softmax: from raw scores to probabilities

## Why this matters

Every `choice` answer this harness measures is a **dict of probabilities**.
Ask
"which team should handle this ticket?" and the model answers
`{"billing": 0.72, "technical": 0.18, ...}`. Softmax is the function that
turns raw model scores into exactly that dict. If you do not know softmax,
every number in `decisionarena/metrics.py` is a black box to you.

## The naive story

Picture a quiz show. Three contestants get **points**: 2, 1, and 0.5. The
points are not percentages - 2 points does not mean "twice as likely as 1
point", it means "more raw score".

Now the show must share out a bag of 100 tickets, in proportion to how well
each contestant did. How many tickets does each get?

Your gut says: divide by the total, so 2 + 1 + 0.5 = 3.5, and you get
0.57 / 0.29 / 0.14. That is *almost* right, and the difference between
"almost right" and "right" is where the interesting part lives.

## What breaks

**Break 1 - the gut answer is not scale-free.** If the points were 20, 10 and
5 (the same contest, ten times the points), the gut answer gives the same
result: 0.57 / 0.29 / 0.14. Good. But a model that is *more confident* does not
produce "ten times the points" - it produces points like 4.0, 1.0, 0.2. The
ratio between winners and losers grows, but so does the absolute size of the
numbers. If a model wants to be twice as sure, does it write 4.0 instead of
2.0? What does "twice as sure" even mean for a raw number?

**Break 2 - the naive exponentials overflow.** The fix people usually reach
for is to exponentiate the scores first (so a score of 2 beats a score of 1 by
*e* times, not 2 times). But `exp(1000)` is bigger than a float can hold. One
overflowing weight makes the total infinite, and infinite divided by infinite
is `NaN` - the whole distribution collapses to `NaN` and every metric downstream
becomes garbage.

**Break 3 - the puzzle.** Take any scores, and add 5 to every one of them:
`[2, 1, 0.5]` becomes `[7, 6, 5.5]`. The contestant order did not change. The
gut answer is unchanged. So why would anyone care that the *numbers* changed?

## The real thing

**Softmax** turns a vector of raw scores (called **logits**) into a
probability distribution:

```
softmax(z)_i = exp(z_i) / sum_j exp(z_j)
```

Three words, three moves:

1. **Exponentiate** every score. `exp` is always positive, so this is where a
   possibly-negative "raw score" becomes a non-negative "weight". It also
   makes gaps *multiplicative*: a score 2 above another scores `e^2 ~ 7.4`
   times the weight, not twice the weight.
2. **Sum** the weights. That total is the normalising constant.
3. **Divide** every weight by the total. The results now sum to 1, so they
   can be read as probabilities.

**Why exponentiate at all?** Because it answers Break 1. Doubling a logit
does not double the probability, but it does something far more useful: it
*sharpens* the distribution in a controlled way. The gap between two logits
gets multiplied by `e`, so a gap of 1 becomes a gap of 2.7 in weight, a gap
of 3 becomes a gap of 20. The bigger the gap, the more the softmax trusts
the ordering. This is the mechanism behind **temperature**, which is lesson
L13.

**Why the overflow fix is legal (Break 2).** Softmax is **invariant to a
constant shift**:

```
softmax(z + c) == softmax(z)   for any constant c
```

Proof in one line: `exp(z_i + c) = exp(z_i) * exp(c)`, so every numerator
gains the same factor `exp(c)` and the denominator gains it too - it cancels.
So we are free to choose the most convenient `c`, and the convenient choice is
`c = max(z)`. After subtracting the maximum, every exponent is `<= 1` and at
least one is exactly 1. Nothing can overflow. The probabilities are
**identical** to the naive version - this is a numerical trick, not a
different formula.

**Break 3 answered.** The constant shift is exactly what makes the stable
version possible. A model that is "more confident" produces larger logits;
subtracting the maximum throws away the common part and keeps only the
*differences*, which are the only part that ever mattered.

## In this repo

- `examples/01_softmax.py` - the naive and stable versions side by side, with
  every intermediate printed. Run it: `python examples/01_softmax.py`.
- `decisionarena/providers.py` - `normalise_answers()` is where a provider's
  raw answers become the `{"probabilities": {...}}` dict that the metrics
  consume. A `choice` answer arrives with probabilities already attached;
  the harness never computes them, it only measures them.
- `decisionarena/metrics.py` - `collect_scored()` reads
  `a["probabilities"]` and asks "what probability did you give the *correct*
  option?". That single number is the input to accuracy, Brier score and ECE.
- `cases/routing.json` - a `choice` question with four `criteria` options.
  That list is the vocabulary softmax is applied over.

## Your turn

Write a file `exercises/L12_softmax.py` that contains:

- a function `softmax(scores: list[float]) -> list[float]` that implements the
  three-step definition from "The real thing", using `math.exp`
- a function `softmax_stable(scores: list[float]) -> list[float]` that
  subtracts the maximum before exponentiating, and returns **the same
  numbers** as `softmax` for ordinary inputs
- a `main()` that prints the probabilities for the scores `[2.0, 1.0, 0.5]`
  with four decimal places, and prints the maximum probability
- a self-check section using `assert` that fails loudly if:
  - the probabilities do not sum to 1 (within `1e-9`)
  - the stable version disagrees with the naive version by more than `1e-9`
  - a higher score never receives a lower probability

Inputs: the score list above. Expected output: three probabilities summing to
1.0, with the largest attached to `2.0`.

**Hint:** the stable version differs from the naive version by exactly one
line, placed *before* the exponentials. Do not add the maximum back at the
end - the shift cancels inside the division, so you do not need to undo it.

**Do not** look at `examples/01_softmax.py` until you have run your own
version and compared the numbers. Then compare.

## Check yourself

Answer these out loud, in your own words, before you move on. If you cannot,
that is the concept to re-teach, not to move past.

1. Why does softmax subtract the maximum instead of just exponentiating
   directly? Name the failure it prevents and the property that makes it legal.
2. You double every logit in a 3-option question. Does the winning option
   still win? Does the probability of winning stay the same? Why?
3. A `choice` answer gives you `{"billing": 0.72, "technical": 0.18, ...}`.
   Which number in `decisionarena/metrics.py` is this dict used to compute, and
   what would go wrong downstream if that dict were slightly off?

## Artifact

Write `docs/notes/L12-softmax.md` - under 200 words, aimed at a smart
friend who has never heard of softmax. It must contain:

- the three-step definition in your own words (no "it is well known that")
- one sentence on why the stable version subtracts the maximum
- one concrete number from your own run of your own code

Then commit it. The artifact is the proof that you understood it, not the
proof that you ran the code.
