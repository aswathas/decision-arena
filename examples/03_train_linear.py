"""Example 03 - Train a linear model with gradient descent.

WHAT THIS TEACHES
    The whole learning loop in one neuron: forward pass, loss, gradient,
    update, repeat. No framework, no numpy - just the chain rule and a bit
    of arithmetic. It is the same loop inside every neural network, one layer
    deep.

WHAT TO LOOK AT FIRST
    `forward`, then `log_loss`, then `gradients`. Then the training loop and
    the printed loss curve. Finally the CHAIN RULE block at the bottom - it
    is the one paragraph that ties the whole thing together.

QUESTIONS TO ANSWER FOR YOURSELF
    1. Why is the loss `-y*log(p) - (1-y)*log(1-p)` and not squared error?
       (What happens to the gradient when p is very close to 0 or 1?)
    2. If you raise the learning rate 100x, what happens to the loss curve?
       Why does the loss sometimes EXPLODE instead of just oscillating?
    3. The model predicts a probability for a `noul` question. In
       cases/routing.json the threshold is 0.5. If the model instead
       produced a raw score, what would the harness's `score_case` have to do
       differently?

Run:  python examples/03_train_linear.py
"""
from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# The data: two features, one label. y = 1 if x1 + x2 > 1 else 0.
# Hand-made so every number below is checkable by eye.
# ---------------------------------------------------------------------------
DATA = [
    # (features, label)   features = [x1, x2]
    # Symmetric under swapping x1 and x2, so the learned weights come out
    # about equal - which is the visible sign that the model found the
    # "x1 + x2 = 1" boundary rather than some arbitrary one.
    ([0.10, 0.10], 0),
    ([0.20, 0.15], 0),
    ([0.15, 0.20], 0),
    ([0.25, 0.25], 0),
    ([0.85, 0.65], 1),
    ([0.65, 0.85], 1),
    ([0.75, 0.75], 1),
    ([0.90, 0.30], 1),
    ([0.30, 0.90], 1),
]
FEATURES = 2
LEARNING_RATE = 5.0
STEPS = 2000
PRINT_EVERY = 200


def sigmoid(z: float) -> float:
    """The logistic function: squash any real number into (0, 1).

    sigma(z) = 1 / (1 + exp(-z))

    Why not just use z directly? Because the model's output has to be a
    probability. The sigmoid is smooth, monotone, and has the neat property
    that its derivative is sigma(z) * (1 - sigma(z)) - which is exactly what
    makes the backward pass below so short.

    (For large negative z, exp(-z) overflows. This form is fine because
    -z is then large POSITIVE and exp of a large positive number is huge but
    representable; the float division still gives the right answer. The
    truly safe version is the log-sum-exp trick used in `log_loss`.)
    """
    return 1.0 / (1.0 + math.exp(-z))


def forward(x: list[float], weights: list[float], bias: float) -> float:
    """The FORWARD PASS.

    z = w . x + b        (a weighted sum - a score)
    p = sigmoid(z)       (a probability)

    Two lines. Everything else in this file is about making those two lines
    better.
    """
    z = bias + sum(w * xi for w, xi in zip(weights, x))
    return sigmoid(z)


def log_loss(y: int, p: float) -> float:
    """Cross-entropy / log loss for ONE example.

        L = -[ y * log(p) + (1 - y) * log(1 - p) ]

    Read it as: if the truth is y = 1, penalise log(p); if the truth is
    y = 0, penalise log(1 - p). Either way we penalise the probability we
    SHOULD have given to the true class.

    The LOG is what makes this useful. Squared error says "you were 0.9 off";
    log loss says "you were off by a FACTOR of e^0.1" and the penalty grows
    without bound as p -> 0. A model that is confidently wrong gets punished
    enormously - which is what you want from a decision model that is going
    to auto-route a customer ticket.

    The naive implementation log(0) = -inf when p is exactly 0 or 1, which
    happens as soon as the sigmoid saturates. The stable form works on the
    SCORE z instead of the probability p, using the log-sum-exp trick:
        log(p)      = log(1/(1+e^-z)) = -log(1+e^-z) = -softplus(-z)
        log(1 - p)  = -softplus(z)
    where softplus(x) = log(1 + e^x), computed stably as
        softplus(x) = max(x, 0) + log(1 + e^-|x|)
    so the exponentiated term is always e^0 = 1 at most.

    This file keeps the simpler clamped form so the arithmetic stays
    visible; `softplus` is used in the docstring above so you know what the
    production version looks like.
    """
    eps = 1e-12
    p = min(max(p, eps), 1.0 - eps)
    if y == 1:
        return -math.log(p)
    return -math.log(1.0 - p)


def gradients(x: list[float], y: int, p: float) -> tuple[list[float], float]:
    """The BACKWARD PASS - the gradient of the loss w.r.t. the parameters.

    Returns (dL/dw, dL/db).

    The chain rule, applied once:

        L = log loss(p),  p = sigmoid(z),  z = w . x + b

        dL/dw_i = dL/dp * dp/dz * dz/dw_i
                = (p - y) * (p * (1 - p)) * x_i
                = (p - y) * p * (1 - p) * x_i

        dL/db  = (p - y) * p * (1 - p)

    The beautiful part is the middle term: dp/dz = p(1-p) is a function of p
    ALONE, so the whole derivative needs no extra machinery. The sigmoid's
    derivative cancels the sigmoid's "squashing" - this is why logistic
    regression is so cheap to train.

    Sign sanity check (read this, it will save you a bug later):
      * p is too HIGH and y = 1 -> (p - y) > 0 -> gradient pushes w down.
        Correct: the score was too big, shrink it.
      * p is too LOW and y = 1  -> (p - y) < 0 -> gradient pushes w up.
        Correct: the score was too small, grow it.
    """
    d_p = p - y                  # dL/dp for log loss
    d_z = d_p * p * (1.0 - p)    # chain through the sigmoid
    d_w = [d_z * xi for xi in x]  # chain through the dot product
    return d_w, d_z


def mean_log_loss(data: list[tuple], weights: list[float], bias: float) -> float:
    """Average loss over the whole dataset - one number to watch."""
    total = 0.0
    for x, y in data:
        p = forward(x, weights, bias)
        total += log_loss(y, p)
    return total / len(data)


def accuracy(data: list[tuple], weights: list[float], bias: float) -> float:
    """Fraction of examples where the predicted CLASS is right."""
    correct = 0
    for x, y in data:
        p = forward(x, weights, bias)
        if (p >= 0.5) == bool(y):
            correct += 1
    return correct / len(data)


def main() -> int:
    print("Training a one-neuron model with gradient descent\n")
    print(f"data      : {len(DATA)} examples, {FEATURES} features")
    print(f"rule      : y = 1 if x1 + x2 > 1 else 0")
    print(f"hyperparams: learning_rate={LEARNING_RATE}, steps={STEPS}")
    print()

    # Start from a neutral model: all weights 0, bias 0 -> p = 0.5 everywhere.
    weights = [0.0] * FEATURES
    bias = 0.0
    print("initial weights:", weights, "bias:", bias)
    print(f"initial loss    : {mean_log_loss(DATA, weights, bias):.6f}")
    print(f"initial accuracy: {accuracy(DATA, weights, bias):.4f}")
    print()

    print("-" * 62)
    print(f"{'step':>6}  {'loss':>10}  {'w1':>8} {'w2':>8} {'bias':>8}  {'acc':>6}")
    print("-" * 62)

    for step in range(1, STEPS + 1):
        # ---- accumulate the gradient over the WHOLE dataset (full batch)
        grad_w = [0.0] * FEATURES
        grad_b = 0.0
        for x, y in DATA:
            p = forward(x, weights, bias)
            dw_vec, db = gradients(x, y, p)
            for i in range(FEATURES):
                grad_w[i] += dw_vec[i]
            grad_b += db
        n = len(DATA)
        grad_w = [g / n for g in grad_w]
        grad_b /= n

        # ---- the UPDATE: walk DOWN the gradient
        # w <- w - lr * dL/dw
        for i in range(FEATURES):
            weights[i] -= LEARNING_RATE * grad_w[i]
        bias -= LEARNING_RATE * grad_b

        if step % PRINT_EVERY == 0 or step == 1:
            loss = mean_log_loss(DATA, weights, bias)
            acc = accuracy(DATA, weights, bias)
            print(f"{step:>6}  {loss:>10.6f}  {weights[0]:>8.4f} {weights[1]:>8.4f} "
                  f"{bias:>8.4f}  {acc:>6.3f}")

    print("-" * 62)
    print()

    final_loss = mean_log_loss(DATA, weights, bias)
    final_acc = accuracy(DATA, weights, bias)
    print(f"final weights  : w1={weights[0]:.4f}, w2={weights[1]:.4f}, bias={bias:.4f}")
    print(f"final loss     : {final_loss:.6f}")
    print(f"final accuracy : {final_acc:.4f}")
    print()
    print("Sanity: the true boundary is x1 + x2 = 1. The learned boundary is")
    print(f"         {weights[0]:.3f}*x1 + {weights[1]:.3f}*x2 + {bias:.3f} = 0")
    print(f"         -> w1 and w2 are equal ({weights[0]:.3f} vs {weights[1]:.3f}), which")
    print(f"            means the model found 'the sum must clear "
          f"{-bias / (weights[0] + weights[1]):.2f}'. A real dataset")
    print("            would not be so kind, but the mechanics are identical.")
    print()

    print("Per-example predictions:")
    for x, y in DATA:
        p = forward(x, weights, bias)
        print(f"  x=({x[0]:.2f}, {x[1]:.2f})  y={y}  p={p:.4f}  "
              f"{'ok' if (p >= 0.5) == bool(y) else 'WRONG'}")
    print()

    # -----------------------------------------------------------------
    # SELF-CHECKS
    # -----------------------------------------------------------------
    print("SELF-CHECKS")
    assert final_loss < 0.05, f"loss should be tiny, got {final_loss}"
    print(f"  [ok] loss dropped to {final_loss:.6f} (< 0.05)")

    assert final_acc == 1.0, f"expected a perfect fit on this toy data, got {final_acc}"
    print(f"  [ok] accuracy is {final_acc:.2f} on the training set")

    # The gradient must point downhill: stepping ALONG it must reduce the
    # loss, and stepping AGAINST it must raise it. Do this from the INITIAL
    # weights, where the gradient is large - at the converged point the
    # gradient is ~0 and the test would be vacuous.
    w2 = [0.0] * FEATURES
    b2 = 0.0
    before = mean_log_loss(DATA, w2, b2)
    gw, gb = [0.0] * FEATURES, 0.0
    for x, y in DATA:
        p = forward(x, w2, b2)
        dw_vec, db = gradients(x, y, p)
        for i in range(FEATURES):
            gw[i] += dw_vec[i] / len(DATA)
        gb += db / len(DATA)
    for i in range(FEATURES):
        w2[i] += 0.5 * gw[i]       # a step UP the gradient (the wrong way)
    b2 += 0.5 * gb
    after = mean_log_loss(DATA, w2, b2)
    assert after > before, (before, after)
    print(f"  [ok] stepping up the gradient raises the loss ({before:.6f} -> {after:.6f})")

    # ... and stepping DOWN it must lower the loss.
    w3 = [0.0] * FEATURES
    b3 = 0.0
    for i in range(FEATURES):
        w3[i] -= 0.5 * gw[i]
    b3 -= 0.5 * gb
    after_down = mean_log_loss(DATA, w3, b3)
    assert after_down < before, (before, after_down)
    print(f"  [ok] stepping down the gradient lowers the loss ({before:.6f} -> {after_down:.6f})")

    # A model with no features at all cannot beat 50% on this data.
    assert accuracy(DATA, [0.0, 0.0], 0.0) < 1.0
    print("  [ok] the zero model is not already perfect")
    print()

    # -----------------------------------------------------------------
    print("=" * 74)
    print("THE CHAIN RULE IN ACTION")
    print("=" * 74)
    print("""
    One number, traced backwards through three layers.

        L = log loss(p)
        p = sigmoid(z)
        z = w . x + b

    We want dL/dw_i. The chain rule says: multiply the local derivatives
    along the path.

    STEP 1 (output -> probability)
        L = -[y log p + (1-y) log(1-p)]
        dL/dp = -y/p + (1-y)/(1-p)
              = (p - y) / (p * (1 - p))
        This is where the LABEL enters the maths. Without a label there is
        no gradient - which is exactly why the harness's friction and
        injection batteries can be run without gold labels: they measure the
        OUTPUT, not the error.

    STEP 2 (probability -> score) - the sigmoid's derivative
        p = 1/(1+e^-z)
        dp/dz = p * (1 - p)
        Note what this does: the sigmoid's "squashing" is cancelled out
        later, because dL/dp already contains a 1/(p(1-p)) factor. What is
        left is (p - y) * p * (1 - p).

    STEP 3 (score -> weights)
        z = w . x + b
        dz/dw_i = x_i
        dz/db   = 1

    MULTIPLYING THE THREE
        dL/dw_i = [ (p - y) / (p(1-p)) ] * [ p(1-p) ] * [ x_i ]
                = (p - y) * p * (1 - p) * x_i
        dL/db   = (p - y) * p * (1 - p)

    Now look at the magnitude. p(1-p) is at most 0.25 and goes to 0 as p
    approaches 0 or 1. So the gradient VANISHES when the model is confident
    - confidently wrong examples contribute almost nothing to the update.
    That is the vanishing-gradient problem, in its simplest form, and it is
    why deep networks need tricks (residual connections, careful
    initialisation, normalisation) that this one-neuron model does not need.

    PRACTICAL CONSEQUENCE FOR A DECISION MODEL
    A decision model that is trained to be over-confident will not be talked
    out of it by more gradient descent, because the examples it is wrong
    about have already saturated the sigmoid. When you see bad calibration,
    temperature (examples/02_temperature.py) is the cheap fix; retraining is
    the expensive one.
    """)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
