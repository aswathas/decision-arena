---
id: L80
phase: 8
title: "Choosing a provider - the decision table"
minutes: 35
concepts: [provider-selection, latency, quality, cost]
prereqs: [L43, L44]
paths: [beginner, provider-live]
exercise_file: docs/notes/L80-provider-decision-table.md
quiz: L80
---

# L80 - Choosing a provider: the decision table

## Why this matters

This repo measures several decision models against each other, but it never
tells you which one to *buy*. That is on purpose: the answer depends on your
tickets, your latency budget and your bill, and nobody else's numbers can
decide it for you. The skill this lesson teaches is turning "which provider is
best?" into a table you fill in with **your own measurements** - a table that
ends in a decision and in the condition that would change it.

## The naive story

Every vendor publishes a benchmark table. Here is one, roughly, from the
Cloudflare launch post:

| model | BANKING77 | CLINC150 | BFCL | median latency |
|---|---|---|---|---|
| Clef 27B | 94.20 | 97.43 | 98.47 | 209.3 ms |
| Jev | 79.74 | 89.27 | 95.75 | 524.1 ms |

Look at it for ten seconds and you will conclude: Clef wins on quality *and*
latency, so buy Clef. That conclusion is the naive story, and it is exactly
what this repo exists to question - because a table like this is measured on
*the vendor's* data, in *the vendor's* serialisation, with *the vendor's*
threshold choices.

## What breaks

**Break 1 - the benchmark is measured on someone else's workload.** The
Cloudflare table above compares a 27B model and a hosted model on five public
datasets. Your workload is support tickets. A model that is superb at
classifying bank intents may be mediocre at telling "I want a refund" apart
from "my card was stolen" - and the only way to know is to run *your* tickets
through *both* models. The harness exists for exactly this: `cases/routing.json`
says in its own description, *"Swap these for your own tickets to get a real
workload measurement."*

**Break 2 - the vendor's latency number and your latency number are different
numbers.** Cloudflare advertises a 209.3 ms median for Clef (a **CLAIM** in
your vault's Claims Ledger - a vendor table, not independently checked). The
independent harness `rmax-ai/jev-vs-clef` *observed* something very different:
Jev at roughly **0.3 s** p50, Clef at **18.7 s** and clef-flash at **18.6 s**
(a **VERIFIED** observation, reproduced in two dated runs). Same models, same
week, wildly different latencies - because latency depends on your region,
your payload, your queue and the hour of the day. The only latency number that
counts is the one you measured on your own calls.

**Break 3 - price per million tokens is not price per decision.** Jev is
$0.042 per Mtok, clef-flash $0.038, Clef $0.24, an OpenAI-compatible gateway
$0.02 by default. Those look like a narrow spread - until you remember that
**the state is re-sent on every call**. A model that costs less per token but
needs three calls to answer one ticket can cost more per ticket. Unit
economics, not unit prices, is what you choose on.

**Break 4 - the capability differences are not interchangeable.** Only
`ClefProvider` sets `supports_images=True`, and only Clef accepts image
inputs. If your tickets contain screenshots, the decision table does not have a
"clef" column you can leave blank - the others are not candidates at all.
Meanwhile a local Laya model has **no per-token price at all**: it costs
electricity, VRAM and your own attention, which is the cheapest option at scale
and the most expensive option to operate.

## The story

Two delivery vans sit on the forecourt. One is cheap and slow, one is
expensive and quick. Each has a brochure, and each brochure says its van is
best - because it was written by the people who sell the van, and it was
measured on the vendor's own parcels.

Your parcels are not the vendor's parcels. The brochures decide nothing.

So you build a table: one row per van, one column per thing that could stop
you choosing it.

Some columns come from the manual - the price per million tokens, whether it
accepts a picture at all, what keys it needs. One of those is not a
preference but a wall. If your tickets carry screenshots and a van cannot
carry screenshots, it is not a candidate, it is out.

Some columns you fill with arithmetic: your own ticket count, times the
tokens a ticket really takes, times the price, over a million.

And one column nobody can fill for you: what the van did on your parcels, at
your thresholds, from your building. That column costs a day and a few
cents.

Then write the decision at the bottom, with the condition attached.

## The real thing

**Provider selection** is a decision under constraints, and the honest way to
make it is a table with one row per candidate and one column per constraint.
Here is the skeleton, with the real numbers from this repo's code:

| provider | price/Mtok (USD) | images | credentials (env vars) | measured on YOUR tickets |
|---|---|---|---|---|
| `jev` (Jev, TypeSafe) | `0.042` | no | `TYPESAFE_API_KEY` | accuracy, ECE, latency |
| `clef` (Clef 27B) | `0.24` | **yes** | `CLOUDFLARE_ACCOUNT_ID` + `CLOUDFLARE_AUTH_TOKEN` | accuracy, ECE, latency |
| `clef:clef-flash` | `0.038` | **yes** | same two | accuracy, ECE, latency |
| `oai` (OpenAI-compatible) | `0.02` (default) | depends on the gateway | `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL` | accuracy **plus adapter overhead** |
| `mock` | `0.042` (a fake number) | no | none | nothing - it is not a model |
| local Laya | **no per-token price** | no | none, but a GPU | latency on your hardware, VRAM |

Three things make this table real rather than decorative:

1. **The prices are read from the code, not remembered.**
   `ClefProvider.PRICES` is `{"clef": 0.24, "clef-flash": 0.038}`; `JevProvider.__init__`
   defaults `price_per_mtok` to `0.042`; `OpenAICompatibleProvider.__init__`
   defaults to `0.02`; `MockProvider.__init__` defaults to `0.042` so the cost
   path is exercised for free. `providers.build_provider("clef:clef-flash")`
   hands you an object that already knows its price.
2. **The capability column is a hard filter, not a preference.**
   `ClefProvider.__init__` passes `supports_images=True` to the base class;
   no other adapter does. `available_providers()` prints a `note` per provider
   for the same reason.
3. **The last column is the one you have to go and measure.** It is the only
   column the vendor cannot fill in for you.

**The arithmetic of the cost column.** One Mtok is a million tokens. Take a
realistic workload: 10,000 tickets a month, each needing one call of about
500 input tokens. That is 5,000,000 tokens = 5 Mtok:

| provider | 5 Mtok costs |
|---|---|
| `clef:clef-flash` @ 0.038 | **$0.19** |
| `jev` @ 0.042 | **$0.21** |
| `clef` @ 0.24 | **$1.20** |
| `oai` @ 0.02 | **$0.10** (plus whatever your gateway really charges) |

Now read that table the right way round: the *ranking* of the top three is
almost irrelevant next to the *absolute* numbers. The entire monthly bill for
the cheapest real option is nineteen cents. On a number this small, the
deciding factor is not price - it is latency, capability, or swap risk. Price
only becomes the deciding factor when you either send far more tokens than I
just guessed, or you batch badly (lesson L81), or you call a provider many
times for one ticket.

**Quality is a column with two sub-columns, and you must not mix them.**
*Vendor benchmark quality* is what the launch post says - a **CLAIM**.
*Workload quality* is what your own battery says - the only number you can
put your name to. The second is measured with `python -m decisionarena run
--provider <spec> --battery routing` against a battery you wrote, and it
comes back as accuracy, mean ECE and mean Brier over a `scored cases` count
you should read first.

**Latency is a distribution, not a number.** The report prints p50, p95 and
max. p50 is the typical call. p95 is the one your users start complaining
about. max is the one that pages you. And a local model adds a shape the
hosted ones do not have: a **cold start**, where the first call after the
server starts pays for loading the weights - which is why `laya-lab/README.md`
recommends `LAYA_PRELOAD=1`. A provider can win on p50 and still lose on max.

**The rule for the final cell.** Choose by **measuring your own workload**,
not by a vendor benchmark. A model that wins the vendor's table may lose on
YOUR tickets, because your tickets are not in the vendor's table. If you
cannot explain, in one sentence, why the winner wins *on your data*, you do
not have a decision - you have a preference.

## In this repo

- `decisionarena/providers.py` - the `Provider` dataclass holds `name`,
  `price_per_mtok`, `wire_keyword`, `supports_images` and `notes`. That
  dataclass *is* the table: every row of it is a column you can sort on.
- `decisionarena/providers.py` - `JevProvider.__init__` defaults
  `price_per_mtok=0.042` and `model="jev-latest"`; the docstring lists the
  pinnable ids `jev-latest | jev-1.14.0 | jev-1.13.0`.
- `decisionarena/providers.py` - `ClefProvider.PRICES` is
  `{"clef": 0.24, "clef-flash": 0.038}`, and `ClefProvider.__init__` is the
  only place in the file that passes `supports_images=True`.
- `decisionarena/providers.py` - `OpenAICompatibleProvider.__init__` defaults
  `price_per_mtok=0.02`, and its docstring warns you to treat its numbers as
  "schema-adapter overhead", not raw model quality.
- `decisionarena/providers.py` - `build_provider(spec)` turns
  `jev` / `clef:clef-flash` / `mock` / `oai` into provider objects, and
  `available_providers()` returns the `(spec, configured, note)` triples that
  the `providers` command prints.
- `decisionarena/providers.py` - `MockProvider` is the row that is *not* a
  candidate: it is the harness's test double.
- `decisionarena/cli.py` - `cmd_run()` prints `price : $X/Mtok` before any
  call, so the price of the thing you are about to run is never a surprise.
- `decisionarena/report.py` - `run_report()` prints the `## Latency` table
  (p50 / p95 / max) - the three numbers your decision table's latency column
  should hold.
- `cases/routing.json` - the five-case battery whose description tells you to
  swap in your own tickets.
- `laya-lab/README.md` - the local option: open weights, a hardware table
  (the 9B variant is the one that fits a 4 GB card) and the two ways to wire
  it into this harness.
- `AI-CONTEXT.md` - `verified_facts` records the price points
  (`clef $0.24/Mtok, clef-flash $0.038/Mtok, jev $0.042/Mtok`) with an
  `evidence` pointer and a `verified_on` date.

## Your turn

Write a file `docs/notes/L80-provider-decision-table.md`. It is the decision
table you will actually use, filled in with numbers you can defend.

It must contain:

- a Markdown table with **one row per real candidate** - `jev`, `clef`,
  `clef:clef-flash` and `oai` (and `local Laya` as a row with "no per-token
  price" in the cost cell) - and these columns:
  - `price_per_mtok` - read from the **real provider objects**, not from
    memory: build each one with `providers.build_provider(...)` and print
    `provider.price_per_mtok` and `provider.supports_images`
  - `images` - the value of `provider.supports_images`
  - `credentials` - the environment variable names from
    `providers.available_providers()` (or from `.env.example`)
  - `cost per 10,000 tickets` - your own arithmetic for 10,000 calls of 500
    input tokens each, using the repo's own formula
  - `latency` - leave it as `not measured yet` until you have a run; then put
    the p50 from your own report in it
  - `quality on my tickets` - leave it as `not measured yet` until you have
    run the routing battery with your own cases
- a second short table: **one row per candidate, one column for "why not",
  or "-" if it won** - the reason each candidate was rejected (price, latency,
  no image support, needs a key you do not have, schema-adapter overhead)
- one paragraph: **your decision**, naming the winner, and the **one
  condition that would change your mind** (for example "if clef-flash p95
  went above 2 s on my payloads I would move the whole routing battery to
  clef")
- one sentence saying plainly that the vendor's benchmark table is not what
  decided it, and what your own measurement is

Inputs: the provider objects from `decisionarena.providers`, the price points
in `decisionarena/providers.py`, and the formulas in
`decisionarena/providers.py`'s `estimate_cost`.

Expected output: a Markdown file with the two tables, the decision paragraph
and the closing sentence - about 400 words.

**Hint:** the selection rule is "measure your own workload, not the vendor's
table". Every cell in the table should be either a number you computed from
this repo's code, or the literal words `not measured yet`. If you catch
yourself writing a number you did not compute, that is the number to delete.

**Do not** put any API key, account id or token in this file or in any file
you commit. Credentials are environment variables only.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. Your table says `clef` is the best model on the Cloudflare benchmark and
   `clef-flash` is cheaper by 6x. Why can that still be the wrong answer for
   your support tickets, and what would you run to find out?
2. Which single column of your table could you fill in honestly *today*, with
   no API key and no network? Which columns need real calls?
3. `clef` costs $0.24/Mtok and `clef-flash` costs $0.038/Mtok - about 6x
   more. Under what workload does that stop mattering, and what does that
   tell you about when cost should decide the table?
4. Why is a local model a legitimate row in the table even though it has no
   price per million tokens?

## Artifact

The artifact **is** `docs/notes/L80-provider-decision-table.md` - the file you
wrote above. Read it once more as if you were handing it to a colleague who
has never heard of this repo: every number in it must be traceable to a
command you ran or an object you printed, and the decision paragraph must
name a condition that would change it.

Then commit it. The artifact is the proof that you chose on measurement, not
on a table somebody else wrote.
