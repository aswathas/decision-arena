"""Tests for the Academy's course loader, gate and progress engine.

Stdlib only, no network, no third-party imports. These run alongside the
metric tests:

    python -m unittest discover -s tests -v
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))

import course_lib as cl  # noqa: E402
import course_check as cc  # noqa: E402
import learn_state as ls  # noqa: E402


class TestFrontmatter(unittest.TestCase):
    def test_parses_scalars_lists_and_folded_blocks(self):
        text = (
            "---\n"
            "id: L01\n"
            "phase: 2\n"
            "title: \"A quoted title\"\n"
            "minutes: 20\n"
            "concepts: [a, b, c]\n"
            "prereqs: []\n"
            "paths: [beginner]\n"
            "---\n"
            "\n## One\n\nbody\n"
        )
        meta, body = cl.parse_frontmatter(text)
        self.assertEqual(meta["id"], "L01")
        self.assertEqual(meta["phase"], 2)
        self.assertEqual(meta["title"], "A quoted title")
        self.assertEqual(meta["concepts"], ["a", "b", "c"])
        self.assertEqual(meta["prereqs"], [])
        self.assertIn("## One", body)

    def test_rejects_missing_frontmatter(self):
        with self.assertRaises(ValueError):
            cl.parse_frontmatter("# no front matter here\n")

    def test_rejects_unterminated_frontmatter(self):
        with self.assertRaises(ValueError):
            cl.parse_frontmatter("---\nid: L01\n")

    def test_sections_are_parsed_in_order(self):
        body = "## A\n\nalpha\n\n## B\n\nbeta\n"
        sections = cl.parse_sections(body)
        self.assertEqual(list(sections.keys()), ["A", "B"])
        self.assertEqual(sections["B"].strip(), "beta")


class TestLessonShape(unittest.TestCase):
    """Every lesson in the repo must satisfy the gate."""

    @classmethod
    def setUpClass(cls):
        cls.lessons = cl.load_lessons()

    def test_course_has_lessons(self):
        self.assertGreater(len(self.lessons), 20,
                           "the Academy should ship a full course, not a stub")

    def test_every_lesson_passes_the_gate(self):
        errors = cc.check_lessons(self.lessons)
        self.assertEqual(errors, [], "lesson gate failed:\n" + "\n".join(errors))

    def test_every_quiz_passes_the_gate(self):
        errors = cc.check_quizzes(self.lessons)
        self.assertEqual(errors, [], "quiz gate failed:\n" + "\n".join(errors))

    def test_lesson_ids_are_unique(self):
        ids = [m["id"] for m in self.lessons]
        self.assertEqual(len(ids), len(set(ids)))

    def test_prereqs_point_backwards(self):
        """A lesson may only depend on lessons that come before it."""
        seen = set()
        for m in self.lessons:
            for pre in m.get("prereqs") or []:
                self.assertIn(pre, seen,
                              "%s depends on %s, which is not earlier" % (m["id"], pre))
            seen.add(m["id"])

    def test_no_lesson_contains_its_own_solution(self):
        """The hard rule: a lesson must not ship the exercise implementation.

        A lesson that contains a `def <name>(` block for the function it asks
        the learner to write has already answered the exercise.
        """
        offenders = []
        for m in self.lessons:
            turn = (m.get("_sections") or {}).get("Your turn") or ""
            for line in turn.splitlines():
                stripped = line.strip()
                if stripped.startswith("def ") and stripped.endswith(":"):
                    offenders.append("%s: '## Your turn' defines a function" % m["id"])
        self.assertEqual(offenders, [], "\n".join(offenders))

    def test_curriculum_index_is_in_sync(self):
        self.assertEqual(cc.check_index(), [])


class TestProgressEngine(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="academy-test-")
        self.progress_path = os.path.join(self.tmp, "progress.json")
        self.lessons = cl.load_lessons()
        self.lesson = self.lessons[0]
        self.quiz = cl.load_quiz(self.lesson["id"])

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _doc(self):
        doc = cl.empty_progress("tester", "beginner")
        doc["created_at"] = ls.now()
        doc["updated_at"] = ls.now()
        return doc

    def test_empty_progress_shape(self):
        doc = self._doc()
        for key in ("learner", "path", "lessons", "concepts", "review_queue",
                    "sessions", "artifacts"):
            self.assertIn(key, doc)

    def test_grading_scores_and_isolates_answers(self):
        answers = [q["answer"] for q in self.quiz["questions"]]
        result = ls.grade_lesson(self.lesson["id"], answers)
        self.assertEqual(result["correct"], len(self.quiz["questions"]))
        self.assertEqual(result["score"], 1.0)
        self.assertEqual(result["missed_concepts"], [])
        # every row carries its explanation for the post-answer feedback
        for row in result["rows"]:
            self.assertTrue(row["explain"])

    def test_wrong_answers_are_detected_and_named(self):
        wrong = [(q["answer"] + 1) % len(q["options"]) for q in self.quiz["questions"]]
        result = ls.grade_lesson(self.lesson["id"], wrong)
        self.assertLess(result["score"], 1.0)
        self.assertTrue(result["missed_concepts"])

    def test_mastery_folds_recent_evidence_more_heavily(self):
        doc = self._doc()
        ls._update_concept(doc, "softmax", 0.5)
        self.assertAlmostEqual(doc["concepts"]["softmax"], 0.5)
        ls._update_concept(doc, "softmax", 1.0)
        # 0.4 * 0.5 + 0.6 * 1.0 = 0.8
        self.assertAlmostEqual(doc["concepts"]["softmax"], 0.8)

    def test_weak_score_enters_the_review_queue(self):
        doc = self._doc()
        ls._sync_review_queue(doc, self.lesson, 0.5, ["softmax"])
        queue = doc["review_queue"]
        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0]["lesson"], self.lesson["id"])
        self.assertFalse(queue[0]["resolved"])

    def test_strong_score_clears_the_review_queue(self):
        doc = self._doc()
        ls._sync_review_queue(doc, self.lesson, 0.5, ["softmax"])
        ls._sync_review_queue(doc, self.lesson, 0.95, [])
        self.assertTrue(doc["review_queue"][0]["resolved"])

    def test_profile_detects_a_stalled_learner(self):
        doc = self._doc()
        doc["lessons"][self.lesson["id"]] = {"status": "in_progress", "attempts": 3,
                                             "last_score": 0.4}
        self.assertEqual(ls._profile(doc), "stalled")

    def test_profile_detects_a_shaky_learner(self):
        doc = self._doc()
        doc["lessons"][self.lesson["id"]] = {"status": "done", "attempts": 1,
                                             "last_score": 0.5}
        self.assertEqual(ls._profile(doc), "shaky")

    def test_profile_steady_for_a_clean_learner(self):
        doc = self._doc()
        doc["lessons"][self.lesson["id"]] = {"status": "done", "attempts": 1,
                                             "last_score": 0.95}
        self.assertEqual(ls._profile(doc), "steady")

    def test_progress_file_round_trips(self):
        doc = self._doc()
        cl.save_progress(doc, self.progress_path)
        loaded = cl.load_progress(self.progress_path)
        self.assertEqual(loaded["learner"], "tester")
        self.assertEqual(loaded["path"], "beginner")


class TestPlacement(unittest.TestCase):
    def test_placement_quiz_is_well_formed(self):
        with open(os.path.join(cl.COURSE_DIR, "placement.json"), "r",
                  encoding="utf-8") as f:
            data = json.load(f)
        questions = data["questions"]
        self.assertGreaterEqual(len(questions), 3)
        for q in questions:
            self.assertGreaterEqual(len(q["options"]), 3)
            self.assertIn(q["answer"], range(len(q["options"])))
            self.assertTrue(q["explain"])
            self.assertIn(q["level"], data["scoring"]["level_points"])


if __name__ == "__main__":
    unittest.main()
