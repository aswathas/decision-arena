---
id: L63
phase: 6
title: "Determinism - same input, same output, twice"
minutes: 30
concepts: [determinism, repeatability, temperature-zero, non-determinism]
prereqs: [L60]
paths: [beginner, provider-live]
exercise_file: exercises/L63_determinism.py
quiz: L63
---

# L63 - Determinism: same input, same output, twice

## Why this matters

Everything else in this harness assumes you can run it again and get the same
numbers. If a model gives a different answer to the same ticket on a
Tuesday than on a Wednesday, then your accuracy is partly a dice roll, your
A/B comparison between two providers is partly a dice roll, and your
regression test suite is a slot machine. Before you can measure a model, you
have to know how much of the measurement is the model and how much is the
roll of the dice.

## The naive story

You ask a model to route a ticket. It answers "billing". You ask again. It
answers "billing" again. So the model is **deterministic** - same input,
same output, always.

That story is right often enough to be dangerous, because it hides the
question you actually care about: *how often is it the same?* "Always" and
"97% of the time" look the same in a demo and are completely different in a
production system.

## What breaks

**Break 1 - sampling.** When a model has temperature above 0, it does not
pick the single most likely token - it *samples*: it picks from the
probability distribution, with a random tie-break. Two identical requests
can then produce two different outputs. This is not a bug; it is what
temperature above 0 *means*. Temperature 0 means "always take the most
likely token", which is the closest thing to a deterministic mode most
providers offer.

**Break 2 - batching and hardware.** Servers batch requests together to use
the GPU efficiently. The *same* prompt can land in a batch with different
neighbours, and floating-point addition is not associative - `a + b + c` and
`c + b + a` can differ in the last bits. Different batch composition, or a
different GPU, or a different kernel, and you get a different output. This is
why "runs on my machine" is not a reproducibility argument.

**Break 3 - the provider changed underneath you.** The model behind the API
name may have been updated overnight. Your prompt is the same, the API name
is the same, the output is different. Nothing in the harness broke; the
*subject* changed. This is why the evidence contract records the provider
name and a run id: so that "which version answered this?" has an answer.

## The real thing

**Determinism**: for a fixed input, the output is identical every time.

**Repeatability**: the *property you can actually measure* - over N repeats
of the same case, how many produced byte-identical answers? The harness
measures this, it does not assume it.

**Non-determinism**: the fraction of repeats that differ. If a case is
non-deterministic 3% of the time, then 3% of your results are noise.

**Temperature-zero** (`temperature: 0`): the setting that asks the model to
always emit the highest-probability token. It removes *sampling* noise. It
does **not** remove batching noise, and it does **not** protect you from the
provider changing the model.

**The rule this lesson exists for.** A model that is 3% non-deterministic can
never be **certified** to a threshold. Read that carefully. Certification
means: "this model is safe to deploy, because its behaviour is bounded".
If 3% of the time the same input produces a different action, then the
action you certify is not the action you get. A guardrail like "escalate
when confidence < 0.6" assumes the confidence number is a property of the
*case*. If the number moves between repeats of the same case, the guardrail
is a coin flip 3% of the time.

**How the harness measures it.** `run_battery()` loops `for rep in
range(repeats)`, so `--repeats 3` writes three JSONL lines per case, each
with a different `repeat` field (0, 1, 2) and the same `case_id`. The report
writer in `decisionarena/report.py` then groups the records by `case_id`,
serialises each record's `answers` dict with `json.dumps(..., sort_keys=True)`,
and compares the **sets** of those strings: if a case produced one distinct
string across its repeats, it is byte-identical, and the report prints
`N/M cases returned byte-identical answers across repeats`. The word
"byte-identical" matters - it compares the whole answer dict, not just the
top label.

Note the mock's behaviour, because it teaches the difference: `MockProvider`
derives its probabilities from a SHA-256 hash of the seed, the question id
and the state, so the mock is deterministic by construction. That is exactly
why it is useful offline, and exactly why the mock's determinism tells you
nothing about a real model's determinism.

## In this repo

- `decisionarena/harness.py` - `run_battery(provider, cases, repeats=1, ...)`
  has the inner loop `for rep in range(repeats)`. That is the whole repeat
  mechanism - one extra line per repeat, and each becomes its own JSONL
  record with `"repeat": rep`.
- `decisionarena/harness.py` - the record dict carries `repeat` and
  `case_id`, which is what makes "the same case, twice" reconstructable
  from the raw file after the fact.
- `decisionarena/report.py` - `run_report(result)` builds the
  `## Determinism` section: it groups `result.records` by `case_id`,
  compares `json.dumps(r["answers"], sort_keys=True)` across repeats, and
  prints `**stable/len(det)** cases returned byte-identical answers across
  repeats`, plus a table of the cases that were not identical.
- `decisionarena/cli.py` - the `run` subcommand exposes `--repeats` (default
  1) and the `swap` subcommand does too.
- `decisionarena/providers.py` - `MockProvider.decide()` computes
  `hashlib.sha256(f"{self.seed}|{qid}|{json.dumps(state, sort_keys=True,
  default=str)}")` - a hash of the *input*, so the same input always gives
  the same output. That is the offline determinism you can rely on.
- `decisionarena/providers.py` - `OpenAICompatibleProvider.decide()` sends
  `"temperature": 0` in the request body - the temperature-zero setting,
  applied at the wire level.
- `runs/20261025-040448-mock.jsonl` - committed evidence with `repeat: 0`
  on every line, because that run used the default `--repeats 1`.

## Your turn

Write a new file `exercises/L63_determinism.py`. It must be runnable
offline, with no API keys and no network.

It must contain:

- a function `compare_repeats(case: dict, questions: dict, repeats: int) ->
  dict` that:
  - builds a `MockProvider` from `decisionarena.providers`
  - calls `provider.decide(case["state"], questions)` `repeats` times
  - serialises each answer dict to a string with `json.dumps(..., sort_keys=True)`
  - returns a dict with at least: `repeats`, `identical` (a boolean - were
    all the strings equal?), `distinct` (the number of distinct strings),
    and `answers` (the answer dict from the first call)
- a `main()` that:
  - loads a real case from `cases/routing.json` using
  `decisionarena.harness.load_cases`
  - runs `compare_repeats` on that case with `repeats=3`
  - prints the case id, the `distinct` count, and one line per question
    showing the `noul` probability from each repeat, so you can see for
    yourself whether they move
  - asserts that `distinct == 1` for the mock, and fails loudly if not

Inputs: the cases in `cases/routing.json`, `repeats=3`. Expected output:
three lines of per-question probabilities that are identical to each other,
and `distinct == 1`.

**Hint:** the comparison has to be on a *canonical string*, not on the dict,
because two dicts with the same keys in a different order are the same
answer but not the same string. Sorting the keys before serialising is what
makes the comparison fair.

**Then extend it** (same file, one more function): a function
`with_jitter(jitter: float, repeats: int) -> dict` that builds a
`MockProvider(jitter=jitter)` and reports the same fields. `MockProvider`
accepts a `jitter` argument in its constructor. Run it with `jitter=0.0` and
then with a non-zero jitter, and compare.

Here is a real trap, and finding it is part of the exercise: the mock's
constructor *stores* `jitter`, but `MockProvider.decide()` in
`decisionarena/providers.py` never reads it. The probability comes from a
SHA-256 hash of the seed, the question id and the state, so the mock stays
byte-identical no matter what you pass for `jitter`. If your `distinct`
count stays at 1 for a large jitter, that is not a bug in your code - it is
the mock telling you, truthfully, that it has no randomness to give. Read
`decide()` and confirm it yourself.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. Name three things that break determinism. For each one, say whether
   temperature 0 would fix it.
2. Your model is 3% non-deterministic. Why can it not be certified to a
   threshold? What would you have to measure to know the size of the problem?
3. The mock is 100% deterministic. Why does that not tell you anything about
   Jev or Clef?

## Artifact

Write `docs/notes/L63-determinism.md` - under 200 words, for a reader who
has never heard of this repo. It must contain:

- the three things that break determinism, one line each
- your own `distinct` count for the mock at `repeats=3`
- one sentence: what would you have to do to measure this on a real provider,
  and what would it cost?

Then commit it. The artifact is the proof you understood the measurement,
not the proof you ran the code.
