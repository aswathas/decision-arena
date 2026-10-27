---
id: L91
phase: 9
title: "Running the experiment at scale"
minutes: 40
concepts: [experiment-design, repeats, sampling, spend-cap]
prereqs: [L90, L72]
paths: [beginner, provider-live]
exercise_file: exercises/L91_experiment.py
quiz: L91
---

# L91 - Running the experiment at scale

## Why this matters

One number from one call is an anecdote. A finding is a number you can
defend, and defending it means showing that it survives the obvious attacks:
what if that call was luck? What if the cost was more than you thought? What
if you only knew what to look for because you had already seen it? This
lesson is the discipline of running the experiment properly - and it is also
the lesson where the offline mock finally teaches you something, by showing
you exactly what it *cannot* show you.

## The naive story

You wrote the hypothesis. You run the battery once. The report comes back
with a mean spread and a flips count, and you write the finding.

The gap between that and a finding is enormous, and the gap is made of three
small things you did not do: you did not **repeat** the calls, so you cannot
separate signal from noise; you did not **pre-register** what you would
compute, so you may have chosen the metric that flattered the result; and
you did not put a **cap** on the spend, so you cannot promise a reader what
it costs.

## What breaks

**Break 1 - one call per case cannot tell you what is noise.** Suppose the
true effect of a format change on a question is 0.10, and the model's own
jitter is 0.05. Run it once and you see 0.10. Run it once and you see 0.02.
Both look like "the effect is small". The difference is not the effect - it is
the luck of that particular call. **Repeats** are how you find out: the
`--repeats` flag makes the runner call the same case several times and write
one JSONL line per call, each with its own `repeat` index. The independent
harness measured this on real models: Clef repeats **byte-identical**, while
Jev's labels were stable but its probabilities jitted by about **0.01-0.05**.
That 0.05 jitter is exactly the size of effect your experiment needs to
survive.

**Break 2 - the metric gets chosen after the number appears.** You run the
battery, look at the results, and then decide whether to report the mean
spread or the flips count. Sometimes both tell the same story. Sometimes they
do not - and when they do not, the one you publish is the one you liked. The
fix is to write down the metric names *before* the run, in a file, and to
compare your results against that file afterwards. If they do not match, that
is a finding too: either the experiment changed under you, or you changed.

**Break 3 - the spend cap is set too high to protect anything.** The cap is
checked *before* each call, so a cap of $0.25 on a $0.001 experiment never
fires - which is the point - but a cap of $50 on the same experiment is not
protection, it is a comment. Set the cap from the plan, not from your
optimism. And remember the exact behaviour from lesson L42: the cap is
checked before the *next* call, so a run that aborts can still finish a
little over the cap.

**Break 4 - "the same call twice" is not the same as "the same question
twice".** Repeats give you the model's variability on a fixed input. They do
**not** give you the variability of your *case set* - five cases is five
cases, however many times you repeat them. A finding that says "on 5 cases
the model was 92% accurate" has a denominator of 5 no matter how many
repeats you ran. Repeats fix one half of the noise problem; the size of your
case set fixes the other.

**Break 5 - you ran the mock and called it a result.** The offline
`MockProvider` is deterministic by construction: its probabilities come from
a SHA-256 hash of the seed, the question id and the state, so repeats are
byte-identical. And its `FORMAT_SHIFT` of `{"prose": 0.0, "flat": -0.04,
"nested": -0.81}` is **designed in** to imitate the published finding. So an
offline friction run gives you a big spread and some flips, and those numbers
say one thing only: the harness works. They are not a measurement of any
model. This is the single most common way a good experiment gets wasted.

## The story

Picture a laboratory bench with a sensitive balance. The balance reads
fine most of the time - but it is not perfect. Tap the bench and the needle
moves a little. That movement is not a measurement of anything; it is the
instrument being an instrument.

Now you want to know whether a change of 0.10 in a probability is real. But
the balance itself wanders by up to about 0.05. So a movement of 0.03 might
be the effect, or it might be the bench being tapped. So you take the same
reading again and again, and the spread of those repeats is your noise floor.

That is what repeats buy. One provider's repeats came back byte-identical,
so for that provider the floor is nothing. Another provider's probabilities jitted by about 0.05, so
on that one an effect of 0.10 is visible but 0.02 is not.

So before you start, write down which numbers you will compute and what
result would kill the hypothesis, in a file. Afterwards, check what you
computed against the file. If they do not match, you have found a bug - and
you found it before publishing, which is the only time finding it is worth
anything.

## The real thing

**Experiment design** for this repo has four decisions, in this order:
what you measure (the hypothesis note), what you compute (the metric names,
pre-registered), how many times you call (repeats), and how much you are
willing to spend (the cap).

**Sampling** here has two layers, and you need both:

- **Repeats** (the same input, many calls) - this is what tells you whether
  the model's own jitter is bigger than your effect. `run_battery()` loops
  `for rep in range(repeats)`, so `--repeats 3` writes three JSONL lines per
  case with `repeat` values 0, 1, 2.
- **Case count** (the size of the battery) - this is what tells you whether
  your effect is a property of the world or of your five tickets. The
  independent harness's labelled accuracy is explicitly flagged **small-n**:
  24 author-labelled cases, Clef at 96%, Jev at 92% -> 83%. A swing of nine
  points on 24 cases is *reported as an observation*, not as a ranking.

**The pre-registration** is the cheapest tool in this lesson: a file, written
before the run, listing the metric names you will compute and the kill
criteria you will judge them against. After the run, you check that the
metrics you report are the metrics you wrote down. Two ways it pays off:

- if they match, a reader can trust that you did not go shopping;
- if they do not match, you have found a bug or a changed plan - and you find
  out *before* publishing, not after.

**The spend cap** is `harness.run_battery(..., spend_cap=0.25)` by default,
exposed as `--spend-cap` on the CLI. The check happens at the top of the
case-and-repeat loop:

```
if cost >= spend_cap:
    aborted, reason = True, f"spend cap ${spend_cap} reached"
    break
```

When it fires, `RunResult.aborted` is True, `RunResult.abort_reason` carries
the message, the report prints `- [!] **ABORTED**: <reason>`, and the run
still writes everything it collected. A capped run is not a failed run - it
is a bounded one, and the evidence up to the cap is still evidence.

**Recording every raw call** is the non-negotiable part. `run_battery()`
appends one record per call to `records` and writes them to
`runs/<run_id>.jsonl`, each line carrying `run_id`, `case_id`, `group`,
`case_class`, `repeat`, `ts`, `latency_s`, `usage`, `cost_usd`, `error`,
`answers` and `gold`. Nothing is summarised away: if a call failed, the
failure is in the file with its error string, and the report's Errors section
tells you that every accuracy above it was computed over a *survivor* set.

**The order of operations, which is the actual lesson:**

1. write the hypothesis note (L90) - claim, delta, kill criteria;
2. compute the plan: cases x formats x repeats = calls; tokens per call from
   a real run; price per Mtok from the code; dollars;
3. set the cap from the plan, with headroom;
4. **pre-register** the metric names and the kill criteria to a file;
5. run it, with `--repeats 3` or more, cap set, `--dry-run` first;
6. summarise the **raw records**, not the report - so you can recompute;
7. check the summary against the pre-registration;
8. judge the kill criteria, one by one, against the numbers.

And the honest last step: **a null result is a result.** If the mean spread
is 0.01 and nothing flips, your hypothesis died and you write it up as a
null - "on our 20 production-shaped tickets, the state shape did not move the
decision". That sentence is worth more than a positive result you cannot
defend, because it saves the next person from running it again.

## In this repo

- `decisionarena/harness.py` - `run_battery(provider, cases, repeats=1,
  spend_cap=0.25, dry_run=False, out_dir="runs", label="")`: the loop is
  `for case in cases:` then `for rep in range(repeats):`, with the cap check
  first and `provider.decide(case["state"], case["questions"])` inside a
  `try` that records the failure instead of dying.
- `decisionarena/harness.py` - `RunResult` carries `records` (the raw
  evidence), `scores`, `cost_total`, `aborted` and `abort_reason`. The raw
  records are what you summarise.
- `decisionarena/harness.py` - `run_format_friction(provider, cases,
  formats=("prose", "flat", "nested"), out_dir="runs")`: the no-labels
  experiment. It writes `runs/<run_id>.json` with `values` per format,
  `spread` and `flips_at_0.5` per question, and a top-level `mean_spread`,
  `max_spread` and `flips_at_0.5`. Note that it has **no repeats parameter
  and no spend cap** - which is why a careful experiment on the format axis
  uses `run_battery()` over an expanded case list instead.
- `decisionarena/harness.py` - `FORMAT_BUILDERS` maps `"prose"`, `"flat"` and
  `"nested"` to one-argument lambdas over a `variants` dict; and
  `battery_hash(cases)` gives the fingerprint to quote.
- `decisionarena/providers.py` - `MockProvider.decide()` hashes
  `f"{self.seed}|{qid}|{json.dumps(state, sort_keys=True, default=str)}"`,
  so it is byte-identical across repeats; and `MockProvider.FORMAT_SHIFT` is
  `{"prose": 0.0, "flat": -0.04, "nested": -0.81}`, the designed-in shift.
- `decisionarena/cli.py` - the `run` subcommand's `--repeats` (default 1) and
  `--spend-cap` (default 0.25); `--dry-run` prints the plan and calls
  nothing.
- `decisionarena/report.py` - `run_report()`'s `## Determinism` section
  reports "**N/M** cases returned byte-identical answers across repeats",
  which is the number that tells you whether your effect is bigger than the
  model's jitter.
- `cases/format_variants.json` - the three contents with their `variants`
  dicts and no `gold`.
- `runs/20261025-040448-friction-mock.json` - a committed friction report:
  `mean_spread 0.42`, `max_spread 0.9271`, `flips_at_0.5: 4`. It is the
  harness's proof of life, and the mock banner in the matching `.md` is the
  reason it is not a finding.
- `AI-CONTEXT.md` - `verified_facts` shows the shape of a recorded fact:
  `claim`, `evidence`, `verified_on`.

## Your turn

Write a file `exercises/L91_experiment.py`. It must run **offline**, with no
API key and no network, using the mock provider.

It must contain:

- a function `plan(n_cases: int, formats: int, repeats: int,
  price_per_mtok: float, tokens_per_call: int, spend_cap: float) -> dict`
  that returns the number of calls, the total input tokens, the cost in USD
  and whether the plan fits inside the cap
- a function `expand_variants(cases: list, formats: list) -> list` that turns
  the format-variant cases into ordinary runnable cases - one case per
  format, each with the state that format's builder produces, and an id that
  says which format it is. Use the harness's own builders rather than
  reinventing them
- a function `pre_register(path: str, metrics: list, kill_criteria: list) ->
  str` that writes a JSON file containing the metric names you will compute
  and the kill criteria you will judge them against - **before** the run
- a function `summarise(result) -> dict` that works from the **raw records**
  of a `RunResult` and returns, per question id: the number of records, the
  mean, the minimum and the maximum of the value across repeats, and whether
  any record fell on a different side of 0.5 from the first one
- a `main()` that:
  - loads `cases/format_variants.json` with `harness.load_cases`
  - calls `plan()` for 3 formats, 3 repeats, the `clef-flash` price `0.038`,
    a token estimate of 160 per call and a cap of `0.25`, and **prints the
    plan before running anything**
  - calls `pre_register()` to write `runs/l91-exercise/pre-registration.json`
  - runs the expanded cases through `harness.run_battery()` with the mock
    provider, `repeats=3`, `spend_cap=0.25` and
    `out_dir="runs/l91-exercise"`
  - calls `summarise()` and prints the per-question table
  - prints a line comparing the metric names in the pre-registration file
    with the metric names your summary produced, and says whether they match
  - prints one line naming the number of records written
- a self-check section using `assert` that fails loudly if:
  - the planned cost does not fit inside the cap
  - the number of records written is not the number of cases times the
    formats times the repeats
  - the metric names in the pre-registration file are not the metric names
    your summary produced
  - the minimum and the maximum of any question are **not** equal to each
    other - because the mock is deterministic, so its repeats are
    byte-identical. This assertion is expected to **pass** offline, and it is
    exactly the assertion that would **fail** against a live provider whose
    probabilities jitter. That contrast is the point of the exercise

Inputs: `cases/format_variants.json`, the price `0.038`, `repeats=3`, a cap of
`0.25`, and the token estimate from one committed mock run.

Expected output: the plan, the pre-registration file, the per-question
summary table, the metrics-match line, the record count, and the four
assertions - with the last assertion passing, and its passing being the
honest offline finding.

**Hint:** the last assertion is the point of the exercise, not a bug in it.
Read `MockProvider.decide()` and work out where its numbers come from - the
answer is a hash of the *input*, so the same input can only ever give the
same output. That is why the offline experiment can validate your pipeline
but can never validate your effect size.

**Do not** treat the mock's numbers as a result about any model, in the
printed output or in the artifact.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. What does `--repeats 3` buy you that one call per case does not, and what
   does it *not* buy you?
2. Why write the pre-registration file before the run instead of afterwards?
3. Your plan says 180 calls at $0.038/Mtok and 160 tokens per call. What
   spend cap would you set, and why not $100?
4. The mock's friction spread is 0.42 with 4 flips. What does that number
   measure, and what would you have to run to turn it into a finding?

## Artifact

Write `docs/notes/L91-experiment.md` - under 300 words, for a reader who
wants to re-run your experiment. It must contain:

- the plan: cases, formats, repeats, calls, tokens, cost, cap
- the metric names you pre-registered, and the line saying whether they
  matched what you computed
- your repeat-variability finding (what happened to the min and max across
  repeats) and the one-sentence reason, taken from reading the provider code
- one sentence stating clearly what this offline run proved and what it
  cannot prove

Then commit it. The artifact is the proof that you can run an experiment
without getting ahead of yourself, not the proof that you got an answer.
