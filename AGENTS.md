# AGENTS.md — working rules for this repo

**Read this first. Then read `AI-CONTEXT.md` for the machine-readable current state.**

This repo belongs to **Aswath** (GitHub `aswathas`). It is the teaching-and-product
engine for a decision-model evaluation harness. Two audiences at once:

1. **Aswath is learning** AI/ML fundamentals by *building* this harness.
2. **Other agents** need to pick up the work cold and know exactly what exists,
   what is verified, and what is not.

If those two goals ever conflict, the learner's understanding wins: explain, quiz,
and let him write the code. Do not silently finish his exercises for him.

## The one-sentence brief

`decision-arena` runs the **same battery** against multiple decision models
(TypeSafe Jev, Cloudflare Clef, OpenAI-compatible gateways, local Laya) and measures
**accuracy, calibration, cost, latency, determinism, injection resistance, and swap
safety** — because every vendor publishes a benchmark where they win.

## Hard rules

1. **Stdlib only.** `decisionarena/` has zero third-party imports. Do not add a
   dependency without a written reason in `AI-CONTEXT.md`. Tests must run on a
   bare `python`.
2. **Never delete.** Archive, move, or supersede — but do not delete user data, notes,
   or evidence. The vault's `Archive/` exists for exactly this reason.
3. **Evidence before claims.** A number without its raw `runs/*.jsonl` behind it is
   marketing. If you cite a result, cite the run file.
4. **The mock is not evidence.** `MockProvider` is an offline simulator for testing
   the harness. Its numbers must never be published as a model evaluation.
5. **Never log or commit secrets.** Keys come from env vars only (see `.env.example`).
6. **One writer per file.** If you parallelise work, give each agent disjoint files.
7. **Update `AI-CONTEXT.md` in the same change as the change it describes.**
   A stale brief is worse than no brief.
8. **The learner writes the exercise code.** In `course/`, an agent may
   scaffold, explain, review, quiz and log — never write the exercise
   implementation, never paste a reference solution. A lesson that ships its
   own answer is a broken lesson.
9. **The course gate must pass.** `python tools/course_check.py --check`
   fails a commit that breaks a lesson, a quiz or the generated index.

## Conventions

- Python 3.9+ compatible syntax, `from __future__ import annotations` at the top of
  every module.
- Docstrings on every public function: what it does, what it returns, what it costs.
- Money is always in **USD**, always reported with the run's token counts beside it.
- Probabilities are floats in `[0, 1]`; confidence is separate from probability.
- Times are ISO-8601 UTC. Run IDs are `<YYYYMMDD>-<HHMMSS>-<label>`.
- Windows: PowerShell 5.1, no `&&` / `||`. Use `python`, not `python3`.

## Layout

```
decisionarena/      the library (providers, harness, metrics, report, cli)
cases/              batteries: routing / injection / format_variants (JSON)
examples/           the learning path — 00_read_the_code … 04_attention_numpy
course/             Decision Arena Academy — the beginner course
  lessons/          one brief per lesson (source of truth)
  quizzes/          one answer-key file per lesson
  curriculum.json   GENERATED index of the whole course
  FORMAT.md         the authoring contract for lessons and quizzes
  placement.json    the placement quiz
skills/             the Academy's skills (learn, arena-coach, course-author)
learning/           the learner's state: progress.json + build_log.md
tests/              stdlib unittest
tools/              check_links.py (vault link gate), sync_brief.py
                    course_check.py (course gate), learn_state.py (progress engine)
                    install_skills.py (install skills into a host)
                    vendor_fonts.py (self-host the site's typefaces)
                    check_site_a11y.py (site accessibility smoke test)
                    hooks/ (session_start.py, stop.py)
docs/               architecture-graph.md (graphify AST graph), decision-log.md
runs/               committed evidence: jsonl + meta.json + .md report
site/               the public site (Astro + Tailwind, static; 48 pages - the
                    landing page, the course index and one page per lesson;
                    DESIGN.md is its design system - read it before touching
                    site/src)
laya-lab/           local Laya experiments (separate venv, torch)
```

## How to work here

```bash
python -m unittest discover -s tests -v     # 7 tests, must stay green
python -m decisionarena providers           # what is configured on this machine
python -m decisionarena run --provider mock --battery all
python -m decisionarena friction --provider mock
python -m decisionarena swap --provider a=jev --provider b=clef:clef-flash

# Decision Arena Academy — the beginner course
python tools/course_check.py --index        # regenerate course/curriculum.json
python tools/course_check.py --check        # the course gate
python tools/learn_state.py init --learner aswath --path beginner
python tools/learn_state.py next            # what to learn next, and why
python tools/learn_state.py status          # progress report
python tools/learn_state.py review          # what to go back to
python tools/learn_state.py feedback        # the closing feedback note
python tools/install_skills.py              # install the skills into .claude/skills/

# The public site (site/)
python tools/check_site_a11y.py             # accessibility smoke test on the built page
cd site && npm run build                   # static build into site/dist
node scripts/capture.mjs                   # recapture .impeccable/review/*.png
node scripts/measure.mjs                   # measure the first viewport
```

## The knowledge map (graphify)

The repo and the Obsidian vault are indexed by **graphify** into a knowledge graph.
Before guessing where something lives, *query the graph*:

```powershell
# the code graph (AST: modules, functions, call edges)
cd C:\Users\aswat\Downloads\Projects\graphify-repo
graphify query "where is the swap safety metric computed"

# the vault graph (concepts, evidence, themes)
cd C:\Users\aswat\Downloads\Projects\graphify-vault-b
graphify query "what connects the format-sensitivity finding to the open model zoo"
```

Both graphs are built with the graphify interpreter recorded in each working
directory's `graphify-out/.graphify_python`. The skill lives at
`C:\Users\aswat\.claude\skills\graphify\SKILL.md`. The code graph's rendered form is
`docs/architecture-graph.md`; the vault's lives in `Learning/Graph/` in the vault.

## The learning loop

Aswath writes the exercise code. The agent explains the code **he** wrote, poses one
micro-exercise, quizzes him, and logs the result. See the skills:

- `learn-by-doing` — the build-and-learn loop
- `teach-persona` — Feynman / Socratic / Napoleon / Dewey teaching moves
- `doubt-resolver` — answer *this* doubt from *his* codebase
- `agent-brief` — keep `AI-CONTEXT.md` honest

Installed at `C:\Users\aswat\.minimax\skills\` and `C:\Users\aswat\.claude\skills\`,
with pointers in `C:\Users\aswat\.agents\rules\`.

## The Obsidian vault

`C:\Users\aswat\Aswaths Obsidian Den\Aswaths Mountain Den` is the learning home.
It has exactly one learning root, `Learning/`:

- `Learning/Foundations/` — AI/ML fundamentals
- `Learning/Decision Models/` — the decision-model field
- `Learning/Course - Decision Models/` — course map, progress, review cards, build log
- `Learning/Graph/` — the knowledge-map output
- `Archive/` — everything retired, never deleted

`tools/check_links.py` is the gate: **zero broken wikilinks** or the build fails.
