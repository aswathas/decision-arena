"""Check Obsidian wikilinks in a vault for broken targets.

WHAT THIS DOES
    Scans every markdown note in an Obsidian vault for wikilinks of the form
    [[Target]] and [[Target|Alias]], resolves each target against the vault's
    note paths, and reports the broken ones with their source file and line
    number. Exit code 0 when there are no broken links, 1 when there are -
    so it can be used as a CI gate.

RESOLUTION RULES
    A link target is resolved if it matches a note:
      * by full relative path WITHOUT the .md extension
        e.g. [[Decision Models/README]] -> "Decision Models/README.md"
      * by basename (with or without extension)
        e.g. [[README]] -> any note called README.md
      * Obsidian's own "shortest path" rule: a path suffix match, e.g.
        [[Research/Claims Ledger]] matches "Decision Models/Research/Claims Ledger.md"
    Heading and block references are stripped before resolving:
      [[Target#heading]]   -> target "Target"
      [[Target#^blockid]]  -> target "Target"
      [[#heading]]         -> a link inside the SAME note; never broken

IGNORED
    Links inside fenced code blocks (``` ... ```) are skipped, so example
    scripts embedded in notes do not produce false positives.

READ-ONLY
    This script never writes to the vault. It only reads.

Usage:
    python tools/check_links.py
    python tools/check_links.py --vault "C:\\path\\to\\vault"
    python tools/check_links.py --json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

DEFAULT_VAULT = r"C:\Users\aswat\Aswaths Obsidian Den\Aswaths Mountain Den"

# [[Target]] or [[Target|Alias]] - the alias is part of the link text.
WIKILINK_RE = re.compile(r"\[\[([^\[\]]+?)\]\]")

# A fenced code block delimiter: ``` or ~~~ (optionally indented).
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")


def iter_markdown_files(vault: str):
    """Yield every .md file under the vault, as (abs_path, rel_path).

    Hidden folders and the Obsidian config folder are skipped - they never
    hold notes you link to.
    """
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != ".obsidian"]
        for name in files:
            if not name.lower().endswith(".md"):
                continue
            abs_path = os.path.join(root, name)
            rel_path = os.path.relpath(abs_path, vault).replace(os.sep, "/")
            yield abs_path, rel_path


def build_index(rel_paths: list[str]):
    """Build the lookup tables used to resolve a link target.

    Returns (by_path, by_basename):
      by_path       - {"decision models/readme": "Decision Models/README.md"}
                      keys are lowercased relative paths without ".md"
      by_basename   - {"readme": ["Decision Models/README.md", ...]}
                      keys are lowercased basenames without ".md"
    """
    by_path: dict[str, str] = {}
    by_basename: dict[str, list[str]] = {}
    for rel in rel_paths:
        no_ext = rel[:-3] if rel.lower().endswith(".md") else rel
        key = no_ext.lower()
        by_path[key] = rel
        base = no_ext.rsplit("/", 1)[-1].lower()
        by_basename.setdefault(base, []).append(rel)
    return by_path, by_basename


def resolve(target: str, by_path: dict[str, str], by_basename: dict[str, list[str]]) -> bool:
    """Return True if the link target points at an existing note.

    Try, in order:
      1. exact relative path without the .md extension
      2. basename (with the extension still attached, e.g. "README.md")
      3. basename without the extension
      4. a path SUFFIX match, which is Obsidian's "shortest unique path" rule
         (e.g. "Research/Claims Ledger" -> "Decision Models/Research/Claims Ledger.md")
    """
    if not target:
        return False
    t = target.strip().replace("\\", "/")
    if t.lower().endswith(".md"):
        t = t[:-3]

    if t.lower() in by_path:
        return True

    base = t.rsplit("/", 1)[-1]
    if base.lower() in by_basename:
        return True

    # suffix match: any note whose path ends with "/<target>"
    suffix = "/" + t.lower()
    for key in by_path:
        if key.endswith(suffix):
            return True
    return False


def strip_alias(raw: str) -> str:
    """Split [[Target|Alias]] into "Target".

    Obsidian's alias syntax puts the DISPLAY text after a pipe; only the part
    before the pipe is the link target. Aliases may themselves contain a
    pipe-free text with "#", so split the alias off FIRST.
    """
    if "|" in raw:
        target, _, _alias = raw.partition("|")
        return target
    return raw


def strip_anchor(target: str) -> tuple[str, str]:
    """Split a raw link target into (note target, anchor).

    [[Target#heading]]  -> ("Target", "#heading")
    [[Target#^block]]   -> ("Target", "#^block")
    [[#heading]]        -> ("", "#heading")   - same-note link
    """
    if "#" not in target:
        return target.strip(), ""
    note, _, anchor = target.partition("#")
    return note.strip(), "#" + anchor


def find_links(text: str):
    """Yield (line_number, raw_target) for every wikilink outside code fences.

    Fenced code blocks are tracked line by line: a line that opens a fence
    (``` or ~~~) turns the fence ON until a matching closing fence turns it
    OFF. Everything in between is ignored.
    """
    fence: str | None = None
    for lineno, line in enumerate(text.splitlines(), start=1):
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = marker[0] * 3      # ``` or ~~~
                continue                   # the fence line itself is not code
            if marker.startswith(fence[0] * 3):
                fence = None
                continue
        if fence is not None:
            continue                       # inside a code block - ignore
        for m in WIKILINK_RE.finditer(line):
            yield lineno, m.group(1)


def scan(vault: str):
    """Scan the vault. Returns a report dict."""
    files = list(iter_markdown_files(vault))
    rel_paths = [rel for _, rel in files]
    by_path, by_basename = build_index(rel_paths)

    total = 0
    resolved = 0
    broken = []
    same_note = 0

    for abs_path, rel_path in files:
        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        for lineno, raw in find_links(text):
            total += 1
            # order matters: the alias is stripped first, then the anchor
            note_target, anchor = strip_anchor(strip_alias(raw))
            if not note_target:
                # [[#heading]] - a link to a heading inside THIS note.
                same_note += 1
                resolved += 1
                continue
            if resolve(note_target, by_path, by_basename):
                resolved += 1
            else:
                broken.append({
                    "file": rel_path,
                    "line": lineno,
                    "target": note_target,
                    "raw": raw,
                })

    return {
        "vault": vault,
        "notes": len(files),
        "total_links": total,
        "resolved_links": resolved,
        "broken_links": len(broken),
        "same_note_links": same_note,
        "broken": broken,
    }


def print_report(report: dict) -> None:
    print(f"vault            : {report['vault']}")
    print(f"notes scanned    : {report['notes']}")
    print(f"total links      : {report['total_links']}")
    print(f"resolved links   : {report['resolved_links']}"
          f"  (includes {report['same_note_links']} same-note [[#heading]] links)")
    print(f"broken links     : {report['broken_links']}")
    print()
    if not report["broken"]:
        print("OK - no broken wikilinks.")
        return
    print("BROKEN LINKS")
    print("-" * 78)
    for b in report["broken"]:
        print(f"  {b['file']}:{b['line']}  [[{b['raw']}]]")
    print("-" * 78)
    print(f"{report['broken_links']} broken link(s).")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="check_links",
        description="Report broken Obsidian wikilinks in a vault (read-only).")
    ap.add_argument("--vault", default=DEFAULT_VAULT,
                    help=f"path to the Obsidian vault (default: {DEFAULT_VAULT})")
    ap.add_argument("--json", action="store_true",
                    help="emit machine-readable JSON instead of text")
    args = ap.parse_args(argv)

    if not os.path.isdir(args.vault):
        print(f"vault not found: {args.vault}", file=sys.stderr)
        return 2

    report = scan(args.vault)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    # CI gate: 0 = clean, 1 = broken links found.
    return 1 if report["broken_links"] else 0


if __name__ == "__main__":
    sys.exit(main())
