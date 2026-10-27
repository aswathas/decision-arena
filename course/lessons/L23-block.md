---
id: L23
phase: 2
title: "The transformer block - attention, MLP, residual and layer norm"
minutes: 40
concepts: [transformer-block, residual-connection, layer-norm, mlp]
prereqs: [L22]
paths: [beginner, foundations]
exercise_file: exercises/L23_block.py
quiz: L23
---

# L23 - The transformer block: attention, MLP, residual and layer norm

## Why this matters

L22 gave you attention - the part that lets one token look at another. On its
own, attention is not a model. A transformer is a **stack of blocks**, and each
block has exactly four parts. Every large language model you will ever call -
Jev, Clef, the open-weight zoo - is built from this same block, repeated
dozens or hundreds of times. Understanding the block is what turns "a model
gave me a probability" into "a model gave me this probability *because of
these four operations*".

And here is the reason this repo cares: the block's four parts are each a
possible source of bad calibration. A residual connection that is missing
makes a deep model train badly. A layer norm that is off makes the activations
drift. None of that shows up in the harness's numbers directly - but it is
why a vendor's probability of 0.95 deserves scepticism.

## The naive story

Picture an office worker with two tools on the desk and a rulebook.

1. The worker **reads around** the desk: they look at the papers relevant to
   the one in front of them and take notes. That is attention.
2. The worker **thinks it through**: they go into a small side room with a
   blackboard and work out what it means. That is the MLP.
3. The worker **keeps the original**: whatever they conclude, they write it on
   a sticky note and stick it on top of the original paper, so the original
   information is never lost. That is the residual connection.
4. The worker **tidies up**: they adjust the numbers so nothing is wildly out
   of scale, so the next person can read them. That is layer norm.

Do all four, in that order, then hand the paper to the next worker. A
transformer is a stack of these workers.

## What breaks

**Break 1 - attention alone cannot do new computation.** The attention
output for a token is a *weighted average of values that already exist*. It
can move information around, but it cannot invent a feature that was not
already there. The MLP is the part that does actual thinking: it applies the
same small nonlinear function to every position independently, which is where
"this word means a refund" gets computed.

**Break 2 - deep stacks lose information.** If you stack 100 blocks and each
one rewrites its input completely, the signal from the first block has to
survive 100 rewrites. It does not, reliably. This is the **vanishing
gradient** problem in its deep-network form, and `examples/03_train_linear.py`
names it in its closing block: "why deep networks need tricks (residual
connections, careful initialisation, normalisation) that this one-neuron model
does not need."

**Break 3 - the numbers drift.** Each block multiplies and adds things. After
a hundred blocks the activations can be enormous or tiny, and the next block's
softmax sees scores that are wildly spread out - which is exactly the
saturated-softmax problem from L22, and the exact reason the `1/sqrt(d_k)`
scaling existed in the first place. Layer norm is the correction.

## The story

Picture an office where a document is passed down a row of desks. Every desk
does the same four things, in the same order, to the paper in front of it.

First the clerk tidies the sheet: the numbers on it get rescaled so none of
them is wildly out of proportion. The pencil marks that carry the meaning stay
where they were; only the size is tamed.

Second the clerk reads around the desk - the papers that matter for this one -
and takes notes.

Third the clerk writes their conclusion on a sticky note and lays it on top of
the original sheet. The original is never thrown away. That sticky note is the
residual connection, and it is also why a note from desk number one can still
reach desk number one after a hundred desks: the signal has a straight path
back.

Fourth the clerk goes into a side room with a blackboard and works the problem
out properly. Reading around the desk can only mix what is already on the desk;
the side room is where something new gets computed. That is the MLP.

Then the sticky note again, and the sheet goes to the next desk. A hundred
desks in a row, each one handing on a sheet of exactly the same shape.

## The real thing

One transformer block, in the order the operations actually happen:

```
x  ->  layer_norm(x)   ->  attention   ->  + x   (residual)
   ->  layer_norm(x)   ->  MLP         ->  + x   (residual)
```

**1. Layer norm** (**layer-norm**). Take the vector for one position and
rescale it so it has a controlled size: subtract the mean of its numbers,
divide by their standard deviation, then multiply by a learned scale and add a
learned shift. The vector's *direction* - the information - is roughly kept;
its *magnitude* is tamed. Note it operates **per position, per feature
dimension**, not across the batch. And note the modern ordering: the norm
comes *before* the sub-layer, not after. ("Pre-norm" is the usual choice
today; "post-norm" was the original.)

**2. Attention** (**attention**). The L22 operation, unchanged: query-key
dot products, scaled by `1/sqrt(d_k)`, softmaxed row-wise, mixed with the
values. Its output has the same shape as its input: `n_tokens x d_model`.

**3. The residual connection** (**residual-connection**). Add the block's
input back to its output: `out = attention_result + x`. This is the sticky
note. It gives the network a choice: it can *change* the representation (use
the attention result) or *keep* it (the residual path passes it through
unchanged). Mathematically it also means the gradient has a straight,
unblocked highway back to earlier layers - which is why deep transformers
train at all.

**4. The MLP** (**mlp**). Two linear layers with a nonlinearity in between,
applied to each position separately. The classic shape: expand from
`d_model` to about `4 * d_model`, apply a nonlinearity, then project back
down to `d_model`. The MLP is where the "thinking" happens - it is the only
part of the block that can compute a new feature from the attention-weighted
mixture.

**The shape bookkeeping**, which is the part people get lost on. With `n`
tokens and model width `d_model`:

| quantity | shape |
|---|---|
| input `x` | `n x d_model` |
| attention output | `n x d_model` |
| MLP hidden layer | `n x (4 * d_model)` |
| MLP output | `n x d_model` |
| block output | `n x d_model` |

The rule to remember: **everything inside a block preserves the shape
`n x d_model`**. The block expands temporarily and squeezes back. That is
why blocks can be stacked: block 30 expects exactly what block 29 produced.

**Why this is worth the trouble for a decision model.** A ticket-answering
model that routes "charged twice" to billing is, mechanically, doing: embed
the ticket, run 24 blocks of "look around, think, keep, tidy", then read the
final vector and score the four options from `cases/routing.json`. The
harness measures only the last step. The block is the part you trust or
distrust underneath.

## In this repo

- `examples/04_attention_numpy.py` - part 2 of the block, in full and
  runnable. `scaled_dot_product_attention(q, k, v)` returns `(weights,
  output)` where the output has the same shape as the input (`n_tokens x
  d_value`); the docstring says so: "The output shape is the same as the
  input". The `main()` self-checks also assert that each output row lies
  inside the convex hull of the value vectors - the weighted-average
  property.
- `examples/03_train_linear.py` - the closing "THE CHAIN RULE IN ACTION"
  block names the two tricks this lesson teaches, in the context of deep
  networks: "why deep networks need tricks (residual connections, careful
  initialisation, normalisation) that this one-neuron model does not need."
  Read that paragraph - it is the bridge from one-neuron maths to a
  transformer.
- `examples/03_train_linear.py` - `forward(x, weights, bias)` is the smallest
  possible version of "a layer that changes the representation":
  `z = w . x + b` then a nonlinearity. A transformer block is `forward`
  applied many times, with attention thrown in and a residual path around it.
- `examples/02_temperature.py` - the layer norm in a decision model is what
  keeps the final option scores in a range where temperature still means
  something. A model whose activations have drifted produces logits so
  spread out that `softmax` is already one-hot at any temperature.
- `cases/routing.json` - the `team` question's four `criteria` are the
  vocabulary the final scoring step works over. A transformer block never
  sees them; it produces the vector they are scored from.
- `decisionarena/providers.py` - `normalise_answers()` flattens whatever the
  vendor returns into `{"kind", "value", "probabilities", "confidence"}`. The
  harness is deliberately blind to the block. That separation is the
  architecture of this project.

## Your turn

Write a file `exercises/L23_block.py` that contains:

- a function `layer_norm(x: list[float], eps: float = 1e-6) -> list[float]`
  that standardises one vector: subtract its mean, divide by its standard
  deviation plus `eps`, and return the list. (Use the population standard
  deviation - divide by the number of elements, not `n - 1`.)
- a function `residual_add(a: list[float], b: list[float]) -> list[float]`
  that returns the elementwise sum of two equal-length vectors
- a function `mlp(x: list[float], w1: list[float], w2: list[float]) ->
  list[float]` that applies a two-layer network with a ReLU (replace every
  negative number with zero) between the layers. `w1` maps the input to a
  hidden layer, `w2` maps the hidden layer back to the input's length.
- a function `block(x: list[float], attention_out: list[float], w1: list[float],
  w2: list[float]) -> list[float]` that runs the whole block in this order:
  attention result -> residual add with `x` -> MLP -> residual add with the
  result of the first residual add
- a `main()` that:
  - takes `x = [1.0, 2.0, 3.0, 4.0]`
  - takes an `attention_out` that is a different vector of the same length
  - prints the layer-normalised `x`
  - prints the block output
  - prints the mean and the standard deviation of the block output, with six
    decimal places

Inputs: the vectors above. Expected output: the layer-normalised vector has
mean about 0 and standard deviation about 1, and the printed mean and
standard deviation of the block output are two numbers you can check.

**Hint:** layer norm is three small steps on one vector - centre, scale,
return - and the `eps` is there so a vector of all zeros does not divide by
zero. The MLP's ReLU is one line: every negative number becomes zero, every
other number stays.

**Do not** copy an implementation of layer norm from anywhere. Write the three
steps, then check the mean and standard deviation you get against the
definition - that check is the whole point of the function.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. In your own words, what are the four parts of a transformer block and what
   is each one for?
2. Why does a residual connection help deep networks train? Give the
   gradient answer, not just the "keeps information" answer.
3. What is the shape of the block's input and output, and why does that
   matter for stacking blocks?
4. The residual connection adds the input to the attention output. What would
   happen to the model's output if you removed it, and how would you notice?

## Artifact

Write `docs/notes/L23-block.md` - under 200 words, aimed at a smart friend
who has never heard of a transformer. It must contain:

- the four parts of the block, one short phrase each
- the shape rule for the block's input and output, with the symbol for the
  token count and the model width
- one concrete number from your own run: the mean and standard deviation of
  the block output

Then commit it. The artifact is the proof that you understood it, not the
proof that you ran the code.
