---
id: L44
phase: 4
title: "Clef - Cloudflare Workers AI"
minutes: 35
concepts: [clef, workers-ai, open-weights, account-token]
prereqs: [L40, L43]
paths: [beginner, provider-live]
exercise_file: docs/notes/L44-clef.md
quiz: L44
---

# L44 - Clef: Cloudflare Workers AI

## Why this matters

Clef is the second real backend, and it exists to break a specific
assumption: that a decision model has to be a closed commercial API. Clef
runs on **Cloudflare Workers AI**, and its weights are **open** - which means
two of the three providers this harness measures are, in some sense, the same
kind of animal wearing different clothes.

## The naive story

Imagine two kitchens again. One is a restaurant with a locked door and a
membership card. The other is a **food truck** parked on Cloudflare's lot:
same chef, same recipes, but the truck belongs to someone else and the fuel
meter is metered by the lot owner instead of by the chef.

Cloudflare Workers AI is the lot. The `account id` says *which lot you are
at*; the `auth token` is the card that opens the gate. Clef is the chef.

## What breaks

**Break 1 - Clef needs two credentials, not one.** `CLOUDFLARE_ACCOUNT_ID`
identifies your account, and `CLOUDFLARE_AUTH_TOKEN` authorises you. Both
must be present. `ClefProvider.decide()` raises
`RuntimeError("CLOUDFLARE_ACCOUNT_ID / CLOUDFLARE_AUTH_TOKEN not set")`
when either is missing, and `available_providers()` reports Clef as
configured only when *both* are present.

**Break 2 - the account id is part of the URL.** Clef's endpoint is not a
fixed string like Jev's - it is built per account and per model:
`https://api.cloudflare.com/client/v4/accounts/<account id>/ai/run/@cf/cloudflare/<model>`.
So the adapter has a `url()` *method*, not a constant. This is the concrete
reason the earlier lesson mentioned a **base URL**: the address of a backend
is a property of the adapter, and an adapter that can be pointed elsewhere is
what lets the same client drive a local server (lesson L45).

**Break 3 - two models, one adapter, very different prices.** `clef` and
`clef-flash` are the same family at different sizes. In the code,
`ClefProvider.PRICES` says `clef` is `$0.24` per Mtok and `clef-flash` is
`$0.038` - a difference of more than six times on the same request. The
adapter's `PRICES` dict is the only place that knows this, so a price can
never drift away from the model it belongs to.

## The real thing

**What Clef is.** `available_providers()` describes them as "Cloudflare
clef-flash 9B" and "Cloudflare clef 27B (vision)", and the repo's short
name for the family is the open-weight decision-model family - the same
family the local Laya server in `laya-lab/` serves. So the comparison this
harness exists to make is: **a hosted open-weights model against a hosted
commercial one**, measured on the same battery.

**The adapter.** `ClefProvider.__init__` takes a model name (default
`clef-flash`), reads `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_AUTH_TOKEN`
from the environment, sets `supports_images=True`, and takes its price from
`PRICES` (falling back to `0.24` for a model it does not know). `url()`
builds the endpoint. `decide(state, questions, images=None)` builds the same
three-field payload as Jev (`model`, `state`, `questions`), adds an `images`
list if one was passed, and POSTs it with a Bearer token.

**The response shape is different.** Cloudflare wraps the payload:

```
{"success": true, "result": {"answers": {...}, "usage": {...}}}
```

So the adapter checks `resp.get("success", True)` and raises
`RuntimeError(f"Cloudflare error: {resp.get('errors')}")` when the call
failed, then reads `result["usage"]` and `result["answers"]`. Two levels of
nesting, where Jev's were at the top - and the harness never notices,
because `normalise_answers()` flattens the answers and `estimate_cost()`
only needs the token count.

**Vision.** `clef` (the 27B model) accepts images; `clef-flash` does not.
The `supports_images` flag on the base `Provider` records that, so the
harness can refuse to send images to a backend that cannot take them. (The
repo's README notes that no vision case set exists yet - the adapter accepts
`images`, but there is nothing to send it.)

**The prices and what they cost.** `clef` at `$0.24` per Mtok, `clef-flash`
at `$0.038`. A 2000-token decision costs `$0.00048` on `clef` and
`$0.000076` on `clef-flash`. Compare Jev's `$0.000042` for the same
2000 tokens: on a small battery the bill is dominated by how many cases you
run, not by which vendor you pick. That is why the spend cap defaults to
`$0.25`.

**Credentials.** `.env.example` gives the PowerShell form:
`setx CLOUDFLARE_ACCOUNT_ID "..."` and `setx CLOUDFLARE_AUTH_TOKEN "..."`.
Both stay in the environment; the adapter puts only the token in the request
header, and the account id in the URL path.

## In this repo

- `decisionarena/providers.py` - `ClefProvider`, its `PRICES` dict
  (`{"clef": 0.24, "clef-flash": 0.038}`), its `url()` method, its
  `supports_images=True`, its two environment variables and its
  `RuntimeError` for missing credentials.
- `decisionarena/providers.py` - `available_providers()`, which lists
  `clef:clef-flash` and `clef:clef` with the note "Cloudflare clef-flash
  9B" and "Cloudflare clef 27B (vision)".
- `decisionarena/providers.py` - `normalise_answers()`, which makes
  Cloudflare's nested `result` payload look like every other provider's
  answers.
- `decisionarena/cli.py` - `cmd_run()` and `cmd_swap()`; the swap example
  in the README pairs `a=jev` with `b=clef:clef-flash`.
- `.env.example` - the `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_AUTH_TOKEN`
  lines.

## Your turn

Write a file `docs/notes/L44-clef.md` - a comparison note about Clef. Two
variants; say which one you did.

**Variant A - you have both Cloudflare credentials.** Run
`python -m decisionarena run --provider clef:clef-flash --battery routing`
and write the note from your own run: the provider name, the cost, the
accuracy, the ECE and the p50 latency, all quoted from the report in
`runs/`.

**Variant B - no credentials, or Workers AI is unreachable from your
machine.** Write the note from the source: read `ClefProvider` in
`decisionarena/providers.py` and the two Cloudflare lines in `.env.example`,
and describe what the adapter would send and cost. Put a line at the top
saying which variant you did and why.

Either way the note must contain:

- the endpoint URL shape, with the two parts that are filled in from your
  environment
- the two env var names, and what happens if only one of them is set
- the two model names and their two prices, and the cost of a 2000-token
  decision on each, computed by your own arithmetic
- one sentence on how Cloudflare's `{"success", "result"}` wrapper differs
  from Jev's flat response, and one sentence on why the harness does not
  care
- one sentence on what `supports_images=True` lets the harness do, and one
  on why it is not yet exercised

**Hint:** the adapter's `url()` method is where the endpoint is assembled -
read the two environment variables it uses and you have the whole URL.

**Never** write a credential, an account id or a token into this note or
any other file.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. Why does Clef need two credentials where Jev needs one, and what does the
   adapter do when only one is present?
2. `clef` costs $0.24 per Mtok and `clef-flash` costs $0.038. On a
   five-case battery, which one decides your bill - and why might that be
   surprising?
3. Cloudflare wraps its answers inside `result`, Jev's are at the top level.
   What part of this repo makes that difference invisible?

## Artifact

The artifact is the note itself: `docs/notes/L44-clef.md`. Under 400 words,
it must state which variant you completed, contain no credential of any kind,
and contain at least three concrete numbers (the two prices and the cost of a
2000-token decision on each model, plus one more if you ran the battery).

Then commit it.
