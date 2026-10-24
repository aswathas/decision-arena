"""Check that `AI-CONTEXT.md` is well-formed and that its evidence actually exists.

`--check` is the CI gate. It fails (exit 1) when:
  * the brief is missing, or has no YAML block
  * a required key is missing from the brief
  * a `verified_facts` entry has no `evidence` or no `verified_on`
  * an `evidence` path does not exist on disk

It cannot check whether a claim is *true* - only whether it is traceable. Truth is
the learner's job, and the evidence files are the proof.

Usage:
    python tools/sync_brief.py --check
    python tools/sync_brief.py            # human-readable report
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BRIEF = REPO / "AI-CONTEXT.md"
VAULT = Path(r"C:\Users\aswat\Aswaths Obsidian Den\Aswaths Mountain Den")

REQUIRED_KEYS = [
    "project", "purpose", "status", "verified_facts", "in_progress",
    "next_actions", "blocked_on", "commands_that_work", "do_not_touch",
]

FACT_KEYS = ["id", "claim", "evidence", "verified_on"]

# evidence strings look like: "runs/20261025-005316-mock.md, runs/other.json"
# or "tests/test_metrics.py via `python -m unittest discover -s tests`"
# Paths may contain spaces (Obsidian note titles), so allow them inside the match.
PATH_RE = re.compile(r"[\w./ -]+?\.(?:py|md|json|jsonl|toml|txt|yaml|yml)\b")


def evidence_exists(raw: str) -> bool:
    """An evidence path may be relative to the repo or to the Obsidian vault."""
    raw = raw.strip().strip("`")
    if (REPO / raw).exists():
        return True
    if (VAULT / raw).exists():
        return True
    return False


def parse_brief(text: str) -> tuple[str, str]:
    """Return (yaml_block, body_after_block)."""
    m = re.search(r"```yaml\n(.*?)\n```", text, flags=re.S)
    if not m:
        return "", text
    return m.group(1), text[m.end():]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit 1 on any problem")
    ap.add_argument("--brief", default=str(BRIEF))
    args = ap.parse_args()

    brief_path = Path(args.brief)
    problems: list[str] = []

    if not brief_path.is_file():
        print(f"FAIL: brief not found: {brief_path}")
        return 1

    text = brief_path.read_text(encoding="utf-8")
    yaml_block, _ = parse_brief(text)
    if not yaml_block:
        problems.append("no ```yaml block found in the brief")
        yaml_block = ""

    for key in REQUIRED_KEYS:
        if not re.search(rf"^\s*{re.escape(key)}\s*:", yaml_block, flags=re.M):
            problems.append(f"missing required key: {key}")

    # verified_facts entries
    facts_section = yaml_block
    m = re.search(r"^verified_facts:\s*$", yaml_block, flags=re.M)
    if m:
        rest = yaml_block[m.end():]
        stop = re.search(r"^\w+:\s*$", rest, flags=re.M)
        facts_section = rest[: stop.start()] if stop else rest
    entries = re.split(r"\n\s*-\s+id:", facts_section)
    entries = [e for e in entries if e.strip()]
    if not entries:
        problems.append("verified_facts has no entries")
    for e in entries:
        body = "id:" + e
        for key in FACT_KEYS:
            if key == "id":
                continue
            if not re.search(rf"^\s+{re.escape(key)}\s*:", body, flags=re.M):
                problems.append(f"verified_facts entry missing '{key}': "
                                f"{body.splitlines()[0][:60]}")

    # evidence paths must exist
    checked_paths = 0
    for e in entries:
        body = "id:" + e
        m2 = re.search(r"^\s+evidence\s*:\s*(.+)$", body, flags=re.M)
        if not m2:
            continue
        for raw in PATH_RE.findall(m2.group(1)):
            checked_paths += 1
            if not evidence_exists(raw):
                problems.append(f"evidence path does not exist: {raw}")

    print(f"brief: {brief_path}")
    print(f"required keys present: {len(REQUIRED_KEYS) - len([p for p in problems if p.startswith('missing required key')])}"
          f"/{len(REQUIRED_KEYS)}")
    print(f"verified_facts entries: {len(entries)}")
    print(f"evidence paths checked: {checked_paths}")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1 if args.check else 0
    print("\nOK: brief is well-formed and its evidence paths exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
