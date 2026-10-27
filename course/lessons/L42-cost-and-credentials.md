---
id: L42
phase: 4
title: "Credentials, cost and the spend cap"
minutes: 30
concepts: [credentials, cost-model, spend-cap, tokens]
prereqs: [L40]
paths: [beginner, provider-live]
exercise_file: exercises/L42_cost.py
quiz: L42
---

# L42 - Credentials, cost and the spend cap

## Why this matters

A harness that can spend money without a ceiling is a harness you cannot
point at a stranger's machine. This repo's promise is that a full comparison
of real providers costs **well under a dollar** - but that only holds because
there is a **spend cap** that aborts the run, and because every price comes
from one number per provider. Get this lesson right and you can run the
comparison on someone else's laptop without their anxiety.

## The naive story

You are renting a car. The rental company does not hand you the keys and
walk away; they put a **fuel limit** on the car and the petrol gauge shows you
how much you have used. The limit is not there because they expect you to
drive badly. It is there so that a mistake - a wrong address, a wrong fuel
cap - costs a bounded amount instead of a month's salary.

The spend cap in `decisionarena/harness.py` is exactly that fuel limit. And
the fuel gauge is the usage dict.

## What breaks

**Break 1 - a key on disk is a key in a git history.** The moment you paste
a real API key into a script, a file, or a chat message, it is compromised.
This repo's rule 5: credentials come from **environment variables only**.
`.env.example` lists every variable name with an empty value; you copy it to
`.env`, fill it in, and never commit the filled file. The code reads
`os.environ.get("TYPESAFE_API_KEY", "")` and never writes a key anywhere -
the key travels in an HTTP `Authorization` header and nowhere else.

**Break 2 - the price is not the cost.** "0.042 per Mtok" means *per million
tokens*. If you do the arithmetic as "tokens times price", a 1000-token call
looks like $42. The actual cost is tiny, and the formula has one division
that people forget.

**Break 3 - the cap is checked before the call, not after.** Look at
`run_battery()`: it compares the running cost against the cap, and if the cap
is already reached it aborts *before* making the next call. So the run can
finish slightly **over** the cap - the last call you were allowed to make
was not yet paid for when the check ran. A cap is a ceiling on the number of
*further* calls, not on the final bill to the cent.

## The story

Picture a hired van with a fuel limit. The hire company fits a collar on the
filler, and the gauge shows what you have used. The limit is not there because
they expect you to drive badly. It is there so that a wrong turn costs a
bounded amount instead of a month of pay.

This harness is that van. The price per provider is one number - dollars per
million tokens - and the cost of a call is that number times the tokens you
sent, divided by a million. The division is the step people skip: "per million
tokens" is a rate for a heap, not for a single token.

And the check happens before the next call, not after the last one. That is
why the total on the bill can sit slightly above the cap: the cap governs how
many further calls you are allowed, not the settlement to the cent.

The key is part of the same story. It travels in an environment variable and
in the request header and nowhere else - never in a script, never in a file
you commit, never in a report. A key written down anywhere has already leaked,
because a committed file stays in the history forever.

## The real thing

**Tokens.** A **token** is the unit a model reads text in - roughly four
characters of English, but not exactly; punctuation and rare words split into
more tokens. Providers count the tokens they *read* and (for some APIs) the
tokens they *wrote*. In this repo the harness only ever uses the **input**
side: `estimate_cost()` reads `usage.get("input_tokens")` and falls back to
`usage.get("prompt_tokens")`, because vendors spell the same field
differently.

**The cost model.** `Provider.estimate_cost(usage)` in
`decisionarena/providers.py`:

```
tokens = usage.get("input_tokens") or usage.get("prompt_tokens") or 0
cost_usd = tokens * price_per_mtok / 1_000_000
```

One multiplication, one division. The `or` chain matters: it accepts either
spelling, and treats a missing or zero count as zero tokens rather than
crashing.

**The real prices in the code** (these are per million input tokens, in USD):

| provider | price_per_mtok | where it comes from |
|---|---|---|
| Jev | `0.042` | default argument of `JevProvider.__init__` |
| Clef (`clef`) | `0.24` | `ClefProvider.PRICES` |
| Clef Flash (`clef-flash`) | `0.038` | `ClefProvider.PRICES` |
| OpenAI-compatible | `0.02` | default argument of `OpenAICompatibleProvider.__init__` |
| Mock | `0.042` | default argument of `MockProvider.__init__` - a fake number, so the cost path is exercised for free |

Worked example: 2000 input tokens on Clef Flash costs
`2000 * 0.038 / 1_000_000` = **$0.000076**. On Clef 27B the same call costs
`2000 * 0.24 / 1_000_000` = **$0.00048**. A 1000-token Jev call costs
`0.042 / 1000` = **$0.000042**.

**The spend cap.** `harness.run_battery()` takes `spend_cap: float = 0.25`
and the CLI exposes it as `--spend-cap` with the same default. Inside the
loop:

```
if cost >= spend_cap:
    aborted, reason = True, f"spend cap ${spend_cap} reached"
    break
```

`RunResult.aborted` becomes `True`, `RunResult.abort_reason` carries the
message, and the report prints `- [!] **ABORTED**: <reason>`. The run is
stopped, not the process - the harness stays alive and everything already
collected is still written to `runs/`.

**Credentials in practice.** `providers.available_providers()` reports, per
provider, whether the right environment variables are present: `jev` needs
`TYPESAFE_API_KEY`; `clef:clef-flash` and `clef:clef` need
`CLOUDFLARE_ACCOUNT_ID` **and** `CLOUDFLARE_AUTH_TOKEN`; `oai` needs
`OPENAI_BASE_URL` and `OPENAI_API_KEY` (and `OPENAI_MODEL` to actually run).
`python -m decisionarena providers` prints that table. If a key is missing,
the adapter raises `RuntimeError("TYPESAFE_API_KEY is not set")` before it
makes any request - it never fails in a way that leaks a key.

## In this repo

- `decisionarena/providers.py` - `Provider.estimate_cost()` (the cost
  formula), `JevProvider.__init__` price default `0.042`,
  `ClefProvider.PRICES` (`{"clef": 0.24, "clef-flash": 0.038}`),
  `OpenAICompatibleProvider.__init__` price default `0.02`,
  `MockProvider.__init__` price default `0.042`.
- `decisionarena/providers.py` - `available_providers()` reads the
  environment variables and returns `(spec, configured, note)` triples.
- `decisionarena/harness.py` - `run_battery(..., spend_cap=0.25, ...)`: the
  cap check, the `cost` accumulation, `RunResult.aborted` and
  `RunResult.abort_reason`.
- `decisionarena/cli.py` - the `run` and `swap` subcommands both take
  `--spend-cap` with default `0.25`.
- `decisionarena/report.py` - `run_report()` prints the cost line
  (`cost: $... (cap $...)`) and the ABORTED line.
- `.env.example` - the list of every environment variable the repo reads.

## Your turn

Write a file `exercises/L42_cost.py` that contains:

- a function `cost_for(price_per_mtok: float, tokens: int) -> float` that
  computes the cost of a call with the same formula the repo uses
- a function `estimate_tokens(text: str) -> int` - your own honest estimate
  of the token count of a piece of text, using the same
  four-characters-per-token idea the mock uses
- a `main()` that prints a small table with one row per provider, showing the
  provider spec, its `price_per_mtok` read from the real provider objects
  (`build_provider("jev")`, `build_provider("clef:clef")`,
  `build_provider("clef:clef-flash")`, `build_provider("oai")`), and the
  cost of a 2000-token call at that price
- a second part that demonstrates the **spend cap**: call
  `harness.run_battery()` twice on the `routing` battery with the mock
  provider - once with the default spend cap, once with a spend cap smaller
  than a single mock call costs (the mock's `_last_usage` gives you its token
  count, so compute it). Use `out_dir="runs/l42-exercise"` so you do not
  mix scratch files with real evidence. Print, for each run, the abort flag,
  the abort reason, and the total cost.
- a self-check section using `assert` that fails loudly if:
  - the cost of 2000 tokens at `0.038` is not approximately `0.000076`
  - the capped run has `aborted` True and the uncapped run has `aborted`
    False
  - the capped run's total cost is **not less** than the uncapped run's total
    cost (the cap can only ever reduce spend)

Inputs: the `routing` battery (`cases/routing.json`), the four provider
specs above, and a 2000-token call. Expected output: a four-row price and
cost table, one uncapped run that completes, and one capped run that reports
`spend cap $... reached`.

**Hint:** the cost model is one multiplication and one division by a
million, and the cap is a comparison the harness makes *before* it makes the
next call - so the run that aborts is the one where the running cost has
already climbed above the cap.

**Do not** put any real key, account id or token in this file, or in any file
you commit. Environment variables only.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. Why does the repo read credentials from environment variables instead of
   a file inside the project?
2. A call uses 2000 input tokens on `clef-flash`. What does it cost, and
   where in the code is that number decided?
3. The spend cap is checked *before* each call. What does that tell you
   about the relationship between the cap and the final bill?

## Artifact

Write `docs/notes/L42-cost.md` - under 250 words, aimed at a smart friend
who has never heard of tokens. It must contain:

- the cost formula in your own words, including what "per Mtok" means
- the cost of a 2000-token call on each of the four real providers, computed
  by your own code
- the default spend cap and where it is set, and one sentence on what
  "aborted" means for the evidence in `runs/`
- a sentence saying that no key was written into any file

Then commit it.
