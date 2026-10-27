---
id: L11
phase: 1
title: "Numbers you can trust - tolerance, rounding and the 0.1+0.2 trap"
minutes: 30
concepts: [float-precision, tolerance, rounding, comparison]
prereqs: [L10]
paths: [beginner, foundations]
exercise_file: exercises/L11_numbers.py
quiz: L11
---

# L11 - Numbers you can trust - tolerance, rounding and the 0.1+0.2 trap

## Why this matters

Half of the bugs in a measurement harness are arithmetic bugs. You compute a
probability distribution, check that it sums to 1, and the assert fires - and
now you do not know whether the maths is wrong or the floats are lying. This
lesson is about telling those two apart, because a harness that cannot trust
its own numbers cannot publish anybody else's.

## The naive story

You write the obvious check:

```python
assert 0.1 + 0.2 == 0.3
```

It fails. Python says `0.1 + 0.2` is `0.30000000000000004`. Your first
thought is that Python is broken. It is not - it is telling you the truth
about a fact of arithmetic that most people never think about.

## What breaks

**Break 1 - decimal fractions are not binary fractions.** Your computer stores
numbers in binary, in slots. `0.5` is exactly representable (it is
`0.1` in binary). `0.1` is not: the nearest binary number to `0.1` is
slightly above it. `0.2` is slightly above `0.2`. Add the two slightly-above
numbers and you land on a number that is slightly above `0.3`. So the error
is not "maths is broken" - the error is real and it is *tiny*.

**Break 2 - exact equality on floats is a bug factory.** `a == b` asks "are
these two binary numbers bit-for-bit identical?". For anything computed by
addition, subtraction, division or an exponential, the answer is "no, and it
was never going to be". The fix is not to round everywhere - rounding hides
real errors. The fix is to compare with a **tolerance**: "are these two
numbers within a tiny distance of each other?"

**Break 3 - but a tolerance has to be chosen, and it is not free.** Too loose
and you accept a genuinely wrong number. Too tight and you fail on a real
difference. The repo uses `1e-9` for probabilities and `1e-12` for exact
sums - a probability is a rounded decimal from a provider, so it deserves
slack; a sum of floats that should be exactly 1 does not.

**Break 4 - rounding is for printing, not for deciding.** Rounding to 4
decimal places is what you do when a human reads the number. If you round
before comparing, you can create differences that were never there - and in
this repo you can also *lose* them: `round(0.99995, 4)` becomes `1.0`, so two
different probabilities can become the same printed number. Decide with the
full-precision value; round only on the way out.

## The real thing

**The tolerance idiom.** Two numbers are "the same" when the distance between
them is below a threshold:

```
almost_equal(a, b)  <=>  abs(a - b) < tol
```

with a typical `tol` of `1e-9` for probabilities and `1e-12` for sums that
should be exactly 1.

**Relative error** - when the numbers are of different sizes, an absolute
tolerance is not enough. `abs(a-b) < 1e-9` is a *big* tolerance for numbers
around `1e-12` and a *tiny* one for numbers around `1e9`. The scale-free
version divides by the size of the numbers:

```
relative_error(a, b) = |a - b| / max(|a|, |b|)
```

For a probability near 0.9, a relative error of `1e-9` means an absolute
difference of about `9e-10`.

**Rounding.** `round(x, places)` returns the closest representable number to
`x` with `places` digits after the point. Two things to know:

- `round()` returns a **float**, not a string. `round(0.30000000000000004, 4)`
  is `0.3`, and `print(round(0.30000000000000004, 4))` shows `0.3`.
- `round()` uses "round half to even": `round(2.5)` is `2`, and
  `round(0.5)` is `0`. Almost nobody wants that, so do not build money on
  `round()` - this repo computes cost in full precision and only formats it
  at print time.

**Where this repo does each thing.**

- **Full precision internally.** `metrics._brier()` computes
  `sum((p - o) ** 2 for p, o in zip(probs, outcomes)) / len(probs)` with no
  rounding at all. `metrics._ece()` likewise compares `abs(conf - acc)`
  against nothing - it just averages.
- **Rounding at the edges.** `metrics.collect_scored()` rounds `p_gold` to 4
  decimal places when it writes a row. `metrics.score_case()` rounds the
  headline `accuracy`, `brier` and `ece` to 4 places. `report.run_report()`
  prints the cost as `${result.cost_total:.6f}` - the *formatting* does the
  rounding, the number itself is untouched.
- **Tolerance in the self-checks.** `examples/01_softmax.py` asserts
  `abs(total - 1.0) < 1e-12` for the sum, and `abs(p_n - p_s) < 1e-12` when
  comparing the naive and stable softmaxes. The probabilities themselves are
  rounded to 6 places for *printing* only.
- **Rounding at the provider boundary.** `MockProvider` stores probabilities
  already rounded to 4 places (`round(w / total, 4)`), and the confidence at
  `round(min(0.99, probs[top] + 0.05), 4)`. So the numbers you read in a run
  file are *already* 4-decimal numbers - which is exactly why your own
  comparisons need a tolerance of about `1e-9` and not `1e-15`.

**The practical rule.** Compare with a tolerance. Round for display. And when
you report a number, say how many digits it has - the repo's money rule is
"always reported with the run's token counts beside it", which is the same
instinct: a number without its precision is a marketing number.

## In this repo

- `examples/01_softmax.py` - the self-check block: `abs(total - 1.0) <
  1e-12`, `abs(p_n - p_s) < 1e-12`, `abs(p - 0.25) < 1e-12`.
- `decisionarena/metrics.py` - `_brier()` and `_ece()` do full-precision
  arithmetic; `score_case()` rounds the three headline numbers to 4 places.
- `decisionarena/metrics.py` - `collect_scored()` rounds `p_gold` to 4 places
  in every row it writes.
- `decisionarena/providers.py` - `MockProvider.decide()` rounds every
  probability and confidence to 4 decimals before returning them.
- `decisionarena/report.py` - `run_report()` formats money with
  `{result.cost_total:.6f}` and prints the ECE as it was computed.
- `decisionarena/harness.py` - `run_battery()` rounds `latency_s` to 4
  places and `cost_usd` to 8 places in every JSONL record.

## Your turn

Write a file `exercises/L11_numbers.py` that contains:

- a function `almost_equal(a: float, b: float, tol: float = 1e-9) -> bool`
  that returns whether the two numbers are within `tol` of each other.
- a function `relative_error(a: float, b: float) -> float` that returns
  `|a - b| / max(|a|, |b|)`, and returns `0.0` when both numbers are zero.
- a function `sum_error(probs: list[float], target: float = 1.0) -> float`
  that returns `abs(sum(probs) - target)` - how far the list is from summing
  to the target.
- a function `round_for_report(x: float, places: int = 4) -> float` that
  returns the number rounded to `places` decimal places.
- a function `differing_options(a: dict[str, float], b: dict[str, float],
  tol: float = 1e-9) -> list[str]` that returns the sorted option keys whose
  probabilities differ by **more than** `tol` between the two distributions.
  Options present in only one of the two dicts count as differing.
- a `main()` that prints:
  - `0.1 + 0.2` and its `repr`
  - whether `almost_equal(0.1 + 0.2, 0.3)` is `True`
  - whether `almost_equal(0.1 + 0.2, 0.3, tol=0.0)` is `True` (it must not
    be)
  - the `sum_error` of the list `[0.72, 0.18, 0.10]`
  - the `relative_error` of `0.72` and `0.70`
  - the `differing_options` of `{"billing": 0.72, "technical": 0.18}` and
    `{"billing": 0.71, "technical": 0.19}`
- a self-check section using `assert` that fails loudly if:
  - `almost_equal(0.1 + 0.2, 0.3)` is not `True`
  - `almost_equal(0.1 + 0.2, 0.3, tol=0.0)` is not `False`
  - `sum_error([0.72, 0.18, 0.10])` is not below `1e-9`
  - `differing_options` on the two dicts above does not return exactly
    `["billing", "technical"]`

Inputs: the literal numbers above. Expected output: `0.30000000000000004`,
then `True`, then `False`, then a `sum_error` of about `1.1e-16`, then a
`relative_error` of about `0.028`, then the two differing option keys.

**Hint:** the question "are these the same number?" is really "are these the
same number *within a tolerance*?" - and the tolerance you pick depends on
how many digits the numbers actually carry. The repo's own self-checks use
`abs(x - y) < 1e-12` for sums and `1e-9` for probabilities.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. Why is `0.1 + 0.2 == 0.3` False, in one sentence that is not "because of
   binary"?
2. When should you round a number, and when should you compare with a
   tolerance? Why is rounding before comparing a bad idea?
3. This repo stores provider probabilities already rounded to 4 decimal
   places. What tolerance would you pick for comparing two providers'
   probability dicts, and why not `1e-15`?

## Artifact

Write `docs/notes/L11-numbers.md` - under 250 words, for a smart friend who
has written Python for years and thinks floats are exact. It must contain:

- your own explanation of why `0.1 + 0.2 != 0.3`, in two or three sentences
- the tolerance idiom, written as a one-line formula
- one concrete number from your own run of your own code - the `sum_error` or
  the `relative_error` you printed

Then commit it. The artifact is the proof that you can defend a tolerance
choice to somebody who wants to use `==`.
