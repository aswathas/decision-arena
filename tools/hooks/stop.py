"""Stop hook: remind the agent to close the learning loop.

When a lesson is marked in progress but has not been recorded, the session
ended with the loop half-open: the learner built something and the mastery was
never written down. This hook prints a one-line reminder so the agent can
record it before the session is forgotten.

It never blocks the session. It exits 0 always. A hook that blocks a stop
would trap the learner in a loop they cannot leave.
"""
from __future__ import annotations

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROGRESS_PATH = os.path.join(REPO_ROOT, "learning", "progress.json")


def main() -> int:
    if not os.path.exists(PROGRESS_PATH):
        return 0
    try:
        with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
            doc = json.load(f)
    except (ValueError, OSError):
        return 0
    lessons = doc.get("lessons") or {}
    open_lessons = sorted(k for k, v in lessons.items()
                           if v.get("status") == "in_progress")
    if not open_lessons:
        return 0
    print("Decision Arena Academy: lesson(s) %s are still marked in progress. "
          "If the learner finished, close the loop with "
          "`python tools/learn_state.py record <id> --answers <a,b,c> --artifact <path>`, "
          "then `python tools/learn_state.py log` and `... feedback`. "
          "If they are mid-way, leave it open - do not record what was not built."
          % ", ".join(open_lessons))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
