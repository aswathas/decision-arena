---
id: L13
phase: 1
title: "Temperature - sharpening and flattening a distribution"
minutes: 30
concepts: [temperature, softmax, sharpness, sampling]
prereqs: [L12]
paths: [beginner, foundations]
exercise_file: examples/02_temperature.py
quiz: L13
---

# L13 - Temperature - sharpening and flattening a distribution

## Why this matters

The probabilities this repo measures are not raw model output - they are the
output of a softmax, and the softmax has a dial on it. Turn that dial and the
model's answers get sharper or flatter *without the model changing its mind
about which option is best*. That sounds harmless. It is not: this repo acts
on a probability crossing a threshold, so the dial can change **what you do**
while the ranking stays exactly the same.

## The naive story

Picture a panel of three judges scoring a support ticket, each from 0 to 10.
Raw scores: billing 8, technical 5, other 4. That is a *spread* of scores, and
it tells you the top judge liked it most. Now you want to convert scores into
"how likely is each option" numbers, and you get the softmax from L12:
exponentiate, sum, divide.

Temperature is one extra step before the exponentiate. Imagine the panel is
strict: multiply every score by a factor before comparing them. A strict panel
makes the winner's win look bigger. A lenient panel squashes the gaps so
everything looks close.

## What breaks

**Break 1 - the intuitive wrong picture: "temperature makes the model think
differently".** It does not. Temperature does not change the ordering of the
options, ever. It changes how the *same* ordering is spread out over the
probability scale. `billing` is still the top option at every temperature.
If you find yourself saying "the model changed its answer", you have confused
"which option is best" with "how far ahead is it".

**Break 2 - "it makes the model more accurate".** It does not. Temperature is
not a fix for a bad model; it is a dial on how loudly the same distribution is
spoken. A model whose top option is the *wrong* option does not become right
at a lower temperature - it just becomes wrong more confidently. Lowering
temperature to make a bad model look good is exactly the trick the mock
provider plays with its confidence field, and it is how you end up with a
system that is confidently wrong.

**Break 3 - temperature is a divisor, so zero is forbidden.** `T = 0` means
"divide every logit by zero". The repo's own example guards against it:
`examples/02_temperature.py` raises `ValueError("temperature must be > 0")`
and has a self-check that asserts temperature `0` is rejected. Note that this
is *not* the same as a text model's API-level `"temperature": 0`, which means
"always pick the most likely token" - that is a sampling convention, not a
division.

**Break 4 - sampling.** A probability distribution has a second use besides
reporting: you can **sample** from it - pick an option at random with
probability `p`. That is how a text model generates the next word. And here
temperature matters to sampling directly: at a low temperature the random
pick almost always lands on the top option (sharp, repetitive text); at a high
temperature it lands almost uniformly (creative, erratic text). This repo
never samples - it always takes the top option - but the word "sharpness" and
the knob itself come from that world, and the OpenAI-compatible adapter in
this repo sends the API-level `"temperature": 0` for exactly that reason.

**Break 5 - and the one that matters most here: the action can change while
the answer does not.** The repo's threshold for the `team` question is `0.6`
(`cases/routing.json`). At `T = 0.25` the top option sits at about `0.98` and
the harness acts. At `T = 4.0` the same option sits at about `0.41`, and the
harness does **not** act - even though the option it would have picked is
identical. Same model, same state, same ranking, different action. This is
why `metrics.action_change_rate()` exists, and why a benchmark that only
compared labels would have missed it entirely.

## The real thing

Temperature is a single positive scalar that divides every logit **before**
the softmax:

```
p_i(T) = exp(z_i / T) / sum_j exp(z_j / T)
```

That is the whole definition. Everything else is a consequence.

**What it does to the shape:**

- `T < 1` (sharpening): the scores get bigger and further apart. The top
  option's probability rises towards 1, the others collapse towards 0. The
  distribution becomes *peaked*.
- `T = 1`: the model's own distribution, untouched.
- `T > 1` (flattening): the scores get smaller and closer together. The
  distribution flattens towards uniform - all options look about equally
  likely, which is the model's way of hedging.

**What it does to the ranking: nothing.** Dividing every logit by the same
positive number cannot reorder them. If `z_a > z_b` then `z_a / T > z_b / T`
for every `T > 0`. So the argmax (the index of the largest value) is
temperature-invariant. Only the *shape* changes.

**How sharp is it? Ask the entropy.** The **entropy** of a distribution is

```
H = -sum(p_i * log(p_i))
```

- a distribution with all its mass on one option has entropy `0`
- a uniform distribution over `n` options has entropy `log(n)` (about `1.0986`
  for 3 options)

Entropy measures "how undecided is this model?". As `T` rises, entropy rises.
That is the cleanest single number for "sharp vs flat", and it is why
`examples/02_temperature.py` prints it next to every row.

**The limits.** As `T -> 0`, the distribution becomes one-hot (all mass on the
top option). As `T -> infinity`, it becomes uniform. `T = 0` itself is
undefined - it is the limit, not a value you can set.

**Why the harness cares.** This repo's decision rule is a threshold on the
probability:

```
act if max(probabilities) >= threshold
```

So temperature sits *directly upstream of the action*. It is the one knob
that can move a decision without moving a label - and the repo has a metric
built specifically to catch that: `metrics.action_change_rate()`, which
compares two providers at a threshold and counts how often the *action*
changes.

**And a caution about calibrating with temperature.** Because raising `T`
flattens a distribution, it can pull an over-confident model's probabilities
back toward calibrated. That is a legitimate deployment dial - but it is also
a way to make a bad model look better on a chart while changing nothing about
the underlying competence. If you use temperature to fix calibration, say so
in your report, and measure it (the ECE, L04) rather than assume it.

## In this repo

- `examples/02_temperature.py` - the file this lesson is built around. Its
  `softmax(logits, temperature=1.0)` divides by the temperature and *then*
  subtracts the maximum (the shift still cancels, so the order does not
  matter). Its `entropy(probs)` computes `H` in nats, with an `if p > 0`
  guard because `0 * log(0)` is `NaN`. Its printed table is (T, probabilities,
  entropy, max p), and it ends with a threshold table showing "acts?".
- `examples/01_softmax.py` - the temperature-free version, for comparison.
- `decisionarena/providers.py` - `OpenAICompatibleProvider.decide()` sends
  `"temperature": 0` in the chat-completions payload. That is the *API-level*
  sampling knob (greedy decoding), a different thing from the logit-level `T`
  in this lesson.
- `decisionarena/metrics.py` - `action_change_rate()`: for each question it
  takes `max((aa["probabilities"] or {0: 0}).values(), default=0)` and
  compares it to the threshold. That comparison is where temperature turns
  into a changed action.
- `cases/routing.json` - the thresholds: `{"is_billing": 0.5, "team": 0.6,
  "severity": 0.5}`. The `0.6` for `team` is the number that matters in the
  example above.
- `decisionarena/providers.py` - `MockProvider` sets a `choice` answer's
  confidence to `probs[top] + 0.05`: a hand-made "sharper than the
  distribution" number, which is what temperature changes honestly.

## Your turn

Extend the existing file `examples/02_temperature.py`. Keep everything that is
already there - it works - and add:

- a function `decision(logits: list[float], labels: list[str], temperature:
  float, threshold: float) -> dict` that returns a dict with exactly three
  keys: `"top"` (the label of the highest-probability option), `"p_top"` (that
  option's probability as a float) and `"acts"` (`True` when `p_top` is at or
  above `threshold`, `False` otherwise).
- an extension to `main()` that prints a decision table for the temperatures
  `[0.25, 0.5, 1.0, 2.0, 4.0]` at a threshold of `0.6`, using the existing
  `logits = [2.0, 1.0, 0.5]` and `labels = ["billing", "technical", "other"]`.
  The table has one row per temperature with the columns: `T`, top label,
  `p_top`, entropy, and `acts`. Reuse the file's existing `softmax()` and
  `entropy()` functions.
- a self-check section using `assert` that fails loudly if:
  - the top label is not the same at every one of the five temperatures
  - at `T = 0.25` the decision does **not** act (it must act)
  - at `T = 4.0` the decision still acts (it must not)
  - `p_top` at `T = 0.25` is not larger than `p_top` at `T = 4.0`

Inputs: the logits `[2.0, 1.0, 0.5]`, the labels, the five temperatures and
the threshold `0.6`. Expected output: five rows, the top label `billing` in
every row, `p_top` falling from about `0.98` at `T = 0.25` to about `0.41` at
`T = 4.0`, and the `acts` column flipping from yes to no somewhere in the
middle of the table.

**Hint:** temperature is applied to the logits *before* the softmax, and
"acts" is exactly the comparison this repo makes with the `thresholds` block
in `cases/routing.json` - the same comparison `action_change_rate()` makes in
`decisionarena/metrics.py`.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. What is the one thing temperature changes about a distribution, and what is
   the one thing it can never change?
2. At `T = 1.0` the top option sits at `0.63`; at `T = 0.25` it sits at about
   `0.98`. With a threshold of `0.6`, what changes - the label, the action, or
   both?
3. Why is lowering the temperature not a way to make a model more accurate?

## Artifact

Write `docs/notes/L13-temperature.md` - under 250 words, for a smart friend
who knows what a distribution is. It must contain:

- the temperature formula in one line, in your own words
- one sentence on why the ranking cannot change
- two concrete numbers from your own run of your own code - the `p_top` at
  two different temperatures, with the threshold you used

Then commit it. The artifact is the proof that you can explain why a knob that
cannot change the answer can still change the decision.
