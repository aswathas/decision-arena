"""Example 02 - Temperature.

WHAT THIS TEACHES
    Temperature is a single scalar that rescales logits BEFORE the softmax.
    T < 1 sharpens the distribution (the model commits), T > 1 flattens it
    (the model hedges), T = 1 leaves it alone. Nothing else about the model
    changes - only how the probability mass is spread.

WHAT TO LOOK AT FIRST
    The printed table of (T, probabilities, entropy). Watch the top
    probability rise and the entropy fall as T drops. Then read the "WHY THIS
    MATTERS" block - that is the part that connects to the harness.

QUESTIONS TO ANSWER FOR YOURSELF
    1. As T -> 0, what does the distribution converge to? And as T -> infinity?
    2. If temperature does not change the RANKING of options, can it still
       change which action you take? (Hint: look at the repo's thresholds in
       cases/routing.json - a flat distribution can sit above 0.6 or below.)
    3. The repo's OpenAI-compatible adapter sends `"temperature": 0`. What is
       the difference between that API-level 0 and this logit-level T?

Run:  python examples/02_temperature.py
"""
from __future__ import annotations

import math


def softmax(logits: list[float], temperature: float = 1.0) -> list[float]:
    """Softmax with a temperature, using the stable max-subtraction trick.

    The ONLY thing temperature does is divide every logit by T before the
    softmax:

        p_i = exp(z_i / T) / sum_j exp(z_j / T)

    Dividing by a number > 1 makes all the scores smaller and closer together
    -> flatter distribution. Dividing by a number < 1 makes them bigger and
    further apart -> sharper distribution. The max-subtraction still works
    because it is applied AFTER the division.
    """
    if temperature <= 0:
        raise ValueError(f"temperature must be > 0, got {temperature}")
    scaled = [z / temperature for z in logits]
    shifted = [z - max(scaled) for z in scaled]
    exponentials = [math.exp(z) for z in shifted]
    total = sum(exponentials)
    return [e / total for e in exponentials]


def entropy(probs: list[float]) -> float:
    """Shannon entropy of a discrete distribution, in nats (natural log).

    H = -sum(p_i * log(p_i))

    Reading it: the UNIFORM distribution over n options has the maximum
    entropy log(n). A distribution that puts all its mass on one option has
    entropy 0. So entropy measures "how undecided is this model?" - and
    temperature directly controls it.

    The `if p > 0` guard matters: log(0) is -inf, and 0 * -inf is NaN, which
    would poison the whole sum.
    """
    total = 0.0
    for p in probs:
        if p > 0:
            total -= p * math.log(p)
    return total


def main() -> int:
    print("Temperature: how one number reshapes a distribution\n")

    # A `choice` question with three options. Same logits, same model - only
    # the temperature changes.
    labels = ["billing", "technical", "other"]
    logits = [2.0, 1.0, 0.5]
    temperatures = [0.1, 0.5, 1.0, 2.0, 5.0]

    print("logits:", logits, " (labels:", labels, ")\n")

    header = f"{'T':>5}  {'probabilities':<34} {'entropy':>8}  {'max p':>6}"
    print(header)
    print("-" * len(header))

    rows = []
    for t in temperatures:
        probs = softmax(logits, t)
        h = entropy(probs)
        rows.append((t, probs, h))
        pretty = " ".join(f"{p:.4f}" for p in probs)
        print(f"{t:>5}  {pretty:<34} {h:>8.4f}  {max(probs):>6.4f}")

    print()
    print("Reading the table:")
    print("  * T = 1.0 is the model's own distribution - no opinion added.")
    print("  * T = 0.1 is nearly a one-hot answer: the model stops hedging.")
    print("  * T = 5.0 is nearly uniform: the model refuses to commit.")
    print(f"  * entropy falls from {rows[0][2]:.4f} to {rows[-1][2]:.4f} as T rises;")
    print(f"    maximum possible entropy for 3 options is log(3) = {math.log(3):.4f}")
    print()

    # -----------------------------------------------------------------
    # WHY TEMPERATURE MATTERS FOR A DECISION-MODEL API
    # -----------------------------------------------------------------
    print("=" * 74)
    print("WHY THIS MATTERS FOR A DECISION-MODEL API")
    print("=" * 74)
    print("""
    A decision model does not answer a question - it answers with a
    DISTRIBUTION, and the caller decides what to do with it. In this repo the
    caller is the THRESHOLD:

        cases/routing.json -> "team": {"thresholds": {"team": 0.6}}

    So the same model, at T = 0.1, gives billing p = 1.0000 (to four
    places) and acts. At T = 5.0, billing p = 0.3907 and the harness records
    "did not act", even though billing is STILL the top option. The ranking
    never changed. The ACTION changed.

    That is the whole point of the harness's action_change_rate() metric: it
    measures whether swapping a provider changes what you DO, not whether it
    changes what it SAYS. Temperature is a lever that can move an action
    without moving a ranking - so a benchmark that only compared labels would
    miss it entirely.

    Second reason: temperature is a knob you can turn AFTER seeing the
    calibration curve. If a model is over-confident on your workload (its
    probabilities are too extreme), raising T flattens the distribution and
    pulls it back toward calibrated. That is a deployment-time dial, not a
    retraining project - which is exactly why a decision-model API exposing
    probabilities instead of a hard label is worth paying for.
    """)

    # Show the threshold effect concretely.
    threshold = 0.6
    print(f"Decision threshold on the top option: {threshold}")
    print(f"{'T':>5}  {'top option':<12} {'p(top)':>7}  {'acts?':>6}")
    for t, probs, _ in rows:
        top = max(range(len(probs)), key=lambda i: probs[i])
        acts = probs[top] >= threshold
        print(f"{t:>5}  {labels[top]:<12} {probs[top]:>7.4f}  {'yes' if acts else 'NO':>6}")
    print()

    # -----------------------------------------------------------------
    # Self-checks
    # -----------------------------------------------------------------
    print("SELF-CHECKS")
    p1 = softmax(logits, 1.0)
    assert abs(sum(p1) - 1.0) < 1e-12
    print("  [ok] probabilities sum to 1")

    h_uniform = entropy([1 / 3, 1 / 3, 1 / 3])
    assert abs(h_uniform - math.log(3)) < 1e-12
    print(f"  [ok] entropy of a uniform distribution is log(3) = {h_uniform:.4f}")

    assert entropy(softmax(logits, 0.1)) < entropy(softmax(logits, 1.0)) < entropy(softmax(logits, 5.0))
    print("  [ok] entropy increases with temperature")

    # Temperature never changes the RANKING of the options.
    for t in temperatures:
        probs = softmax(logits, t)
        assert probs[0] > probs[1] > probs[2], (t, probs)
    print("  [ok] ranking is preserved at every temperature")

    try:
        softmax(logits, 0.0)
        raise AssertionError("temperature 0 should be rejected")
    except ValueError:
        print("  [ok] temperature 0 is rejected (it would divide by zero)")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
