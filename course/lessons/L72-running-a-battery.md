---
id: L72
phase: 7
title: "Running a battery end to end"
minutes: 40
concepts: [battery, runner, repeats, cli]
prereqs: [L70, L42]
paths: [beginner, provider-live]
exercise_file: decisionarena/cli.py
quiz: L72
---

# L72 - Running a battery end to end

## Why this matters

You have built a battery of cases. Now you have to actually run it, against a
real provider, and end up with evidence on disk that somebody else can
check. Between "here is a case file" and "here is a run file" there is a
whole command line, and the flags on it are the difference between a
$0.02 experiment and a $400 surprise. This lesson walks the real command
line, in order, and shows you exactly what lands on disk.

## The naive story

You run the model on your cases and print the answers. You eyeball them.
They look right. You write down "accuracy 90%" in a document.

You have just produced the one thing this repo exists to destroy: a number
with no evidence behind it. The harness exists so that "accuracy 90%" is
never a thing you type - it is always a thing you *derive* from a file
somebody else can open and recompute.

## What breaks

**Break 1 - running without checking what is configured.** If your API key
is missing, the provider raises, the run continues, and you get a report
full of errors and a zero. The first command to run is always
`providers` - it tells you what this machine can actually talk to.

**Break 2 - spending real money by accident.** A provider call costs money.
A battery of 100 cases at 3 repeats is 300 calls. `run_battery()` protects
you with a **spend cap**: it checks the running total *before* each call and
aborts the run when the cap is reached. But a cap you set too high is no
protection, and a cap you forget to set is the default - $0.25.

**Break 3 - one repeat is not evidence of stability.** A single call per case
gives you one number per case, and you cannot tell a stable 90% from a
lucky 90%. `--repeats` runs each case several times so you can compare -
which is how the determinism section of the report gets anything to say.

**Break 4 - a dry run that calls anyway.** `--dry-run` must print what
*would* happen and make **no calls and no files**. If your dry run spends
money, you have a bug in your CLI, not a convenience.

## The real thing

**A battery** is a named set of cases. This repo has three: `routing`
(5 labelled tickets), `injection` (3 adversarial states), `format` (3
contents in 3 serialisations each). `cli.py` keeps the mapping in one dict,
`BATTERIES`, so the name you type on the command line and the file the
runner opens cannot drift apart.

**A runner** is the loop that calls the provider over every case, records
what came back, and stops when it is told to. Here that is
`harness.run_battery()`.

**Repeats** are additional calls of the *same* case, recorded as extra JSONL
lines with an incrementing `repeat` field.

**The CLI** is `python -m decisionarena`, with four subcommands: `providers`,
`run`, `friction`, `swap`.

Here is the whole sequence, in the order you should actually do it.

**Step 1 - what is configured on this machine?**

```
python -m decisionarena providers
```

This calls `providers.available_providers()` and prints a table of
`spec / configured / note`. `mock` is always `yes`; `jev` is `yes` only if
`TYPESAFE_API_KEY` is set; `clef:clef-flash` needs
`CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_AUTH_TOKEN`; `oai` needs
`OPENAI_BASE_URL` and `OPENAI_API_KEY`. The command prints the env var names
to set. It makes no calls and costs nothing.

**Step 2 - see what you are about to run, without running it.**

```
python -m decisionarena run --provider mock --battery routing --dry-run
```

`cmd_run()` prints `provider`, `battery`, `price`, then
`DRY RUN - no calls will be made` and one line per case: the case id, its
`class`, and its question ids. Then it returns. No calls, no cost, no files.
Use this every time you change a battery.

**Step 3 - the real thing, offline first.**

```
python -m decisionarena run --provider mock --battery routing --repeats 3
```

`cmd_run()` calls `harness.run_battery(provider, cases, repeats=3,
spend_cap=args.spend_cap, out_dir=args.out_dir)`, then
`report.run_report(result)`, prints it, and writes
`runs/<run_id>.md`. The run writes three files, all named with the same run
id:

- `runs/<run_id>.jsonl` - the raw evidence. One line per call. With
  `--repeats 3` and 5 cases, 15 lines. Each line has `run_id`, `case_id`,
  `group`, `case_class`, `repeat` (0, 1, 2), `ts`, `latency_s`, `usage`,
  `cost_usd`, `error`, `answers` and `gold`.
- `runs/<run_id>.meta.json` - the provenance: `run_id`, `provider`,
  `price_per_mtok`, `cases`, `repeats`, `battery_hash`, `dry_run`,
  `started_at`, `finished_at`, `duration_s`, `cost_usd`, `spend_cap_usd`,
  `uuid`.
- `runs/<run_id>.md` - the report, derived from the two files above.

A real committed example: `runs/20261025-040448-mock.meta.json` has
`"run_id": "20261025-040448-mock"`, `"battery_hash": "fd9fb7c25685"`,
`"cases": 5`, `"repeats": 1`, `"cost_usd": 3.28e-05`,
`"spend_cap_usd": 0.25`.

**Step 4 - two providers, one battery.** The swap command is the whole point
of the repo - the same battery, two models, compared.

```
python -m decisionarena swap --provider a=jev --provider b=clef:clef-flash
```

`cmd_swap()` parses `label=spec` (so `a=jev` means "call this one a"), runs
both providers over the same cases, then computes three things:
`metrics.label_agreement()` (do they pick the same label?),
`metrics.probability_gap()` (how far apart are the probabilities?) and
`metrics.action_change_rate()` (at your thresholds, does the *action*
change?). The last one is the one that matters for a product: two models can
agree on the label and still disagree about whether to act. The output goes
to `runs/swap-report.md`.

**The money flags.**

- `--spend-cap` (default `0.25`) - the maximum USD the run may spend.
  `run_battery()` checks the running cost *before* each call and breaks out
  of both loops with `aborted=True` and a reason. The report then prints an
  `ABORTED` line. Set it deliberately, not by default.
- `--dry-run` - print the plan, make no calls, write no files. Free.

**The honest rule about the mock.** `python -m decisionarena run --provider
mock ...` proves the *harness* works end to end: the files land, the report
renders, the metrics compute. It says **nothing** about any model. The
report writer knows this - `run_report()` checks `result.provider.startswith
("mock")` and puts a banner at the top saying the run is simulated and must
never be quoted as evidence.

## In this repo

- `decisionarena/cli.py` - `main()` builds the `argparse` parser: the
  `providers`, `run`, `friction` and `swap` subcommands, each with
  `set_defaults(func=...)`. The `run` subcommand's flags are `--provider`,
  `--battery`, `--repeats`, `--spend-cap`, `--out-dir`, `--dry-run`.
- `decisionarena/cli.py` - `BATTERIES` maps `routing`, `injection`, `format`
  and `all` to files; `_load_battery(name)` loads them with
  `harness.load_cases()`.
- `decisionarena/cli.py` - `cmd_run()` is the whole run flow: build the
  provider, load the battery, print the header, handle `--dry-run`, call
  `harness.run_battery()`, call `report.run_report()`, write the `.md`, and
  print the path to the raw evidence.
- `decisionarena/cli.py` - `cmd_swap()` parses the two `label=spec` values,
  runs both providers, and builds the matrix of agreement / gap /
  action-change.
- `decisionarena/harness.py` - `run_battery()` has the spend cap check
  (`if cost >= spend_cap`) and the `aborted` / `abort_reason` fields on
  `RunResult`.
- `decisionarena/harness.py` - `RunResult` is the object the CLI passes
  around: `provider`, `started_at`, `finished_at`, `meta`, `records`,
  `scores`, `cost_total`, `aborted`, `abort_reason`.
- `decisionarena/providers.py` - `build_provider(spec)` turns `jev`,
  `clef:clef-flash`, `mock` or `oai` into a provider object;
  `available_providers()` powers the `providers` command.
- `decisionarena/report.py` - `run_report(result)` is the report writer; the
  `## Determinism` section only appears when a case was run more than once.

## Your turn

Edit `decisionarena/cli.py` and add one thing:

- Add a **new subcommand** called `runs` that lists the run files in the
  output directory, newest last, with the run id, the provider and the cost
  from the matching `<run_id>.meta.json`. It must read the `.meta.json` files
  from `--out-dir` (default `runs`) and print one line per run. Do not
  modify `providers`, `run`, `friction` or `swap`.
- Register it in `main()`'s parser the same way the others are registered,
  with `set_defaults(func=...)`, and give it an `--out-dir` flag defaulting
  to `runs`.
- It must make **no provider calls** and cost nothing.

Inputs: the `.meta.json` files already in `runs/`. Expected output: one line
per committed run, showing the run id, the provider and the cost in USD.
After you add it, `python -m decisionarena runs` should list the runs that
are already on disk.

**Hint:** you already have everything you need in this file - the `providers`
command shows you the pattern for a command that only prints, and the `run`
command shows you how `--out-dir` is read. The one new thing you need is
the JSON file read; `json` is already imported at the top of `cli.py`.

**Do not** add a `--provider` flag to your new command. It must not be able
to call anything.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. Name the three files a run writes, and say which one you would open to
   check whether a specific case was answered correctly.
2. What does `--spend-cap 0.25` actually do, and what happens to the rest of
   the battery when it is hit?
3. You ran `python -m decisionarena run --provider mock --battery routing`
   and the report says "accuracy 40%". What have you learned, and what have
   you *not* learned?

## Artifact

Write `docs/notes/L72-running-a-battery.md` - under 250 words, for a reader
who has never run a harness. It must contain:

- the three commands, in order, with what each one tells you
- the three files a run writes and what is in each
- the actual `battery_hash` and `cost_usd` from one run you made yourself,
  with its run id
- one sentence: what `--dry-run` is for, and why it must never cost money

Then commit it. The artifact is the proof you can run the harness, not the
proof you ran it once.
