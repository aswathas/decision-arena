---
id: L32
phase: 3
title: "Training one neuron with gradient descent"
minutes: 40
concepts: [gradient-descent, learning-rate, training-loop, loss-curve]
prereqs: [L31]
paths: [beginner, foundations]
exercise_file: examples/03_train_linear.py
quiz: L32
---

# L32 - Training one neuron with gradient descent

## Why this matters

L31 gave you a direction. This lesson turns that direction into a process:
repeat "compute the loss, compute the gradient, take a small step against the
gradient" until the loss stops moving. That loop is **gradient descent**, and
it is the training loop of every neural network ever built - including the
decision models this repo measures. Nothing else changes when you go from one
neuron to a 70-billion-parameter transformer: the loop is identical, the
numbers are just bigger.

The **loss curve** - the plot of loss against step number - is the artifact
this repo cares about most, because it is the first place a broken training
run becomes visible.

## The naive story

Imagine you are blindfolded on a hillside and you want to get to the bottom.
You feel the slope, take a step downhill, feel again, step again. Repeat.

The naive story says: "take a big step each time, so you get down fast". And
if the hill is tiny, that is right. If the step is too big for the hill, you
will not reach the bottom - you will overshoot it, land on the other side,
and oscillate. Step too big and you can even end up somewhere worse than
where you started.

## What breaks

**Break 1 - how big is "a step"?** The size of the step is the **learning
rate**. It is the one knob you set, and it is the one that decides whether
training converges, oscillates, or explodes. Too small: the loss crawls down
for thousands of steps and you give up before it finishes. Too large: the loss
goes up and then up more. The right value is not a constant - it depends on
the scale of your features and the shape of your loss.

**Break 2 - one example at a time is noisy.** If you compute the gradient
from a single example and step, you follow a jagged path. If you average the
gradient over the whole dataset first and then step, the path is smooth and
reliable. The cost is that you look at the whole dataset on every step. In
`examples/03_train_linear.py` this is the **full batch** version: the loop
accumulates `grad_w` and `grad_b` over all nine examples, divides by `n`, and
only then updates.

**Break 3 - the loss curve has more than one shape.** Converging is not the
only outcome. You should be able to recognise, from the curve alone:
- **converging** - the loss falls and then flattens
- **oscillating** - the loss bounces around a floor, the learning rate is
  slightly too big
- **exploding** - the loss grows, often to a number like `nan`, the learning
  rate is far too big

A run that produces `nan` has usually taken a step so large it jumped off
the landscape entirely.

## The real thing

The training loop, in full:

```
w = 0, b = 0                        # start from a neutral model
for step in 1..N:
    p   = forward(x, w, b)          # 1. forward pass: make a prediction
    L   = log_loss(y, p)            # 2. loss: how surprised were we
    dL/dw, dL/db = gradients(...)   # 3. backward pass: which way is downhill
    w -= lr * dL/dw                 # 4. update: take a small step downhill
    b -= lr * dL/db
```

Four steps, repeated. The **forward pass** is the model's prediction. The
**loss** is the number to minimise (L30). The **backward pass** is the
gradient (L31). The **update** is the subtraction.

**The learning rate is the only thing between "converges" and "diverges".**
Look at the update: `w -= lr * dL/dw`. The gradient says *which direction*;
`lr` says *how far*. A good learning rate is one where the step lands you
near the bottom without overshooting. The classic rule of thumb is that if
your loss goes up, your learning rate is too big - halve it and try again.

**Why the learning rate can explode rather than just oscillate.** Multiply the
gradient by a large `lr` and the new weights can land far outside the region
where the loss surface is well behaved. From there the gradient is computed
on a wildly wrong model, which produces another wild step, and the numbers
grow without bound. That is `nan` and `inf` in the printed loss column. It
is not subtle: if your loss column shows `nan`, look at the learning rate
first.

**The loss curve is the diagnostic.** Three lines in the output of
`examples/03_train_linear.py` tell you what happened:

```
  step        loss      w1      w2    bias    acc
    1   0.693147  0.0000  0.0000  0.0000  0.556
  200   0.344000  ...
 2000   0.012345  ...
```

- The **loss column** is the curve. Flat at the end = converged.
- The **accuracy column** tells you whether the converged model is any good.
  A model can have a low loss and still be useless if the classes are
  imbalanced.
- The **weights column** tells you *what* the model learned. In this example
  the data is symmetric under swapping the two features, so a model that
  found the true rule ends with `w1` and `w2` nearly equal. Equal weights
  are the *shape* of the correct answer, not just a loss number.

**What training does and does not tell you.** Training makes the loss small
on the data you trained on. It tells you nothing about whether the model is
calibrated on data it has never seen, and nothing about whether the
probability it reports is honest. That gap - low training loss, bad
calibration - is lesson L33.

## In this repo

- `examples/03_train_linear.py` - the whole lesson in one file, in the
  order you should read it: `forward(x, weights, bias)` (the forward pass),
  `log_loss(y, p)` (the loss), `gradients(x, y, p)` (the backward pass),
  then the training loop inside `main()`.
- `examples/03_train_linear.py` - the module-level constants at the top:
  `DATA` (nine hand-made examples), `FEATURES = 2`, `LEARNING_RATE = 5.0`,
  `STEPS = 2000`, `PRINT_EVERY = 200`. Those are the two knobs - learning
  rate and step count - and `PRINT_EVERY` is what makes the loss curve
  printable.
- `examples/03_train_linear.py` - the training loop accumulates the gradient
  over the whole dataset (`grad_w[i] += dw_vec[i]`, then `grad_w = [g / n for
  g in grad_w]`) before updating. That is full-batch gradient descent, and
  it is why the curve is smooth.
- `examples/03_train_linear.py` - `mean_log_loss(data, weights, bias)` is
  the loss curve's y-value, recomputed every `PRINT_EVERY` steps.
- `examples/03_train_linear.py` - the self-checks in `main()` are the
  gradient sign test: stepping *up* the gradient must *raise* the loss, and
  stepping *down* it must *lower* it. If those two asserts fail, the
  gradient is wrong, not the learning rate.
- `examples/03_train_linear.py` - the closing sanity block prints the
  learned boundary and checks that `w1` and `w2` came out equal, which is
  the visible sign the model found the `x1 + x2 = 1` rule rather than some
  arbitrary boundary.
- `decisionarena/metrics.py` - the harness's own loss-shaped measurement,
  `_brier(probs, outcomes)`, is the squared-error cousin of the loss the
  training loop minimises. Training minimised cross-entropy; the harness
  reports Brier and ECE.
- `examples/02_temperature.py` - the training in `examples/03` produces a
  model that is over-confident on this tiny dataset. Temperature is the
  deployment-time correction for that, and it is why L24 put temperature
  before this lesson.

## Your turn

You are editing an existing repo file, `examples/03_train_linear.py`. Do not
change any existing function. Add **one new function** and call it from
`main()`.

Add:

- `def train_curve(learning_rate: float, steps: int) -> list[float]` - it
  must train a model on the existing `DATA` from scratch (weights and bias
  starting at zero), using the existing `forward`, `log_loss` and
  `gradients` functions, and return a list of loss values: the loss after
  every step, computed with the existing `mean_log_loss`. It must not print
  anything and must not touch the module-level `LEARNING_RATE` or `STEPS`.
- Inside `main()`, after the existing training loop and its output:
  - train the model twice more, once with `learning_rate = 0.5` and
    `steps = 2000`, and once with `learning_rate = 50.0` and
    `steps = 2000`, using your new function
  - print the first loss, the loss at step 200 and the final loss of each
    run, as `lr=<lr> first=<loss> step200=<loss> final=<loss>` with six
    decimal places
  - print a line `explodes=<True or False>` that is `True` when the
    `lr = 50.0` run's final loss is greater than its first loss
  - print a line `lr50_final_nan=<True or False>` that is `True` when the
    `lr = 50.0` run's final loss is not a finite number

Inputs: the existing `DATA`, `FEATURES` and the three learning rates above.
Expected output: the `lr = 0.5` run converges to a loss close to the one the
existing loop reaches, the `lr = 50.0` run's loss ends up worse than it
started (so `explodes=True`), and the `lr = 50.0` run's final loss is
probably `nan` (so `lr50_final_nan=True`).

**Hint:** the update rule is the one in the existing training loop - subtract
the learning rate times the accumulated gradient, and divide the accumulated
gradient by the number of examples first. The reason the big learning rate
explodes is not mysterious: it takes a step so large that the new weights
land somewhere the loss surface does not behave, and the next gradient is
computed on garbage.

**Do not** change `LEARNING_RATE` or `STEPS` at the top of the file. Your
runs must not affect the existing output, because that output is the
explanation other learners read.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. What are the four steps of one iteration of the training loop, and which
   one does the learning rate affect?
2. What does the loss curve look like when the learning rate is far too
   large, and how would you tell that apart from a curve that is merely
   slow?
3. Why does the training loop divide the accumulated gradient by the number
   of examples before stepping?
4. The training loop ends with a very low loss. What does that NOT tell you
   about the model?

## Artifact

Write `docs/notes/L32-training.md` - under 200 words, aimed at a smart friend
who has never heard of gradient descent. It must contain:

- the four steps of the training loop in one line each
- the first and final loss at `lr = 0.5` and at `lr = 50.0`, from your own
  run
- one sentence on what the shape of the curve tells you about the learning
  rate

Then commit it. The artifact is the proof that you understood it, not the
proof that you ran the code.
