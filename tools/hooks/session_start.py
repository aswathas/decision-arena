"""SessionStart hook: put the learner's course state in front of the agent.

Reads learning/progress.json and prints a short status block. When there is no
progress yet it prints one line telling the agent to onboard the learner.

Contract: print to stdout, exit 0, never crash. A hook that raises would block
the whole session, which is a far worse outcome than a missing status line.
"""
from __future__ import annotations

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROGRESS_PATH = os.path.join(REPO_ROOT, "learning", "progress.json")


def main() -> int:
    if not os.path.exists(PROGRESS_PATH):
        print("Decision Arena Academy: no learner progress yet. "
              "If the learner wants to learn, run the /learn onboarding "
              "(3 questions + placement quiz) and then create learning/progress.json "
              "with: python tools/learn_state.py init --learner <name> --path <path>")
        return 0
    try:
        with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
            doc = json.load(f)
    except (ValueError, OSError):
        print("Decision Arena Academy: progress file unreadable; ignore it and continue.")
        return 0

    lessons = doc.get("lessons") or {}
    done = [k for k, v in lessons.items() if v.get("status") == "done"]
    in_progress = [k for k, v in lessons.items() if v.get("status") == "in_progress"]
    queue = [q for q in doc.get("review_queue", []) if not q.get("resolved")]

    print("Decision Arena Academy")
    print("  learner : %s" % doc.get("learner"))
    print("  path    : %s" % doc.get("path"))
    print("  lessons : %d done" % len(done))
    if in_progress:
        print("  in progress: %s" % ", ".join(sorted(in_progress)))
    if queue:
        print("  review queue: %s" % ", ".join(q["lesson"] for q in queue))
    print("  next    : python tools/learn_state.py next")
    print("  status  : python tools/learn_state.py status")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # never break the session
        print("Decision Arena Academy hook: skipped (%s)" % exc)
        sys.exit(0)
