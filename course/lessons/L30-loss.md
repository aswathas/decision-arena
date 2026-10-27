---
id: L30
phase: 3
title: "Loss - cross-entropy as surprise"
minutes: 35
concepts: [cross-entropy, log-loss, surprise, negative-log-likelihood]
prereqs: [L12]
paths: [beginner, foundations]
exercise_file: exercises/L30_loss.py
quiz: L30
---

# L30 - Loss: cross-entropy as surprise

## Why this matters

A model produces probabilities. Somebody has to say how *bad* those
probabilities are, and that number is the **loss**. Without a loss there is
no training, no comparison between two models, and no way to say "this model
got worse". The loss function is also the definition of what a model is
supposed to care about - because the loss decides which mistakes are
expensive.

In this repo you will not train a model, but you will read the results of
training, and the harness's own metric - the Brier score in
`decisionarena/metrics.py` - is a cousin of the loss you learn here. Worse,
the reason a decision model's confidence often *looks* like a probability is
a statement about cross-entropy.

## The naive story

The model says "billing, 72%". It was wrong. So how wrong? The obvious
answer: the mistake was `1 - 0.72 = 0.28`. Take the average of those
mistakes over a dataset: that is the loss.

Simple, and it works, and it is exactly what the Brier score does. But it
has one fatal flaw, which we will meet in "What breaks".

## What breaks

**Break 1 - the penalty does not grow fast enough.** With squared error, a
model that says `0.999` and is wrong pays `0.998`. A model that says `0.51`
and is wrong pays `0.49`. The confident model is punished almost twice as
much, which sounds right until you notice the *ratio*: the confident mistake
is twice as big but not a hundred times as big. For a decision model that
auto-routes a customer ticket, "confidently wrong" should be catastrophic -
a hundred times worse than "nearly right" - not twice as bad.

**Break 2 - the same question has different possible answers.** Some
questions have one right answer, some have several. A loss that treats "the
model gave 0.72 to one of three acceptable answers" as a total failure is
wrong about the world. Cross-entropy handles this naturally, because it
sums the loss over *all* the acceptable answers.

**Break 3 - probabilities of exactly zero are impossible to score.** If a
model says `p = 0` for the right answer, any loss that uses `1 - p` says
"the mistake was 1.0", the same as saying `p = 0.5`. But saying `p = 0` is
an infinitely confident mistake, and it should be punished infinitely
harder. Only a loss with a logarithm can express that.

## The real thing

**Cross-entropy** measures the **surprise** of the truth under the model's
own distribution, in **nats** (natural log units).

Start with a single prediction and a single truth:

- The truth is class `y`. The model gave that class probability `p`.
- **Surprise** is `-log(p)`. If the model was right and certain (`p = 1`),
  the surprise is `0`. If the model was certain and wrong (`p = 0.001`),
  the surprise is huge.
- Why the log? Because "surprise" in information theory is measured in nats,
  and `-log(p)` is exactly the number of nats of information you would need
  to hear the truth stated, given that the model had already said `p`. A
  probability of `0.001` costs about 6.9 nats; a probability of `0.9` costs
  about 0.105 nats.

**The one-example form** (this is what `examples/03_train_linear.py` calls
`log_loss`):

```
L = -[ y * log(p) + (1 - y) * log(1 - p) ]
```

For a binary truth `y` in `{0, 1}`. Read it as: penalise the probability you
should have given to the true class. If `y = 1`, penalise `log(p)`; if `y =
0`, penalise `log(1 - p)`. (In `examples/03_train_linear.py` the `y == 1`
branch returns `-math.log(p)` and the other branch returns
`-math.log(1.0 - p)` - exactly this formula, split into two cases.)

**The multi-class form**, which is the general one:

```
L = - sum over classes c of  y_c * log(p_c)
```

where `y_c` is 1 for the true class and 0 for the others. So for a single
true class, this collapses to `-log(p_true)`. This is also called
**log-loss**, and `-log(p_true)` is the **negative log-likelihood** of the
observed answer.

**Concrete numbers you can check by hand.** Suppose the truth is "billing"
and the model says:

| p given to "billing" | loss `-log(p)` | what it means |
|---|---|---|
| 0.90 | 0.105 | the model basically knew - cheap |
| 0.50 | 0.693 | a coin flip - one nat |
| 0.10 | 2.303 | the model was surprised - two and a bit nats |
| 0.001 | 6.908 | the model was certain and wrong - brutal |
| 0.0001 | 9.210 | - |

Two things to notice:

1. **The penalty is unbounded.** As `p` goes to zero, the loss goes to
   infinity. That is Break 1 answered: a confident mistake is punished
   without limit, which is exactly what you want from a model that will
   auto-route a ticket.
2. **The scale is multiplicative.** `p = 0.01` is not "10x worse than
   `p = 0.1`". It is `2.303` nats versus `0.105` nats - about 22x worse.
   The log turns "less likely" into "more surprising", and surprise is
   additive.

**Why it is called cross-entropy.** The **entropy** of the model's own
distribution is its average surprise over all outcomes; the **cross-entropy**
is the average surprise of the *truth* under the model. When they are equal
- the truth and the model agree - the loss is at its minimum, `log(n)` for
`n` classes. Cross-entropy punishes the model for being *surprised by the
truth*, and that is why the gradient pushes the right class's probability up
and everything else's down.

**And the connection to this repo.** The Brier score in
`decisionarena/metrics.py` is squared error, not cross-entropy:

```
_brier(probs, outcomes) = mean( (p - o)^2 )
```

So the harness deliberately measures the *gentler* thing. Cross-entropy is
what you minimise while training; the Brier score is what you report
afterwards, because it stays in the same units as a probability (a number
between 0 and 1) and can be read as "mean squared probability error". ECE,
the third metric, answers a different question entirely: not "how far off are
you" but "when you say 90%, are you right 90% of the time".

## In this repo

- `examples/03_train_linear.py` - `log_loss(y, p)` is the one-example
  cross-entropy, written out with the `eps = 1e-12` clamp so `log(0)` never
  appears. Its docstring says the important thing: "log loss says 'you were
  off by a FACTOR of e^0.1' and the penalty grows without bound as p -> 0.
  A model that is confidently wrong gets punished enormously - which is what
  you want from a decision model that is going to auto-route a customer
  ticket."
- `examples/03_train_linear.py` - `mean_log_loss(data, weights, bias)` is
  the loss over a whole dataset - the single number the training loop
  watches and prints every 200 steps. That printed column *is* the loss
  curve.
- `decisionarena/metrics.py` - `_brier(probs, outcomes)` is the squared-error
  alternative, the same "how wrong were you" question answered in a
  different unit.
- `decisionarena/metrics.py` - `collect_scored()` produces the `(probability,
  outcome)` pairs that `_brier` and `_ece` consume. A probability of the
  gold option and a 0/1 outcome - the same ingredients as cross-entropy,
  without the log.
- `examples/01_softmax.py` - `softmax_stable(logits)` is the function whose
  output is being scored by the loss. Logits in, probabilities out, then the
  loss says how surprised the truth was.

## Your turn

Write a file `exercises/L30_loss.py` that contains:

- a function `log_loss(y: int, p: float) -> float` that returns the
  one-example cross-entropy from "The real thing". Clamp `p` into
  `[1e-12, 1 - 1e-12]` before taking any logarithm, and raise `ValueError`
  if `y` is not 0 or 1
- a function `cross_entropy(probs: list[float], correct_index: int) -> float`
  that returns `-log(probs[correct_index])` for the multi-class case, with
  the same clamp
- a function `mean_log_loss(rows: list[tuple[int, float]]) -> float` that
  averages `log_loss` over a list of `(y, p)` pairs
- a function `surprise_bits(nats: float) -> float` that converts nats to
  bits (divide by `log(2)`)
- a `main()` that:
  - computes the loss for the truth class being given `p = 0.90`, `p = 0.50`,
    `p = 0.10` and `p = 0.001`, and prints each as `p=<p> loss=<loss>` with
    six decimal places
  - prints the loss for a three-option question where the correct option got
    `0.72`
  - prints the mean loss over the rows
    `[(1, 0.9), (1, 0.5), (0, 0.2), (1, 0.001)]`
  - prints the same mean in bits

Inputs: the probabilities listed above. Expected output: the loss for `p =
0.001` is about 6.9 and much larger than the loss for `p = 0.90`, which is
about 0.105.

**Hint:** "surprise in nats" means natural log. Check `math.log(0.001)` by
hand first - that is your `p = 0.001` loss, and it should be about 6.9078.
If your number is 0.001 instead, you forgot the minus sign.

**Do not** use squared error anywhere in this file. If you find yourself
computing `(p - y) ** 2`, you have written the Brier score, not the loss.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. What does `-log(p)` mean when `p` is the probability the model gave the
   correct answer? What are its units?
2. Why does cross-entropy punish a confident mistake more than a hesitant
   mistake? Give two reasons - one about the shape of the curve, one about
   the units.
3. Why does the loss go to infinity as `p` approaches zero? What is wrong
   with the alternative of clamping `p` to zero instead?
4. This repo measures the Brier score, not cross-entropy. Why might you
   prefer the Brier score when *reporting* a model's quality?

## Artifact

Write `docs/notes/L30-loss.md` - under 200 words, aimed at a smart friend who
has never heard of cross-entropy. It must contain:

- one sentence defining cross-entropy in terms of surprise
- the two loss numbers from your own run: the loss at `p = 0.90` and the loss
  at `p = 0.001`
- one sentence on why a confident mistake is punished without limit

Then commit it. The artifact is the proof that you understood it, not the
proof that you ran the code.
