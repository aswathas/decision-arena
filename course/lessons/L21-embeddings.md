---
id: L21
phase: 2
title: "Embeddings - numbers as places in space"
minutes: 35
concepts: [embeddings, vectors, similarity, geometry]
prereqs: [L20]
paths: [beginner, foundations]
exercise_file: exercises/L21_embeddings.py
quiz: L21
---

# L21 - Embeddings: numbers as places in space

## Why this matters

After L20 the text is a list of numbers. But a list of numbers does not say
what a word *means*. The token id 8821 does not tell you that "charged" is
closer to "refunded" than to "cat". A model needs a way to say "these two
things are about the same thing", and that way is an **embedding**: a fixed
list of numbers that places every piece of text as a point in a space.
Everything downstream - attention, similarity, semantic search - is geometry on
those points.

## The naive story

Picture a map of a city. Every address is a point on that map. Two addresses
that are close together are near each other in the real world; two that are
far apart are not. If you draw the map in two dimensions, you can eyeball
"are these two places near each other?" by looking at the picture.

An embedding is a map of meaning, and the coordinates are the numbers. Nothing
in the numbers is a word - the whole meaning is in the *relative positions*.

## What breaks

**Break 1 - "close" has to be a number, not a vibe.** A map you look at is
fine for a human. A program needs a formula. The usual one is the **dot
product** of two vectors: multiply matching coordinates and add them up. Two
points pointing the same way get a big number; perpendicular points get about
zero; opposite points get a negative number. So "similar" becomes
arithmetic.

**Break 2 - a dot product is not a distance.** Two points far apart but
pointing the same way (for example `[10, 0]` and `[100, 0]`) have a huge dot
product, yet they are obviously far apart in space. So dot product measures
*direction*, not *distance*. When you want distance, you use the Euclidean
distance - the ordinary straight-line distance - and when you want a 0-to-1
"how similar" number, you use **cosine similarity**: the dot product
divided by the two lengths, so only the direction matters.

**Break 3 - meaning is not one axis.** Real embeddings live in hundreds or
thousands of dimensions, and we do not get to say "dimension 7 is about
animals". The geometry is distributed. This is why people draw embeddings in
2-D for teaching: the picture is a simplification, but the *idea* - near means
similar - survives.

## The story

A town planner draws a chart of the whole district on one sheet of paper.
Nothing on the chart is a name. The planner works backwards from the traffic:
the grocer's van and the bakery's van run the same route every morning, so their
pins go on top of each other, and the bus depot ends up on the far side of the
river from them. Ask the planner what a pin means and they shrug - they never
decided where the pins went, only which journeys shared a road.

Two offices draw two charts, and the same shop can carry a different address on
each. The number is the pin's address on that one sheet, and nothing more.

Now the practical difficulty. The clerk at the desk cannot measure nearness by
eye and report "close". They need a rule they can do with a calculator:
multiply matching coordinates and add them up. That number grows when two pins
point the same way, however far apart they sit - it measures direction, not
distance. Divide by the length of each pin and only the direction survives,
which is the number they actually want: how aligned are these two things?

## The real thing

An **embedding** of a piece of text is a **vector**: an ordered list of
floats, say `[0.9, 0.1]`. Two things are called **similar** when their
embeddings are close in that space.

Worked example, hand-picked numbers, 2 dimensions:

```
"cat"      -> [0.0, 1.0]
"dog"      -> [0.1, 0.9]
"billing"  -> [1.0, 0.0]
"technical"-> [0.9, 0.2]
```

Distances (straight-line, Euclidean):

```
dist("cat", "dog")        = sqrt((0.0-0.1)^2 + (1.0-0.9)^2) = 0.141
dist("cat", "billing")    = sqrt((0.0-1.0)^2 + (1.0-0.0)^2) = 1.414
dist("billing","technical")= sqrt((1.0-0.9)^2 + (0.0-0.2)^2) = 0.224
```

So "cat" and "dog" are near each other and far from "billing", and "billing"
and "technical" are near each other. That nearness *is* the meaning the model
has learned.

**Cosine similarity** on the same points:

```
cos("cat", "dog")         = (0.0*0.1 + 1.0*0.9) / (1.0 * 0.906) = 0.993
cos("cat", "billing")     = (0.0*1.0 + 1.0*0.0) / (1.0 * 1.0)    = 0.000
cos("billing","technical") = (1.0*0.9 + 0.0*0.2) / (1.0 * 0.922)  = 0.977
```

Note the near-orthogonal pair: "cat" and "billing" score exactly zero, not
because they are unrelated but because their directions happen to be
perpendicular in this toy example. Cosine similarity lives in `[-1, 1]`;
dot products are unbounded.

**Why this is the machinery of meaning.** Because the geometry is *learned*.
A model is trained so that words that appear in similar contexts end up near
each other. "Refund" ends up near "charge" not because anyone wrote down that
they are related, but because tickets that mention one tend to mention the
other. The map is drawn by the data.

## In this repo

- `examples/04_attention_numpy.py` - the variable `x` holds three 2-D
  **embeddings**, one per token: `[1.0, 0.0]` for "the", `[0.0, 1.0]` for
  "cat", `[0.9, 0.1]` for "dog". The comment in the file says it plainly:
  "In a real model: the output of the embedding layer." The comment above it
  explains why those numbers were chosen - token 0 and token 2 are similar
  vectors, so they should attend to each other.
- `examples/04_attention_numpy.py` - `attention_scores()` computes exactly
  the dot product from this lesson: it multiplies each query row by each key
  column. So the "similarity" here is a dot product between two embeddings.
  That is the bridge from this lesson to L22.
- `examples/03_train_linear.py` - the features of each example
  (`[0.10, 0.10]`, `[0.85, 0.65]`, ...) are the same idea: a small vector per
  row, and the model learns a score from it. A logistic regression's features
  are a hand-made embedding.
- `decisionarena/providers.py` - the repo itself does not embed anything. It
  sends the raw `state` string to a vendor and measures the returned
  probabilities. That is deliberate: the harness measures the *output* of the
  model, not the mechanism inside it.

## Your turn

Write a file `exercises/L21_embeddings.py` that contains:

- a function `dot(a: list[float], b: list[float]) -> float` that returns the
  dot product of two equal-length vectors
- a function `distance(a: list[float], b: list[float]) -> float` that returns
  the Euclidean distance between two vectors
- a function `cosine_similarity(a: list[float], b: list[float]) -> float` that
  returns the cosine similarity, and returns `0.0` when either vector has
  length zero (a zero vector has no direction)
- a function `nearest(query: list[float], vectors: dict[str, list[float]]) ->
  str` that returns the key of the vector closest to `query`
- a `main()` that:
  - defines the four toy embeddings from "The real thing" - "cat" -> [0.0, 1.0],
    "dog" -> [0.1, 0.9], "billing" -> [1.0, 0.0], "technical" -> [0.9, 0.2]
  - prints the distance from "cat" to "dog" and from "cat" to "billing",
    with four decimal places
  - prints the cosine similarity from "cat" to "dog" and from "cat" to
    "billing", with four decimal places
  - prints the nearest neighbour of "cat" and the nearest neighbour of
    "billing"
  - prints a line `nearest_cat=cat_to_dog_is_closer` style summary is NOT
    required; instead print `nearest_of_cat=<name>` and
    `nearest_of_billing=<name>`

Inputs: the four toy embeddings above. Expected output: "dog" is the nearest
neighbour of "cat" and "technical" is the nearest neighbour of "billing", the
"cat"/"dog" distance is much smaller than the "cat"/"billing" distance, and
the "cat"/"billing" cosine similarity is about 0.0.

**Hint:** cosine similarity is the dot product divided by the two vector
lengths, and the two lengths multiply together - so compute each length once
and use them twice, rather than taking two separate square roots.

**Do not** stop at the nearest neighbour. Print the raw numbers too, because
the whole lesson is that the numbers *are* the meaning, and you should be
able to check each one by hand.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. What is an embedding, in one sentence, and what does it mean for two
   pieces of text to be "close"?
2. Why can the dot product of two vectors be large even when the vectors are
   far apart? What does cosine similarity fix?
3. Where does the *meaning* in an embedding come from - a human writing a
   definition, or the training data?
4. In `examples/04_attention_numpy.py`, which two tokens have embeddings that
   are close to each other, and what does the file do with that fact?

## Artifact

Write `docs/notes/L21-embeddings.md` - under 200 words, aimed at a smart friend
who has never heard of embeddings. It must contain:

- one sentence defining an embedding
- the distance and the cosine similarity between "cat" and "dog" from your
  own run of your own code
- one sentence on why the cosine similarity of "cat" and "billing" is about
  zero even though they are nothing alike

Then commit it. The artifact is the proof that you understood it, not the
proof that you ran the code.
