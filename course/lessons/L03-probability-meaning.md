---
id: L03
phase: 0
order: 5
title: "What a probability means here - and what it does not"
minutes: 25
concepts: [probability, uncertainty, odds]
prereqs: [L02, L10]
paths: [beginner, provider-live]
exercise_file: docs/notes/L03-probability-meaning.md
quiz: L03
---

# L03 - What a probability means here - and what it does not

## Why this matters

This repo is built on one number: the probability a model attaches to a
decision. Every headline metric - accuracy, Brier score, ECE, the
action-change rate - is a statement about those numbers. If you do not know
exactly what `0.9` claims, you cannot tell an over-confident model from a
well-calibrated one, and calibration is the whole point.

## The naive story

Picture a rain forecast. It says there is a **90% chance of rain** tomorrow.
What does that sentence mean?

Most people read it as "90% of tomorrow is wet". That is a cute joke and it
is wrong. The forecast is not making a claim about how much of the day is wet.
It is making a claim about **how often similar days turn out rainy**: if the
forecast had been issued for a hundred similar days, about ninety of them
would have rained, and ten would not.

That is the reading this repo uses. A probability is a **long-run frequency**
over repeated, similar situations - not a promise about the one case in front
of you.

## What breaks

**Break 1 - a probability is about the model, not about the world.** `0.9` does
not mean "this email is 90% about billing". It means: *given this state, this
model said "billing" with a probability of 0.9*. Change the model and the
number changes, even though the email did not. This is exactly why the repo
runs the same battery against several models.

**Break 2 - a probability is not a promise.** Even a calibrated model that
says 0.9 will be wrong one time in ten. If the harness treated a 0.9 as a
guarantee, then a model that says 0.9 on everything would look perfect on the
easy cases and terrible on the hard ones. The repo instead pairs the
probability with the outcome: `metrics.collect_scored()` returns two parallel
lists, `probs` (the model's number) and `outcomes` (1 or 0, whether it was
right). That pair is the raw material of every calibration metric.

**Break 3 - the same 0.9 can arrive as a boolean.** Some providers answer a
`noul` question with `{"type": "boolean", "boolean": true}` rather than with
a number. `normalise_answers()` folds that into `kind="noul"` and the value
becomes `True`. Then `metrics.collect_scored()` does `float(a["value"])` - and
`float(True)` is `1.0`. So a boolean answer is treated as a probability of
1.0, not as a probability of 0.5. Nothing is broken, but you should know that
a vendor returning `true` is claiming certainty, not a coin flip.

**Break 4 - "how sure are you?" is a different number.** See L04. The short
version now: probability is a claim about *the outcome*; confidence is a claim
about *the model's own feeling*, and this repo keeps them in two separate
fields.

## The story

Imagine a hundred mornings. On each one, before anyone goes outside, a
forecaster writes a single number on a card and pins it to a board: the
chance of rain today.

Now count the cards. On the mornings where the card said 0.9, it rained about
ninety times out of a hundred. On the mornings where the card said 0.6, it
rained about sixty times. That is the whole meaning of the number: a tally
of what happened on the days when the card said that.

Notice what it does not say. Not that ninety percent of today's sky is wet.
Not that today's forecast is ninety percent correct. On its own it says
nothing about today - it describes a population of days that resemble today.

And the tally belongs to the forecaster, not the weather. Swap the person at
the desk and the rain still falls on the same mornings, but the cards read
differently. A second forecaster might write 0.4 on a morning when the first
wrote 0.9, and both could be honest about their own past.

Which is why the number has to be counted against outcomes afterwards. A
desk that says 0.9 every morning and is right seven times in ten is not
lying - it is miscalibrated, and only the tally sheet shows it.

## The real thing

**Probability** - a float in `[0, 1]`. In this repo the rule from `AGENTS.md`
is exact: "Probabilities are floats in `[0, 1]`; confidence is separate from
probability."

A probability `p` attached to a decision means:

> Out of many similar situations, in about `p` of them (as a fraction), this
> decision would be the right one.

**Frequency, concretely.** If the model says `0.9` for a yes/no question and
it is *calibrated* (meaning: when it says 0.9, it is right 90% of the time),
then in 100 similar cases you expect about 90 yes and 10 no. Not "90% of the
answer is yes". The number describes a repeated experiment.

**Odds** - the same information written as "how many times more likely".
Odds are `p / (1 - p)`. A probability of 0.9 is odds of 9 to 1. The
translation table you should be able to read off the top of your head:

| probability | odds |
|---|---|
| 0.50 | 1 : 1 (a coin flip) |
| 0.75 | 3 : 1 |
| 0.90 | 9 : 1 |
| 0.99 | 99 : 1 |

Why care about odds? Because odds multiply when independent evidence stacks,
probabilities do not. And because "9 to 1" is what a person actually means by
"I am very sure" - it is much easier to feel than "0.9".

**Uncertainty** - the honest width around the number. Two ways to be
uncertain:

- **Aleatoric** uncertainty: the world itself is ambiguous. The email really
  could be billing or sales, and no model can settle it. This shows up as the
  *task* being hard.
- **Epistemic** uncertainty: the model does not know. It has not seen enough
  examples like this. This shows up as a model that is *confident and wrong* -
  and that is the dangerous one, because a 0.95 that is wrong costs more than
  a 0.6 that is wrong.

**Where the repo uses all this.**

- The **threshold** is a policy about probability: `cases/routing.json` says
  `"thresholds": {"is_billing": 0.5, "team": 0.6, "severity": 0.5}`. The
  model says 0.58 for billing; the threshold says act or do not act. The
  threshold is *your* decision, not the model's.
- The **Brier score** punishes wrong probability, not just wrong answers: a
  `0.99` that is wrong costs about a `0.5` that is wrong, squared.
- The **ECE** (expected calibration error) compares the probabilities to the
  outcomes bucket by bucket and asks: when it says 0.8, is it right 80% of the
  time?

## In this repo

- `decisionarena/metrics.py` - `collect_scored()` returns `probs, outcomes,
  rows`. For a `noul` it takes `p = float(a["value"])` and `o =
  int(bool(gold_value))`. For a `choice` it looks up the gold option in the
  `probabilities` dict. That `(p, o)` pair is the definition of a
  calibrated/over-confident answer.
- `decisionarena/metrics.py` - `_brier()` is `sum((p - o) ** 2) / n`, and
  `_ece()` buckets the pairs by probability and averages
  `abs(confidence - accuracy)` weighted by bucket size.
- `decisionarena/metrics.py` - `action_change_rate()` compares each answer's
  top probability against the case's threshold, which is where a probability
  becomes an action.
- `decisionarena/providers.py` - `normalise_answers()` keeps `probabilities`
  and `confidence` in separate fields, and defaults both when a provider
  omits them.
- `cases/routing.json` - the thresholds, sitting next to the gold answers.
- `decisionarena/harness.py` - `run_format_friction()` measures how far a
  probability *moves* when only the shape of the state changes. That experiment
  needs no labels at all, because it compares a probability against itself.

## Your turn

Write the file `docs/notes/L03-probability-meaning.md`. It is a note to a
friend who has just asked you what "90% chance of rain" really means. It must
contain, in this order:

1. **"What it means"** - one paragraph that explains a probability as a
   long-run frequency over similar cases, and states explicitly that it is a
   claim about the *model's* answer on that *state*, not about the world.
2. **"What it does not mean"** - at least three bullet points, each one
   tempting misreading, each corrected in the same bullet. Include the "90% of
   the day is wet" one.
3. **"Probability and odds"** - the four-row table above (0.50, 0.75, 0.90,
   0.99 against their odds), and one sentence saying which one to use when.
4. **"Two kinds of uncertainty"** - one sentence each for the kind that lives
   in the world and the kind that lives in the model.
5. **"One number from this repo"** - a real number you saw, with the command
   you ran. Either the probability a `noul` answer carried in one of your own
   runs, or the threshold `0.6` for the `team` question in
   `cases/routing.json`. If the number came from the mock provider, say so
   and say that it is a harness number, not a model measurement.

Expected output: a markdown note of roughly 350-500 words with the table, the
bullets and at least one traceable number.

**Hint:** the frequency reading of a probability comes from the word
"similar" - the cases are repeated, and the model is the same in each. For
odds, the denominator is the probability of the outcome *not* happening, which
is why odds and probabilities are not interchangeable.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. A model says 0.9 for "is this about billing". Write down exactly what
   that sentence claims, and one thing it does not claim.
2. Why does this repo store the probability and the outcome side by side
   instead of just keeping the answers?
3. Your team uses a threshold of 0.6 to act. What happens to the action
   when the same model answers 0.72 at one run and 0.58 at another, and why is
   that a problem for a *swapped* model?

## Artifact

Publish `docs/notes/L03-probability-meaning.md` - the note you just wrote. The
artifact is the proof that you can explain a probability to someone without
using the words "chance" and "probably" as a substitute for an explanation.
