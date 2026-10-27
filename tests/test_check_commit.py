"""The commit-message checker, proved on the cases it must catch.

    python -m unittest discover -s tests

A gate nobody has tested is a gate nobody can trust. The audit of the figures
gate found that a gate can pass everything you throw at it; this test makes
sure the commit gate does not have the same disease.
"""
from __future__ import annotations

import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

import check_commit  # noqa: E402

GOOD = (
    "Teach the attention lesson with a story, a diagram and a picture\n"
    "\n"
    "The attention lesson is where a beginner stops reading, so it now opens\n"
    "with a scene and shows the mechanism moving.\n"
    "\n"
    "Workstream: C - the illustrated course, phases 5 to 7\n"
    "Files: 3 files - one lesson, one figure, one illustration\n"
    "\n"
    "Gates:\n"
    "  - python tools/check_course_figures.py -> no problem for L22\n"
)

OWNED = [os.path.join("course", "lessons", "L22-attention.md")]


class CheckSubject(unittest.TestCase):
    def test_a_good_subject_passes(self):
        self.assertEqual(check_commit.check_subject("Teach the attention lesson"), [])

    def test_a_placeholder_subject_fails(self):
        self.assertTrue(check_commit.check_subject("wip"))
        self.assertTrue(check_commit.check_subject("fix"))
        self.assertTrue(check_commit.check_subject("..."))

    def test_a_long_subject_fails(self):
        self.assertTrue(check_commit.check_subject("x" * 73))

    def test_a_trailing_period_fails(self):
        self.assertTrue(check_commit.check_subject("Teach the attention lesson."))

    def test_a_conventional_prefix_fails(self):
        self.assertTrue(check_commit.check_subject("feat(L22): add a figure"))

    def test_an_empty_subject_fails(self):
        self.assertTrue(check_commit.check_subject("   "))


class CheckMessage(unittest.TestCase):
    def test_the_house_shape_passes(self):
        self.assertEqual(check_commit.check_message(GOOD, OWNED), [])

    def test_a_workstream_file_needs_a_workstream_line(self):
        problems = check_commit.check_message(
            GOOD.replace("Workstream: C - the illustrated course, phases 5 to 7\n", ""),
            OWNED,
        )
        self.assertTrue(any("Workstream" in p for p in problems))

    def test_an_empty_workstream_line_fails(self):
        problems = check_commit.check_message(GOOD.replace("Workstream: C - the illustrated course, phases 5 to 7", "Workstream:   "), OWNED)
        self.assertTrue(any("empty" in p for p in problems))

    def test_a_big_commit_needs_gates(self):
        problems = check_commit.check_message(
            GOOD.replace("Gates:\n  - python tools/check_course_figures.py -> no problem for L22\n", ""),
            OWNED * 6,
        )
        self.assertTrue(any("Gates" in p for p in problems))

    def test_a_multi_file_commit_needs_a_body(self):
        problems = check_commit.check_message("Teach the attention lesson\n", OWNED * 2)
        self.assertTrue(any("no body" in p for p in problems))

    def test_a_file_outside_the_owned_paths_needs_no_workstream(self):
        problems = check_commit.check_message(
            GOOD.replace("Workstream: C - the illustrated course, phases 5 to 7\n", ""),
            [os.path.join("site", "src", "styles", "global.css")],
        )
        self.assertEqual([p for p in problems if "Workstream" in p], [])


if __name__ == "__main__":
    unittest.main()
