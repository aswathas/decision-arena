# AI-CONTEXT.md — machine-readable current state

> Updated in the **same change** as the thing it describes. If you changed the repo
> and did not touch this file, you left the next agent a lie.
>
> Machine-readable brief first, human summary second. Regenerate with
> `python tools/sync_brief.py --check` (fails when the file is stale).

```yaml
project: decision-arena
purpose: >
  An open, neutral harness that runs one battery against many decision models
  (TypeSafe Jev, Cloudflare Clef, OpenAI-compatible gateways, local Laya) and
  measures accuracy, calibration, cost, latency, determinism, injection
  resistance and swap safety. Exists because every vendor publishes a benchmark
  where they win, and the two headline tables disagree.
status: building            # building | working | product | paused
version: 0.1.0
license: Apache-2.0
python_requires: ">=3.9"
dependencies: []            # stdlib only, in decisionarena/

verified_facts:
  - id: harness-offline
    claim: "The harness runs end to end with zero credentials via MockProvider."
    evidence: "runs/20261025-005316-mock.md, runs/20261025-005353-friction-mock.json"
    verified_on: 2026-10-25
  - id: unit-tests
    claim: "29/29 stdlib unittest cases pass (python -m unittest discover -s tests): 7 metric tests plus 22 Academy tests."
    evidence: "tests/test_metrics.py, tests/test_learn_state.py"
    verified_on: 2026-10-27
  - id: academy-course
    claim: "Decision Arena Academy ships 46 lessons and 46 quizzes across 10 phases; the course gate passes and course/curriculum.json is in sync."
    evidence: "course/curriculum.json, tools/course_check.py, course/lessons/L00-what-is-a-decision-model.md"
    verified_on: 2026-10-27
  - id: academy-loop
    claim: "The learning loop runs end to end offline: init -> start -> grade -> record -> feedback, tracking per-concept mastery and a review queue."
    evidence: "tools/learn_state.py, learning/README.md"
    verified_on: 2026-10-27
  - id: academy-skills
    claim: "Three Academy skills live in skills/ (learn, arena-coach, course-author) and install project-locally into .claude/skills/ without touching the pre-existing global 'learn' skill."
    evidence: "skills/learn/SKILL.md, skills/arena-coach/SKILL.md, skills/course-author/SKILL.md, tools/install_skills.py"
    verified_on: 2026-10-27
  - id: academy-hooks
    claim: "SessionStart injects the learner's progress and Stop reminds the agent to close the loop; both exit 0 and never block the session."
    evidence: ".claude/settings.json, tools/hooks/session_start.py, tools/hooks/stop.py"
    verified_on: 2026-10-27
  - id: cli-surface
    claim: "providers / run / friction / swap all work from `python -m decisionarena`."
    evidence: "runs/20261025-005316-mock.md"
    verified_on: 2026-10-25
  - id: mock-is-not-evidence
    claim: "MockProvider output is a harness test, never a model evaluation."
    evidence: "decisionarena/providers.py, decisionarena/report.py"
    verified_on: 2026-10-25
  - id: laya-wire-compat
    claim: "laya-serve exposes POST /v1/systemone, the same wire format as Jev."
    evidence: "laya-lab/README.md"
    verified_on: 2026-10-25
  - id: price-points
    claim: "clef $0.24/Mtok, clef-flash $0.038/Mtok, jev $0.042/Mtok."
    evidence: "Learning/Decision Models/Research/Claims Ledger.md"
    verified_on: 2026-10-25
  - id: vault-restructured
    claim: "The vault has one Learning/ root, Archive/ for strays, and ZERO broken wikilinks (49 notes, 102 links)."
    evidence: "tools/check_links.py exits 0 on the live vault"
    verified_on: 2026-10-25
  - id: examples-run
    claim: "All five teaching examples in examples/ run with exit 0 on a bare python."
    evidence: "examples/README.md"
    verified_on: 2026-10-25
  - id: skills-installed
    claim: "Four custom skills are installed for mcode and Claude Code, with pointers in ~/.agents/rules, and all 8 SKILL.md files pass quick_validate.py."
    evidence: "C:/Users/aswat/.minimax/skills/learn-by-doing/SKILL.md"
    verified_on: 2026-10-25
  - id: vault-graph
    claim: "The vault knowledge graph builds: post-restructure 458 nodes, 587 edges, 35 labelled communities; baseline (pre-restructure) 380 nodes, 444 edges, 28 communities."
    evidence: "docs/architecture-graph.md"
    verified_on: 2026-10-25
  - id: repo-graph
    claim: "The repo AST graph builds: 188 nodes, 358 edges, 9 communities across 16 Python files."
    evidence: "docs/architecture-graph.md"
    verified_on: 2026-10-25
  - id: graphify-query
    claim: "graphify query answers codebase questions from the graph: 'where is the swap safety metric computed' returns action_change_rate() at decisionarena/metrics.py:136 and cmd_swap() at decisionarena/cli.py:89."
    evidence: "docs/architecture-graph.md"
    verified_on: 2026-10-25
  - id: friction-raw-evidence
    claim: "The friction command now persists its raw calls and run metadata, so every friction number on the site has a committed raw file behind it: 9 calls, mean spread 0.42, max spread 0.9271, 4 of 9 questions flipping at 0.5."
    evidence: "runs/20261027-212313-friction-mock.jsonl, runs/20261027-212313-friction-mock.meta.json"
    verified_on: 2026-10-27
  - id: public-site
    claim: "The public site builds from site/ (Astro 7 + Tailwind 4, static) and ships 48 pages: the landing page (one figure plate with the measure and learn doors, the friction field, and the evidence links), a course index, and one page per lesson. It is published by CI at https://aswathas.github.io/decision-arena/ on every push to main. The Impeccable detector reports 0 findings at 1440x900 and 390x844, and the a11y and link check passes on every built page."
    evidence: "site/src/pages/index.astro, site/src/pages/lessons/[id].astro, .github/workflows/pages.yml, tools/check_site_a11y.py"
    verified_on: 2026-10-28
  - id: course-reader-reads-the-repo
    claim: "The course pages are rendered from the repository's own files, not copied: the lesson body is course/lessons/*.md imported as markdown, the quiz is course/quizzes/*.json, and the index is the generated course/curriculum.json. A lesson file that moves fails the build instead of publishing a stale copy."
    evidence: "site/src/data/course.ts, course/curriculum.json"
    verified_on: 2026-10-28
  - id: site-no-third-party-runtime
    claim: "The site makes no third-party runtime request: both typefaces are self-hosted woff2 files vendored from the upstream releases by tools/vendor_fonts.py."
    evidence: "tools/vendor_fonts.py, site/public/fonts/fonts.css"
    verified_on: 2026-10-27

in_progress:
  - id: laya-local
    what: "Local Laya provider (in-process) + JevProvider base_url pointing at laya-serve."
    state: "not started; laya-lab/README.md has the Windows setup"
  - id: academy-first-pass
    what: "Aswath works through the Academy himself, starting at L00, and his first learner artifacts land in docs/notes/ and exercises/."
    state: "course complete and gated; the learning pass has not happened yet"
  - id: academy-vault-bridge
    what: "Mirror the Academy build log into the Obsidian vault (Learning/Course - Decision Models/Build Log.md) without duplicating the source of truth."
    state: "not started; the repo's learning/build_log.md is authoritative for now"
  - id: site-deployment
    what: "Publish site/dist to a public URL so the repository's front door is a real page."
    state: "published by CI at https://aswathas.github.io/decision-arena/ (GitHub Pages, every push to main rebuilds and redeploys it). An earlier host at https://pm51wr5jr44rf.space.minimax.io still serves the older one-page build and its deploy endpoint now refuses this session; it is not the canonical home."

next_actions:
  - "Day 1 of the Academy: `python tools/learn_state.py init --learner aswath --path beginner`, then `/learn` for L00."
  - "Day 2: work through examples/01_softmax.py and 02_temperature.py, quiz, log."
  - "Day 5: live Jev + Clef run on the routing battery; repo flips PUBLIC."
  - "Day 6 parity: one client, three providers (Jev / Clef / local Laya) on one battery."
  - "Calibration pass: ECE + reliability curve per provider."
  - "Format-friction finding: write it up and publish it."
  - "Day 11-12: fine-tune on Kaggle 2xT4, push the checkpoint to HuggingFace."
  - "Day 13: decide the product from evidence, then build v1."

blocked_on:
  - id: cloudflare-creds
    need: "CLOUDFLARE_ACCOUNT_ID + CLOUDFLARE_AUTH_TOKEN"
    owner: user
    why: "Clef parity run on Day 6"
    alternative: "TypeSafe TYPESAFE_API_KEY only, then compare two providers"
  - id: typesafe-creds
    need: "TYPESAFE_API_KEY"
    owner: user
    why: "Jev parity run on Day 6"
  - id: kaggle-gpu
    need: "Kaggle account with GPU access enabled (2xT4)"
    owner: user
    why: "Fine-tuning on Days 11-12"
  - id: no-gemini-key
    need: "GEMINI_API_KEY / GOOGLE_API_KEY"
    owner: none
    why: "graphify semantic extraction"
    workaround: "Host subagents do the extraction (already how the vault graph was built)"

commands_that_work:
  - "python -m unittest discover -s tests -v"
  - "python -m decisionarena providers"
  - "python -m decisionarena run --provider mock --battery all"
  - "python -m decisionarena friction --provider mock"
  - "python -m decisionarena swap --provider a=mock --provider b=mock"
  - "python tools/course_check.py --index"
  - "python tools/course_check.py --check"
  - "python tools/learn_state.py init --learner aswath --path beginner"
  - "python tools/learn_state.py next"
  - "python tools/learn_state.py status"
  - "python tools/learn_state.py review"
  - "python tools/learn_state.py feedback"
  - "python tools/install_skills.py --target claude-project"
  - "python tools/check_site_a11y.py"
  - "python tools/vendor_fonts.py"
  - "cd site && npm run build && node scripts/capture.mjs && node scripts/measure.mjs"
  - "python tools/check_links.py --vault \"C:\\Users\\aswat\\Aswaths Obsidian Den\\Aswaths Mountain Den\""
  - "uv venv --python 3.12 && uv pip install laya \"laya[serve]\""

do_not_touch:
  - "C:\\Users\\aswat\\.agents\\skills\\  — registry-managed by a third party"
  - "runs/*.jsonl — committed raw evidence, append-only"
  - "C:\\Users\\aswat\\Aswaths Obsidian Den\\Aswaths Mountain Den\\Archive\\ — archived, never deleted"
  - "Any file whose name contains a secret, or any .env file"
```

## Summary

**What exists.** Three things, all real. (1) A working, dependency-free harness
that can already exercise the full pipeline offline: providers (mock, Jev,
Clef, OpenAI-compatible), three batteries (routing / injection / format),
metrics, a Markdown report writer, and a swap-safety comparator. (2)
**Decision Arena Academy** - a self-contained beginner course in `course/`
(46 lessons, 46 quizzes, 10 phases), with three skills (`skills/`), a
per-concept mastery engine (`tools/learn_state.py`), a course gate
(`tools/course_check.py`) and session hooks. 29/29 unit tests pass. (3) A
public site in `site/` - 48 static pages: a landing page carrying two equal
doors on one figure plate, the friction field plotted from the committed run,
every number linked to its raw file, and a course reader that renders the 46
lessons and their quizzes straight from the repository's own files.

**What is real.** Nothing measured yet from a live provider - every committed
number so far comes from the mock and proves only that the harness works. The
friction run behind the site's headline numbers is committed as raw calls
(`runs/20261027-212313-friction-mock.jsonl`) plus its report and metadata, and
the site says on its face that this is a measurement of the simulator and not
of a model. The pricing and capability facts in the vault were verified against
vendor pages and third-party benchmarks on 2026-10-25, and are marked with their
source. The Academy itself is verified only as *material*: the gate proves the
lessons are well-formed, not that they teach well. That is what the learner's
own progress file is for.

**What is next.** Aswath runs the Academy himself, starting at L00, and his
first learner artifacts land in `docs/notes/` and `exercises/`. The first
genuinely publishable artifact remains the **format-friction finding**: how far
a decision probability moves when only the *shape* of the input state changes
(prose vs flat JSON vs nested JSON). The independent harness
`rmax-ai/jev-vs-clef` reported a 0.90 / 0.86 / 0.09 spread across exactly that
axis. Reproducing it on Laya would be a real, novel, checkable contribution.

**What is blocked.** Credentials for the live providers and a GPU-enabled
Kaggle account, all owned by the user. Nothing else is blocked - the Academy
runs fully offline.
