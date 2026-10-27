---
id: L93
phase: 9
title: "Publishing - evidence before claims"
minutes: 30
concepts: [publishing, evidence-contract, claim-status, review]
prereqs: [L92]
paths: [beginner, provider-live]
exercise_file: docs/notes/L93-publication.md
quiz: L93
---

# L93 - Publishing: evidence before claims

## Why this matters

This is the last lesson, and it is the one the repo exists for. Everything
before it - the harness, the batteries, the metrics, the hypothesis, the
experiment - exists so that this moment can be done in a way that survives
scrutiny. Publishing is not "posting the number". Publishing is handing
somebody the **repo, the command, the raw evidence and the one finding**,
and letting them check it.

The rule this repo is built around is one sentence long, and it is in
`AGENTS.md` as hard rule 3: *evidence before claims. A number without its raw
`runs/*.jsonl` behind it is marketing.*

## The naive story

You got a result. You write a post: "We tested X and found Y. Link to the
repo." Maybe you attach a screenshot of the report. The post is clear, the
number is bold, and the repository link is right there.

The naive story believes that a link is enough. It is not. A link invites a
reader to start at the front door of a repository, and if the front door is
the README of a project with 40 files and no indication of which run produced
the number, the reader will not find it, will not check it, and will
reasonably assume the number was produced for the post. **Marketing is not a
lie. It is a number that a reader cannot check.** The fix is not to be more
modest; it is to make checking easy.

## What breaks

**Break 1 - the evidence was not committed.** The run happened, the report
was printed, and then... the run files were never committed, because the
working tree was messy and the run ids looked like log spam. Now the number
in the post has no raw file behind it. This repo's `AI-CONTEXT.md` lists
`runs/*.jsonl — committed raw evidence, append-only` under `do_not_touch`
precisely because this is the failure that keeps happening.

**Break 2 - the reader cannot tell the mock from the model.** Every mock
report in this repo opens with the banner:

```
> [!] **SIMULATED RUN - `mock` provider.** These numbers come from an offline
> simulator that exists to test the harness. They are **not** a measurement of
> any real model and must never be quoted as evidence.
```

The banner exists because a mock report and a real report have the *same
tables*. If you publish a number without saying which kind of report it came
from, you have made a harness test look like a model evaluation - and that
breaks hard rule 4.

**Break 3 - the reader cannot reproduce the run.** The command is missing, or
it is wrong, or it needs a key you have not explained, or it costs $40 and
the reader closes the tab. A finding is only checkable if the check is cheap.
The repo's own promise in `README.md` is the standard: *"A full battery sweep
costs **well under $1**. That is the whole point: the experiment is cheap
enough to re-run on every model release."*

**Break 4 - the finding is one of eleven findings.** A post that reports
everything has no finding. A finding is one sentence, one number, one
boundary. Eleven findings is a dashboard, and a dashboard cannot be checked
sentence by sentence - it can only be admired.

**Break 5 - the null result stays in the drawer.** Here is the habit this
lesson has to break. A run that came out flat - no spread, no flips, no
effect - feels like a failure, so it does not get written up. But *"on our 20
production-shaped tickets, the state shape did not move the decision"* is a
result. It saves the next person a week and a few dollars, it is checkable in
exactly the same way as a positive result, and it is often the more useful of
the two - because a positive result that everyone reproduces is worth less
than a negative one that everyone stops repeating.

**Break 6 - you never reviewed your own package.** Publishing without a
review is how the credential leaks and the stale number ships. A review is
five minutes and a checklist.

## The story

A stranger on another machine decides whether to believe your number. They
will not read your reasoning. They will look at the number and ask one
question - and the answer has to be sitting right there in front of them.

So you pack a parcel and hand it over. Four things go in it. The **repo**,
so the reader's first act is running something rather than fighting a
package manager. The **command**: one line to type, the name of the key it
wants, and what it will cost - well under a dollar, because a check nobody
can afford is not a check. The **raw evidence**, one line per call, so a
reader can count instead of believing. And the **one finding**: a single
sentence somebody else can disagree with, carrying the identifiers that
point at the file behind it.

Then you read your own parcel before you let it go. Does every identifier
resolve to a file that exists. Does one number recompute by hand from the
raw lines. Is the simulator labelled as a simulator everywhere it appears.
Is the denominator visible. Is there a credential in anything you are about
to commit.

And if the answer turned out to be no? You send the same parcel, with a
sentence that says there was no effect.

## The real thing

**Publishing** in this repo means putting four things in front of a reader,
in this order:

1. **The repo** - a public repository, `Apache-2.0` licensed (the same
   licence as the models it measures), pure standard library, no install
   step. `README.md` is the front door, and the batteries table, the commands
   table and the output contract are already there.
2. **The command** - the exact command, with the provider spec and the
   battery name, the environment variable names it needs, and what it costs.
   The reader should be able to copy one line.
3. **The raw evidence** - the committed run files: `<run_id>.jsonl`,
   `<run_id>.meta.json` and the derived `<run_id>.md`, all in `runs/`. The
   `.jsonl` is the evidence; the `.md` is a convenience. The identifiers that
   tie a finding to its evidence are the run id, the `battery_hash` and the
   `uuid`.
4. **The one finding** - the single checkable sentence from lesson L92, with
   its evidence identifiers, its status label and its limitations.

That is the whole contract. A reader who has those four can check you. A
reader who has only the number has nothing.

**The evidence contract** says what may never be broken:

- raw first, then meta, then report - the report is always derived, and a
  report that disagrees with its own metrics is a bug in the formatting;
- the report is never edited by hand, and a number is never typed into a
  report that did not come out of the raw file;
- raw run files are **append-only** - never edited, never deleted, never
  tidied;
- the mock is labelled as a mock, in the banner, in the provider table's
  `note` column, in `AI-CONTEXT.md`'s `verified_facts`, and in your write-up.

**Claim status** travels with the claim. The vault's status key -
VERIFIED / CLAIM / UNCERTAIN / CONFLICT, defined in
`Learning/Decision Models/Research/Claims Ledger.md` - tells a reader how
much weight to put on each sentence. Two practical rules for publishing:

- your own finding, with committed raw evidence, is **VERIFIED** - and that
  label is about *your measurement*, not about the world;
- a vendor's benchmark number that you did not independently check is a
  **CLAIM**, and you must not put it next to your own number in the same
  voice.

**Review** is the last thing before you publish, and it is a checklist, not
a feeling. Before making this repo public, or before publishing a write-up,
check:

1. **Every identifier resolves.** Each run id in the write-up exists in
   `runs/`; each `battery_hash` matches the `.meta.json` of the run you
   mean.
2. **The numbers recompute.** Pick one number from the finding and recompute
   it by hand from the `.jsonl` - the accuracy over the scored cases, or the
   cost from `usage.input_tokens` and `price_per_mtok`. If it does not
   match, stop.
3. **The mock is labelled.** No mock number is presented as a measurement of
   a model, anywhere.
4. **The n is stated.** The reader can see the denominator, and the number is
   not read as more precise than the case set allows.
5. **No credentials.** No key, account id or token in any committed file,
   including the ones you are about to add. Credentials are environment
   variables only; `.env.example` lists the names with empty values.
6. **The repo still passes its own gates.** `python -m unittest discover -s
   tests -v` (7 tests) and `python tools/course_check.py --check` both pass.
   A public repo that fails its own checks is a different kind of marketing.
7. **The decision log has the entry.** A significant choice - which battery,
   which thresholds, which provider, what it cost, what would change your
   mind - goes into `docs/decision-log.md` in the same change.

**And if you are wrong later.** The rule "never delete" covers your own
findings too. A correction is **appended**: the original run files stay, a
new entry goes into the decision log, and the write-up says plainly what
changed and when. Deleting the run that turned out to be wrong would leave
the repository looking better than it is, which is exactly the failure the
evidence contract exists to prevent.

**Publishing a null result is publishing.** Nothing above changes when the
result is null. Same repo, same command, same raw files, same one sentence -
just a sentence that reports no effect. If you write it, it counts.

## In this repo

- `AGENTS.md` - hard rule 3 ("evidence before claims") and hard rule 4 ("the
  mock is not evidence"), plus rule 2 ("never delete") and rule 5 (never log
  or commit secrets).
- `AI-CONTEXT.md` - the `verified_facts` list (each fact with `claim`,
  `evidence`, `verified_on`), and the `do_not_touch` list containing
  `runs/*.jsonl — committed raw evidence, append-only`.
- `README.md` - the front door: zero-install, the commands table, the
  batteries table, the output contract ("Commit the raw evidence. A number
  without its raw calls behind it is marketing"), the live-credentials
  section, and the cost promise ("well under $1").
- `runs/` - the committed evidence, in the three-file shape, plus
  `swap-report.md`.
- `runs/20261025-040448-mock.md` - the banner in action: the first three
  lines of the file are the SIMULATED RUN warning, before the report even
  starts.
- `decisionarena/report.py` - `run_report()` prepends that banner when
  `result.provider.startswith("mock")`; `friction_report()` and
  `swap_report()` are the other two report shapes.
- `decisionarena/harness.py` - `run_battery()` writes the `.jsonl` and the
  `.meta.json`; `battery_hash(cases)` produces the fingerprint that ties a
  finding to its cases.
- `docs/decision-log.md` - the format (`date · decision · why · what it cost
  · what would change our mind`) and the entries that show what a good one
  looks like, including *"The repo starts private and flips public on Day
  5"* and its reason: *"A public repo with only mock output invites the exact
  misreading the mock banner exists to prevent."*
- `docs/decision-log.md` - the entry *"Raw run files are committed"*, whose
  reason is *"The claim of this repo is that evidence should travel with the
  number."*
- `tools/course_check.py` - one of the gates a publisher runs before making
  a repo public.
- `tests/` - the stdlib unittest suite, run with
  `python -m unittest discover -s tests -v`.
- The vault's `Learning/Decision Models/Research/Claims Ledger.md` - the
  status key, and the worked example of a claim labelled **CLAIM** (the
  vendor benchmark table) next to one labelled **VERIFIED** (the observed
  latency in the independent harness).

## Your turn

Write a file `docs/notes/L93-publication.md`. It is the package you hand to
the public: what you claim, what supports it, and how a reader checks it.

It must contain these sections, in this order:

- `## The finding` - the one sentence from lesson L92, unchanged
- `## The package` - the four things, each with the real value:
  1. **the repo**: its path or URL, its licence, and the two files a reader
     should open first
  2. **the command**: the exact line, the environment variable names it
     needs (names only), and what it costs
  3. **the raw evidence**: the run id, the `.jsonl`, the `.meta.json` and the
     `.md` file names, all from `runs/`
  4. **the finding**: the sentence, with its status label and its three
     limitations in one line each
- `## The reviewer's checklist` - six or seven bullets, each one a check the
  reader can carry out in five minutes, phrased as checks (not as
  assertions about your own work)
- `## The null-result version` - the same finding written as it would be if
  the result had come out flat, with the labels and identifiers you would
  still publish. Write it even if your result was positive
- `## What I did not publish` - anything you deliberately left out (a mock
  run, a scratch directory, a number you could not recompute) and one line
  on why
- `## If it turns out to be wrong` - your correction plan: what gets
  appended, what stays, and where the correction is recorded. Remember the
  repo never deletes
- `## Final checks` - the two gate commands you ran and their results, and
  the confirmation that no committed file contains a credential

Inputs: your finding from lesson L92, the files in `runs/`, `README.md`,
`AGENTS.md`, `AI-CONTEXT.md` and `docs/decision-log.md`.

Expected output: the seven sections above, 500-800 words, with every
identifier and command copied from a real file or a real run.

**Hint:** the package is already assembled - this lesson is about writing
down what is there, in an order a reader can follow. If you have to guess at
a value, that value is missing from your package.

**Do not** include any credential, and do not include any mock number
without labelling it as a mock number.

## Check yourself

Answer these out loud, in your own words, before you move on.

1. Name the four things a published finding must contain, and say which one
   is the difference between a finding and a post.
2. Why does a link to the repository not make a number checkable on its own?
3. What is wrong with publishing a result you have not reviewed, and what
   does the review actually consist of?
4. What goes wrong if you delete the run that turned out to be wrong, and
   what do you do instead?

## Artifact

The artifact **is** `docs/notes/L93-publication.md`. Before you commit it,
hand it to a reader who has never seen this repo and check that they can
answer one question without asking you anything: *can I check this claim,
and what will it cost me?*

Then commit it. The artifact is the proof that you know how to publish a
finding, not the proof that the finding is true.
