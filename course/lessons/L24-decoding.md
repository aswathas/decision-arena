---
id: L24
phase: 2
title: "From logits to a decision - argmax, sampling and generation"
minutes: 35
concepts: [sampling, generation, decoding, temperature-applied]
prereqs: [L13, L23]
paths: [beginner, foundations]
exercise_file: exercises/L24_decoding.py
quiz: L24
---

# L24 - From logits to a decision: argmax, sampling and generation

## Why this matters

You now know how a model builds its numbers: tokens in, blocks, and at the
very end a vector of **logits** - one raw score per possible next thing. The
last step is to turn those logits into an actual output, and there are two
very different ways to do that depending on what kind of model you are
talking to.

A **chat LLM** generates text, one token at a time, by *sampling* from the
distribution. A **decision model** like the ones this repo measures does not
generate anything: it hands back a distribution over a fixed list of options,
and the harness measures that distribution. Getting these two confused is the
single most common misunderstanding in this field, and this repo is built
around the difference.

## The naive story

The model computes scores for the possible next things. You pick the highest
score. Done. That is what most people mean by "the model decides".

## What breaks

**Break 1 - picking the highest score always gives the same answer.** If you
always take the argmax, the model is deterministic: same ticket, same
answer, forever. For a chat LLM that is a dull but harmless model. For a
harness that measures **determinism** across repeats, it hides the thing you
are trying to measure. And it throws away information - a model that says
`{"billing": 0.72, "technical": 0.18}` has told you something a hard label
cannot: that the second choice is still very much alive.

**Break 2 - always picking the top is not "the answer".** Sampling means
picking from the distribution in proportion to its probabilities: with the
distribution above, "billing" comes up about 72% of the time and "technical"
about 18% of the time, over many tries. The temperature knob (L13) tilts that
distribution: a lower temperature makes the top choice even more likely, a
higher one spreads the mass around. Sampling plus temperature is how you get
either a crisp answer or a genuinely varied one, from the same model.

**Break 3 - the two model types are not variants of each other.** A chat LLM
has an open vocabulary of tens of thousands of tokens and generates a
sequence of them. A decision model has a **closed vocabulary** - the options
you listed in the question - and returns a distribution over exactly those,
once. The decision model's "decoding" is not a loop; it is a single softmax
over your options.

## The story

At the end of a shift the cook has a row of dishes scored on a slate: 2.0, 1.0, 0.5. Those scores are not answers. They are raw numbers, not shares of anything.

The slate goes through an oven that turns scores into shares adding up to one. Nothing is thrown away. The top dish gets the biggest share, but the other two still get some - and that leftover is information you would have lost if the oven simply announced the winner.

Two people serve from the same slate. The first always points at the top dish: same ticket, same answer, always. The second reaches in with a spinner and takes in proportion to the shares, so the top dish comes up about 72% of the time and the second about 18%.

One dial sits on the oven. Turn it and the shares sharpen or spread out. The order never changes, but the sizes move.

A rule is written by the door: a dish is served only if its share clears a line. Spread the shares enough and the top dish no longer clears it. Same slate, same cook, same shift - and nothing goes out.

A chat model is that oven in a loop: it serves one word, writes it down, and runs the oven again.

## The real thing

**Decoding** is the step that turns logits into output. There are two
families.

**Family 1: the decision model (closed vocabulary, one shot).**

```
logits over the options in the question's `criteria`
  -> softmax (L12)           -> probabilities dict
  -> argmax                  -> the chosen option
  -> the caller decides what to DO with the probabilities
```

This is what `decisionarena/providers.py` deals in. `normalise_answers()`
flattens the vendor's reply into `{"kind", "value", "probabilities",
"confidence"}`, and `decisionarena/metrics.py` measures the probabilities
dict. The harness never samples. It never generates. It asks "what probability
did you put on the right option?" and "does the top probability clear the
threshold?" - `action_change_rate()` in `decisionarena/metrics.py` is
literally that question.

**Family 2: the chat LLM (open vocabulary, many steps).**

```
logits over the whole vocabulary
  -> softmax / temperature   -> a distribution over the next token
  -> sample (or take argmax) -> one token
  -> append it, run the model again -> logits for the next token
  -> repeat until a stop condition
```

That loop is **generation**. Each pass through the model produces one token.
A 200-token answer is 200 forward passes. And note: the *same* softmax that
L12 taught you is the whole of the probability machinery at each step -
temperature just divides the logits by `T` before it, exactly as
`examples/02_temperature.py` does.

**Where temperature lands.** In both families, temperature is applied to the
logits *before* the softmax:

```
p_i = exp(z_i / T) / sum_j exp(z_j / T)
```

- `T = 1` - the model's own distribution, no opinion added.
- `T < 1` - sharper. The top option wins more often. In the decision model
  this is the "commit" dial; in a chat LLM it is "stop waffling".
- `T > 1` - flatter. More of the mass spreads to the alternatives.

**The consequence the harness was built to catch.** Temperature never changes
the *ranking* of the options, but it can change whether the top option clears
the threshold. `cases/routing.json` sets `"team": 0.6`. At `T = 0.1` the
billing option sits at `p = 0.9999` and the harness records "acted". At
`T = 5.0` the same option sits at `p = 0.39` - below 0.6 - and the harness
records "did not act": same model, same ranking, different *action*. That is why
`examples/02_temperature.py` prints an "acts? yes / NO" column, and why
`decisionarena/metrics.py` has `action_change_rate()` and not just
`label_agreement()`.

**The one-line difference between the two families.** Chat LLM: softmax over
the whole vocabulary, then sample, then feed the token back and repeat.
Decision model: softmax over your options, then stop. Same softmax. Different
size of room. Different number of steps.

## In this repo

- `decisionarena/providers.py` - `normalise_answers()` is where the two
  families meet the harness. A `choice` answer carries a `probabilities`
  dict and a `confidence`; a `noul` answer carries a single number; a `score`
  answer carries a level index. No `text` field anywhere. The harness's
  output contract has no room for generated prose, on purpose.
- `decisionarena/providers.py` - `MockProvider.decide()` is the only place in
  the repo that manufactures a distribution itself: it builds weights per
  option, normalises them into a `probabilities` dict, and picks `top =
  max(probs, key=lambda k: probs[k])`. That `max` is the argmax - the
  decision model's decoding step, written out.
- `decisionarena/metrics.py` - `collect_scored()` pulls the probability of
  the *gold* option out of the `probabilities` dict. That single number is
  what accuracy, the Brier score and the ECE are all computed from. A
  generated-text model would give you nothing here.
- `decisionarena/metrics.py` - `action_change_rate()` compares two providers
  at the thresholds: does the top probability clear the bar, or not. This is
  the metric that a temperature change would move.
- `examples/02_temperature.py` - the `softmax(logits, temperature)` function
  is the temperature-applied softmax, and its `main()` prints both the
  probability table and the "acts?" column at threshold 0.6.
- `cases/routing.json` - the `thresholds` block (`is_billing: 0.5`, `team:
  0.6`, `severity: 0.5`) is the decision rule that sits between the
  distribution and the action. Between the model and the world.
- `decisionarena/providers.py` - `OpenAICompatibleProvider.decide()` is the
  one place where a chat-style API meets the decision protocol: it sends
  `"temperature": 0` to the endpoint and then *parses JSON out of the
  generated message*. That parsing step is the seam between generation and
  decision, and the file's own comment calls the numbers it produces
  "schema-adapter overhead", not the model's raw quality.

## Your turn

Write a file `exercises/L24_decoding.py` that contains:

- a function `argmax_choice(probs: dict[str, float]) -> str` that returns the
  key with the largest probability
- a function `sample(probs: dict[str, float], rng: random.Random) -> str` that
  picks a key in proportion to its probability - take `rng.random()` once
  and walk the keys accumulating probability until you cross the draw
- a function `apply_temperature(logits: list[float], temperature: float) ->
  list[float]` that divides every logit by the temperature, raises
  `ValueError` if the temperature is not greater than zero
- a function `distribution_after_temperature(logits: list[float],
  temperature: float) -> list[float]` that applies the temperature and then
  a stable softmax, and returns the probabilities
- a `main()` that:
  - uses the logits `[2.0, 1.0, 0.5]` and the labels
    `["billing", "technical", "other"]` from `examples/02_temperature.py`
  - prints the argmax label
  - prints the distribution at `T = 0.1`, `T = 1.0` and `T = 5.0`, with four
    decimal places
  - prints, for each of those three temperatures, the label of the top option
    and whether its probability clears the threshold `0.6`, as
    `T=<t> top=<label> p=<prob> acts=<yes|NO>`
  - draws 1000 samples at `T = 1.0` using a `random.Random` seeded with a
    fixed seed, and prints how many times each label came up

Inputs: the logits, labels and threshold above. Expected output: the same
top label at every temperature, but `acts=yes` at `T = 0.1` and `acts=NO` at
`T = 5.0`, and a sample count that shows "billing" appearing far more often
than the other two.

**Hint:** the temperature is applied to the logits, not to the
probabilities - divide first, then softmax. And for the sampler, the
cumulative sum is the trick: draw one number in `[0, 1)`, then find the first
label whose running total of probabilities exceeds it.

**Do not** use `random.choice` or `random.choices` with weights for the
sampler - write the cumulative walk yourself, so you can see exactly why a
0.72 probability comes up about 72% of the time.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. What is the difference between the vocabulary a chat LLM decodes over and
   the vocabulary a decision model decodes over?
2. Why does the harness measure the `probabilities` dict rather than the
   chosen option?
3. Temperature is applied to the logits before the softmax. What happens to
   the *ranking* of the options when temperature changes, and what happens
   to the *action*?
4. Name the threshold in `cases/routing.json` for the `team` question, and
   say what number has to clear it.

## Artifact

Write `docs/notes/L24-decoding.md` - under 200 words, aimed at a smart friend
who has never heard of decoding. It must contain:

- one sentence on the difference between a decision model and a chat LLM at
  the decoding step
- one sentence on what temperature does to the distribution and what it does
  not do
- one concrete number from your own run: the top probability at `T = 0.1` and
  at `T = 5.0`, and which of those clears the 0.6 threshold

Then commit it. The artifact is the proof that you understood it, not the
proof that you ran the code.
