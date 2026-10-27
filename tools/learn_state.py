"""Learner progress and feedback engine for Decision Arena Academy.

One JSON file (``learning/progress.json``) is the machine-readable state of a
learner's journey through the course. This module is the only thing that
writes it, so the rules stay in one place:

  * which lesson is next, and WHY
  * per-concept mastery (0.0 - 1.0)
  * the review queue (what the learner has not got yet)
  * the feedback note that closes a session

Command line:

    python tools/learn_state.py init --learner aswath --path beginner
    python tools/learn_state.py start L12
    python tools/learn_state.py grade L12 --answers 1,0,1
    python tools/learn_state.py record L12 --quiz-score 0.67 --artifact docs/notes/softmax.md
    python tools/learn_state.py next
    python tools/learn_state.py review
    python tools/learn_state.py status
    python tools/learn_state.py feedback
    python tools/learn_state.py log --lesson L12 --summary "softmax finally clicked"

Costs: pure file IO, no network, no third-party imports.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import course_lib as cl  # noqa: E402


def now() -> str:
    """Current UTC timestamp, ISO-8601 to the second.

    Uses timezone-aware now() rather than the deprecated utcnow(), so it is
    correct on Python 3.9 and warning-free on 3.12+.
    """
    stamp = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    return stamp.isoformat().replace("+00:00", "Z")


# ------------------------------------------------------------------ helpers
def _concepts_of(lesson: dict) -> list:
    return list(lesson.get("concepts") or [])


def _update_concept(doc: dict, concept: str, score: float) -> None:
    """Fold a new score into a concept's mastery.

    Recent evidence counts more, but a single bad quiz does not erase a
    concept the learner has already demonstrated: the new score is weighted
    0.6 and the history 0.4.
    """
    concepts = doc.setdefault("concepts", {})
    prior = concepts.get(concept)
    if prior is None:
        concepts[concept] = round(score, 4)
    else:
        concepts[concept] = round(0.4 * float(prior) + 0.6 * score, 4)


def _record_attempt(doc: dict, lesson_id: str, score) -> None:
    entry = doc.setdefault("lessons", {}).setdefault(
        lesson_id, {"status": "in_progress", "attempts": 0, "concepts": {}})
    entry["attempts"] = int(entry.get("attempts", 0)) + 1
    if score is not None:
        entry["last_score"] = round(float(score), 4)
        entry["scores"] = list(entry.get("scores", [])) + [round(float(score), 4)]


def _sync_review_queue(doc: dict, lesson: dict, score, missed: list) -> None:
    """Add or clear a review entry for this lesson.

    A lesson goes into the queue when the quiz score is below the pass mark,
    or when specific concepts were missed. It leaves the queue when the
    learner scores at or above the strong mark with no missed concepts.
    """
    queue = doc.setdefault("review_queue", [])
    lesson_id = lesson["id"]
    existing = next((q for q in queue if q.get("lesson") == lesson_id), None)

    weak = score is not None and float(score) < cl.MASTERY_PASS
    if weak or missed:
        if existing is None:
            existing = {"lesson": lesson_id, "title": lesson.get("title"),
                        "added_at": now(), "hits": 0}
            queue.append(existing)
        existing["hits"] = int(existing.get("hits", 0)) + 1
        existing["reason"] = ("missed concepts: %s" % ", ".join(missed)) if missed \
            else "quiz score %.0f%% (pass mark %d%%)" % (float(score) * 100,
                                                         cl.MASTERY_PASS * 100)
        existing["concepts"] = sorted(set((existing.get("concepts") or []) + missed))
        existing["resolved"] = False
    elif score is not None and float(score) >= cl.MASTERY_STRONG:
        if existing is not None:
            existing["resolved"] = True
            existing["resolved_at"] = now()


def _profile(doc: dict) -> str:
    """Coarse learner profile from the last few scored lessons.

    'steady'   - scoring fine, nothing needs review
    'shaky'    - some concepts below the pass mark, review needed
    'stalled'  - same lesson attempted three or more times without a pass
    """
    lessons = doc.get("lessons") or {}
    scores = [l["last_score"] for l in lessons.values() if l.get("last_score") is not None]
    queue = [q for q in doc.get("review_queue", []) if not q.get("resolved")]
    stalled = any(int(l.get("attempts", 0)) >= 3 and (l.get("last_score") or 0) < cl.MASTERY_PASS
                  for l in lessons.values())
    if stalled:
        return "stalled"
    if queue:
        return "shaky"
    if scores and sum(scores) / len(scores) < cl.MASTERY_PASS:
        return "shaky"
    return "steady"


def _weakest_concepts(doc: dict, limit: int = 5) -> list:
    concepts = doc.get("concepts") or {}
    weak = [(c, s) for c, s in concepts.items() if float(s) < cl.MASTERY_PASS]
    weak.sort(key=lambda kv: kv[1])
    return weak[:limit]


def _unlocked_concepts(doc: dict) -> list:
    concepts = doc.get("concepts") or {}
    return sorted(c for c, s in concepts.items() if float(s) >= cl.MASTERY_PASS)


# ----------------------------------------------------------------- grading
def grade_lesson(lesson_id: str, answers: list) -> dict:
    """Grade a set of answers against a lesson's quiz.

    `answers` is a list of zero-based option indexes, in question order.

    Returns a dict with the score, per-question verdicts and explanations.
    Callers must not show any of this before the learner has answered.
    """
    quiz = cl.load_quiz(lesson_id)
    questions = quiz.get("questions") or []
    rows = []
    correct = 0
    for i, q in enumerate(questions):
        picked = answers[i] if i < len(answers) else None
        ok = picked is not None and int(picked) == int(q.get("answer"))
        if ok:
            correct += 1
        rows.append({
            "question_id": q.get("id"),
            "concept": q.get("concept"),
            "prompt": q.get("prompt"),
            "picked": picked,
            "correct_answer": q.get("answer"),
            "ok": ok,
            "explain": q.get("explain", ""),
        })
    total = len(questions)
    score = (correct / total) if total else 0.0
    missed_concepts = sorted({r["concept"] for r in rows if not r["ok"] and r["concept"]})
    return {
        "lesson_id": lesson_id,
        "total": total,
        "correct": correct,
        "score": round(score, 4),
        "rows": rows,
        "missed_concepts": missed_concepts,
    }


# ---------------------------------------------------------------- commands
def cmd_init(args) -> int:
    if cl.load_progress() and not args.force:
        print("progress already exists at %s (use --force to start over; "
              "the old file is archived, never deleted)" % cl.PROGRESS_PATH)
        return 1
    doc = cl.empty_progress(args.learner, args.path)
    doc["created_at"] = now()
    doc["updated_at"] = now()
    path = cl.save_progress(doc)
    print("started a learning path: %s (%s)" % (args.path, cl.PATH_LABELS.get(args.path, "")))
    print("progress file: %s" % path)
    print("next: python tools/learn_state.py next")
    return 0


def cmd_start(args) -> int:
    doc = cl.load_progress()
    if doc is None:
        print("no progress yet - run: python tools/learn_state.py init --learner <name>")
        return 1
    lessons = cl.load_lessons()
    lesson = cl.lesson_by_id(lessons, args.lesson)
    if lesson is None:
        print("unknown lesson: %s" % args.lesson)
        return 1
    entry = doc.setdefault("lessons", {}).setdefault(
        lesson["id"], {"status": "in_progress", "attempts": 0, "concepts": {}})
    if entry.get("status") != "done":
        entry["status"] = "in_progress"
        entry["started_at"] = now()
    doc["updated_at"] = now()
    cl.save_progress(doc)
    print("lesson %s marked in progress: %s" % (lesson["id"], lesson["title"]))
    print("brief: %s" % lesson["_rel"])
    return 0


def cmd_grade(args) -> int:
    if not os.path.exists(cl.PROGRESS_PATH):
        print("no progress yet - run: python tools/learn_state.py init --learner <name>")
        return 1
    answers = [a.strip() for a in args.answers.split(",") if a.strip() != ""]
    try:
        answers = [int(a) for a in answers]
    except ValueError:
        print("--answers must be comma-separated option indexes, e.g. 1,0,2")
        return 2
    try:
        result = grade_lesson(args.lesson, answers)
    except FileNotFoundError:
        print("no quiz file for lesson %s" % args.lesson)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def cmd_record(args) -> int:
    doc = cl.load_progress()
    if doc is None:
        print("no progress yet - run: python tools/learn_state.py init --learner <name>")
        return 1
    lessons = cl.load_lessons()
    lesson = cl.lesson_by_id(lessons, args.lesson)
    if lesson is None:
        print("unknown lesson: %s" % args.lesson)
        return 1

    score = None
    missed = []
    if args.answers:
        try:
            answers = [int(a.strip()) for a in args.answers.split(",") if a.strip() != ""]
        except ValueError:
            print("--answers must be comma-separated option indexes")
            return 2
        graded = grade_lesson(lesson["id"], answers)
        score = graded["score"]
        missed = graded["missed_concepts"]
    elif args.quiz_score is not None:
        score = float(args.quiz_score)

    _record_attempt(doc, lesson["id"], score)
    entry = doc["lessons"][lesson["id"]]
    entry["status"] = "done"
    entry["completed_at"] = now()
    if args.notes:
        entry["notes"] = args.notes

    if score is not None:
        for concept in _concepts_of(lesson):
            _update_concept(doc, concept, score)

    if args.artifact:
        arts = doc.setdefault("artifacts", [])
        arts.append({"lesson": lesson["id"], "path": args.artifact, "at": now()})
        entry["artifact"] = args.artifact

    _sync_review_queue(doc, lesson, score, missed)
    doc["updated_at"] = now()
    doc["sessions"].append({"at": now(), "lesson": lesson["id"],
                             "score": score, "artifact": args.artifact})
    cl.save_progress(doc)

    print("recorded %s: score=%s artifact=%s"
          % (lesson["id"], score if score is not None else "n/a",
             args.artifact or "none"))
    if missed:
        print("missed concepts: %s" % ", ".join(missed))
    print("run: python tools/learn_state.py feedback")
    return 0


def cmd_next(args) -> int:
    doc = cl.load_progress()
    if doc is None:
        print("no progress yet - run: python tools/learn_state.py init --learner <name>")
        return 1
    lessons = cl.load_lessons()
    path = doc.get("path") or "beginner"
    done = doc.get("lessons") or {}
    order = [m for m in lessons if path in (m.get("paths") or [])] or lessons
    nxt = None
    for m in order:
        if (done.get(m["id"]) or {}).get("status") != "done":
            nxt = m
            break
    queue = [q for q in doc.get("review_queue", []) if not q.get("resolved")]
    if args.json:
        print(json.dumps({
            "next": None if nxt is None else {"id": nxt["id"], "title": nxt["title"],
                                             "file": nxt["_rel"], "minutes": nxt.get("minutes")},
            "review_queue": queue,
            "profile": _profile(doc),
        }, indent=2, ensure_ascii=False))
        return 0
    if queue:
        q = queue[0]
        print("BEFORE the next lesson, review: %s (%s)" % (q["lesson"], q.get("reason", "")))
        print("  brief: %s" % _brief_for(lessons, q["lesson"]))
    if nxt is None:
        print("path '%s' complete. Every lesson in this path is done." % path)
        print("next: python tools/learn_state.py status")
        return 0
    print("NEXT LESSON: %s - %s" % (nxt["id"], nxt["title"]))
    print("  brief    : %s" % nxt["_rel"])
    print("  minutes  : %s" % nxt.get("minutes"))
    print("  concepts : %s" % ", ".join(_concepts_of(nxt)))
    prereqs = nxt.get("prereqs") or []
    if prereqs:
        print("  prereqs  : %s" % ", ".join(prereqs))
    return 0


def _brief_for(lessons: list, lesson_id: str) -> str:
    m = cl.lesson_by_id(lessons, lesson_id)
    return m["_rel"] if m else "unknown"


def cmd_review(args) -> int:
    doc = cl.load_progress()
    if doc is None:
        print("no progress yet - run: python tools/learn_state.py init --learner <name>")
        return 1
    queue = [q for q in doc.get("review_queue", []) if not q.get("resolved")]
    if not queue:
        print("review queue is empty - nothing to go back to.")
        return 0
    weak = _weakest_concepts(doc)
    queue.sort(key=lambda q: (min([doc.get("concepts", {}).get(c, 1.0)
                                   for c in (q.get("concepts") or [])] or [1.0]),
                               -int(q.get("hits", 0))))
    if args.json:
        print(json.dumps({"queue": queue, "weakest_concepts": weak,
                          "profile": _profile(doc)}, indent=2, ensure_ascii=False))
        return 0
    print("REVIEW QUEUE (%d item(s))" % len(queue))
    for q in queue:
        print("  %s %s" % (q["lesson"], q.get("title", "")))
        print("      reason   : %s" % q.get("reason", ""))
        print("      brief    : %s" % _brief_for(cl.load_lessons(), q["lesson"]))
        print("      hits     : %s" % q.get("hits", 1))
    if weak:
        print("\nweakest concepts right now:")
        for c, s in weak:
            print("  %-28s %.0f%%" % (c, float(s) * 100))
    return 0


def cmd_status(args) -> int:
    doc = cl.load_progress()
    if doc is None:
        print("no progress yet - run: python tools/learn_state.py init --learner <name>")
        return 1
    lessons = cl.load_lessons()
    path = doc.get("path") or "beginner"
    order = [m for m in lessons if path in (m.get("paths") or [])] or lessons
    done = doc.get("lessons") or {}
    done_ids = [k for k, v in done.items() if v.get("status") == "done"]
    by_phase = {}
    for m in order:
        ph = int(m.get("phase", 0))
        slot = by_phase.setdefault(ph, {"total": 0, "done": 0})
        slot["total"] += 1
        if m["id"] in done_ids:
            slot["done"] += 1
    unlocked = _unlocked_concepts(doc)
    weak = _weakest_concepts(doc)
    queue = [q for q in doc.get("review_queue", []) if not q.get("resolved")]
    payload = {
        "learner": doc.get("learner"),
        "path": path,
        "lessons_done": len(done_ids),
        "lessons_total": len(order),
        "phases": {str(k): v for k, v in sorted(by_phase.items())},
        "concepts_unlocked": unlocked,
        "concepts_weak": [{"concept": c, "score": s} for c, s in weak],
        "review_queue": len(queue),
        "profile": _profile(doc),
        "artifacts": len(doc.get("artifacts", [])),
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0
    print("learner : %s" % payload["learner"])
    print("path    : %s" % path)
    print("lessons : %d/%d done" % (payload["lessons_done"], payload["lessons_total"]))
    print("profile : %s" % payload["profile"])
    print("artifacts published: %d" % payload["artifacts"])
    print("\nby phase:")
    for ph, slot in sorted(by_phase.items()):
        bar = "#" * slot["done"] + "." * (slot["total"] - slot["done"])
        print("  phase %-2s %-46s %s %d/%d" % (ph, cl.PHASE_TITLES.get(ph, ""), bar,
                                              slot["done"], slot["total"]))
    if unlocked:
        print("\nunlocked concepts (%d): %s" % (len(unlocked), ", ".join(unlocked)))
    if weak:
        print("weak concepts (%d): %s" % (len(weak),
              ", ".join("%s %.0f%%" % (c, float(s) * 100) for c, s in weak)))
    if queue:
        print("review queue: %d item(s) - run: python tools/learn_state.py review" % len(queue))
    return 0


def cmd_feedback(args) -> int:
    """Print the closing feedback note for a session."""
    doc = cl.load_progress()
    if doc is None:
        print("no progress yet - run: python tools/learn_state.py init --learner <name>")
        return 1
    profile = _profile(doc)
    unlocked = _unlocked_concepts(doc)
    weak = _weakest_concepts(doc)
    queue = [q for q in doc.get("review_queue", []) if not q.get("resolved")]
    lessons = cl.load_lessons()
    order = [m for m in lessons if (doc.get("path") or "beginner") in (m.get("paths") or [])]
    done = doc.get("lessons") or {}
    nxt = next((m for m in order if (done.get(m["id"]) or {}).get("status") != "done"), None)

    lines = []
    lines.append("FEEDBACK")
    lines.append("")
    if unlocked:
        lines.append("You now have: %s" % ", ".join(unlocked))
    else:
        lines.append("No concept is fully unlocked yet - that is fine, the first lesson "
                     "is where the map gets drawn.")
    if weak:
        lines.append("Still shaky: %s"
                     % ", ".join("%s (%.0f%%)" % (c, float(s) * 100) for c, s in weak))
    if queue:
        lines.append("Go back to: %s" % ", ".join(q["lesson"] for q in queue))
    lines.append("")

    if profile == "stalled":
        lines.append("PATTERN: you have tried the same lesson three times without "
                     "clearing the pass mark.")
        lines.append("Do not grind it. Ask for a DIFFERENT explanation of that one "
                     "concept, rebuild it from a smaller piece, then come back.")
    elif profile == "shaky":
        lines.append("PATTERN: the new material is going in faster than the old "
                     "material is settling.")
        lines.append("Spend one short session on the review queue before the next "
                     "new lesson.")
    else:
        lines.append("PATTERN: steady. Keep the pace - one lesson, one artifact, "
                     "one explanation you could give to a friend.")

    if nxt:
        lines.append("")
        lines.append("NEXT: %s - %s (%s)" % (nxt["id"], nxt["title"], nxt["_rel"]))
    else:
        lines.append("")
        lines.append("NEXT: your path is complete. Pick a new path or publish a finding.")
    text = "\n".join(lines)
    if args.json:
        print(json.dumps({"profile": profile, "unlocked": unlocked,
                          "weak": [{"concept": c, "score": s} for c, s in weak],
                          "queue": queue,
                          "next": None if nxt is None else {"id": nxt["id"],
                                                           "title": nxt["title"]}},
                         indent=2, ensure_ascii=False))
    else:
        print(text)
    return 0


def cmd_log(args) -> int:
    """Append one session to learning/build_log.md (append only, never rewritten)."""
    os.makedirs(cl.LEARN_DIR, exist_ok=True)
    entry = "\n## %s - %s\n\n**Lesson:** %s\n**What I wrote:** %s\n**Concept unlocked:** %s\n" % (
        datetime.date.today().isoformat(),
        args.title or args.lesson,
        args.lesson,
        args.summary or "(not stated)",
        args.concept or "(not stated)")
    if args.note:
        entry += "**Note:** %s\n" % args.note
    entry += "\n"
    with open(cl.BUILD_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry)
    print("appended to %s" % cl.BUILD_LOG_PATH)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="learn_state",
                                 description="Decision Arena Academy progress engine")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="start a learning path")
    p.add_argument("--learner", required=True)
    p.add_argument("--path", default="beginner", choices=list(cl.PATH_ORDER))
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("start", help="mark a lesson in progress")
    p.add_argument("lesson")
    p.set_defaults(func=cmd_start)

    p = sub.add_parser("grade", help="grade a quiz attempt (prints the answers)")
    p.add_argument("lesson")
    p.add_argument("--answers", required=True,
                   help="comma-separated zero-based option indexes, in question order")
    p.set_defaults(func=cmd_grade)

    p = sub.add_parser("record", help="record a finished lesson")
    p.add_argument("lesson")
    p.add_argument("--quiz-score", type=float, default=None)
    p.add_argument("--answers", default=None,
                   help="if given, the quiz is graded here and the score is used")
    p.add_argument("--artifact", default=None)
    p.add_argument("--notes", default=None)
    p.set_defaults(func=cmd_record)

    p = sub.add_parser("next", help="what to learn next, and why")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_next)

    p = sub.add_parser("review", help="what to go back to")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_review)

    p = sub.add_parser("status", help="progress report")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("feedback", help="closing feedback note for a session")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_feedback)

    p = sub.add_parser("log", help="append to the build log")
    p.add_argument("--lesson", required=True)
    p.add_argument("--title", default=None)
    p.add_argument("--summary", default=None)
    p.add_argument("--concept", default=None)
    p.add_argument("--note", default=None)
    p.set_defaults(func=cmd_log)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
