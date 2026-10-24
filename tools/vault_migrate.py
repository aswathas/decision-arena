"""One-shot vault migration: one learning home, archive the strays, fix every wikilink.

WHY THIS EXISTS
---------------
The Obsidian vault grew sideways: two learning series at the top level, notes that
are actually personal scratch, Obsidian demo folders, and nine broken wikilinks
pointing at notes that were planned but never written.

After this script runs:
  Learning/                        <- the ONLY learning root
    Foundations/                   <- was "AI Foundations/"
    Decision Models/               <- was "Decision Models/"
    Course - Decision Models/      <- new: course map, progress, cards, log
    Graph/                         <- new: graphify output
  Project Ideas/                   <- unchanged, stays top level (business framing)
  Archive/                         <- retired + scratch, NEVER deleted
  rough notes/                     <- unchanged, personal
  Welcome.md                       <- rewritten as the vault front door

RULES
-----
* Nothing is deleted. Every move is a move; every archive is a copy-in-place.
* Every wikilink must resolve afterwards. `tools/check_links.py` is the gate.
* Links to notes that were planned but never written become STUB notes, not broken
  links - the gap stays visible instead of disappearing.

Usage:
    python tools/vault_migrate.py --dry-run     # print the plan, change nothing
    python tools/vault_migrate.py               # apply
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

VAULT = Path(r"C:\Users\aswat\Aswaths Obsidian Den\Aswaths Mountain Den")

# ---------------------------------------------------------------- move table
# (source relative path, destination relative path)
MOVES: list[tuple[str, str]] = []

FOUNDATION_FILES = [
    "01 - Foundations - Tensors to Transformers.md",
    "02 - LLMs - What They Actually Are.md",
]
DECISION_FILES = [
    "01 - Decision Models - What They Are.md",
    "02 - Jev Deep Dive - TypeSafe System One.md",
    "03 - Clef Deep Dive - Cloudflare Open Weights.md",
    "04 - Jev vs Clef - and the Whole 2026 Field.md",
    "05 - Building With Decision Models.md",
    "06 - Project Ideas.md",
    "07 - The Open Model Zoo.md",
]
RESEARCH_FILES = [
    "Benchmarks and Pricing Evidence.md",
    "Claims Ledger.md",
    "Ecosystem Map.md",
]
# scratch / demo / Obsidian-owned folders that are not learning material
ARCHIVE_ENTRIES = [
    "202603261422.md",
    "202603261424.md",
    "Untitled 1.md",
    "my test notes.md",
    "create a link.md",
    "things i learned in solidity fundamentals.md",
    "templates",
    "hello pookie",
]

# ------------------------------------------------------------- link rewrite
# exact-target replacements, applied first, longest-first
LINK_RULES: list[tuple[str, str]] = [
    # README files get stable, unique, sortable names (Obsidian resolves by path)
    ("AI Foundations/README", "Learning/Foundations/00 - Foundations Index"),
    ("Decision Models/README", "Learning/Decision Models/00 - Decision Models Index"),
    # colon-vs-dash mismatches between the index and the actual filenames
    ("AI Foundations/01 - Foundations: Tensors to Transformers",
     "Learning/Foundations/01 - Foundations - Tensors to Transformers"),
    ("AI Foundations/02 - LLMs: What They Actually Are",
     "Learning/Foundations/02 - LLMs - What They Actually Are"),
]
# prefix rewrites, applied after the exact rules
PREFIX_RULES: list[tuple[str, str]] = [
    ("AI Foundations/", "Learning/Foundations/"),
    ("Decision Models/", "Learning/Decision Models/"),
]

LINK_RE = re.compile(r"\[\[([^\]\[]+)\]\]")

# ------------------------------------------------------------------- stubs
# Notes that the index promises but that were never written. Each stub is a
# promise with a deadline, not a placeholder that hides the gap.
STUBS: dict[str, str] = {
    "Learning/Foundations/03 - System 1 vs System 2.md": (
        "PLANNED - not yet written.\n\n"
        "Yann LeCun's argument: System 1 vs System 2, world models, JEPA as a "
        "predictor of representations rather than pixels.\n\n"
        "**Why it matters here:** the phrase 'System 1' collides with TypeSafe's "
        "'System One'. They are different things that share a marketing word. "
        "Read this note before you let the two bleed into each other.\n\n"
        "**Status:** in the Day 1-4 foundations queue. See "
        "`Learning/Course - Decision Models/00 Course Map.md`.\n"
    ),
    "Learning/Foundations/04 - JEPA Deep Dive.md": (
        "PLANNED - not yet written.\n\n"
        "I-JEPA, V-JEPA, V-JEPA 2/2.1: the mechanics, the maths, the open "
        "releases, and a from-scratch build ladder.\n\n"
        "**Related:** the four LEJEPA experiment notes in `Project Ideas/` are the "
        "primary sources for this one.\n\n"
        "**Status:** in the Day 1-4 foundations queue.\n"
    ),
    "Learning/Foundations/05 - JAX - The Functional Stack.md": (
        "PLANNED - not yet written.\n\n"
        "Why JAX exists, the library map, the traps, and where it is still the "
        "right tool.\n\n"
        "**Status:** in the Day 1-4 foundations queue.\n"
    ),
    "Learning/Foundations/06 - Open-Weight Model Landscape.md": (
        "PLANNED - not yet written.\n\n"
        "Llama-class and everything else: licences, what 'open' really means, "
        "small models you can actually run, and the non-text models.\n\n"
        "**Status:** in the Day 1-4 foundations queue.\n"
    ),
    "Learning/Foundations/07 - What To Build.md": (
        "PLANNED - not yet written.\n\n"
        "Concrete open-source System-1 style projects, ranked by feasibility for "
        "one person, with compute budgets.\n\n"
        "**Status:** in the Day 1-4 foundations queue.\n"
    ),
    "Learning/Foundations/08 - How to Learn.md": (
        "PLANNED - not yet written.\n\n"
        "The learning ladder, the free resources, hardware budgets, and the "
        "'build to learn' project sequence.\n\n"
        "**Status:** in the Day 1-4 foundations queue.\n"
    ),
    "Project Ideas/Distill - a Local Decision Model for Your Edge.md": (
        "PLANNED - not yet written.\n\n"
        "The 'ship a small domain model' play: take a decision backbone, fine-tune "
        "it on a narrow vertical, run it at the edge, and keep the per-decision "
        "cost near zero.\n\n"
        "**Why it matters:** this is the shape of the long tail in the open model "
        "zoo (biomedical, Indic-language, omni-modal fine-tunes). See "
        "`Learning/Decision Models/07 - The Open Model Zoo.md` and "
        "`Learning/Decision Models/06 - Project Ideas.md` idea 5.\n\n"
        "**Status:** Day 11-12 fine-tune notes will land here.\n"
    ),
}


def plan_moves() -> list[tuple[str, str]]:
    moves = []
    for name in FOUNDATION_FILES:
        moves.append((f"AI Foundations/{name}", f"Learning/Foundations/{name}"))
    moves.append(("AI Foundations/README.md", "Learning/Foundations/00 - Foundations Index.md"))
    for name in DECISION_FILES:
        moves.append((f"Decision Models/{name}", f"Learning/Decision Models/{name}"))
    moves.append(("Decision Models/README.md", "Learning/Decision Models/00 - Decision Models Index.md"))
    for name in RESEARCH_FILES:
        moves.append((f"Decision Models/Research/{name}", f"Learning/Decision Models/Research/{name}"))
    for name in ARCHIVE_ENTRIES:
        moves.append((name, f"Archive/{name}"))
    return moves


def rewrite_links(text: str) -> str:
    def repl(m: re.Match) -> str:
        raw = m.group(1)
        alias = ""
        target = raw
        if "|" in raw:
            target, alias = raw.split("|", 1)
        anchor = ""
        if "#" in target:
            target, anchor = target.split("#", 1)
        target = target.strip()
        anchor = anchor.strip()
        new = target
        if new.startswith("Learning/"):
            return m.group(0)          # already migrated - leave it alone
        for old, rep in LINK_RULES:
            if new == old:
                new = rep
                break
        else:
            for old, rep in PREFIX_RULES:
                if new.startswith(old):
                    new = rep + new[len(old):]
                    break
        out = f"[[{new}"
        if anchor:
            out += f"#{anchor}"
        if alias:
            out += f"|{alias}"
        return out + "]]"
    return LINK_RE.sub(repl, text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--vault", default=str(VAULT))
    args = ap.parse_args()
    vault = Path(args.vault)
    if not vault.is_dir():
        print(f"vault not found: {vault}")
        return 2

    moves = plan_moves()

    print("=== MOVE PLAN ===")
    for src, dst in moves:
        s = vault / src
        d = vault / dst
        status = "ok " if s.exists() else "MISS"
        print(f"  [{status}] {src}  ->  {dst}")
    missing = [s for s, _ in moves if not (vault / s).exists()]
    if missing:
        print(f"\n{len(missing)} source(s) missing; re-run after they exist.")
        if args.dry_run:
            return 0

    if args.dry_run:
        print("\n(dry run - nothing changed)")
        return 0

    for d in ("Learning/Foundations", "Learning/Decision Models/Research",
              "Learning/Course - Decision Models", "Learning/Graph", "Archive"):
        (vault / d).mkdir(parents=True, exist_ok=True)

    for src, dst in moves:
        s, d = vault / src, vault / dst
        if not s.exists():
            continue
        d.parent.mkdir(parents=True, exist_ok=True)
        if d.exists():
            print(f"  skip (dest exists): {dst}")
            continue
        shutil.move(str(s), str(d))
        print(f"  moved -> {dst}")

    # prune emptied source folders
    for old in ("AI Foundations", "Decision Models/Research", "Decision Models"):
        p = vault / old
        if p.is_dir() and not any(p.iterdir()):
            p.rmdir()
            print(f"  removed empty dir: {old}")

    # stub notes
    for rel, body in STUBS.items():
        p = vault / rel
        if p.exists():
            continue
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
        print(f"  stub created: {rel}")

    # Windows cannot put ':' in a filename - it becomes an alternate data stream
    # and the file body silently vanishes. Detect and report rather than ship a
    # broken note.
    for rel in list(STUBS):
        p = vault / rel
        if p.exists() and ":" in p.name:
            print(f"  WARNING: illegal ':' in filename -> {p.name}")

    # rewrite links everywhere
    changed = 0
    for p in vault.rglob("*.md"):
        if ".obsidian" in p.parts:
            continue
        original = p.read_text(encoding="utf-8", errors="replace")
        updated = rewrite_links(original)
        if updated != original:
            p.write_text(updated, encoding="utf-8")
            changed += 1
    print(f"  rewrote links in {changed} file(s)")

    print("\nMigration applied. Now run the gate:")
    print('  python tools/check_links.py')
    return 0


if __name__ == "__main__":
    sys.exit(main())
