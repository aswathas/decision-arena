"""Example 01 - Softmax, from scratch.

WHAT THIS TEACHES
    Softmax turns a vector of raw scores ("logits") into a probability
    distribution: all values positive, all summing to 1, and the largest score
    getting the largest probability. This is the single most reused operation
    in machine learning - it is what turns "which option?" into "how likely is
    each option?".

WHAT TO LOOK AT FIRST
    `softmax_naive` and its three printed steps (exp -> sum -> divide). Then
    `softmax_stable` and the note about why we subtract the max.

QUESTIONS TO ANSWER FOR YOURSELF
    1. What is the gradient of softmax with respect to its input? (Do not look
       it up - reason about "if one score rises, where does the mass go?")
    2. Softmax is invariant to adding a constant to every logit. Why does that
       matter for training a neural network?
    3. The repo's `noul` answers are a single probability. A `choice` answer
       is a whole distribution. Where does that distribution come from in the
       provider, and why would a decision-model API return one and not the
       other?

Run:  python examples/01_softmax.py
"""
from __future__ import annotations

import math


def softmax_naive(logits: list[float]) -> list[float]:
    """The three-step definition, spelled out.

    Step 1: exponentiate every score. exp() is always positive, so this is
            where "raw score" becomes "non-negative weight".
    Step 2: add the weights up. That total is the normalising constant.
    Step 3: divide every weight by the total, so the results sum to 1.

    Nothing here is wrong. It is just not safe for large scores - see
    `softmax_stable`.
    """
    exponentials = [math.exp(x) for x in logits]          # step 1
    total = sum(exponentials)                              # step 2
    return [e / total for e in exponentials]               # step 3


def softmax_stable(logits: list[float]) -> list[float]:
    """The numerically safe version: subtract the max BEFORE exponentiating.

    WHY: math.exp(1000) overflows to Infinity (and math.exp(-1000) underflows
    to 0.0). Once any weight is Infinity, the total is Infinity, and
    Infinity/Infinity is NaN. The whole distribution collapses to NaN.

    The fix is one line: subtract the largest logit from every logit before
    exponentiating. Why is that allowed? Because softmax is INVARIANT to a
    constant shift:

        softmax(z + c) == softmax(z)   for any constant c

    Proof: exp(z_i + c) = exp(z_i) * exp(c), so every numerator gains the same
    factor exp(c) and the denominator gains it too - it cancels. So we are
    free to choose the most convenient c, and c = max(z) guarantees every
    exponentiated value is <= exp(0) = 1 and at least one is exactly 1.

    Net effect: the same probabilities, no overflow.
    """
    shifted = [x - max(logits) for x in logits]
    exponentials = [math.exp(x) for x in shifted]
    total = sum(exponentials)
    return [e / total for e in exponentials]


def show_softmax(logits: list[float], label: str) -> list[float]:
    """Print every intermediate step so the numbers are visible, not magic."""
    print(f"  {label}")
    print(f"    scores (logits) : {logits}")
    exponentials = [math.exp(x) for x in logits]
    print(f"    exp(score)      : {[round(e, 6) for e in exponentials]}")
    total = sum(exponentials)
    print(f"    sum of exps     : {round(total, 6)}")
    probs = [e / total for e in exponentials]
    print(f"    probabilities   : {[round(p, 6) for p in probs]}")
    print(f"    check: sum      : {round(sum(probs), 10)}")
    return probs


def main() -> int:
    print("Softmax: raw scores -> probabilities\n")

    # ---------------------------------------------------------------
    # A realistic example: the repo's `choice` question type asks which team
    # should handle a support ticket. The model returns one score per option.
    # ---------------------------------------------------------------
    logits = [2.0, 1.0, 0.5]
    labels = ["billing", "technical", "other"]

    print("STEP 1 - the naive definition, every intermediate printed")
    probs = show_softmax(logits, "logits = [2.0, 1.0, 0.5]")
    print("    meaning         : billing %.1f%%, technical %.1f%%, other %.1f%%"
          % (probs[0] * 100, probs[1] * 100, probs[2] * 100))
    print()

    print("STEP 2 - the same computation, shifted by the max (numerically stable)")
    shifted = [x - max(logits) for x in logits]
    print(f"    shifted scores  : {shifted}")
    print(f"    exp(shifted)    : {[round(math.exp(x), 6) for x in shifted]}")
    print("    -> every exponent is now <= 1, so nothing can overflow")
    stable = softmax_stable(logits)
    print(f"    probabilities   : {[round(p, 6) for p in stable]}")
    print()

    print("STEP 3 - what overflow actually looks like")
    try:
        big = [1000.0, 1001.0, 1002.0]
        naive_big = softmax_naive(big)
        print(f"    naive on {big} -> {naive_big}")
    except OverflowError as exc:
        print(f"    naive on [1000, 1001, 1002] raised OverflowError: {exc}")
        print("    (exp(1000) is bigger than a float can hold)")
    stable_big = softmax_stable([1000.0, 1001.0, 1002.0])
    print(f"    stable on the same input -> {[round(p, 6) for p in stable_big]}  <- fine")
    print()

    print("STEP 4 - the option labels for our ticket example")
    for label, p in zip(labels, probs):
        bar = "#" * int(round(p * 40))
        print(f"    {label:<10} {p:6.3f}  {bar}")
    print()

    # ---------------------------------------------------------------
    # Self-checks. `assert` is the right tool here: it vanishes under
    # `python -O`, and it documents the contract of the function.
    # ---------------------------------------------------------------
    print("SELF-CHECKS")
    # 1. the output is a probability distribution
    total = sum(softmax_stable(logits))
    assert abs(total - 1.0) < 1e-12, f"probabilities must sum to 1, got {total}"
    print("  [ok] probabilities sum to 1")

    # 2. equal scores -> equal probabilities
    uniform = softmax_stable([1.0, 1.0, 1.0, 1.0])
    assert all(abs(p - 0.25) < 1e-12 for p in uniform), uniform
    print(f"  [ok] uniform input -> uniform output {uniform}")

    # 3. ordering is preserved: a bigger score never gets a smaller probability
    ordered = [0.0, 1.0, 2.0, 3.0]
    ps = softmax_stable(ordered)
    assert all(ps[i] < ps[i + 1] for i in range(len(ps) - 1)), ps
    print(f"  [ok] ordering preserved {[round(p, 4) for p in ps]}")

    # 4. (bonus) naive and stable agree on ordinary inputs
    for p_n, p_s in zip(softmax_naive(logits), stable):
        assert abs(p_n - p_s) < 1e-12
    print("  [ok] naive and stable agree on ordinary inputs")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
