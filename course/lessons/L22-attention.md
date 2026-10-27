---
id: L22
phase: 2
title: "Attention - which words look at which"
minutes: 40
concepts: [attention, scaled-dot-product, context, queries-keys-values]
prereqs: [L21, L12]
paths: [beginner, foundations]
exercise_file: examples/04_attention_numpy.py
quiz: L22
---

# L22 - Attention: which words look at which

## Why this matters

L21 gave you embeddings: a point in space for every word. But a point on its
own does not know what the sentence means. The word "bank" means a river edge
or money depending on the other words around it. Something has to decide
which other words matter for this word, right now, in this sentence. That
something is **attention**. It is the part of the model that lets one word
look at another and borrow meaning from it.

In this repo, attention is the mechanism that a decision model uses when it
reads a ticket and weighs "charged twice" against "subscription" against
"please refund". The harness never sees attention - it only sees the
probabilities that come out the far end. But if you want to know *why* a
model routed a ticket to billing, attention is where the answer lives.

## The naive story

Picture a classroom where every student can raise their hand to point at
another student. Each student also decides, secretly, how much attention to
give each other student - a fraction, like "I pay 60% attention to that one,
30% to that one, 10% to the one over there". The fractions for one student add
up to 100%. Then each student writes down an answer that is a weighted mix of
what the students they are pointing at have to say.

That is attention: every position in the sequence computes a set of weights
over all positions, and mixes their value vectors accordingly.

## What breaks

**Break 1 - the weights are not written by hand.** Who looks at whom is
decided by the model. Each token produces three vectors: a **query** ("what
am I looking for?"), a **key** ("what do I have to offer?"), and a **value**
("what do I actually contribute?"). The score of looking from token *i* to
token *j* is the dot product of *i*'s query with *j*'s key - and that dot
product is exactly the similarity from L21.

**Break 2 - a raw dot product is not a weight.** The scores come out as raw
numbers that can be negative and can be large. A weight must be a
non-negative fraction. That is where softmax comes in - and this is exactly
the softmax you already wrote in L12 and `examples/01_softmax.py`, applied
along a different axis: over *tokens* instead of over *options*.

**Break 3 - the dot products get too big, and the softmax dies.** Here is the
subtle one, and it is why attention has a scaling factor. A dot product of
two random vectors of dimension `d_k` grows with `d_k` - roughly like
`sqrt(d_k)` in size. By the time you softmax it, the scores are so spread
out that one of them wins overwhelmingly and the rest are rounded to zero. A
softmax that has nearly collapsed to one-hot has a **vanishing gradient**: the
model can no longer tell how it should adjust, because nothing is sensitive
to a change in the scores. So the standard fix is to divide every score by
`sqrt(d_k)` before the softmax, which pulls the scores back into the range
where the softmax still has room to move.

## The real thing

**Scaled dot-product attention**, one head, four steps:

```
S = Q @ K^T             # raw scores: how much does token i match token j?
S = S / sqrt(d_k)       # scale: keep the softmax out of the saturated zone
W = softmax(S, row)     # weights: each ROW is now a distribution over tokens
O = W @ V               # output: each token's new vector is a weighted mix of values
```

Reading each line carefully:

- `Q @ K^T` produces an `n x n` matrix. Entry `(i, j)` is token *i*'s query
  dotted with token *j*'s key. It is a raw score: not a probability, possibly
  negative, and not comparable across rows yet.
- `S / sqrt(d_k)` divides every score by the square root of the key
  dimension. `d_k` is the length of one key vector. If the key vectors are
  64 numbers long, divide by 8.
- `softmax(S, row)` is applied **row-wise**. Each row is one token's scores
  over all the other tokens; softmax turns that row into a distribution that
  sums to 1. So the row is the distribution, and the columns have no
  meaning on their own.
- `W @ V` mixes the value vectors using those weights. Each output row is a
  convex combination of the value rows - a weighted average.

**Where "context" comes from.** After step 4, token *i*'s vector is no longer
just its own embedding. It is its embedding *plus what it borrowed from the
tokens it attended to*. That borrowed information is **context**: the word
"bank" has been rewritten to mean "money bank", because that is what the
neighbouring words pointed at. The output of the attention layer is a
contextualised embedding.

**Why the scaling is not optional.** Suppose `d_k = 64`, so you divide by 8.
Without the division, a score of 64 becomes 8 after scaling - still large, but
notice what the division does to the *spread* between the top score and the
runner-up: dividing by a constant scales the spread by the same constant. The
softmax of a vector whose gaps are 8x wider is dramatically closer to one-hot.
That matters because a one-hot softmax has a vanishing gradient: `softmax` is
flat at its extremes, so the model learns almost nothing from that step. The
`scaling factor keeps the logits in a range where softmax still has slope.`

**One softmax, two uses.** This is the sentence to carry out of the lesson:

```
examples/01_softmax.py  - softmax over OPTIONS  -> {"billing": 0.71, ...}
examples/04_attention_numpy.py - softmax over TOKENS -> attention weights
```

Same function. Different axis. A decision model's routing probability is a
softmax over the `criteria` options in `cases/routing.json`; an attention
weight is a softmax over the tokens of the ticket.

## In this repo

- `examples/04_attention_numpy.py` - this file *is* the lesson. Read in this
  order:
  - `attention_scores(q, k)` - the raw `Q @ K^T`. Its docstring says it
    plainly: "These are NOT probabilities yet - they are raw, unnormalised,
    and can be negative."
  - `scaled_dot_product_attention(q, k, v)` - the whole four-step operation,
    including the `d_k = len(q[0])` and the division by `math.sqrt(d_k)`.
    Its docstring's "WHY THE 1/sqrt(d_k)?" paragraph is the exact reason
    spelled out.
  - `softmax_row(row)` - the L12 softmax again, max-subtraction included.
    The docstring says it: "this is the ONLY place softmax appears in a
    transformer block."
  - `matmul(a, b)` - the triple loop behind the matrix multiply, with a
    comment pointing back at the `sum(w * xi ...)` line in
    `examples/03_train_linear.py`.
- `examples/04_attention_numpy.py` - `main()` prints the four steps in order
  with every intermediate matrix, plus the "Reading the result" block. It
  also asserts `abs(sum(row) - 1.0) < 1e-12` for every row - the
  distribution check.
- `examples/04_attention_numpy.py` - the closing "CONNECTING BACK" block ties
  attention to `decisionarena/providers.py`: a `choice` answer's
  `probabilities` dict is a softmax over the options, and the attention
  weights are a softmax over tokens.
- `cases/routing.json` - the `team` question's four `criteria` keys are the
  vocabulary a routing softmax is applied over. The `state` string is the
  text that would be tokenized and embedded before any attention ran.
- `examples/03_train_linear.py` - the "vanishing gradient" note in the
  chain-rule block: "the gradient VANISHES when the model is confident -
  confidently wrong examples contribute almost nothing to the update." Same
  disease, one layer apart.

## Your turn

You are editing an existing repo file, `examples/04_attention_numpy.py`.
Add **one new function** to that file and call it from `main()`. Do not change
any existing function.

Add:

- `def scaled_dot_product_attention_unscaled(q, k, v)` - the same four-step
  attention operation as the existing `scaled_dot_product_attention`, but
  **without** the division by `sqrt(d_k)` in step 2. It must return the same
  pair the scaled version returns: `(weights, output)`, where `weights` is
  the list of weight rows and `output` is the mixed values.
- Inside `main()`, after the existing "STEP 3" block, print:
  - the unscaled raw score matrix (from step 1 of the unscaled run)
  - the unscaled weight matrix
  - the largest weight in each row of the unscaled matrix, and the largest
    weight in each row of the scaled matrix, side by side
  - a line reading `scaling_matters=<True or False>` that is `True` when the
    unscaled rows are more peaked (largest weight strictly greater) than the
    scaled rows
- Add one `assert` that the unscaled weights still sum to 1 per row - the
  scaling changes *how peaked* the distribution is, not whether it is a
  distribution.

Inputs: the existing `q`, `k`, `v` already in `main()` (the three tokens
"the", "cat", "dog" with 2-dimensional vectors).

Expected output: two weight matrices that differ, with the unscaled one
visibly more peaked (weights closer to 0 and 1) than the scaled one, and
`scaling_matters=True`.

**Hint:** the two functions differ by exactly one step, and the docstring of
`scaled_dot_product_attention` labels the steps "Step 1 ... Step 2 ... Step 3
... Step 4" for you. Read the "WHY THE 1/sqrt(d_k)?" paragraph in that same
docstring before you write the line.

**Do not** delete or rewrite `scaled_dot_product_attention`. The point of
the exercise is to have both versions in one file so you can see the
difference in the printed numbers.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. What are the query, the key and the value of a token each for? Which one
   decides *who looks at whom*, and which one decides *what gets carried*?
2. Why is the softmax applied row-wise, so that each ROW sums to 1? What
   would a column mean?
3. Explain in your own words why `1/sqrt(d_k)` is needed. What goes wrong in
   the softmax if you leave it out?
4. The softmax in `examples/01_softmax.py` and the softmax in
   `examples/04_attention_numpy.py` are the same function. What is different
   between them - the function, or the thing being softmaxed?

## Artifact

Write `docs/notes/L22-attention.md` - under 200 words, aimed at a smart friend
who has never heard of attention. It must contain:

- one sentence describing what attention does, in terms of what a token
  "looks at"
- the four steps of scaled dot-product attention in one line each
- one concrete number from your own run: the largest weight in the unscaled
  row for one token, and the largest weight in the scaled row for the same
  token

Then commit it. The artifact is the proof that you understood it, not the
proof that you ran the code.
