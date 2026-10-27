# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Astro 7 + Tailwind CSS 4, static output. Chosen by the user over plain static
HTML/CSS (recommended) and React + Vite. Static output means the site deploys
to any static host with no server runtime, matching the harness's own
stdlib-only, zero-install posture.

The site lives in `site/` inside the `decision-arena` repository, so its
source and the product it describes are versioned together.

## Users

**Primary: engineers choosing between decision-model vendors.** They have a
real workload - support tickets, routing, triage, scoring - and they need to
decide whether to buy, keep, or replace a model provider. They arrive
skeptical, because every vendor publishes a benchmark table where they win,
and two headline tables disagree with each other. Their job is to pick a
vendor on evidence rather than on marketing, and to be able to defend the
choice to their team.

They are technical, they can run a terminal, and they will check the claim
before they believe it.

**Secondary: absolute beginners learning AI/ML fundamentals.** They use
Decision Arena Academy, the 46-lesson course that lives in the same
repository. They are not evaluating vendors; they are learning what a neural
network is, why a probability is not a confidence, and how the harness
measures anything at all. They need the course to be genuinely learnable by
someone who has never heard of softmax.

## Product Purpose

Decision Arena runs **the same battery** against multiple decision models
(TypeSafe Jev, Cloudflare Clef, OpenAI-compatible gateways, local Laya) and
measures accuracy, calibration, cost, latency, determinism, injection
resistance and swap safety.

It exists because the field's headline comparison tables disagree with each
other, and because a vendor benchmark measures the vendor's workload rather
than yours.

The Academy exists because a harness that measures things nobody can explain
is a trap for the person running it. The course teaches the maths and the
method from first principles, so the numbers the harness prints can be
defended rather than believed.

Success for the harness means: a third party can run the comparison for under
a dollar and reach the same conclusion, because every published number has
its raw call log behind it. Success for the Academy means: a beginner can
explain softmax, temperature, gradient descent and attention without notes,
because they wrote them.

## Positioning

The mechanism a neighbouring product could not truthfully copy: **one client,
many providers, one battery, and raw evidence per run**. Not a leaderboard -
a referee. The differentiator is not a better score, it is that every claim
comes with the `runs/*.jsonl` that produced it and a command anyone can
re-run.

The second, more unusual position: the project publishes its own finding
rather than its own score. The format-friction result - how far a decision
probability moves when only the *shape* of the input state changes - is
measurable with no labels at all, and reproducing it on a third provider
would be a checkable contribution rather than a marketing claim.

Third position: the teaching is not a brochure. The course and the harness
are the same artefact, and the repository's rules are the same rules the
learner is held to.

## Operating Context

- **Environments.** A bare `python` with no virtualenv, and a browser. The
  library is stdlib-only by rule, and the site must be equally frictionless to
  read and to build.
- **Workflows.** Clone, `python -m decisionarena providers`, run a battery
  against a provider, read the Markdown report, read the raw JSONL behind it.
  For a learner: `python tools/learn_state.py next`, then `/learn`.
- **Credentials.** Provider API keys come from environment variables only.
  A reader with no keys can still run the whole pipeline against the offline
  simulator - but that simulator is explicitly **not** a model evaluation, and
  the site must never let a reader confuse the two.
- **Cost.** A full battery sweep costs well under $1. This is a feature: the
  experiment is cheap enough to re-run on every model release, and a reader
  should be able to reproduce a finding without asking anyone's permission.
- **Rituals.** Every run writes raw evidence first and a report second. Every
  significant decision gets an entry in `docs/decision-log.md` with what it
  cost. Nothing is deleted; things are archived.

## Capabilities and Constraints

**Capabilities.** Provider adapters (Jev, Clef, OpenAI-compatible, local Laya,
offline mock). Three batteries: routing, injection, format variants. Metrics:
accuracy, Brier score, ECE with reliability bins, inter-provider agreement,
probability gap, and action-change rate (swap safety). A Markdown report
writer. A spend cap and a dry-run mode. A 46-lesson course with per-concept
mastery tracking, a review queue and a course gate.

**Constraints.**
- The library is stdlib-only. A third-party import is not allowed without a
  written reason.
- **The mock is never evidence.** Simulator output proves the harness works;
  it never evaluates a model, and no number from it may be published as a
  model result.
- **Evidence before claims.** A number without its raw run file behind it is
  marketing.
- Never delete. Archive only.
- The repository will be public, so no secret, credential, or private path may
  appear in anything published from it.
- Licence: Apache-2.0, matching the models it measures.

**Undecided / open.** Whether the site's centre of gravity is the harness or
the Academy - the primary visitor and the product truth above are settled, but
the entry point is a surface decision, taken in the surface brief rather than
here.

## Brand Commitments

- The name is **Decision Arena**. The harness is the arena; the providers are
  the players; the referee is the product.
- **Decision Arena Academy** is the course's name. "Academy" is a commitment
  to a structured, gated, beginner-first path - not a marketing word.
- The voice is a neutral referee: precise, unhyped, allergic to superlatives.
  It states what was measured, on what, and what the number does not show.
- "The mock is not evidence" is a brand commitment, not a disclaimer - it
  appears in the harness, in the course, and on the site.

## Evidence on Hand

Real, and available to the site:
- The harness itself and its committed run files (`runs/*.jsonl`,
  `*.meta.json`, `*.md`) - including a real friction report with mean spread
  0.42, max spread 0.9271, and 4 of 9 questions flipping at 0.5, all from the
  offline simulator and labelled as such.
- The course: 46 lessons, 46 quizzes, 10 phases, a placement quiz, a
  per-concept mastery engine, a course gate.
- `docs/decision-log.md` - the decisions and what they cost.
- `docs/architecture-graph.md` - the code graph, 188 nodes, 9 communities.
- Vendor pricing verified against vendor pages on 2026-10-25: clef
  $0.24/Mtok, clef-flash $0.038/Mtok, jev $0.042/Mtok.
- The vault's claims ledger, which labels every claim VERIFIED, CLAIM,
  UNCERTAIN or CONFLICT.

**Absences the site must not fabricate:**
- No live-provider measurement has been made yet. Every committed number comes
  from the offline simulator.
- No customer, testimonial, user count, or revenue figure exists.
- No pricing or commercial terms for any product exist.
- No deployment, uptime or performance claim about a hosted service exists,
  because no hosted service exists.

## Product Principles

1. **Evidence before claims.** Every number shown must be traceable to a raw
   file, and the site should make that traceability visible rather than
   implied.
2. **One battery, many providers.** The comparison is the product. Never
   present a single provider's result as the answer.
3. **Teach the method, not the conclusion.** A reader who cannot explain
   calibration cannot check it. The Academy exists so that the numbers have
   an owner who understands them.
4. **Refuse the flattering comparison.** If the simulator's numbers are more
   interesting than the real ones, publish the simulator's numbers labelled
   as the simulator's.
5. **Frictionless to try, honest about cost.** A full battery under $1, a
   no-credentials path that still teaches the truth, and no hidden spend.

## Accessibility & Inclusion

No product-specific standard was established. General web accessibility
applies: semantic structure, keyboard operability, visible focus, and
legible contrast are part of the craft floor, not optional extras. The
audience includes developers reading on varied hardware and screen sizes, so
the site must be usable at mobile widths and at 200% zoom.
