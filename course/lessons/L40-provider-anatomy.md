---
id: L40
phase: 4
title: "Anatomy of a provider adapter"
minutes: 35
concepts: [provider-adapter, wire-protocol, usage-accounting, base-url]
prereqs: [L02, L12]
paths: [beginner, provider-live]
exercise_file: exercises/L40_provider_anatomy.py
quiz: L40
---

# L40 - Anatomy of a provider adapter

## Why this matters

Every number this repo publishes comes from one call: `provider.decide(state,
questions)`. The provider is the thing that talks to a model - TypeSafe Jev,
Cloudflare Clef, a local Laya server, or the offline mock. If you do not know
what sits between the harness and the model, then every later measurement
(accuracy, ECE, cost, latency, swap safety) is a number whose meaning you
cannot check.

## The naive story

Picture a restaurant. The kitchen is the model. The waiter is the **adapter**
(a small piece of code that speaks to one kitchen). The customer is the
harness. The customer never walks into the kitchen - they tell the waiter
"table 4 wants the refund dish", and the waiter comes back with a plate.

If the waiter changes, the kitchen changes, the dish changes - but the
customer's order and the plate they receive do not. The customer cannot tell
which kitchen cooked the food, and that is the whole point of a waiter.

## What breaks

**Break 1 - different kitchens use different words for the same thing.** This
repo's yes/no question type is called `noul`. Cloudflare's API accepts it.
Vercel's AI Gateway calls the very same primitive `boolean` and **rejects**
`noul` outright. If the adapter does not translate, the request fails at the
kitchen door and the harness records an error instead of an answer.

**Break 2 - the plate is not the same shape as the order.** A provider returns
whatever its API returns. One returns `{"noul": 0.9}`, another returns
`{"boolean": true}`, a third returns `{"value": 0.9}`. If the harness has to
know those differences, the harness has one code path per vendor and no
comparison is possible.

**Break 3 - the meter is not optional.** In 2025 you call an API, and a
number of tokens was consumed, and money left your account. An adapter that
forgets to record usage is an adapter that cannot be costed - and this repo's
whole selling point is that a full comparison costs under a dollar, so someone
has to know the number to the cent.

## The real thing

A **provider adapter** is one object that hides one vendor's quirks behind a
single method. In this repo the base class is the `Provider` dataclass in
`decisionarena/providers.py`. Field by field:

| field | what it is | why it exists |
|---|---|---|
| `name` | a short string like `"jev:jev-latest"` or `"clef:clef-flash"` | it identifies the provider in every run id, report and evidence file |
| `price_per_mtok` | US dollars per **million tokens** (0.042 for Jev, 0.24 for Clef) | the harness turns token counts into money with this one number |
| `wire_keyword` | the vendor's word for our yes/no question type (`"noul"` by default) | it is the translation key for Break 1 |
| `supports_images` | `True` or `False` | Clef accepts images; Jev does not; the harness must not send what a vendor cannot take |
| `notes` | free text | human-facing caveats, e.g. why a number should not be trusted |
| `_last_usage` | a dict of the token counts from the **most recent** call | the meter from Break 3 |

The method is the contract:

```
decide(state, questions) -> {qid: {"kind", "value", "probabilities", "confidence"}}
```

One call, one state (the world as text), a dict of questions, and a dict of
answers back. Three helpers make the contract work:

- `normalise_questions(questions, wire_keyword)` - rewrites our canonical
  `{"type": "noul"}` into the vendor's keyword when they differ. This is
  where `wire_keyword` is used.
- `normalise_answers(answers)` - flattens whatever came back into
  `{"kind", "value", "probabilities", "confidence"}`. A `boolean` answer
  becomes `kind="noul"`, and the value is read from either `noul` or
  `boolean` - one shape for every vendor, so the metrics never branch.
- `estimate_cost(usage)` - takes the usage dict and returns
  `tokens * price_per_mtok / 1_000_000`. Note the two possible token keys:
  `input_tokens` **or** `prompt_tokens`; different vendors spell it
  differently, so the function accepts either.

**Why one adapter means providers are interchangeable.** The harness calls
`decide()` and nothing else. It never knows if the answer came from a cloud
API or from a simulator on your laptop. The battery, the metrics and the swap
matrix are written against the *contract*, not against a vendor. That is why
`build_provider("clef:clef-flash")` and `build_provider("mock")` are the same
kind of object, and why `python -m decisionarena swap --provider a=jev
--provider b=clef:clef-flash` is one line of code instead of two programs.

**Base URL.** Some adapters need to know *where* to send the request. The
hard-coded URLs are in the adapters themselves - `JevProvider.URL` is
`https://api.typesafe.ai/v1/systemone`, and `ClefProvider.url()` builds
`https://api.cloudflare.com/client/v4/accounts/<account id>/ai/run/@cf/cloudflare/<model>`.
An adapter that can be pointed at a local server instead of a cloud endpoint
is what lets the local Laya server (lesson L45) reuse the same client.

## In this repo

- `decisionarena/providers.py` - `Provider` (the dataclass and the
  `decide`/`estimate_cost` contract), `normalise_questions()`,
  `normalise_answers()`, `build_provider()`, `available_providers()`.
- `decisionarena/providers.py` - `JevProvider`, `ClefProvider`,
  `OpenAICompatibleProvider`, `MockProvider`: four adapters, one contract.
- `decisionarena/harness.py` - `run_battery()` calls `provider.decide(...)`
  and then reads `getattr(provider, "_last_usage", {})` and
  `provider.estimate_cost(usage)`. That pair of lines is the entire usage
  accounting mechanism.
- `decisionarena/cli.py` - `cmd_run()` prints `provider.price_per_mtok` as
  the price line of every run.
- `examples/00_read_the_code.py` - prints the real source of `Provider`,
  `MockProvider`, `normalise_questions` and `normalise_answers`.

## Your turn

Write a file `exercises/L40_provider_anatomy.py` that contains:

- a function `describe(provider) -> list[str]` that takes any provider object
  and returns one human-readable line per field of the base `Provider`
  dataclass: `name`, `price_per_mtok`, `wire_keyword`, `supports_images`,
  `notes`. The line must contain the field name and its value.
- a function `total_cost(provider, usage_list) -> float` that sums
  `provider.estimate_cost(usage)` over a list of usage dicts, and returns the
  total.
- a `main()` that:
  - builds a provider with `providers.build_provider("mock")` and prints
    `describe(provider)`
  - calls `provider.estimate_cost({"input_tokens": 1000})` and prints the
    result with six decimal places
  - calls `providers.normalise_questions({"q": {"type": "noul"}},
    wire_keyword="boolean")` and prints the resulting dict, proving the
    keyword was translated
  - calls `providers.normalise_answers({"q": {"type": "boolean",
    "boolean": True}})` and prints the resulting dict, proving the vendor's
    `boolean` came back as `kind="noul"`
- a self-check section using `assert` that fails loudly if:
  - the normalised question's `type` is not `"boolean"`
  - the normalised answer's `kind` is not `"noul"`
  - `total_cost` for a provider with `price_per_mtok=0.042` and one call of
    `{"prompt_tokens": 1_000_000}` is not approximately `0.042`

Inputs: the `mock` provider, the usage dicts above. Expected output: the five
field lines, a cost of `0.000042` for 1000 tokens at the mock's price of
0.042/Mtok, a translated question dict, and an answer dict whose `kind` is
`"noul"`.

**Hint:** the dataclass's fields are declared on the base class, so you can
read them straight off the instance. For the keyword translation, read
`normalise_questions` and ask what it does when the wire keyword is different
from the one in the question.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. What does `wire_keyword` do that `notes` cannot do, and why does it have
   to live in the adapter rather than in the harness?
2. The harness reads `_last_usage` with `getattr(provider, "_last_usage", {})`.
   Why the `getattr` with a default instead of `provider._last_usage`?
3. `estimate_cost` accepts both `input_tokens` and `prompt_tokens`. What
   would happen to your cost report if it accepted only one of them?

## Artifact

Write `docs/notes/L40-provider-anatomy.md` - under 250 words, for a smart
friend who has never used an API. It must contain:

- the `decide()` contract in your own words: what goes in, what comes out
- one sentence on why `normalise_answers` exists
- the real cost of one 1000-token call at Jev's price, computed with
  `estimate_cost`, with the token count beside it

Then commit it. The artifact is the proof that you can explain the adapter,
not the proof that you read this file.
