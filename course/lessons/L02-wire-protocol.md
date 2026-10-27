---
id: L02
phase: 0
order: 4
title: "The wire protocol - state in, answers out"
minutes: 35
concepts: [wire-protocol, state, json, normalisation]
prereqs: [L01]
paths: [beginner, provider-live]
exercise_file: exercises/L02_wire_protocol.py
quiz: L02
---

# L02 - The wire protocol - state in, answers out

## Why this matters

Every provider in this repo - TypeSafe Jev, Cloudflare Clef, an
OpenAI-compatible gateway, and the offline mock - is called the same way and
is handed the same thing. That shared contract is the reason a third party can
swap models and compare them. Learn the contract and the rest of the harness
becomes readable.

## The naive story

Think of a hotel reception desk. The guest (the harness) hands over a note
describing their situation, plus a list of the things the hotel needs to know.
Reception (the provider) does whatever it does in the back, then hands back a
card with the answers filled in. The guest does not enter the back office, and
does not care what model is doing the work in there.

The two things the guest hands over have names in this repo:

- the **state**: the world, as text or as JSON. One customer message, one
  incident, one email. It is *data*, never an instruction.
- the **questions**: a dict keyed by question id, each with a `type`, an
  `instructions` string, and usually a `criteria` list of allowed options.

## What breaks

**Break 1 - a provider's answer shape is not our answer shape.** TypeSafe
returns `{"type": "noul", "noul": 0.9}`. The Vercel-style gateway returns
`{"type": "boolean", "boolean": true}`. A generic chat endpoint might return
`{"type": "value", "value": 0.9}`. If the metrics had to know all three, every
metric would need a branch per vendor and no comparison would be fair.

**Break 2 - the request shape is also vendor-specific.** Jev wants
`{"model", "state", "questions"}` posted to
`https://api.typesafe.ai/v1/systemone`. Clef wants the same three keys plus
an optional `images` list. The OpenAI-compatible adapter does something
cleverer: it puts the `state` and the `questions` inside a *prompt object* that
is sent as text, and asks for JSON back - because those gateways often will
not accept the native schema. That parsing step is a tax the adapter pays so
the harness does not.

**Break 3 - "one line of JSON" is not one shape.** The response wrapper is
`{"answers": {qid: {...}}}`. Inside, the answers may have keys named after
the question type (`noul`, `choice`, `score`) or a generic `value`. Without a
translation step, downstream code has to guess.

## The story

Picture a hotel front desk, but a chain where every branch has its own
habits. A guest arrives and hands over two things: a note describing their
situation, and a slip listing what the hotel needs to know. The guest does
not step behind the counter and does not care which hotel they are at.

Behind the counter, each branch works differently. One fills in a form with
typed fields. Another writes the answers on a card. A third shouts into a
back room and the answers come back on a tape.

What the guest receives is the same everywhere: a card with a box per
question, and inside each box the same four compartments - the kind of
answer, the answer itself, a number beside each option where the branch had
one, and how sure the branch was. If the branch had no number, that
compartment is simply empty.

One rule holds at every branch. The guest's note is data, never an
instruction. In one branch's files, that note literally contains the words
ignore all previous instructions - and it goes behind the counter exactly as
written, because the instructions live on the hotel's own slip.

Same two things in, same four compartments out. That is why you can swap
hotels and compare what came out.

## The real thing

**The request** (this is the payload in `JevProvider.decide()` and
`ClefProvider.decide()`):

```json
{
  "model": "jev-latest",
  "state": "I was charged twice for my subscription this month.",
  "questions": {
    "is_billing": {"type": "noul", "instructions": "Is this about a payment?"},
    "team": {"type": "choice", "instructions": "Which team?", "criteria": {...}},
    "severity": {"type": "score", "instructions": "How severe?", "criteria": [...]}
  }
}
```

Three keys: `model`, `state`, `questions`. `state` is whatever the case says it
is - in `cases/routing.json` it is a plain string; in
`cases/format_variants.json` the same content appears as a flat JSON dict and
as a nested JSON dict. The harness never reformats it for you, because the
*shape* of the state is one of the things being measured.

**The response** (what comes back over the wire):

```json
{
  "answers": {
    "is_billing": {"type": "noul", "noul": 0.9},
    "team": {"type": "choice", "choice": "billing",
             "probabilities": {"billing": 0.72, "technical": 0.18},
             "confidence": 0.77},
    "severity": {"type": "score", "score": 1.0, "probabilities": {"1": 0.6}, "confidence": 0.8}
  }
}
```

**The normalised shape** - what `normalise_answers()` in
`decisionarena/providers.py` produces, and what every metric in the repo
actually consumes:

```json
{
  "is_billing": {"kind": "noul", "value": 0.9, "probabilities": {}, "confidence": null},
  "team": {"kind": "choice", "value": "billing",
           "probabilities": {"billing": 0.72, "technical": 0.18}, "confidence": 0.77}
}
```

Four keys, always: `kind`, `value`, `probabilities`, `confidence`. The rules
`normalise_answers()` follows:

- `kind` is the answer's `type`, but `boolean` is rewritten to `noul`.
- `value` is read from the key that matches the kind: `noul` or `boolean` for
  a `noul`, `choice` for a `choice`, `score` for a `score`, and a generic
  `value` key for anything else.
- `probabilities` defaults to `{}` when the provider sent none.
- `confidence` defaults to `None` when the provider sent none.

**Why normalise at all?** Because it makes the four keys the only interface.
`metrics.collect_scored()` reads `a["kind"]`, `a["value"]` and
`a["probabilities"]` and nothing else. `metrics.label_agreement()` reads
`a["kind"]` and `a["value"]`. A provider that invents a new answer shape only
has to be understood in one place - the adapter - not in every metric.

**And the state is never an instruction.** In `cases/injection.json` the state
literally contains "IGNORE ALL PREVIOUS INSTRUCTIONS". The protocol has no
field for instructions to the model; the instructions live in the `questions`
dict, which is *ours*, not the input's. The injection battery exists to measure
whether a model can keep that line.

## In this repo

- `decisionarena/providers.py` - the module docstring states the protocol
  directly: request is `{"state", "questions"}` (plus `model` in the
  payload), response is `{"answers": {id: {...}}}`. Then
  `normalise_questions()` (outbound translation), `normalise_answers()`
  (inbound translation), and `NUL_KEYWORDS = ("noul", "boolean")`.
- `decisionarena/providers.py` - `JevProvider.decide()` builds the payload
  with the three keys and calls `normalise_answers(resp.get("answers") or {})`
  before returning. `ClefProvider.decide()` does the same and can add
  `images`. `OpenAICompatibleProvider.decide()` nests the state and the
  questions inside a prompt and parses JSON back out of the message.
- `decisionarena/harness.py` - `run_battery()` calls
  `provider.decide(case["state"], case["questions"])` - state and questions,
  straight from the case file - and stores the returned dict under
  `"answers"` in the JSONL evidence line.
- `cases/format_variants.json` - the same content in three states (`prose`,
  `flat`, `nested`), which is how this repo measures state-shape sensitivity.
- `cases/injection.json` - states that contain hostile instructions, to test
  that the state is treated as data.

## Your turn

Write a file `exercises/L02_wire_protocol.py` that contains:

- a function `build_request(model: str, state, questions: dict) -> dict` that
  returns the request payload with exactly three keys - `model`, `state` and
  `questions` - and returns the `questions` dict unchanged.
- a function `parse_response(payload: dict) -> dict` that takes a raw
  provider response of the form `{"answers": {qid: {...}}}` and returns the
  **normalised** shape. It must use
  `decisionarena.providers.normalise_answers` for the translation - do not
  re-implement it.
- a function `describe(answers: dict) -> list[str]` that returns one
  human-readable line per question id, naming the `kind`, the `value` and the
  number of keys in `probabilities`.
- a `main()` that:
  - builds a request for the first case of `cases/routing.json` (load it with
    `json`; the file is a dict with a `"cases"` list) and prints the request's
    three keys in sorted order
  - takes a hand-written raw response in which one answer comes back as
    `{"type": "boolean", "boolean": true}` (the Vercel-style spelling) and
    one as `{"type": "choice", "choice": "billing", "probabilities":
    {"billing": 0.72}}`, wraps it as `{"answers": {...}}`, parses it and
    prints the resulting lines
- a self-check section using `assert` that fails loudly if:
  - the request payload does not have exactly the keys `model`, `state`,
    `questions`
  - the parsed boolean answer does not come back with `kind == "noul"`
  - the parsed choice answer does not come back with `value == "billing"` and
    `probabilities == {"billing": 0.72}`

Inputs: the first case of `cases/routing.json` and the hand-written raw
response above. Expected output: the three request keys, then one line per
answer showing `kind=noul` for the boolean answer and `kind=choice` for the
other.

**Hint:** the request keys are literally the three keys in the payload that
`JevProvider.decide()` builds, and the normalised shape is whatever
`normalise_answers()` hands back - the answer dict comes back from the
provider already flattened, so there is nothing left to flatten yourself.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. Name the three keys of a request payload, and say which one is "the world"
   and which one is "the questions".
2. What are the four keys of a normalised answer, and which of them can be
   `None` or empty?
3. Why does `normalise_answers()` rewrite `boolean` into `noul`, instead of
   letting the metrics handle both?

## Artifact

Write `docs/notes/L02-wire-protocol.md` - under 250 words, for someone who
has never called an API. It must contain:

- the request payload drawn as a small JSON snippet with the three keys
- the four keys of the normalised answer shape
- one sentence on why the state is data and never an instruction

Then commit it. The artifact is the proof that you can draw the contract from
memory.
