---
id: L43
phase: 4
title: "Jev - TypeSafe System One"
minutes: 35
concepts: [jev, system-one, decision-model-api, api-key]
prereqs: [L40]
paths: [beginner, provider-live]
exercise_file: docs/notes/L43-jev.md
quiz: L43
---

# L43 - Jev: TypeSafe System One

## Why this matters

Jev is the first of the three real backends this harness measures, and it is
the one that defines the **wire protocol** everything else is built to match.
Jev is not a chat model you prompt and read a paragraph back from. It is a
**decision-model API**: you hand it a state and a set of questions, and it
hands back probabilities. That difference is why this repo's metrics are
possible at all.

## The naive story

Think of a clinic triage desk. The patient arrives (that is the **state**).
The desk has a fixed set of questions it always asks - "is this about a
payment?", "which team should handle it?", "how severe is it?". The desk does
not write a report about the patient; it **decides** and gives you a
confidence for each question.

TypeSafe's **System One** API is that triage desk. The name of the wire
format comes from the same family: the endpoint is
`https://api.typesafe.ai/v1/systemone`.

## What breaks

**Break 1 - it is not a chat API.** If you send Jev a chat prompt and expect
a paragraph, you are using the wrong shape entirely. The request is a
structured payload - `{"model", "state", "questions"}` - and the response is a
structured `{"answers": {...}}` where each answer carries a `type` and a
value (a probability for `noul`, an option key for `choice`, a level index
for `score`).

**Break 2 - the endpoint is a single, specific URL.** Not
`/chat/completions`. Not `/v1/complete`. It is `/v1/systemone`. Every
adapter in this repo knows one URL, and this is it.

**Break 3 - no key, no call.** `JevProvider.decide()` checks the key
*before* it builds a request and raises `RuntimeError("TYPESAFE_API_KEY is
not set")`. So a missing credential is a clear error, not a mysterious 401
or a hang.

## The story

Picture a triage desk in a clinic. A patient arrives - that is the state. The
desk has a fixed card of questions it always asks: is this about payment,
which team should take it, how severe is it. The desk does not write a letter
about the patient. It decides, and it hands back a card where each answer is a
number, a team name or a level.

Jev's System One API is that desk. You send the patient and the card of
questions as a structured payload, and the desk hands back structured answers:
a probability for the yes/no question, an option for the multiple choice, a
level for the severity. No paragraph to parse, and no instruction about how to
read the reply.

The desk has one fixed address - a single specific URL, not a family of chat
paths - and one key. The key is checked before the request is built, so a
missing key produces a plain error naming the environment variable you forgot,
rather than a puzzling refusal from the far end.

The desk also keeps its own meter: the reply says how many tokens it consumed,
so the fare can be worked out. And it stamps which model answered, because
"latest" is a moving target and a pinned version is not.

## The real thing

**What Jev is.** TypeSafe's decision model, exposed as the System One API.
This repo's `JevProvider` docstring lists the available model ids:
`jev-latest`, `jev-1.14.0`, `jev-1.13.0`. The default is `jev-latest`, and
the provider's name in every report is `jev:<model>` - so `jev:jev-1.14.0`
is a different, pinnable provider from `jev:jev-latest`. Pinning matters for
an evaluation: if you compare `jev-latest` today with `jev-latest` next
month, you may be comparing two different models.

**The request.** `JevProvider.decide(state, questions)` builds:

```
{
  "model": self.model,
  "state": state,
  "questions": normalise_questions(questions, self.wire_keyword)
}
```

and POSTs it as JSON to `JevProvider.URL` with an `Authorization: Bearer
<key>` header and a `Content-Type: application/json` header. The default
timeout is 60 seconds.

**The response.** Two fields matter: `resp["usage"]` (the token counts, which
become `_last_usage` and then money through `estimate_cost`) and
`resp["answers"]` (passed through `normalise_answers()` so the harness sees
one shape regardless of vendor).

**The credential.** `TYPESAFE_API_KEY`, read from the environment
(`os.environ.get("TYPESAFE_API_KEY", "")`). `.env.example` shows the
PowerShell form: `setx TYPESAFE_API_KEY "..."`. The key never appears in a
report, a log line or a committed file - the adapter only ever puts it in the
request header.

**The price.** `0.042` USD per million input tokens, the default argument of
`JevProvider.__init__`. So a 2000-token decision costs
`2000 * 0.042 / 1_000_000` = **$0.000084**.

**How to check whether your machine is set up.** Run
`python -m decisionarena providers`. The `jev` row says `yes` or `no`, and
`available_providers()` decides that by looking for `TYPESAFE_API_KEY` in
the environment. Then a dry run costs nothing and calls nothing:
`python -m decisionarena run --provider jev --battery routing --dry-run`.

## In this repo

- `decisionarena/providers.py` - `JevProvider`, its `URL` class attribute
  (`https://api.typesafe.ai/v1/systemone`), its model default `jev-latest`,
  its price default `0.042`, its key lookup and its
  `RuntimeError("TYPESAFE_API_KEY is not set")`.
- `decisionarena/providers.py` - `build_provider("jev")` and
  `build_provider("jev:jev-1.14.0")`; `available_providers()` for the
  configured/not-configured check.
- `decisionarena/providers.py` - `_post_json()` - the shared helper that
  builds the urllib request and parses the JSON reply.
- `decisionarena/cli.py` - `cmd_run()` and the `providers` subcommand.
- `.env.example` - the `TYPESAFE_API_KEY` line.

## Your turn

Write a file `docs/notes/L43-jev.md` - a comparison note about Jev. This is
a **writing** exercise, not a coding one, and it has two variants. Pick the
one that matches your machine and say which one you did.

**Variant A - you have `TYPESAFE_API_KEY` set.** Run
`python -m decisionarena run --provider jev --battery routing`, open the
report in `runs/`, and write the note from what you actually observed:
the provider name in the run id, the cost of the run, the accuracy and ECE
the report shows, and the latency p50. Quote numbers only from your own run.

**Variant B - you have no key, or the API is unreachable from your machine.**
Write the note entirely from the source: read `JevProvider` in
`decisionarena/providers.py` and the `TYPESAFE_API_KEY` line in
`.env.example`, and write down what the adapter *would* send and what it
would cost. Mark the note clearly with a line saying which variant you did
and why.

Either way the note must contain:

- the endpoint URL and the env var name, and the model ids the adapter's
  docstring lists
- the request payload's three fields, in your own words
- the price per Mtok, and the cost of one 2000-token decision computed by
  your own arithmetic
- one sentence on why `jev-latest` and `jev:jev-1.14.0` should not be
  compared as if they were the same model
- one sentence on what the dry-run flag lets you check without spending
  anything

**Hint:** the adapter's docstring is the shortest honest summary of the
provider, and the `--dry-run` branch in `cmd_run()` is where the "no calls
will be made" behaviour lives.

**Never** write a key, even a partial one, into this note or any other file.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. What is the difference between a decision-model API and a chat API, in
   terms of what goes in and what comes out?
2. The provider's name is `jev:<model>`. Why does the harness build the name
   that way instead of just `jev`?
3. If `python -m decisionarena providers` says `jev` is not configured, what
   exactly is missing, and what would the error look like if you called
   `decide()` anyway?

## Artifact

The artifact for this lesson is the note itself: `docs/notes/L43-jev.md`.
It must be under 400 words, must state which variant you completed, must
contain no credential of any kind, and must contain at least two concrete
numbers (the price per Mtok and the cost of a 2000-token decision, plus one
more if you ran the battery).

Then commit it.
