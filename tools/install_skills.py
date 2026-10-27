"""Install the Academy skills into the hosts that can run them.

    python tools/install_skills.py --list
    python tools/install_skills.py                     # project-local (default)
    python tools/install_skills.py --target claude-user
    python tools/install_skills.py --target minimax-user
    python tools/install_skills.py --target all --force

Why the default is project-local: a global ``learn`` skill already exists on
this machine and drives a different course. Installing into the repo means
``/learn`` inside decision-arena is the Academy, and everywhere else the old
skill is untouched. Overwriting a global skill requires ``--force`` AND
``--target claude-user`` / ``--target minimax-user`` - and it still refuses if
the destination was not installed by this script.

Each installed copy gets a marker file so this script can tell its own
installs from someone else's skill.

Costs: file copy only. No network.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_SRC = os.path.join(REPO_ROOT, "skills")
MARKER = ".installed-by-decision-arena"

TARGETS = {
    "claude-project": ("Claude Code (this repo)", lambda: os.path.join(REPO_ROOT, ".claude", "skills")),
    "claude-user": ("Claude Code (your home dir)",
                    lambda: os.path.join(os.path.expanduser("~"), ".claude", "skills")),
    "minimax-user": ("MiniMax Code (your home dir)",
                     lambda: os.path.join(os.path.expanduser("~"), ".minimax", "skills")),
}


def available_skills() -> list:
    """Names of the skills in the repo's skills/ directory."""
    if not os.path.isdir(SKILLS_SRC):
        return []
    return sorted(n for n in os.listdir(SKILLS_SRC)
                  if os.path.isdir(os.path.join(SKILLS_SRC, n)))


def is_ours(dest: str) -> bool:
    """True when the destination directory carries our marker file."""
    return os.path.exists(os.path.join(dest, MARKER))


def install_skill(name: str, dest_root: str, force: bool = False) -> tuple:
    """Copy one skill into dest_root. Returns (ok, message)."""
    src = os.path.join(SKILLS_SRC, name)
    if not os.path.isdir(src):
        return False, "%s: no such skill in the repo" % name
    dest = os.path.join(dest_root, name)
    if os.path.exists(dest):
        if not is_ours(dest):
            if not force:
                return False, ("%s: %s already exists and was not installed by this "
                               "script - not touching it (use --force to override)"
                               % (name, dest))
        shutil.rmtree(dest)
    os.makedirs(dest_root, exist_ok=True)
    shutil.copytree(src, dest)
    with open(os.path.join(dest, MARKER), "w", encoding="utf-8") as f:
        f.write("installed by decision-arena tools/install_skills.py\n")
    return True, "%s -> %s" % (name, dest)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="install_skills",
                                 description="install the Academy skills into a host")
    ap.add_argument("--target", default="claude-project",
                    choices=list(TARGETS.keys()) + ["all"],
                    help="where to install. default: claude-project (this repo only)")
    ap.add_argument("--force", action="store_true",
                    help="overwrite a destination that this script did not install")
    ap.add_argument("--list", action="store_true", help="list the skills and the targets")
    args = ap.parse_args(argv)

    skills = available_skills()
    if args.list:
        print("skills in the repo:")
        for s in skills:
            print("  %s" % s)
        print("\ntargets:")
        for key, (label, path) in TARGETS.items():
            print("  %-16s %s" % (key, label))
            print("  %-16s %s" % ("", path()))
        return 0

    if not skills:
        print("no skills found in %s" % SKILLS_SRC)
        return 1

    targets = list(TARGETS.keys()) if args.target == "all" else [args.target]
    failures = 0
    for key in targets:
        label, path_fn = TARGETS[key]
        root = path_fn()
        print("%s (%s)" % (label, root))
        for name in skills:
            ok, msg = install_skill(name, root, force=args.force)
            print("  %s %s" % ("[ok]  " if ok else "[skip]", msg))
            if not ok:
                failures += 1
    if failures:
        print("\n%d install(s) skipped. Read the messages above." % failures)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
