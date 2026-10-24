"""Example 04 - Single-head self-attention.

WHAT THIS TEACHES
    How a transformer decides what to look at. Every token produces a query,
    every token produces a key, and the attention weight for one token over
    another is a softmax over query-key dot products. Same softmax as
    examples/01_softmax.py - just applied to scores instead of options.

WHAT TO LOOK AT FIRST
    `attention_scores` (the raw dot products), then `scaled_dot_product_attention`
    (the divide by sqrt(d_k) and the softmax), then the printed 3x3 weight
    matrix. Then the closing block that connects it back to this repo.

QUESTIONS TO ANSWER FOR YOURSELF
    1. Why divide by sqrt(d_k)? What happens to the softmax if you do not?
       (Remember: softmax of a large number is nearly one-hot.)
    2. The weight matrix is 3x3 and each ROW sums to 1. What does a row
       mean, and why is it the row rather than the column that is the
       "distribution"?
    3. A decision model like Jev returns a distribution over OPTIONS. In this
       example, what plays the role of an "option", and what plays the role
       of the "state"?

Run:  python examples/04_attention_numpy.py
"""
from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# numpy is optional. If it is installed we use it for the matrix maths; if not
# we fall back to a pure-Python implementation so this script NEVER crashes on
# a machine without numpy. Both paths print the same numbers.
# ---------------------------------------------------------------------------
try:
    import numpy as np
    HAVE_NUMPY = True
except ImportError:  # pragma: no cover - depends on the machine
    np = None
    HAVE_NUMPY = False


def matmul(a, b):
    """Matrix multiply, written out so you can see what it does.

    `a` is (m x k), `b` is (k x n), result is (m x n).
    result[i][j] = sum over t of a[i][t] * b[t][j]

    This is the "dot product of a row of A with a column of B" - the same
    operation as the `sum(w * xi ...)` line in examples/03_train_linear.py,
    applied to whole rows and columns at once.

    With numpy: a @ b. Without: the explicit triple loop.
    """
    if HAVE_NUMPY:
        # numpy wants arrays, not lists of lists
        return np.asarray(a, dtype=float) @ np.asarray(b, dtype=float)
    m = len(a)
    k = len(a[0])
    n = len(b[0])
    out = [[0.0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            total = 0.0
            for t in range(k):
                total += a[i][t] * b[t][j]
            out[i][j] = total
    return out


def softmax_row(row: list[float]) -> list[float]:
    """Softmax over a single vector, with the max-subtraction stability trick.

    Identical in spirit to examples/01_softmax.py - and note that this is
    the ONLY place softmax appears in a transformer block. Attention is a
    softmax over "how much do I look at each other token", and the output
    distribution of a decision model is a softmax over "which option".
    Same function, different question.
    """
    shifted = [x - max(row) for x in row]
    exponentials = [math.exp(x) for x in shifted]
    total = sum(exponentials)
    return [e / total for e in exponentials]


def attention_scores(q: list[list[float]], k: list[list[float]]) -> list[list[float]]:
    """Raw query-key dot products: S = Q @ K^T.

    S[i][j] = how much token i's query matches token j's key.
    These are NOT probabilities yet - they are raw, unnormalised, and can be
    negative. The next step turns them into a distribution.
    """
    k_transposed = [[k[j][i] for j in range(len(k))] for i in range(len(k[0]))]
    return matmul(q, k_transposed)


def scaled_dot_product_attention(q, k, v):
    """The full attention operation.

    Step 1  S = Q @ K^T          (how much does token i match token j?)
    Step 2  S = S / sqrt(d_k)     (keep the softmax out of the saturated zone)
    Step 3  W = softmax(S, row)   (each row becomes a distribution over tokens)
    Step 4  O = W @ V             (each token's output = weighted mix of values)

    WHY THE 1/sqrt(d_k)?
        d_k is the size of the key vector. A dot product of two random
        d_k-dimensional vectors has a standard deviation of about sqrt(d_k),
        so it grows with dimension. By the time you softmax, large-magnitude
        scores produce a nearly one-hot distribution, whose gradient is
        nearly zero (see the vanishing-gradient note in examples/03). Dividing
        by sqrt(d_k) keeps the scores in a range where the softmax still has
        room to move.

    The output shape is the same as the input: (n_tokens x d_value). Each
    row of the output is a weighted average of the value vectors, where the
    weights are that row of the attention matrix.
    """
    d_k = len(q[0])
    scores = attention_scores(q, k)
    scaled = [[s / math.sqrt(d_k) for s in row] for row in scores]
    weights = [softmax_row(row) for row in scaled]
    return weights, matmul(weights, v)


def fmt_matrix(rows: list[list[float]], width: int = 8) -> str:
    """Print a small matrix in a fixed-width, readable grid."""
    lines = []
    for row in rows:
        lines.append("  " + " ".join(f"{v:>{width}.4f}" for v in row))
    return "\n".join(lines)


def main() -> int:
    print("Single-head self-attention, from scratch\n")
    print(f"numpy available: {HAVE_NUMPY}"
          + (" (using numpy for the matrix multiply)" if HAVE_NUMPY
             else " (falling back to pure Python)"))
    print()

    # -----------------------------------------------------------------
    # A tiny 3-token example. Each token is a 2-dimensional vector.
    # In a real transformer these are embeddings; here they are chosen so
    # the answer is obvious by eye: token 0 and token 2 are similar, so they
    # should attend to each other, and token 1 is different from both.
    # -----------------------------------------------------------------
    tokens = ["the", "cat", "dog"]
    d_model = 2

    # Embeddings (in a real model: the output of the embedding layer).
    x = [
        [1.0, 0.0],   # the
        [0.0, 1.0],   # cat
        [0.9, 0.1],   # dog  (close to "the", far from "cat")
    ]

    # One head of projections. In a real model these are learned matrices:
    #   Q = X @ Wq,  K = X @ Wk,  V = X @ Wv
    # Here we use Wq = Wk = Wv = identity so the arithmetic stays visible.
    q = [row[:] for row in x]
    k = [row[:] for row in x]
    v = [row[:] for row in x]

    print("tokens     :", tokens)
    print(f"d_model    : {d_model}  (each token is a {d_model}-dim vector)")
    print("embeddings :")
    print(fmt_matrix(x))
    print()

    # ---- Step 1: raw scores
    scores = attention_scores(q, k)
    print("STEP 1 - raw query-key dot products  S = Q @ K^T")
    print("          (row i = token i's query; column j = token j's key)")
    print(fmt_matrix(scores))
    print()

    # ---- Step 2: scaling
    scale = math.sqrt(len(q[0]))
    scaled = [[s / scale for s in row] for row in scores]
    print(f"STEP 2 - scaled by 1/sqrt(d_k) = 1/{scale:.4f} = {1 / scale:.4f}")
    print(fmt_matrix(scaled))
    print()

    # ---- Step 3: softmax into a distribution
    weights, output = scaled_dot_product_attention(q, k, v)
    print("STEP 3 - softmax over each ROW  (now every row sums to 1)")
    print(fmt_matrix(weights))
    print("  rows:")
    for i, tok in enumerate(tokens):
        parts = "  ".join(f"{tokens[j]}={weights[i][j]:.4f}" for j in range(len(tokens)))
        print(f"    token {i} ({tok:<4}) looks at: {parts}")
    print()

    # ---- Step 4: the weighted values
    print("STEP 4 - output = W @ V  (each row is a weighted mix of the values)")
    print(fmt_matrix(output))
    print()

    print("Reading the result:")
    print("  * token 0 ('the') and token 2 ('dog') are similar vectors, so their")
    print("    query-key dot product is high and the softmax gives them most of")
    print("    each other's attention.")
    print("  * token 1 ('cat') points in a different direction, so it attends")
    print("    mostly to itself.")
    print()

    # -----------------------------------------------------------------
    # SELF-CHECKS
    # -----------------------------------------------------------------
    print("SELF-CHECKS")
    for row in weights:
        assert abs(sum(row) - 1.0) < 1e-12, row
    print("  [ok] every attention row sums to 1 (a distribution over tokens)")

    assert all(w >= 0 for row in weights for w in row)
    print("  [ok] every attention weight is non-negative")

    # The most-similar pair should get the largest weight.
    assert weights[0][2] > weights[0][1], weights[0]
    assert weights[2][0] > weights[2][1], weights[2]
    print("  [ok] the similar pair (token 0, token 2) attends to each other most")

    # The output is a weighted average of the values, so it must lie inside
    # the convex hull of the value vectors: with these inputs, non-negative
    # and each component <= the max component of the values.
    for row in output:
        for c, val in enumerate(row):
            assert -1e-12 <= val <= max(r[c] for r in v) + 1e-12, (row, c)
    print("  [ok] each output row lies inside the convex hull of the values")
    print()

    # -----------------------------------------------------------------
    print("=" * 74)
    print("CONNECTING BACK")
    print("=" * 74)
    print("""
    1. THE SOFTMAX IS THE SAME OPERATION
       In examples/01_softmax.py the softmax turned a vector of scores over
       OPTIONS into a distribution over options. Here it turns a row of
       scores over TOKENS into a distribution over tokens. Identical
       function, different axis:

           softmax(z_i) = exp(z_i) / sum_j exp(z_j)

       If you understand one, you understand both. That is why this repo
       leans on softmax implicitly everywhere a probability shows up.

    2. A DECISION MODEL'S OUTPUT IS A SOFTMAX OVER CHOICES
       Look at decisionarena/providers.py, `normalise_answers`: a `choice`
       answer comes back as

           {"type": "choice", "choice": "billing",
            "probabilities": {"billing": 0.71, "technical": 0.22, "other": 0.07},
            "confidence": 0.76}

       That `probabilities` dict IS a softmax over the options in the
       question's `criteria` (see cases/routing.json, the "team" question).
       The model computed a score per option and normalised them. The
       attention weights above are a softmax over tokens; the routing
       probability is a softmax over teams. Same operation, different
       vocabulary.

    3. WHERE ATTENTION WOULD FIT IN A DECISION MODEL
       A `noul` question is a binary judgement with a probability. To make
       it good, the model has to read the TICKET and weigh the parts of it
       that matter ("charged twice" matters, "subscription" matters,
       "please refund" matters) against the parts that do not. That is
       attention: a learned weighting over the pieces of the state.

       The harness in this repo does not care HOW the model does that. It
       measures whether the resulting distribution is calibrated
       (metrics._ece) and whether swapping the provider changes the
       decision (metrics.action_change_rate). That separation - mechanism
       versus measurement - is the whole architecture of the project.
    """)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
