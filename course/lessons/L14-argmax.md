---
id: L14
phase: 1
title: "Logits, argmax and why temperature never changes the ranking"
minutes: 30
concepts: [logits, argmax, ranking-invariance]
prereqs: [L12, L13]
paths: [beginner, foundations]
exercise_file: exercises/L14_argmax.py
quiz: L14
---

# L14 - Logits, argmax and why temperature never changes the ranking

## Why this matters

Two different numbers hide behind the word "the model's answer". One is the
**logit** - a raw score, before any conversion. The other is the
**probability** - after softmax. The harness only ever thresholds, compares
and reports the probability, but the *label* it reports comes from the
argmax, and if you cannot compute an argmax in your head you cannot tell a
model that changed its mind from a model that merely re-scaled its confidence.

## The naive story

A quiz show with three contestants. The scores on the board are raw: 8, 5, 4.
Those raw scores are the **logits** - unconverted, unbounded, possibly
negative, and definitely not adding up to anything meaningful. They only
become probabilities after the softmax from L12.

Now, the only thing most people actually want from that board is a single
answer: **who won?** The name of that operation is **argmax** - the index of
the largest value. It is the "pick the winner" function, and it is the reason
you can talk about a model's answer without mentioning probability at all.

## What breaks

**Break 1 - logits are not probabilities.** They are not in `[0, 1]`. They do
not sum to 1. They can be negative. A logit of `8` does not mean "8% likely"
- it means "the raw score was 8", and what that turns into depends entirely
on the other logits next to it. Add `100` to every logit and the model is
*exactly as certain* as before (L12's shift invariance), while every logit
now looks more impressive.

**Break 2 - "the score is bigger" is not a fact about the model.** Because
softmax cares only about the *gaps* between logits, the absolute size of a
logit is meaningless. Multiply every logit by 3 and the **ranking does not
change at all** - same winner, same order, same label. (The probabilities do
change: they get sharper, exactly as a temperature below 1 does. What cannot
change is the order.) This is the **ranking-invariance** property, and it is
the formal reason L13's temperature cannot change which option wins:
dividing every logit by a positive number is just one particular rescaling.

**Break 3 - argmax on the logits and argmax on the probabilities agree, but
only because softmax is monotonic.** Softmax is *order-preserving*: it never
promotes a lower logit over a higher one. So `argmax(z) == argmax(p)`. But
this is a theorem, not something you may assume in general - and the day you
replace softmax with some other squashing function (or with a hand-written
probability dict from a provider), you have to check it. The mock provider
computes its top option with `max(probs, key=lambda k: probs[k])` - from the
*probabilities*, not from logits.

**Break 4 - the label a model reports and the label its distribution prefers
can be different things.** In this repo, a `choice` answer carries two
independent facts: the `value` (the option the model says it picked) and the
`probabilities` (what it thinks of every option). `metrics.collect_scored()`
uses the `probabilities` to get `p_gold` and uses the `value` to decide
"correct" - so if a provider reports `value = "billing"` while its
distribution peaks at `"technical"`, the harness will happily report a
correctness that disagrees with the model's own preference. Nothing crashes;
you just get a strange number.

**Break 5 - ties need a rule.** If two options have the same probability,
who wins? Python's `max()` returns the **first** one it sees. A tie-break rule
that is not written down is a tie-break rule that will differ between your
laptop and the next run - and this repo cares a lot about determinism.

## The story

Imagine a quiz show where three contestants hold up numbered cards. The
numbers are not percentages and do not add up to anything. They are marks on
a board, and the only thing the audience wants is the name of the contestant
with the highest mark.

So a stagehand walks along the board with a pointer, touches the highest
mark, and that is the winner. The pointer is the operation: it hands back a
position, and you look the name up yourself.

Here is the surprising part. Suppose the stagehand is told to double every
mark on the board. The marks all grow - the winner's mark grows by most,
because it was the biggest - and the pointer moves to exactly the same
contestant. The order did not change, because you cannot reorder a set of
numbers by making them all bigger in the same proportion. The temperature
dial from the last lesson scales every score the same way, and the winner is
the same there too.

Add the same amount to every mark instead, and again nothing reorders. Only
the gaps carry information.

Which means "the model was more sure" has to be unpacked first. If only the
gaps grew, the model did not change its mind - it said the same thing more
loudly.
## The real thing

**Logit** - a raw, uncalibrated score that a model produces for each option.
The softmax (L12) turns logits into probabilities; the temperature (L13)
rescales logits before that. The chain is always:

```
logits  --(divide by T)-->  scaled logits  --(softmax)-->  probabilities  --(argmax)-->  label
```

**Argmax** - the index of the largest element of a list. Three properties you
should be able to state:

1. It returns a **position**, not a value. To get the name, you index the same
   list you ranked.
2. It is **not sensitive to scale**: multiplying every value by a positive
   constant leaves the argmax untouched.
3. It needs a **tie-break rule** on ties. The standard one is "the first
   (lowest index) wins", and it should be stated wherever it is used.

**Ranking-invariance** - the property, stated properly:

> For any list `v` and any positive constant `c`,
> `argmax(c * v) == argmax(v)`, and the full ranking is unchanged too.

Not just the winner: the whole order survives. Proof in one line: if
`v_i > v_j` then `c * v_i > c * v_j` whenever `c > 0`, so every pairwise
comparison comes out the same way.

Two corollaries this course leans on:

- **Temperature cannot change the ranking** (L13). `T` divides by a positive
  number, which is a rescaling, and rescaling preserves order. So the *label*
  is temperature-invariant. The *probability* is not - and that is why the
  threshold-based **action** can change.
- **Adding a constant to every logit changes nothing either** (L12's shift
  invariance). The absolute size of a logit carries no information; only the
  gaps do.

## In this repo

**Where the repo uses each piece.**

- `decisionarena/providers.py` - `MockProvider.decide()` picks the top option
  with `max(probs, key=lambda k: probs[k])` and reports it as the `choice`
  value, alongside the full `probabilities` dict and a `confidence`.
- `decisionarena/metrics.py` - `label_agreement()` compares two providers by
  their `value` fields (and for a `noul`, by which side of `0.5` the
  probability falls on). `action_change_rate()` uses
  `max((aa["probabilities"] or {0: 0}).values(), default=0)` - the top
  probability, i.e. the softmax of the top logit, compared against the
  threshold.
- `decisionarena/metrics.py` - `collect_scored()` reads
  `dist.get(gold_value, 0.0)` for a `choice` and
  `dist.get(str(int(gold_value)), 0.0)` for a `score`: the probability of the
  *gold* option, which is not necessarily the top one.
- `cases/routing.json` - the `team` question's four `criteria` keys are the
  vocabulary an argmax is taken over.

## Your turn

Write a file `exercises/L14_argmax.py` that contains:

- a function `argmax(values: list[float]) -> int` that returns the index of
  the largest value. **Ties go to the lowest index.**
- a function `ranked_indices(values: list[float]) -> list[int]` that returns
  the indices ordered from the largest value to the smallest. **Ties go to
  the lower index first.**
- a function `top_k(probs: dict[str, float], k: int) -> list[tuple[str,
  float]]` that returns the `k` highest-probability options as
  `(option, probability)` pairs, sorted by probability from high to low. On a
  tie, the option whose name comes first alphabetically wins, so the result
  is always the same for the same input.
- a function `most_likely_level(probs: dict[str, float], level_names:
  list[str]) -> str` that takes a `score` answer's probability dict (whose keys
  are the **string** forms of the indices, like `"0"`, `"1"`, `"2"`) and the
  ordered list of level names, and returns the name of the level with the
  highest probability. On a tie, the lower index wins.
- a function `ranking_invariant(values: list[float], factor: float) -> bool`
  that returns whether the ranking is unchanged when every value is multiplied
  by `factor`.
- a `main()` that:
  - loads the first case of `cases/routing.json` with `json.load` (the file is
    a dict with a `"cases"` list)
  - builds a `providers.MockProvider()` and calls
    `provider.decide(case["state"], case["questions"])`
  - takes the `team` answer's `probabilities` dict and the option names in the
    order of the question's `criteria` keys, and prints:
    - the `argmax` position and the option name at that position
    - the full ranking as option names, most likely first
    - the `top_k` result for `k = 2`
    - the `most_likely_level` of the `severity` answer, using the
      `severity` question's `criteria` list as the level names
  - prints whether the ranking is invariant under a factor of `3.0` and under
    a factor of `0.5`
- a self-check section using `assert` that fails loudly if:
  - `argmax([1.0, 3.0, 3.0])` is not `1` (the tie goes to the lower index)
  - the option name at the `argmax` position is not the same option as the
    `value` the provider reported for the `team` question
  - the `most_likely_level` of the `severity` answer does not match the level
    the provider reported for `severity`
  - `ranking_invariant` is not `True` for both `3.0` and `0.5`

Inputs: the first case of `cases/routing.json`, and the offline mock provider
(no API key, no network). Expected output: the winning option and its
position, the four options in ranked order, the top two options with their
probabilities, the severity level name, and `True` for both invariance
checks.

**Hint:** argmax returns a *position*, so to print a name you index the same
list you ranked - and the tie-break rule has to be the same in every function
that has to agree with it. For the score question, the probability dict is
keyed by the **string** form of the index, so it needs converting before you
can use it as a position.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. What is the difference between a logit and a probability, and what makes a
   logit's absolute size meaningless?
2. Why does temperature change the probability but never the ranking?
3. A provider reports `value = "billing"` but its probability dict peaks at
   `"technical"`. Which one does `collect_scored()` use for the probability
   of the gold option, and which one does it use to decide "correct"?

## Artifact

Write `docs/notes/L14-argmax.md` - under 250 words, for someone who has heard
the word "logit" and nothing else. It must contain:

- one sentence saying what a logit is and one saying what argmax does
- the ranking-invariance property, written as one sentence with the condition
  that makes it true
- one concrete number from your own run of your own code - the winning
  option's probability, with the option's name

Then commit it. The artifact is the proof that you can explain why "bigger
score" is not the same as "more likely" - and why this repo is right not to
care about the size of a score at all.
