---
id: L73
phase: 7
title: "Reading the report - and not over-reading it"
minutes: 35
concepts: [report, metric-reading, interpretation, uncertainty]
prereqs: [L72, L52]
paths: [beginner, provider-live]
exercise_file: decisionarena/report.py
quiz: L73
---

# L73 - Reading the report - and not over-reading it

## Why this matters

The report is the part people quote. It is a tidy Markdown file with a
headline table, and it is the easiest thing in this repo to over-read. Two
run reports in this repo can look completely different and be equally
uninformative - one because it measured five easy cases, one because it
measured the mock. A report tells you what happened. Deciding what it
*means* is a separate, harder job, and this lesson is about the gap.

## The naive story

The report has a table: accuracy 92.0%, mean ECE 0.08, mean Brier 0.11. So
the model is good: high accuracy, low calibration error. Ship it.

But look at that table again. How many cases were behind the 92%? Which
cases? Were they the easy ones? Was it the mock? Was the number 92.0%
because it was 92.0%, or because it was 91.67% rounded? Nobody checked,
because the table is right there and the table looks authoritative.

## What breaks

**Break 1 - the number has no run file behind it.** The report is a
*derived* document. It is `report.run_report(result)` formatting what the
runner already produced. It can be wrong in two ways: the underlying data
was wrong, or the formatting lied. Either way, the only way to know is to
open the raw JSONL and check. A report you cannot regenerate from raw data
is marketing. This repo's rule 3 is exactly this: *a number without its raw
`runs/*.jsonl` behind it is marketing.*

**Break 2 - a mean over five cases has a huge confidence interval.** This is
the one that catches everybody. If a model gets 5 cases right, that is 100%.
Get 4 right, that is 80%. Those are two outcomes from a set of five. Now
imagine a different model getting 3 right - 60%. Is 80% better than 60%?
You cannot tell. The difference is one case. One case could be a coin flip
on a borderline ticket. A mean over a small n is not a measurement of
quality; it is a measurement of *how many small cells you had*. The
`scored cases` row in the headline table tells you the n. Read it first.

**Break 3 - the mock's numbers look exactly like a real model's.** The mock
produces a report with the same tables, the same columns, the same
percentages. If you read only the numbers, you cannot tell. That is why
`run_report()` puts a banner at the top of every mock report: *"SIMULATED
RUN - `mock` provider ... must never be quoted as evidence."* The banner is
not decoration - it is the difference between a harness test and a claim.

**Break 4 - the metrics measure different things and you will mix them
up.** Accuracy asks: did it pick the right answer? Brier asks: how far was
the stated probability from the truth? ECE asks: when it says 0.8, is it
right 80% of the time? A model can have great accuracy and terrible
calibration - it gets the right answers while stating sloppy probabilities.
Which one you care about depends on what the probability is *for*: if 0.6
is your auto-route threshold, calibration is the metric that matters,
because it is about the number near the threshold.

## The story

A report is a summary of somebody else's reading of a pile of numbers.
It arrives looking authoritative, with a headline table and percentages that
line up in neat columns. It is the easiest document in the repo to over-read.

So read it in a fixed order, like a customs officer.

First the banner. If it says the run was simulated, stop. You have learned
that the machinery works. You have learned nothing about any model.

Then find the denominator before you find the number. The report says
"accuracy 80.0%" and you find "scored cases: 5" underneath. Now the 80%
means four out of five. Another model got three out of five. Those differ by
one ticket - and one borderline ticket is close to a coin flip. The
percentage's precision was hiding that.

Then the fingerprint. Two reports from two different batteries were asked
different questions, so their accuracies are not comparable.

Then the metrics, each read as "over N cases". Accuracy asks whether the top
answer was right. Calibration asks whether when it says 0.8 it is right 80%
of the time. If 0.6 is your auto-route line, calibration decides the work.

And the last question is not in the report: what would you do differently if
the number were three points higher?

## The real thing

**A report** in this repo is a derived, human-readable view of a run. It
has no authority over the raw file. It is a convenience for reading, and a
convenience can be wrong.

**Reading a report, in order.** Here is the discipline, applied to the
actual sections `run_report()` emits:

1. **Is this a simulated run?** Read the banner first. If it says `mock`,
   stop. You learn that the harness works. You learn nothing about models.
2. **How many cases?** `scored cases` in the headline table. If it is 5,
   treat every number in the report as a rough description of those 5
   cases. This is the step people skip, and it is the step that stops you
   from over-reading.
3. **The battery hash.** The header line prints
   `battery hash: <12 chars>`. Two reports with different hashes were run
   against different questions and their accuracies are not comparable.
   If you cannot find a matching `battery_hash` in the `meta.json` of a run
   file, you are reading a report with no evidence behind it.
4. **The headline table.** `accuracy`, `mean ECE`, `mean Brier`. Read each
   as "over N scored cases", and remember the n. `mean ECE` is `n/a` when
   there were no labelled outcomes - and `n/a` is information: it means the
   battery could not score that run.
5. **Latency.** p50 / p95 / max over the calls. p95 is the number a user
   feels; the max is the number that pages you.
6. **Errors.** If the errors table is not empty, every accuracy number
   above is computed over a *survivor* set. The cases that failed are not
   random - they are usually the hardest ones.
7. **By group.** The per-group accuracy table. This is where `class` and
   `group` pay off: a model can look fine overall and be terrible on one
   slice.
8. **Determinism.** Only present when a case ran more than once.
   `**stable/total** cases returned byte-identical answers across repeats`.
   If it is not all of them, every average in the report has noise baked in.

**Uncertainty** is not a vibe; it is a number you can compute. With `n`
scored cases and accuracy `a`, a rough standard error is
`sqrt(a * (1 - a) / n)`. At `a = 0.8`, `n = 5`: `sqrt(0.8*0.2/5) =
sqrt(0.032) â‰ˆ 0.18`. So the accuracy is 80% Â± 18% at one standard
deviation - a 95% range that runs roughly from 44% to 96%. The honest
statement is not "this model scores 80%"; it is "this model scored 4 of 5
cases, which is not enough to tell it apart from a model that scored 3".

You do not need a statistics course to make this point. You need the
denominator. **Always read the n before the number.**

**Interpretation** is the last step, and it is not the harness's job. The
harness produces numbers. Interpretation is: what decision would I make
differently if this number were 3 points higher? If the answer is "none",
you do not need more precision - and if the answer is "I would ship it",
you need to know the n before you believe it.

**And the rule that ties it together.** `report.py` contains no measurement.
All the measurement is in `metrics.py`; `report.py` only formats. So when
you want to change a number, you change `metrics.py` and re-derive. A
report that disagrees with its own metrics is a bug in the formatting - and
the fastest way to find out is to recompute one number by hand from the raw
JSONL.

## In this repo

- `decisionarena/report.py` - `run_report(result)` is the whole report
  writer. Its first act is the mock check:
  `if result.provider.startswith("mock")` it prepends the SIMULATED RUN
  banner. It then prints the header (run id, timestamps, battery hash, cost),
  the `## Headline` table, `## Latency`, `## Errors`, `## By group` and
  `## Determinism`.
- `decisionarena/report.py` - the Determinism section groups
  `result.records` by `case_id`, compares
  `json.dumps(r["answers"], sort_keys=True)` across repeats, and prints
  `**{stable}/{len(det)}** cases returned byte-identical answers across
  repeats`.
- `decisionarena/report.py` - `friction_report(report)` renders the
  format-friction table with the `flips@0.5` column, and `swap_report(matrix)`
  renders the swap-safety table with `action change rate at threshold`.
- `decisionarena/metrics.py` - `aggregate(case_scores)` produces the
  headline: `cases`, `scored_cases`, `accuracy`, `mean_ece`, `mean_brier`.
  `scored_cases` is your n.
- `decisionarena/metrics.py` - `score_case()` returns `accuracy`, `brier`,
  `ece` per case, all `None` when there are no gold labels.
- `decisionarena/harness.py` - `run_battery()` returns a `RunResult` whose
  `records` list is the raw evidence the report was derived from. If you
  want to check a number, `result.records` is where you check it.
- `runs/20261025-040448-mock.md` - a real mock report, with the SIMULATED
  RUN banner at the top and `scored cases 5` in the headline table. That
  report is a **harness test**, and it is committed as evidence of exactly
  that and nothing else.
- `runs/20261027-212313-friction-mock.md` - the friction report: `cases 3`,
  `questions measured 9`, `mean spread 0.42`, `max spread 0.9271`, and
  `questions whose side of 0.5 flips across formats: 4`.
- `AGENTS.md` - hard rule 4: "The mock is not evidence. `MockProvider` is an
  offline simulator for testing the harness. Its numbers must never be
  published as a model evaluation."

## Your turn

Edit `decisionarena/report.py` and add **one** thing:

- Add a function `evidence_pointer(result, out_dir: str = "runs") -> str` that
  returns a short string naming the raw file that the given run came from -
  the path of the `<run_id>.jsonl` in `out_dir` - so that any reader of a
  report is told where the underlying evidence lives. Derive the run id
  from the `result` you are given (`result.meta["run_id"]`).
- Then call it from `run_report(result)` and include the returned string in
  the report's header, so the pointer appears in the `.md` file.
- Do not change any existing number, table or section.

Inputs: a `RunResult` - the object `harness.run_battery()` returns.
Expected output: a string containing the run id and the path to the
`<run_id>.jsonl` file; and after your change, `python -m decisionarena run
--provider mock --battery routing` prints a report whose header contains
that pointer.

**Hint:** `run_battery()` already decided where to write the evidence - it
took `out_dir` as an argument and used it for both the `.jsonl` and the
`.meta.json`, and the default it uses is `runs`. The run id you need is in
`result.meta`. You do not need to recompute anything; you need to name a
file that already exists - so give `out_dir` a default value rather than
requiring the caller to supply it.

**Then, in your artifact, do the human part:** pick one number from a
report you produced and recompute it by hand from the raw JSONL - the mean
accuracy over the scored cases, for example. If your hand calculation does
not match the report, you have found something worth fixing.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. Why is the report never the source of truth in this repo, and what is?
2. A report says "accuracy 80.0%" over 5 scored cases. What is the honest
   sentence you would write instead, and why?
3. The mock's report has a banner the real providers' reports do not. What
   is that banner protecting you from?

## Artifact

Write `docs/notes/L73-reading-the-report.md` - under 250 words, for a reader
who has never seen a benchmark report. It must contain:

- the four checks you do, in order, before you believe any number
- one number you recomputed by hand from a raw JSONL file, and whether it
  matched the report
- one sentence on why the mock's numbers are not evidence
- one sentence: what you would need to collect before you could make a
  product decision from a report

Then commit it. The artifact is the proof you can read a report without
over-reading it.
