---
id: L41
phase: 4
title: "Build your own provider - the mock, and what it is not"
minutes: 35
concepts: [mock-provider, determinism, harness-testing, seed]
prereqs: [L40]
paths: [beginner, provider-live]
exercise_file: exercises/L41_mock_provider.py
quiz: L41
---

# L41 - Build your own provider: the mock, and what it is not

## Why this matters

The `mock` provider exists so the whole pipeline - battery, metrics, swap
matrix, friction report - can be exercised with **zero credentials and zero
spend**. Without it you could not learn the harness until you had a credit
card and three API keys. But there is a trap: the mock produces numbers that
look exactly like real numbers, and those numbers are worthless as evidence.

## The naive story

Imagine a flight simulator. It does not fly a real plane, and it does not
teach you how to fly a real plane on its own. But it teaches you the
*instruments*: what the altimeter looks like in a stall, what the checklist
sounds like, what to do when an engine catches fire. You learn the cockpit
procedures without burning fuel.

The mock provider is the flight simulator of this repo. It is not the plane.

## What breaks

**Break 1 - the mock is not evidence.** This repo's rule number 4 says it
outright: the mock is not evidence. `report.run_report()` prints a warning
banner at the top of every mock run - *"SIMULATED RUN ... These numbers come
from an offline simulator ... They are not a measurement of any real model and
must never be quoted as evidence."* If you publish "accuracy 80 %" from a mock
run, you have published a number about a piece of code you wrote.

**Break 2 - a simulator that changes every run teaches you nothing.** If the
mock answered randomly, every run would give a different result, and you
could never tell whether a change in your metrics code caused a change in the
score or whether the mock just rolled differently. So the mock is
**deterministic**: the same state and the same question give the same answer,
every time. The `seed` field is what makes that true.

**Break 3 - "deterministic" is a claim you can test, so test it.** Any
deterministic program can be made non-deterministic by accident: one
`dict` iteration order change, one `random` call, one timestamp read. The
mock in this repo avoids all three - it derives its numbers from a **hash** of
the seed, the question id and the serialised state, which is a pure function
of its inputs.

## The story

Picture a fire drill in an empty building. There are no flames, but the alarm
is real, the doors unlock on schedule, and the supervisor times how long
everyone takes to get out. The drill cannot tell you whether the building
would survive a real fire. It tells you something else, and it is the thing
you actually need first: that your alarm, your doors and your people know what
to do.

The mock provider is that drill for this harness. It answers, it answers fast,
it costs nothing, and every report labels it a simulation. What it proves is
that the battery loads, the answers come back, the metrics compute and the
report prints.

A drill has to be repeatable too. If the alarm rang at a different minute each
time, you could never tell whether a change in your score came from a change
in your people or from a change in the drill. So the drill is scheduled, and
so is the mock: its numbers come from a hash of the seed, the question and the
state, so the same inputs always produce the same answer. Change the seed and
you get a different rehearsal, one that behaves like a different colleague -
which is how you rehearse swapping one colleague for another without spending
anything.

## The real thing

`MockProvider` in `decisionarena/providers.py` is a `Provider` subclass, so
it obeys the same `decide()` contract as Jev and Clef. Four things are worth
knowing precisely:

1. **It is deterministic by construction.** Every number comes from
   `hashlib.sha256(f"{self.seed}|{qid}|{json.dumps(state, sort_keys=True,
   default=str)}")` - the first 32 bits of the digest become a uniform number
   in `[0, 1)`. Same seed, same question, same state, same number. Always.
2. **The seed is the knob.** `MockProvider(seed="...")` changes every number
   it produces, and does so reproducibly. Two mocks with different seeds are
   two different "models" you can compare - which is exactly how you test the
   swap machinery without spending anything.
3. **It reproduces the SHAPE of the published findings, not the models.** The
   class attribute `FORMAT_SHIFT = {"prose": 0.0, "flat": -0.04, "nested":
   -0.81}` is the whole story: when the state is a nested structure instead
   of prose, the mock's `noul` probability is pushed down by 0.81. That is a
   *simulated* version of the reported format-friction effect, so the
   friction report has something to find. The mock also mimics the other
   published shapes: `choice` and `score` answers stay stable across formats,
   and `noul` answers carry no `confidence` while `choice`/`score` do.
4. **It fakes the meter so cost accounting is exercised.**
   `MockProvider.decide()` sets `_last_usage` to a deterministic token
   estimate (`len(str(state)) // 4` plus the length of the serialised
   questions, both divided by 4). So the cost path in `run_battery()` runs
   for free.

**The honest summary.** The mock tells you: *my metrics, my runner, my swap
matrix and my report all work end to end, on a stable input.* It tells you
nothing at all about Jev, Clef or Laya.

## In this repo

- `decisionarena/providers.py` - `MockProvider`, its `FORMAT_SHIFT` dict, its
  `_detect_format()` helper (which classifies a state as prose, flat or
  nested) and its hash-based probability source.
- `decisionarena/providers.py` - `normalise_answers()` is what the mock's
  raw answer dict is passed through before the caller sees it.
- `decisionarena/report.py` - `run_report()` prints the "SIMULATED RUN"
  banner whenever `result.provider.startswith("mock")`.
- `decisionarena/cli.py` - `cmd_run()` and `cmd_friction()` and `cmd_swap()`
  all work with `--provider mock`; `providers.available_providers()` lists
  mock as always configured, with the note "offline simulator - tests the
  harness, proves nothing about real models".
- `decisionarena/harness.py` - `run_battery()` writes `<run_id>.jsonl` and
  `<run_id>.meta.json` for mock runs too, so the evidence pipeline is
  exercised as well.

## Your turn

Write a file `exercises/L41_mock_provider.py` that contains:

- a class `MyProvider(providers.Provider)` - your own tiny deterministic
  provider. It must:
  - set `name` to something like `"mine"` and `price_per_mtok` to `0.0`
  - implement `decide(self, state, questions)` so that the answer for a given
    question depends **only** on the state and the question id - for example
    a probability derived from the number of characters in the state, mapped
    into `[0, 1]`
  - return its answers through `providers.normalise_answers(...)`, so the
    shape matches every other provider
  - set `self._last_usage` to a dict with an `input_tokens` key
- a function `same_answer_twice(p, state, questions) -> bool` that calls
  `p.decide(...)` twice on the same inputs and returns whether the two
  results are equal
- a `main()` that:
  - builds a `MyProvider` and the questions from `cases/routing.json`
    (`routing-001`), and prints the answer for the `team` question
  - prints whether `same_answer_twice(...)` is `True`
  - builds a second `providers.MockProvider(seed="other-seed")` and shows
    that its `noul` answer for the same state is a fixed number that you
    print twice, to prove the seed makes runs reproducible
- a self-check section using `assert` that fails loudly if:
  - two calls on the same state and questions return different answers
  - your provider's answers do not have the same keys as
    `providers.normalise_answers(...)` output for the mock (i.e. every
    answer dict has exactly the keys `kind`, `value`, `probabilities`,
    `confidence`)
  - a *different* state produces a *different* answer from your provider
    (a provider that always says the same thing would pass the first
    determinism check and still be useless)

Inputs: the `routing-001` case from `cases/routing.json`. Expected output:
one answer dict, `True` for the determinism check, and a stable repeated
number for the seeded mock.

**Hint:** the easiest deterministic source of a number that depends on the
state is the state itself - its length, or the sum of its characters. The
mock does the same thing, only with a hash, because a hash is hard to
accidentally collide and easy to make reproducible.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. The mock's `FORMAT_SHIFT` shifts the `noul` probability by -0.81 for a
   nested state. Why does the mock bother to simulate that, and why can you
   still not quote a mock friction number as a finding?
2. What is the difference between "deterministic" and "the same output because
   I hard-coded it"? Why does the repo care about the difference?
3. If your own provider returns the same answer for every state, would the
   determinism check catch it? What would catch it?

## Artifact

Write `docs/notes/L41-mock-provider.md` - under 250 words, for someone who
has never run this repo. It must contain:

- one sentence saying what the mock is and one sentence saying what it is
  not
- the exact reason the mock's numbers may never be published as evidence
- one concrete number from your own run: the repeated seeded mock value, and
  the number of characters you used in your own provider
- one line stating the property your own provider guarantees and how you
  proved it

Then commit it.
