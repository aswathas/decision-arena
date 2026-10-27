"""Check a commit message against the house shape.

    python tools/check_commit.py <message-file>              # check a message
    python tools/check_commit.py <message-file> --staged     # also use the staged files
    python tools/check_commit.py --message "subject"         # check a subject only

Used by the commit-msg hook in .githooks/, and usable by hand. It never
rewrites a message: it says what is missing.

The rules, and why each one exists:

  - a subject under 72 characters, because it has to survive a terminal and a
    GitHub list;
  - a subject that is prose, not a placeholder, because "wip" tells a reader
    nothing in three months;
  - a "Workstream:" line when the commit touches an agent-owned file, because
    a parallel build has to be readable per workstream;
  - a "Gates:" section when the commit is more than three files, because a
    reader must be able to re-run the proof.

Costs: file reads only. No network, no writes.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

MAX_SUBJECT = 72

# Subjects that say nothing. A commit may be small, but it may not be opaque.
PLACEHOLDERS = {
    "wip", "fix", "fixes", "fixed", "update", "updates", "updated", "temp",
    "tmp", "test", "testing", "changes", "minor", "stuff", "asdf", "todo",
    "...", ".", "commit", "misc", "cleanup", "clean up", "improve",
}

# The paths a workstream owns. A commit that touches one of these and does not
# say whose work it is has lost the one line a reader needs.
OWNED_PREFIXES = (
    os.path.join("course", "lessons"),
    os.path.join("site", "src", "figures"),
    os.path.join("site", "public", "illustrations"),
)

WORKSTREAM_RE = re.compile(r"^Workstream:(.*)$", re.MULTILINE)
GATES_RE = re.compile(r"^(Gates|Verified):", re.MULTILINE)
SUBJECT_RE = re.compile(r"^[^\n]+")


def staged_files() -> list[str]:
    """The paths in the index, as git sees them."""
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]


def check_subject(subject: str) -> list[str]:
    """Return the problems with a subject line."""
    problems: list[str] = []
    if not subject.strip():
        return ["the commit has no subject"]
    if len(subject) > MAX_SUBJECT:
        problems.append("the subject is %d characters, and the limit is %d"
                        % (len(subject), MAX_SUBJECT))
    if subject.endswith("."):
        problems.append("the subject ends with a period")
    bare = subject.strip().strip(".").lower()
    if bare in PLACEHOLDERS:
        problems.append("the subject %r is a placeholder; say what changed" % subject)
    if re.match(r"^(fix|feat|chore|docs|style|refactor|test)\(", subject, re.IGNORECASE):
        problems.append("the subject uses a conventional-commit prefix; this repo writes prose")
    if subject.strip() != subject:
        problems.append("the subject has leading or trailing whitespace")
    return problems


def check_message(message: str, files: list[str]) -> list[str]:
    """Return the problems with a whole commit message."""
    problems: list[str] = []
    parts = message.split("\n\n", 1)
    subject = SUBJECT_RE.match(parts[0]).group(0) if parts[0].strip() else ""
    problems += check_subject(subject)

    body = parts[1] if len(parts) > 1 else ""
    if not body.strip():
        if len(files) > 1:
            problems.append("the commit touches %d files and has no body; say what changed"
                            % len(files))
        return problems

    owned = [f for f in files
             if f.replace("/", os.sep).startswith(OWNED_PREFIXES)
             or f.replace(os.sep, "/").startswith(tuple(p.replace(os.sep, "/") for p in OWNED_PREFIXES))]
    if owned:
        match = WORKSTREAM_RE.search(body)
        if not match:
            problems.append("the commit touches %d workstream-owned file(s) and has no "
                            "'Workstream:' line; say whose work this is" % len(owned))
        elif not match.group(1).strip():
            problems.append("the 'Workstream:' line is empty")

    if len(files) > 3 and not GATES_RE.search(body):
        problems.append("the commit touches %d files and has no 'Gates:' section; name the "
                        "commands that proved it" % len(files))
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="check_commit",
                                 description="check a commit message against the house shape")
    ap.add_argument("message_file", nargs="?", help="the file holding the commit message")
    ap.add_argument("--message", help="check a subject string instead of a file")
    ap.add_argument("--staged", action="store_true",
                    help="also check the files in the index")
    args = ap.parse_args(argv)

    if args.message:
        message = args.message
    elif args.message_file:
        if not os.path.isfile(args.message_file):
            print("no such file: %s" % args.message_file)
            return 1
        with open(args.message_file, "r", encoding="utf-8") as handle:
            message = handle.read()
    else:
        ap.error("give a message file or --message")

    files = staged_files() if args.staged else []
    problems = check_message(message, files)

    if problems:
        print("commit message rejected:")
        for problem in problems:
            print("  - %s" % problem)
        print()
        print("The house shape is in skills/commit-history/references/message-format.md")
        return 1

    print("commit message is fine")
    return 0


if __name__ == "__main__":
    sys.exit(main())
