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
    claim: "7/7 stdlib unittest cases pass (python -m unittest discover -s tests)."
    evidence: "tests/test_metrics.py"
    verified_on: 2026-10-25
  - id: cli-surface
    claim: "providers / run / friction / swap all work from `python -m decisionarena`."
    evidence: "runs/20261025-005316-mock.md"
    verified_on: 2026-10-25
  - id: mock-is-not-evidence
    claim: "MockProvider output is a harness test, never a model evaluation."
    evidence: "decisionarena/providers.py"
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

in_progress:
  - id: laya-local
    what: "Local Laya provider (in-process) + JevProvider base_url pointing at laya-serve."
    state: "not started; laya-lab/README.md has the Windows setup"
  - id: day-2-learning
    what: "Aswath works through examples/00 .. examples/04 himself."
    state: "scaffolds exist; the learning pass has not happened yet"

next_actions:
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
  - "python tools/check_links.py --vault \"C:\\Users\\aswat\\Aswaths Obsidian Den\\Aswaths Mountain Den\""
  - "uv venv --python 3.12 && uv pip install laya \"laya[serve]\""

do_not_touch:
  - "C:\\Users\\aswat\\.agents\\skills\\  — registry-managed by a third party"
  - "runs/*.jsonl — committed raw evidence, append-only"
  - "C:\\Users\\aswat\\Aswaths Obsidian Den\\Aswaths Mountain Den\\Archive\\ — archived, never deleted"
  - "Any file whose name contains a secret, or any .env file"
```

## Summary

**What exists.** A working, dependency-free harness that can already exercise the full
pipeline offline: providers (mock, Jev, Clef, OpenAI-compatible), three batteries
(routing / injection / format), metrics, a Markdown report writer, and a swap-safety
comparator. Seven unit tests pass.

**What is real.** Nothing measured yet from a live provider — every committed number so
far comes from the mock and proves only that the harness works. The pricing and
capability facts in the vault were verified against vendor pages and third-party
benchmarks on 2026-10-25, and are marked with their source.

**What is next.** The learning path (`examples/`) and the vault restructure are in
flight. The first genuinely publishable artifact is the **format-friction finding**:
how far a decision probability moves when only the *shape* of the input state changes
(prose vs flat JSON vs nested JSON). The independent harness `rmax-ai/jev-vs-clef`
reported a 0.90 / 0.86 / 0.09 spread across exactly that axis. Reproducing it on
Laya would be a real, novel, checkable contribution.

**What is blocked.** Credentials for the live providers and a GPU-enabled Kaggle
account, all owned by the user. Nothing else is blocked.
