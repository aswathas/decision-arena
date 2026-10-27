---
id: L31
phase: 3
title: "Gradient - the direction of steepest ascent"
minutes: 35
concepts: [gradient, derivative, chain-rule, partial-derivative]
prereqs: [L30, L11]
paths: [beginner, foundations]
exercise_file: exercises/L31_gradient.py
quiz: L31
---

# L31 - Gradient: the direction of steepest ascent

## Why this matters

L30 gave you a loss: one number saying how surprised the model was by the
truth. A number is useless unless you can ask "which way do I change the
model to make this number smaller?". The **gradient** is the answer to that
question. It is the direction in parameter space where the loss grows
fastest - so walking the *opposite* way is how a model learns.

This is the mechanic behind everything the harness later measures. A model
that is badly calibrated was trained with a gradient that pushed its
probabilities too far; a model that is confidently wrong has a vanishing
gradient, so more training barely moves it.

## The naive story

You are standing on a hill in thick fog. You cannot see the slope. But you
can feel the ground: put your foot slightly forward and back and notice which
way the ground rises. The direction that rises fastest is the **gradient** -
the steepest ascent. To go downhill, walk the other way.

For a function of one number, this is easy: the **derivative** is the slope.
For a function of many numbers - a loss that depends on every weight in the
model - you need one slope per weight, and those slopes are **partial
derivatives**: the rate of change with respect to that weight alone, with
every other weight held fixed.

## What breaks

**Break 1 - you cannot get the gradient by treating the model as a black
box.** The obvious method: nudge each weight a tiny amount, recompute the
loss, and see how much it moved. That works! It is called a numerical
gradient. But it needs two forward passes per weight, and with a million
weights that is a million forward passes per training step. Real models use
**backpropagation** - the chain rule - to get every partial derivative in
about the cost of one forward pass.

**Break 2 - the chain rule is not optional.** The loss does not depend
directly on the weights. It depends on the weights through the score `z`,
which goes through the sigmoid to become `p`, which goes into the loss. So
"how much does the loss change if I nudge `w`?" is a product of three local
rates of change. Miss one and your gradient is wrong by a factor, and the
model trains in the wrong direction while looking like it is training.

**Break 3 - the chain rule has a multiplication in it, and that multiplication
is the whole story.** Here is the direct answer to the classic question "why
does a confidently-wrong model learn so slowly?".

For logistic regression, the gradient of the loss with respect to a weight
`w_i` is:

```
dL/dw_i = (p - y) * p * (1 - p) * x_i
```

Read the factors left to right:

- `(p - y)` - the **direction**. If `p` is too high and `y = 1`, this is
  positive, and the update (which subtracts the gradient) shrinks the
  weight. If `p` is too low, it is negative, and the weight grows. The
  direction is always right.
- `p * (1 - p)` - the **size**. This is the derivative of the sigmoid, and
  it is the whole story. It is at most `0.25`, and it *vanishes* as `p`
  approaches 0 or 1. At `p = 0.99` it is `0.0099`; at `p = 0.5` it is `0.25`.
  So a confidently-wrong example contributes almost **nothing** to the
  update - not because the direction is wrong, but because the step size is
  nearly zero.
- `x_i` - the input feature, which says *which* weight gets the push.

So a model that has saturated its sigmoid on the examples it gets wrong
essentially cannot be talked out of it by more gradient descent. The
examples that would correct it have vanishing gradients. This is the
**vanishing gradient** problem in its simplest form.

**And the fix.** The `p * (1 - p)` factor exists because the loss was
measured on `p` while the model was built out of `z`. If you measure the
loss on `z` instead - a loss that is linear in `z` - the factor disappears
by cancellation. That is exactly why real models do not use a plain sigmoid
plus a plain log loss at the output.

## The real thing

**The chain rule, concretely.** We want `dL/dw_i` for the chain

```
L = log loss(p)
p = sigmoid(z)
z = w . x + b
```

Multiply the local derivatives along the path:

```
dL/dw_i = (dL/dp) * (dp/dz) * (dz/dw_i)
        = [ (p - y) / (p(1-p)) ] * [ p(1-p) ] * [ x_i ]
        = (p - y) * p * (1 - p) * x_i
```

Step by step, with the numbers:

- `dL/dp = (p - y) / (p(1-p))` - the loss's own sensitivity to the
  probability. Note the `1/(p(1-p))` in the denominator.
- `dp/dz = p(1-p)` - the sigmoid's sensitivity to its input. This is where
  the factor cancels.
- `dz/dw_i = x_i` and `dz/db = 1` - the score's sensitivity to the weights.

The cancellation is the beautiful part: the sigmoid's "squashing" is
undone by the loss's own blow-up, and what is left is `(p - y) * p(1-p) * x_i`.
The full worked version with the same numbers is in the closing block of
`examples/03_train_linear.py`, under the heading "THE CHAIN RULE IN ACTION".

**Where the label enters.** `dL/dp` contains `y`. Without a label there is
no gradient - which is precisely why this repo's friction and injection
batteries can run without gold labels: they measure the *output*, not the
*error*. `decisionarena/harness.py` calls `metrics.score_case()` only when a
case has a `"gold"` key, and the friction path (`run_format_friction`) never
needs one.

**Partial derivative versus gradient.** The **partial derivative**
`dL/dw_i` is one number: the sensitivity of the loss to one parameter, with
everything else frozen. The **gradient** is the whole collection of those
numbers, one per parameter, written as a vector with the same shape as the
parameter vector. When you say "walk down the gradient", you mean: move each
parameter in the direction that decreases the loss, by an amount proportional
to its partial derivative.

**One important asymmetry to keep straight.** The gradient points *uphill*
(steepest ascent). Gradient descent subtracts it, so you walk downhill. In
`examples/03_train_linear.py` the update is literally
`weights[i] -= LEARNING_RATE * grad_w[i]`.

## In this repo

- `examples/03_train_linear.py` - `gradients(x, y, p)` is the whole backward
  pass in three lines, and its docstring names the chain explicitly:
  `dL/dw_i = dL/dp * dp/dz * dz/dw_i = (p - y) * (p * (1 - p)) * x_i`. It
  also carries a "Sign sanity check" - too high and `y = 1` means the
  gradient pushes the weight down; too low means up.
- `examples/03_train_linear.py` - the closing "THE CHAIN RULE IN ACTION"
  block walks the three steps with the actual formulas, including
  `dL/dp = (p - y) / (p * (1 - p))` and the cancellation that leaves
  `(p - y) * p * (1 - p) * x_i`. It ends with the paragraph that matters
  most for this repo: "So the gradient VANISHES when the model is confident -
  confidently wrong examples contribute almost nothing to the update. That is
  the vanishing-gradient problem, in its simplest form, and it is why deep
  networks need tricks (residual connections, careful initialisation,
  normalisation) that this one-neuron model does not need."
- `examples/03_train_linear.py` - `log_loss(y, p)` is the forward half of
  the chain (L30), and `forward(x, weights, bias)` is the middle step.
  `gradients` consumes their output `p` directly.
- `examples/03_train_linear.py` - the self-checks in `main()` prove the sign
  of the gradient empirically: stepping *up* the gradient must *raise* the
  loss, stepping *down* it must *lower* the loss. That is a gradient check
  you can run, and it is what L31's exercise asks you to build.
- `decisionarena/harness.py` - `run_battery()` calls
  `metrics.score_case()` only `if case.get("gold") and answers and not
  error`. No gold label, no error measurement - the same fact as above, in
  the harness.
- `decisionarena/metrics.py` - `collect_scored()` pairs each probability
  with a 0/1 outcome. The outcome is the `y`; the loss you would train on
  is the cross-entropy over those pairs.

## Your turn

Write a file `exercises/L31_gradient.py` that contains:

- a function `sigmoid(z: float) -> float` that returns `1 / (1 + exp(-z))`
- a function `log_loss(y: int, p: float) -> float` - the one-example
  cross-entropy from L30, with `p` clamped into `[1e-12, 1 - 1e-12]`
- a function `loss_of(x: list[float], y: int, weights: list[float],
  bias: float) -> float` that computes the probability from `weights` and
  `bias` and then the loss
- a function `numeric_partial(f, point: list[float], index: int,
  h: float = 1e-6) -> float` that estimates one partial derivative
  **numerically**: evaluate `f` at the point, then at the point with
  coordinate `index` increased by `h`, and divide the difference by `h`
- a function `numeric_gradient(f, point: list[float]) -> list[float]` that
  returns one numeric partial derivative per coordinate
- a function `analytic_gradient(x: list[float], y: int, weights: list[float],
  bias: float) -> list[float]` that returns the analytic partial derivatives
  of the loss with respect to each weight, using the chain rule you just
  learned
- a `main()` that:
  - uses `x = [0.85, 0.65]`, `y = 1`, `weights = [0.0, 0.0]`,
    `bias = 0.0` (the model is at the start, so `p = 0.5`)
  - prints the analytic gradient and the numeric gradient, side by side,
    with six decimal places
  - asserts that every analytic gradient matches the numeric gradient to
    within `1e-5`
  - repeats the comparison at `weights = [3.0, -1.0]`, `bias = 0.5`, where
    the model is confident, and prints both gradients again
  - prints a line `step_ratio=<number>` showing the ratio between the size of
    the gradient at the confident point and the size at the neutral point,
    with four decimal places

Inputs: the weight vectors above. Expected output: at the neutral point the
two gradients agree to within `1e-5`; at the confident point the gradient
magnitude is much smaller than at the neutral point, and the `step_ratio` is
well below 1.

**Hint:** the analytic gradient is the one printed in the `gradients()`
docstring of `examples/03_train_linear.py` - the chain of three local
derivatives multiplied together. For the numeric part, the partial derivative
with respect to coordinate `i` is the change in `f` caused by moving that one
coordinate, divided by the size of the move. Do not compute more than one
coordinate at a time.

**Do not** hard-code the analytic answer for the two test points. The
assertion comparing it to the numeric gradient is the whole exercise - a
hard-coded value would pass the assert without proving anything.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. What does the gradient of a function tell you, and why does gradient
   descent subtract it rather than add it?
2. Walk through the chain rule for `dL/dw_i` in logistic regression: what
   are the three local derivatives and what does each one mean?
3. Why does a confidently-wrong example contribute almost nothing to the
   update? Name the exact factor and explain its shape.
4. In this repo, why can the injection and friction batteries run without
   gold labels, while the routing battery cannot?

## Artifact

Write `docs/notes/L31-gradient.md` - under 200 words, aimed at a smart friend
who has never heard of a gradient. It must contain:

- one sentence defining the gradient as a direction
- the analytic and numeric gradient values from your own run at the neutral
  point, and the `step_ratio` you measured at the confident point
- one sentence on why a confidently-wrong model learns slowly, naming the
  factor

Then commit it. The artifact is the proof that you understood it, not the
proof that you ran the code.
