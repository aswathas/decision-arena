---
id: L54
phase: 5
title: "Action-change rate - swap safety"
minutes: 35
concepts: [action-change-rate, swap-safety, thresholds, hysteresis-intro]
prereqs: [L53, L02]
paths: [beginner, foundations, provider-live]
exercise_file: exercises/L54_swap_safety.py
quiz: L54
---

# L54 - Action-change rate: swap safety

## Why this matters

Here is the question a real buyer asks, and it is not "which model is more
accurate?". It is: **"if I swap my vendor, what changes?"** If the answer is
"the same decisions, the same escalations, the same tickets auto-closed",
then the swap is boring and safe. If the answer is "a few percent of tickets
take a different path", you need to know which few percent - because that is
where your risk is. This repo's answer to that question is the **action-change
rate**.

## The naive story

Picture two thermostats on the same wall, both set to heat at 22 °C. One
reads 21.9 °C, the other reads 22.1 °C. Do they "agree"? They are on the
same side of the set point, so yes - and in every way that matters they are
the same thermostat. Nobody calls the difference between 21.9 and 22.1 a
behaviour change.

Now picture the same two thermostats in a house where the set point is 21.5 °C.
One reads 21.4 (below - heater off) and the other reads 21.6 (above - heater
on). They are still "close", they might even look like they agree, but one of
them is heating the house and the other is not. The action changed.

**Swap safety** is the property that the second thing does not happen.

## What breaks

**Break 1 - agreeing on the label is not the same as acting the same way.**
The `team` question in `cases/routing.json` has a threshold of `0.6`, not
`0.5`. Two providers can both pick `"billing"` - perfect label agreement -
and still disagree about whether to act on it: provider A says `billing` at
0.62 (above 0.6, act), provider B says `billing` at 0.58 (below 0.6, do not
act). The labels agree; the actions do not.

**Break 2 - a tiny probability difference can flip a decision.** Take the
`is_billing` question with its threshold of `0.5`. Provider A says `0.48`,
provider B says `0.52`. The difference is `0.04` - four percentage points -
and it flips the action completely. This is not an edge case in the
arithmetic; it is the normal condition of a threshold sitting in the middle
of the distribution of two models' outputs.

**Break 3 - a threshold with no margin is a switch that flickers.** Even
without swapping vendors, a single threshold invites **flapping**: the
probability wobbles around the threshold and the action flips back and
forth. The fix is a **margin** - two thresholds instead of one, so the
provider must clear a higher bar to start acting and drop below a lower bar
to stop. That is called **hysteresis**, and this repo does not implement it
- it measures the *damage* that hysteresis would prevent, which is exactly
what the action-change rate is for.

## The story

Picture two thermostats on the same wall, both set to heat at 22 °C. One reads
21.9 °C, the other 22.1 °C. They agree, and in every way that matters they are
the same thermostat. Nobody calls the difference between those readings a
behaviour change.

Now put the set point at 21.5 °C. One reads 21.4 and the other 21.6. Still
close, still looking like agreement - but one of them has the heater on and
the other has it off. The action changed.

That gap is the question a buyer actually asks. Not which model is more
accurate, but: if I swap the vendor, what changes? The same decisions, the
same escalations, the same tickets closed automatically means a boring, safe
swap. A few percent of tickets taking a different path means you need to know
which few percent, because that is where your risk sits.

A label is not an action. The routing questions carry their own thresholds,
and two providers can pick the same team and still disagree about whether to
act on it - one just above the threshold, one just below. And a probability
difference of 0.04 is enough to flip a threshold, because a threshold sitting
in the middle of two models' outputs is the normal condition, not an edge
case.

## The real thing

**The metric.** `action_change_rate(a, b, thresholds)` in
`decisionarena/metrics.py` takes two providers' answers and a dict of
thresholds, and returns `{"compared", "action_changes",
"action_change_rate", "changes"}`.

For each question in the thresholds dict that both providers answered:

- if the question is a `noul`, the provider **acts** when its probability is
  `>= threshold`;
- otherwise, the provider acts when its **top** probability (the largest
  value in its `probabilities` dict) is `>= threshold`.

If A acts and B does not (or the reverse), that is one **action change**, and
the rate is `action_changes / compared`.

**The thresholds.** They live with the cases, not with the code. In
`cases/routing.json` every case carries:

```
"thresholds": {"is_billing": 0.5, "team": 0.6, "severity": 0.5}
```

`cases/injection.json` carries the same shape with its own question ids
(`contains_pii`, `is_destructive`, `severity`). The thresholds are a
*product decision*: `0.6` on `team` means "only route automatically when the
model is fairly sure". A different company would choose different numbers,
and the harness measures whatever numbers you give it.

**Where it is used.** `decisionarena/cli.py`'s `cmd_swap()` runs one battery
against two providers, then per case calls `action_change_rate()` with that
case's thresholds, and rolls the results up. `decisionarena/report.py`'s
`swap_report()` prints the action-change rate next to agreement and the
probability gaps, and - when there are changes - a table titled "Decisions
that would change" with the case, the question, which provider acts, and
both providers' values.

**How to read it.**

| agreement | action-change rate | what it means |
|---|---|---|
| high | low | the swap is safe: same labels, same actions |
| high | high | the labels agree but the *decisions* are not safe - a threshold problem |
| low | low | the providers differ in opinion but rarely near a threshold |
| low | high | the swap is dangerous |

**The hysteresis introduction.** With one threshold, a provider acts when
`p >= t`. With hysteresis you use two: act when `p >= t + margin`, and keep
acting until `p < t - margin`. The band between them is a "do not change
your mind" zone. Two models whose probabilities differ by 0.04 will almost
never disagree about the action inside such a band - so the action-change
rate falls, and the flapping stops. The trade-off you accept is a delay: the
system becomes slower to react near the threshold. That is a real cost, and
it is a product decision, not a modelling one.

**Why this is the metric the repo was built around.** The repo's brief is
that every vendor publishes a benchmark where they win. Label agreement and
accuracy are both vendor-favourable framings. The action-change rate is
neither: it asks what *you* would have to change in production if you
changed vendor, which is the only question a buyer actually has.

## In this repo

- `decisionarena/metrics.py` - `action_change_rate()`, the metric; note the
  `noul` branch (compare the value) and the other branch (compare the top
  probability), and the `changes` list it returns.
- `cases/routing.json` - the thresholds dict `{"is_billing": 0.5, "team":
  0.6, "severity": 0.5}` on every case.
- `cases/injection.json` - the same idea with the injection battery's
  question ids.
- `decisionarena/cli.py` - `cmd_swap()`, which takes `--provider a=...`
  `--provider b=...`, picks up the thresholds from the cases, and sums the
  per-case action changes.
- `decisionarena/report.py` - `swap_report()`, which prints "action change
  rate at threshold" and the "Decisions that would change" table with
  `a_acts`, `b_acts`, `a_value` and `b_value`.
- `examples/02_temperature.py` - the temperature knob changes the
  probabilities *behind* the threshold, which is another way to move actions
  without moving labels.

## Your turn

Write a file `exercises/L54_swap_safety.py` that contains:

- a function `make_answers(noul_value: float, top_option: str, top_prob: float) -> dict`
  that builds one answer dict in the shape `normalise_answers()` produces,
  holding a `noul` answer for `is_billing` (value `noul_value`) and a `choice`
  answer for `team` (value `top_option`, with `probabilities` where
  `top_option` has probability `top_prob` and the other options share the
  rest). Both providers in this exercise pick `"billing"` for `team`, so the
  label always agrees
- a function `changed(a: dict, b: dict, thresholds: dict) -> dict` that calls
  `metrics.action_change_rate()` and returns its result
- a function `with_hysteresis(a: dict, b: dict, thresholds: dict, margin: float) -> dict`
  that computes the same thing but with the two-threshold rule: a provider
  acts when its value is `>= threshold + margin`, and does **not** act when
  its value is `<= threshold - margin`; between the two, it keeps the
  previous state, which for a single-shot comparison means it acts only if
  **both** providers are above `threshold + margin`. Use `margin=0.05`
- a `main()` that runs three experiments and prints, for each, the label
  agreement rate, the action-change rate, and (for the third) the
  action-change rate under hysteresis:
  1. **Same label, different action.** `team` top probability `0.62` for A and
     `0.58` for B, with the threshold `0.6`. Expect label agreement `1.0` and
     an action change.
  2. **A small gap flips a 0.5 threshold.** `is_billing` value `0.48` for A
     and `0.52` for B, with the threshold `0.5`. Expect a 0.04 difference and
     an action change.
  3. **The same pair under hysteresis.** Experiment 2's pair, with a margin
     of `0.05`. Expect the action change to disappear.

  For each experiment, pass **only the threshold of the question under
  test** - `{"team": 0.6}` for experiment 1 and `{"is_billing": 0.5}` for
  experiments 2 and 3 - so that the reported rate is about that question
  alone. In experiments 2 and 3 give both providers the same `team` top
  probability (`0.9`) so that the `team` question cannot be the thing that
  changes. In every experiment both providers pick `"billing"` for `team`, so
  the label always agrees.
- a self-check section using `assert` that fails loudly if:
  - experiment 1's label agreement rate is not `1.0` (both providers said
    `"billing"`)
  - experiment 1's action-change rate is not `1.0` (0.62 clears 0.6, 0.58
    does not)
  - experiment 2's action-change rate is not `1.0` (0.48 and 0.52 straddle
    0.5)
  - experiment 3's action-change rate is not `0.0` (the margin swallows the
    0.04 difference)

Inputs: the threshold entries from `cases/routing.json` - `0.6` for `team`
and `0.5` for `is_billing`. Expected output: three blocks, each with an
agreement rate, an action-change rate and - for the third - a rate of `0.0`
under hysteresis.

**Hint:** the whole metric is one comparison per question - "is this value
at or above the threshold?" - and hysteresis is the same comparison with a
second, lower threshold added. Read `action_change_rate()` and notice that
the `noul` branch and the `choice` branch compare two different things.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. Two providers agree on the label `"billing"` for `team`. Name the one
   number that could still differ and flip the action, and say which
   threshold it is compared against.
2. Why is a 0.04 probability difference enough to change what you do, and
   what is that called when it happens without any vendor swap?
3. What do you give up when you add hysteresis, and who should decide that
   trade-off?

## Artifact

Write `docs/notes/L54-swap-safety.md` - under 300 words, for a smart friend
who has heard of A/B testing. It must contain:

- the action-change rate you measured in each of your three experiments,
  with the numbers you fed in
- one sentence explaining why "the labels agreed" and "the actions agreed" are
  different claims
- one sentence on what hysteresis buys and what it costs
- one sentence saying who should choose the threshold values, and why

Then commit it.
