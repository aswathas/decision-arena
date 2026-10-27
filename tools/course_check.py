"""The course gate: validate every lesson, quiz and reference in the Academy.

    python tools/course_check.py --check     # validate, fail if anything is wrong
    python tools/course_check.py --index      # regenerate course/curriculum.json
    python tools/course_check.py --both       # regenerate, then validate

A lesson is only allowed to exist if it has all of these:

  * a valid front matter block with id / phase / title / minutes / concepts /
    prereqs / paths / exercise_file / quiz
  * every section in the required order: Why this matters, The naive story,
    What breaks, The real thing, In this repo, Your turn, Check yourself,
    Artifact
  * a quiz file with at least three questions, each with a prompt, options, a
    valid answer index and an explanation
  * prereqs that point at real lessons

This is the "never delete, always gate" rule of the repo applied to teaching
material: a broken lesson is worse than a missing lesson, because a learner
would trust it.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import course_lib as cl  # noqa: E402


def check_lessons(lessons: list) -> list:
    """Return a list of error strings for the lesson files."""
    errors = []
    seen_ids = set()

    for m in lessons:
        lid = m.get("id")
        fname = os.path.basename(m.get("_file", ""))
        tag = fname

        for key in cl.REQUIRED_FRONTMATTER:
            if key not in m or m[key] is None or m[key] == "":
                errors.append("%s: missing front-matter key '%s'" % (tag, key))
            elif key != "prereqs" and m[key] == []:
                # an empty prereq list is legal - the first lesson has none
                errors.append("%s: front-matter key '%s' must not be empty" % (tag, key))

        if lid:
            if lid in seen_ids:
                errors.append("%s: duplicate lesson id '%s'" % (tag, lid))
            seen_ids.add(lid)
            if not lid.startswith("L"):
                errors.append("%s: lesson id '%s' must start with 'L'" % (tag, lid))
            if not fname.startswith(lid + "-"):
                errors.append("%s: filename must start with the id '%s-'"
                              % (tag, lid))
            try:
                phase = int(m.get("phase"))
            except (TypeError, ValueError):
                errors.append("%s: phase must be an integer" % tag)
                phase = None
            if phase is not None and phase not in cl.PHASE_TITLES:
                errors.append("%s: phase %s is not a known phase %s"
                              % (tag, phase, sorted(cl.PHASE_TITLES)))

        paths = m.get("paths") or []
        if not paths:
            errors.append("%s: lesson must belong to at least one learning path" % tag)
        for p in paths:
            if p not in cl.PATH_ORDER:
                errors.append("%s: unknown path '%s' (known: %s)"
                              % (tag, p, ", ".join(cl.PATH_ORDER)))

        minutes = m.get("minutes")
        if not isinstance(minutes, int) or minutes <= 0:
            errors.append("%s: minutes must be a positive integer" % tag)

        # ---- body sections, in order
        sections = m.get("_sections") or {}
        for required in cl.REQUIRED_SECTIONS:
            if required not in sections:
                errors.append("%s: missing section '## %s'" % (tag, required))
            elif not sections[required].strip():
                errors.append("%s: section '## %s' is empty" % (tag, required))

        present = [s for s in sections if s in cl.REQUIRED_SECTIONS]
        expected = [s for s in cl.REQUIRED_SECTIONS if s in sections]
        if present != expected:
            errors.append("%s: sections are out of order" % tag)

        # ---- exercise file
        ex = m.get("exercise_file")
        if ex:
            ex_path = os.path.join(cl.REPO_ROOT, ex.replace("/", os.sep))
            if not os.path.exists(ex_path):
                # A file the learner is going to create does not exist yet.
                # Those paths are constrained to two known areas so a typo in
                # a real repo path still fails the gate.
                if not (ex.startswith("exercises/") or ex.startswith("docs/notes/")):
                    errors.append("%s: exercise_file '%s' does not exist and is not "
                                  "under exercises/ or docs/notes/ (learner-created "
                                  "files live there)" % (tag, ex))
            else:
                base = os.path.basename(ex)
                turn = (sections.get("Your turn") or "")
                if base not in turn:
                    errors.append("%s: '## Your turn' does not name the exercise "
                                  "file '%s'" % (tag, base))

        # ---- quiz reference
        if m.get("quiz") and lid and m["quiz"] != lid:
            errors.append("%s: quiz id '%s' must equal the lesson id '%s'"
                          % (tag, m["quiz"], lid))

    # ---- prereqs resolve AND come earlier in the order
    seen = set()
    for m in lessons:
        for pre in (m.get("prereqs") or []):
            tag = os.path.basename(m.get("_file", ""))
            if pre not in seen_ids:
                errors.append("%s: prereq '%s' does not exist" % (tag, pre))
            elif pre not in seen:
                errors.append("%s: prereq '%s' comes later in the order - a lesson "
                              "may never depend on a later one" % (tag, pre))
        seen.add(m["id"])

    return errors


def check_quizzes(lessons: list) -> list:
    """Return a list of error strings for the quiz files."""
    errors = []
    for m in lessons:
        lid = m.get("id")
        tag = os.path.basename(m.get("_file", ""))
        path = os.path.join(cl.QUIZZES_DIR, "%s.json" % lid)
        if not os.path.exists(path):
            errors.append("%s: missing quiz file course/quizzes/%s.json" % (tag, lid))
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                quiz = json.load(f)
        except ValueError as exc:
            errors.append("%s: quiz is not valid JSON (%s)" % (tag, exc))
            continue
        if quiz.get("lesson_id") != lid:
            errors.append("%s: quiz lesson_id must be '%s'" % (path, lid))
        questions = quiz.get("questions") or []
        if len(questions) < 3:
            errors.append("%s: a quiz needs at least 3 questions (has %d)"
                          % (path, len(questions)))
        concepts = set(m.get("concepts") or [])
        for i, q in enumerate(questions):
            qid = q.get("id") or ("q%d" % (i + 1))
            if not q.get("prompt"):
                errors.append("%s: %s has no prompt" % (path, qid))
            options = q.get("options") or []
            if len(options) < 2:
                errors.append("%s: %s needs at least 2 options" % (path, qid))
            if len(set(options)) != len(options):
                errors.append("%s: %s has duplicate options" % (path, qid))
            ans = q.get("answer")
            if not isinstance(ans, int) or not (0 <= ans < len(options)):
                errors.append("%s: %s answer index %r is out of range" % (path, qid, ans))
            if not q.get("explain"):
                errors.append("%s: %s has no explanation" % (path, qid))
            if concepts and q.get("concept") not in concepts:
                errors.append("%s: %s concept '%s' is not listed on the lesson"
                              % (path, qid, q.get("concept")))
    # orphan quizzes
    known = {m.get("id") for m in lessons}
    for qid in cl.quiz_ids():
        if qid not in known:
            errors.append("course/quizzes/%s.json: no lesson with id '%s'" % (qid, qid))
    return errors


def check_index() -> list:
    """Return errors when course/curriculum.json is out of date."""
    if not os.path.exists(cl.CURRICULUM_PATH):
        return ["course/curriculum.json is missing - run: python tools/course_check.py --index"]
    with open(cl.CURRICULUM_PATH, "r", encoding="utf-8") as f:
        try:
            committed = json.load(f)
        except ValueError as exc:
            return ["course/curriculum.json is not valid JSON (%s)" % exc]
    fresh = cl.build_index()
    if committed != fresh:
        return ["course/curriculum.json is stale - run: "
                "python tools/course_check.py --index"]
    return []


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="course_check",
                                 description="validate the Decision Arena Academy course")
    ap.add_argument("--check", action="store_true", help="validate only")
    ap.add_argument("--index", action="store_true", help="regenerate course/curriculum.json")
    ap.add_argument("--both", action="store_true", help="regenerate, then validate")
    args = ap.parse_args(argv)
    if not (args.check or args.index or args.both):
        args.check = True

    if args.index or args.both:
        path = cl.write_index()
        print("wrote %s" % os.path.relpath(path, cl.REPO_ROOT).replace("\\", "/"))

    if args.check or args.both:
        lessons = cl.load_lessons()
        errors = check_lessons(lessons) + check_quizzes(lessons) + check_index()
        if errors:
            print("COURSE CHECK FAILED - %d problem(s):\n" % len(errors))
            for e in errors:
                print("  - %s" % e)
            return 1
        print("course check passed: %d lessons, %d quizzes, index in sync"
              % (len(lessons), len(cl.quiz_ids())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
