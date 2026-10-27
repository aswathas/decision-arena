---
id: L20
phase: 2
title: "Tokens - how text becomes numbers"
minutes: 30
concepts: [tokenization, vocabulary, token-ids, attention-window]
prereqs: [L10]
paths: [beginner, foundations]
exercise_file: exercises/L20_tokens.py
quiz: L20
---

# L20 - Tokens: how text becomes numbers

## Why this matters

Everything this harness measures is a number that came out of a model, and
every model that reads text has to do the same first thing: turn the text into
numbers. In this repo the text is the `state` field of a case - the support
ticket in `cases/routing.json`. A ticket like "Hi, I was charged twice for my
subscription this month" is a string to you and to me, but a model cannot do
arithmetic on a string. Tokens are the bridge. If you do not know what a token
is, then "the model read the ticket" is a phrase with no meaning in it, and so
is the cost line on your invoice.

## The naive story

Imagine a school with a strict rule: there are exactly 10,000 allowed words on
a big list on the wall. Every word gets a number, 1 to 10,000. A sentence is
then a list of numbers: "please refund" becomes `[4417, 88, 9021]`.

That is the whole naive picture. Text in, numbers out, done.

## What breaks

**Break 1 - there is no word for "charged-twice".** Real text contains
typos, made-up product names, code, ticket IDs, and half a word glued to the
next one by a missing space. A fixed list of words cannot represent any of
those, so a real tokenizer chops text into **subwords** - pieces that are often
word-like and often not. "tokenization" itself is usually not one token.

**Break 2 - the same text is not always the same number of tokens.** The
tokenizer has learned which pieces are common, so "subscription" might be one
token while "subscript" is three. And the same word can be a different number
of tokens in a different context. If your cost model assumes "one word = one
token", your invoice will be wrong, sometimes by a lot.

**Break 3 - the list has a hard limit.** A tokenizer's **vocabulary** is
finite. Its **token ids** are just the indices into that vocabulary, and there
is a highest id. Separately, the model has an **attention window**: the maximum
number of tokens it can hold in mind at once. Anything past the window is not
"old context the model skimmed" - it is gone. The model cannot use it, and it
does not even know it is gone.

## The real thing

Three names, one pipeline.

**Tokenization** is the process of cutting text into tokens. The tool that
does it is a **tokenizer**, and the list of tokens it knows is its
**vocabulary**. Each token gets an integer - its **token id** - which is the
index of that token in the vocabulary.

```
text      : "I was charged twice"
tokens    : ["I", " was", " charged", " twice"]
token ids : [40, 317, 8821, 1902]
```

Three consequences follow, and all three matter later:

1. **Token ids are meaningless on their own.** The id 40 is not "I". It is
   "whatever sits at position 40 in this vocabulary". Two different tokenizers
   - two different vendors - will assign completely different ids to the same
   text. So token ids are only ever meaningful *relative to a vocabulary you
   also have*.
2. **Tokens are what gets counted.** Cost is per token. In this repo,
   `Provider.estimate_cost()` in `decisionarena/providers.py` multiplies the
   input token count by `price_per_mtok` and divides by a million. The token
   count is not a detail of the billing department; it is the billing formula.
3. **The attention window is a hard ceiling.** A model with an 8,000-token
   window that receives 9,000 tokens of ticket will not quietly read all of it.
   It will be truncated - usually from the front, which is where your
   instructions live. This is a deployment failure mode, not a model quality
   issue, and it is exactly the kind of thing this harness exists to catch
   when it compares providers.

## In this repo

- `cases/routing.json` - the `state` string of `routing-001` is the text that
  has to become tokens: "Hi, I was charged twice for my subscription this
  month. Please refund the extra charge and confirm when it lands." Each of
  the five cases is a different-length ticket, so each is a different token
  count.
- `decisionarena/providers.py` - `JevProvider.decide()` and
  `ClefProvider.decide()` both put `"state": state` into the JSON payload.
  That string is the text the vendor's own tokenizer will cut up. The harness
  never tokenizes anything itself.
- `decisionarena/providers.py` - `MockProvider.decide()` ends with a
  deliberately crude token estimate:
  `self._last_usage = {"input_tokens": max(1, len(str(state)) // 4 + ...)}`.
  Four characters per token is a rough average for English text - good enough
  to exercise the cost accounting, and it is a simulator, not evidence.
- `decisionarena/providers.py` - `Provider.estimate_cost()` is where tokens
  become money: `tok * self.price_per_mtok / 1_000_000`.
- `examples/04_attention_numpy.py` - the three "tokens" in the attention
  example are `["the", "cat", "dog"]`. They are already cut, and their token
  ids are simply their positions: 0, 1, 2. A real model would have a
  vocabulary of tens of thousands and ids that look nothing like their order.

## Your turn

Write a file `exercises/L20_tokens.py` that contains:

- a function `tokenize(text: str) -> list[str]` that splits `text` into
  tokens by lowercasing it and splitting on whitespace, dropping empty
  pieces
- a function `token_ids(tokens: list[str], vocab: dict[str, int]) ->
  list[int]` that returns the vocabulary index of each token, and raises
  `KeyError` with a readable message naming the missing token
- a function `build_vocab(tokens: list[str]) -> dict[str, int]` that assigns
  ids 0, 1, 2, ... in order of first appearance in the token list
- a function `count_tokens(text: str) -> int` that returns how many tokens
  `text` produces
- a `main()` that:
  - takes the `state` string of `routing-001` from `cases/routing.json` (read
    the JSON file, do not retype the ticket)
  - prints the token count
  - builds the vocabulary and prints how many *distinct* tokens there are
  - prints the id of the token "subscription"
  - prints what fraction of the ticket is made of tokens that appear more
    than once, as `repeated_share = <number>` with four decimal places

Inputs: the `routing-001` state string. Expected output: a token count, a
distinct-token count, the id of "subscription", and a `repeated_share` line.

**Hint:** the whole point of this exercise is that ids depend on the
vocabulary you build, so build the vocabulary from the *same* token list you
are encoding, and build it in order of first appearance - not alphabetically.

**Do not** assume one word is one token forever. Real tokenizers split
"subscription" into pieces, and that is why the vocabulary is finite.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. What is the difference between a token, a vocabulary, and a token id? Give
   one sentence each.
2. Why can two vendors use different token ids for the same word without
   either of them being wrong?
3. A ticket is 12,000 tokens and the model's window is 8,000. What actually
   happens, and which part of the ticket is most likely to be lost?
4. In this repo, where do tokens turn into money? Name the function.

## Artifact

Write `docs/notes/L20-tokens.md` - under 200 words, aimed at a smart friend
who has never heard of a tokenizer. It must contain:

- one sentence defining a token, a vocabulary and a token id
- the token count of the `routing-001` ticket from your own run of your own
  code
- one sentence on what happens to text that is longer than the attention
  window

Then commit it. The artifact is the proof that you understood it, not the
proof that you ran the code.
