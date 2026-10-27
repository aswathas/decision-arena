---
id: L81
phase: 8
title: "Cost arithmetic and batching"
minutes: 30
concepts: [cost-arithmetic, batching, token-accounting, unit-economics]
prereqs: [L42]
paths: [beginner, provider-live]
exercise_file: exercises/L81_cost_arithmetic.py
quiz: L81
---

# L81 - Cost arithmetic and batching

## Why this matters

Cost is the part of this repo that looks like arithmetic and behaves like
engineering. The price per million tokens is printed on three websites and
changes rarely. What actually decides your bill is **how many tokens you
send**, and the single biggest lever on that is **batching** - asking several
questions in one call instead of one question per call. Get this wrong and you
can pay five times the bill for exactly the same answers.

## The naive story

You look up the price: $0.038 per million tokens for `clef-flash`. You have
10,000 tickets a month. Each ticket is one call, and each call reads about 500
tokens. So you compute 10,000 × 500 = 5,000,000 tokens = 5 Mtok, and
5 × $0.038 = **$0.19** a month. You move on.

That arithmetic is *correct*. It is also the arithmetic of a specific design -
one call per ticket - and the design is where the money is. The same 10,000
tickets, answered with three separate calls each (one per question), sends the
**same ticket text three times**. Now the bill is not 5 Mtok. It is closer to
6 Mtok, for exactly the same three answers. Nobody notices, because the
invoice looks the same shape as always.

## What breaks

**Break 1 - the price is per million tokens, and a token is not a
character.** `estimate_cost()` reads the provider's own token count, and the
provider counts *its* way. The mock's way, in `MockProvider.decide()`, is a
deliberately simple estimate: the state's character length divided by four,
plus the character length of each question's JSON divided by four. Four
characters per token is roughly right for English prose. It is a rough
estimate for JSON, and it is an estimate of the *input* side only.

**Break 2 - the state is re-sent on every call.** This is the whole lesson.
A decision model has no memory between calls. Every call carries the full
state again. So the cost of answering *N* questions about one ticket is not
"N times one question's cost" - it is "N times the state, plus the
questions". The state is the expensive part, and it is the part you send
again for free.

**Break 3 - batching is not always allowed.** There are real limits. The
vault's Claims Ledger records, from the Cloudflare schema docs, that **Clef
accepts 1-64 questions per request**; TypeSafe's Jev gives you 64k of context
per request and 32k per question. So you can batch - but not without limit,
and not if your shared state plus questions exceeds the context window.

**Break 4 - the bill and the metrics can disagree.** Here is the number
that should make you suspicious. From the committed run
`runs/20261025-040448-mock.jsonl`, the first line - `routing-001` - records
`"usage": {"input_tokens": 161}` and `"cost_usd": 6.76e-06`. Check it:
`161 × 0.042 / 1,000,000 = 0.000006762`. The file agrees with the formula to
the last digit. If your own run's numbers do not reproduce from the raw file
this way, you have a bug - and the raw file is the thing that is right.

## The story

Picture a courier with a heavy parcel. The parcel is the ticket - the
whole customer message, every time. The courier has no memory. She does not
remember that she delivered the same parcel to this address yesterday.

So when you ask three questions about one ticket, she walks the whole heavy
parcel down the street three times. Three times the long document goes on
the van, and the three little questions ride along each time. The bill is
three lots of the expensive thing plus one lot of the cheap thing.

Ask all three questions in a single trip and the parcel goes once. The state
is 28 tokens, the three questions are 133. One call costs 161 tokens; three
calls cost 216. The same three answers, and you just threw away 55 tokens -
about a quarter of the call - by making three trips.

Which is why the number to optimise is the cost per ticket, not the price
per token. One provider charges $0.02 per Mtok but needs four calls to
answer a ticket. Another charges $0.24 and answers in one.

You are only ever charged for what you send. The answer comes back for free.

## The real thing

**Cost arithmetic** is three steps, and the repo does exactly these three:

```
tokens = usage.get("input_tokens") or usage.get("prompt_tokens") or 0
cost_usd = tokens * price_per_mtok / 1_000_000
```

Step one: get the input token count. The `or` chain accepts either spelling
(`input_tokens` or `prompt_tokens`) and treats a missing count as zero rather
than crashing. Step two: multiply by the price per million tokens. Step
three: divide by a million. **Mtok means million tokens.** Forget the division
and a 500-token call looks like $19.

**Work the arithmetic in your head, then check the code.** One call of 500
tokens on `clef-flash`: `500 × 0.038 / 1,000,000 = $0.000019`. Ten thousand
of those: `$0.19`. On `clef` at $0.24: `500 × 0.24 / 1,000,000 = $0.00012`,
and ten thousand of those is `$1.20`. On `jev` at $0.042:
`500 × 0.042 / 1,000,000 = $0.000021`, ten thousand = `$0.21`.

Those four numbers are the ones to keep. Now the interesting part.

**Token accounting** means knowing which part of a call is the *state* and
which part is the *questions*. Take the real case `routing-001` from
`cases/routing.json` and apply the mock's own rule:

| part | characters | mock's token estimate |
|---|---|---|
| the state (the ticket text) | 113 | 113 // 4 = **28** |
| the three questions (as JSON) | 532 | 532 // 4 = **133** |
| **one call, all three questions** | | **161** |

And that 161 is not a guess: the committed run file records exactly
`"input_tokens": 161` for `routing-001`.

Now the same three questions, asked as three separate calls, each carrying the
same state:

| design | tokens |
|---|---|
| one call, three questions | 28 + 133 = **161** |
| three calls, one question each | 3 × 28 + 133 = **216** |
| saving from batching | **55 tokens, about 25%** |

Batching is not a rounding trick - it is 55 fewer tokens for the same three
answers, because the state goes over the wire once instead of three times.
And the saving grows with the size of the state: the ledger records states
of about 13 KB in the independent harness. A long state re-sent three times
is three times the biggest thing in the request.

**Batching** is therefore the single biggest cost lever in this harness. It
does not need a new model, a new prompt or a better price - it needs fewer
requests. The harness already does it: every case in `cases/routing.json`
carries all three of its questions (`is_billing`, `team`, `severity`) in one
`questions` dict, and `run_battery()` makes **one** call per case per repeat.
Ask all three questions in that one call and you pay for the ticket once.

**Unit economics** is the number you should actually optimise: **cost per
ticket**, not cost per token. It is

```
cost_per_ticket = calls_per_ticket × tokens_per_call × price_per_mtok / 1_000_000
```

`calls_per_ticket` is the one you control, and it is the one the vendor's
price page says nothing about. A provider at $0.02/Mtok that needs four
calls per ticket is more expensive than a provider at $0.24/Mtok that needs
one. This is also why the local Laya option deserves a row in your decision
table (lesson L80): its per-token price is zero, but its "calls per ticket"
is whatever your batching code does, and its real cost is the GPU you keep
busy.

**One more asymmetry worth knowing.** The Claims Ledger records that Jev's
output tokens are **free** and that Clef does not charge for output tokens
either. These are decision models: you send a state, you get a probability,
there is no long answer to pay for. So the cost of a decision model is
**entirely the input side** - which puts the whole weight of your bill on
the state you send, and makes batching even more valuable than it would be
for a chat API that billed you for the answer too.

## In this repo

- `decisionarena/providers.py` - `Provider.estimate_cost(usage)` is the whole
  cost model: `tok = usage.get("input_tokens") or usage.get("prompt_tokens")
  or 0`, then `tok * self.price_per_mtok / 1_000_000`.
- `decisionarena/providers.py` - `MockProvider.decide()` sets `_last_usage`
  to `{"input_tokens": max(1, len(str(state)) // 4 + sum(len(json.dumps(q))
  for q in questions.values()) // 4)}`. That is the token rule to mirror, and
  it is why the mock can exercise the money path with zero spend.
- `decisionarena/providers.py` - `ClefProvider.PRICES` is
  `{"clef": 0.24, "clef-flash": 0.038}`; `JevProvider.__init__` defaults to
  `0.042`; `OpenAICompatibleProvider.__init__` defaults to `0.02`.
- `decisionarena/harness.py` - `run_battery()` makes **one** call per case per
  repeat (`provider.decide(case["state"], case["questions"])`), so every case
  in a battery is already a batch of all its questions.
- `decisionarena/harness.py` - the record dict carries `usage` and
  `cost_usd` for every single call, and the run's total lands in
  `meta["cost_usd"]` next to `meta["spend_cap_usd"]`.
- `decisionarena/cli.py` - `cmd_run()` prints `price : $X/Mtok` before the
  run; the `run` subcommand's `--spend-cap` defaults to `0.25`.
- `cases/routing.json` - every case carries three questions in one dict and a
  `thresholds` dict; the case descriptions say to swap in your own tickets.
- `runs/20261025-040448-mock.jsonl` - the committed evidence: `routing-001`
  with `"usage": {"input_tokens": 161}` and `"cost_usd": 6.76e-06`, and
  `routing-002` with 154 tokens and `6.47e-06`. Both reproduce exactly from
  the formula.
- `runs/20261025-040448-mock.meta.json` - the run's own bookkeeping:
  `"price_per_mtok": 0.042`, `"cost_usd": 3.28e-05`, `"spend_cap_usd": 0.25`.
- `laya-lab/README.md` - the local option, where the per-token price is zero
  and the cost is your hardware instead.

## Your turn

Write a file `exercises/L81_cost_arithmetic.py` that contains:

- a function `cost_for(price_per_mtok: float, tokens: int) -> float` that
  computes the cost of one call using the repo's own formula (read it from
  `Provider.estimate_cost` in `decisionarena/providers.py`)
- a function `state_tokens(state) -> int` and a function
  `question_tokens(questions: dict) -> int` that reproduce the mock's token
  rule - the state's characters divided by four, and the questions' JSON
  characters divided by four (read the rule from `MockProvider.decide()`)
- a function `ticket_cost(state, questions, price_per_mtok, one_call: bool) ->
  dict` that returns the **token count** and the **cost in USD** for answering
  all the questions about one ticket, either as one batched call
  (`one_call=True`) or as one call per question (`one_call=False`, so the
  state is sent once per question)
- a function `monthly_cost(price_per_mtok: float, tickets: int,
  tokens_per_ticket: int) -> float` - the bill for `tickets` tickets of
  `tokens_per_ticket` tokens each
- a `main()` that loads the real case `routing-001` from `cases/routing.json`
  with `harness.load_cases`, and prints:
  - the token count and the cost of that ticket, batched and unbatched, at
    `0.038` (clef-flash) - so you can see the saving in tokens and in cents
  - the monthly bill for 10,000 tickets at 500 tokens each, at each of the
    three real prices `0.038`, `0.042` and `0.24`
  - one line showing your own hand-computed cost for a single 500-token call
    at `0.038`, next to the number your code produced, so the two can be
    compared
- a self-check section using `assert` that fails loudly if:
  - the cost of 500 tokens at `0.038` is not approximately `0.000019`
  - the batched ticket costs **less** than the unbatched ticket
  - the monthly bill for 10,000 tickets of 500 tokens at `0.038` is not
    approximately `0.19`
  - your computed token count for `routing-001` is **not** equal to the
    `usage.input_tokens` value recorded in the committed run file
    `runs/20261025-040448-mock.jsonl` for that case

Inputs: the `routing` battery, the price points `0.038` / `0.042` / `0.24`,
and the committed mock run file.

Expected output: the batched-vs-unbatched comparison for one real ticket, a
three-row monthly table, and the hand-arithmetic cross-check - all with the
assertions passing.

**Hint:** the token rule is one line in `MockProvider.decide()` in
`decisionarena/providers.py`, and the "cost of a call" formula is one line in
`Provider.estimate_cost()`. The batching saving comes from one observation:
in the unbatched design, the **state** is counted once per question, while
the questions themselves are counted once each either way.

**Do not** treat the mock's token estimate as a real provider's token count -
it is the mock's own estimate, and the real number comes from the provider's
`usage` in the raw file. Mirror the rule so the arithmetic is checkable; do
not present it as a measurement.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. A call reads 500 input tokens on `clef-flash`. What does it cost, and what
   does it cost if you make it ten thousand times?
2. Why does batching save tokens? Say it in terms of what is on the wire, not
   in terms of "efficiency".
3. A provider at $0.02/Mtok takes four calls per ticket; a provider at
   $0.24/Mtok takes one. Which is cheaper per ticket, and what is the general
   rule this illustrates?
4. These models charge nothing for output tokens. What does that do to the
   shape of your bill?

## Artifact

Write `docs/notes/L81-cost-arithmetic.md` - under 250 words, for a reader who
has never heard of tokens. It must contain:

- the cost formula in your own words, including what "per Mtok" means
- the batched and unbatched token counts and costs you measured for
  `routing-001`, and the saving
- the three monthly numbers you computed (10,000 tickets at 500 tokens)
- one sentence saying which number you found hardest to believe, and what you
  did to check it

Then commit it. The artifact is the proof that you can do this arithmetic
without a spreadsheet, not the proof that you ran the code.
