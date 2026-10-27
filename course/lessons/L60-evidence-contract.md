---
id: L60
phase: 6
title: "The evidence contract - raw calls before conclusions"
minutes: 35
concepts: [evidence-contract, jsonl, provenance, reproducibility]
prereqs: [L42]
paths: [beginner, provider-live]
exercise_file: decisionarena/harness.py
quiz: L60
---

# L60 - The evidence contract: raw calls before conclusions

## Why this matters

Every vendor in this field publishes a table where their model wins. Two of
those tables, put side by side, disagree. This repo exists so a third party
can run the comparison themselves - and the only reason that is possible is
that the harness writes down **what actually happened**, not just what it
concluded. If you skip that, you are not measuring models, you are writing
marketing with extra steps.

## The naive story

Picture a science-fair project. You run your experiment, get a number, write
it on a poster: "our robot is 94% accurate." Your friend asks, "can I see the
robot?" and you point at the poster. That is the failure mode this whole repo
is built against.

The fix is old and boring: **keep the raw notes**. Every observation goes in
a notebook, in the order it happened, with the date on it. The number on the
poster is a *summary* you compute from the notebook - never the other way
round. If your friend wants to check, they read the notebook.

That is the entire idea. Everything else in this lesson is the mechanics.

## What breaks

**Break 1 - the summary cannot be re-derived.** You wrote "accuracy 0.94"
in a Markdown file, then edited the case file, then edited the metric
formula. Now the number on the poster describes a battery that no longer
exists. Nobody - including you - can tell what the number meant. The
summary outlived the evidence.

**Break 2 - the evidence is not identifiable.** Suppose you ran three
batteries in an afternoon. Which one produced the number you are quoting?
Without a **run id** stamped on every record and on the summary, you are
guessing. And guessing is how the two disagreeing vendor tables happened.

**Break 3 - the case file drifted.** You edited `cases/routing.json` after
the run to "fix" a typo in a question. The old run's numbers were measured
against the *old* questions. Now the run file and the case file disagree, and
there is no way to tell which questions produced which answers - unless the
run recorded a **fingerprint** of the case file at the time of the run.

## The real thing

**The evidence contract** has three parts, and the order matters:

1. **Raw first.** Every call to a provider is written to
   `runs/<run-id>.jsonl` with the provider's own output, the latency, the
   token usage, the cost, and the error field (if any). JSONL means *JSON
   Lines*: one JSON object per line, so a file with 12 calls has 12 lines
   and you can read one call with a text editor without parsing the rest.
2. **Then meta.** A sibling file `runs/<run-id>.meta.json` records *about*
   the run: the run id, the provider name, the price per million tokens, the
   number of cases, the number of repeats, the **battery hash**, the start
   and finish timestamps, the total cost, the spend cap, and a uuid.
3. **Then the report.** The human-readable Markdown is *derived* from the
   raw file. If you want to change a number, you change the metric code and
   re-derive. You never edit a report by hand, and you never type a number
   into a report that did not come out of the raw file.

**Why the run id?** It is a label that ties the three files together and
appears inside every JSONL line too, so a single line can be traced back to
the run that produced it even if the file gets copied. In this repo the
pattern is `<YYYYMMDD>-<HHMMSS>-<label>` - for example
`20261025-040448-mock` and `20261025-040448-friction-mock`.

**Why the battery hash?** `battery_hash()` in `decisionarena/harness.py`
takes the list of cases, serialises it with `json.dumps(..., sort_keys=True)`,
hashes it with SHA-256 and keeps the first 12 hex characters. It is a
**fingerprint**: if the case file changes in any way, the hash changes. So
the hash in `meta.json` tells a reader "these numbers were measured against
*exactly this* set of cases". Two runs with the same hash were run against
the same questions; two runs with different hashes were not, and comparing
them is comparing apples to oranges. This is the fix for Break 3.

**Why is the raw file the thing that is committed?** Because a raw file is
**checkable**. The report says "accuracy 92%"; the raw file has the actual
probability on every question; a reader can recompute the accuracy by hand
and see whether the report is telling the truth. A number with no raw file
behind it is a claim, not a measurement. This repo's rule is blunt: *a
number without its raw `runs/*.jsonl` behind it is marketing.*

**Provenance** is the umbrella word for "where did this come from": which
provider, which model version, which cases, when, at what price. `meta.json`
is the provenance record; the JSONL lines are the observations.

**Reproducibility** is the ability to get the same answer again. It needs
two things: the raw file (so you can check without re-running) and the
fingerprint (so you know the inputs were the same). Determinism - whether
the *model* repeats itself - is a separate question, and it is lesson L63.

## In this repo

- `decisionarena/harness.py` - `run_battery()` is the runner. It builds one
  `rec` dict per call, appends it to `records`, and at the end writes
  `records` to `runs/<run_id>.jsonl` and `meta` to
  `runs/<run_id>.meta.json`. The JSONL write happens **before** the CLI ever
  calls the report writer.
- `decisionarena/harness.py` - `battery_hash(cases)` produces the 12-char
  fingerprint stored in `meta["battery_hash"]`.
- `decisionarena/harness.py` - `load_cases(path)` reads the battery file, so
  the hash is computed from exactly the cases that were run.
- `decisionarena/report.py` - `run_report(result)` only *formats* what the
  runner already produced. There is no measurement in `report.py`; if you
  want to change a number you change `metrics.py`.
- `decisionarena/cli.py` - `cmd_run()` calls `harness.run_battery(...)`,
  prints the report, and writes `runs/<run_id>.md` next to the raw files.
- `runs/20261025-040448-mock.meta.json` - a real meta file: `run_id
  "20261025-040448-mock"`, `provider "mock"`, `battery_hash
  "fd9fb7c25685"`, `cost_usd 3.28e-05`, `spend_cap_usd 0.25`.
- `runs/20261025-040448-mock.jsonl` - the raw file from that run id. Each
  line carries `run_id`, `case_id`, `group`, `case_class`, `repeat`, `ts`,
  `latency_s`, `usage`, `cost_usd`, `error`, `answers` and `gold`. Note
  that the run id is a timestamp to the second, so two runs launched in the
  same second can share an id - which is exactly why the **battery hash**,
  not the file name, is the authority on which cases a run covered.
- `AGENTS.md` - hard rule 3: "Evidence before claims. A number without its
  raw `runs/*.jsonl` behind it is marketing."

## Your turn

Edit `decisionarena/harness.py`. Add one thing, and add it in the right
place:

- In `run_battery()`, every JSONL line must also carry the **provider name**.
  Right now the provider name lives only in `meta.json`, so a single line
  copied out of the JSONL file has no way to say which model produced it.
  Add it to the record dict that `run_battery()` builds for each call, so
  every written line carries it.
- Do not change the file names, the meta keys, or the ordering of the
  existing fields. The contract is additive.
- Do not write a new function. This is one new key in one dict.

Inputs: nothing new - `run_battery()` already has the provider object.
Expected output: after `python -m decisionarena run --provider mock
--battery routing`, each line of `runs/<run_id>.jsonl` contains a provider
name that matches the `provider` field in the matching `<run_id>.meta.json`.
Check it yourself by opening both files.

**Hint:** the provider's name is already on the provider object that
`run_battery()` receives, and the JSONL line is just that one `rec` dict
written out. Add the key where the dict is built, not where it is written -
then the report and the raw file cannot drift apart.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. In your own words: what is the evidence contract, and which of the three
   files is the one you are not allowed to edit by hand?
2. A colleague sends you a number, "92.3% routing accuracy", and a run id.
   What three things do you check in `runs/` before you repeat that number
   anywhere?
3. Two runs of the same provider have different `battery_hash` values.
   What went wrong, and can their accuracies still be compared?

## Artifact

Write `docs/notes/L60-evidence-contract.md` - under 200 words, for a smart
friend who has never read this repo. It must contain:

- the three files a run produces, and which one is derived
- one sentence on what the battery hash protects you from
- the actual `battery_hash` value from a run you made yourself, with its
  run id

Then commit it. The artifact is the proof you understood the discipline, not
the proof you ran the code.
