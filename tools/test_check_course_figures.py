"""Prove the extended figures gate catches the defects the old one certified.

    python tools/test_check_course_figures.py

A gate nobody has tested is a gate nobody can trust. Each case below is a
figure that the OLD gate passed and the NEW gate must reject.
"""
from __future__ import annotations

import os
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

import check_course_figures as gate  # noqa: E402

GOOD = """
<figure class="fig">
  <div class="fig__frame">
    <img class="fig__picture" src="/illustrations/L00.jpg" alt="A line drawing of a door." />
    <svg class="fig__svg" viewBox="0 0 640 340" role="img" aria-labelledby="L00-t L00-d">
      <title id="L00-t">A title</title>
      <desc id="L00-d">A description of the drawing.</desc>
      <path class="m-draw" style="--m-length: 120;" d="M 10 10 L 130 10" fill="none" />
    </svg>
  </div>
  <figcaption class="fig__caption"><span class="edge-code">figure L00</span></figcaption>
</figure>
"""

CASES = [
    ("aria-labelledby points at an id that does not exist",
     GOOD.replace('aria-labelledby="L00-t L00-d"', 'aria-labelledby="nope-1 nope-2"')),
    ("the title carries no id",
     GOOD.replace('<title id="L00-t">', "<title>")),
    ("the figure shows no picture",
     GOOD.replace('<img class="fig__picture" src="/illustrations/L00.jpg" alt="A line drawing of a door." />', "")),
    ("the picture has no alt text",
     GOOD.replace('alt="A line drawing of a door."', 'alt=""')),
    ("the picture comes after the diagram",
     GOOD.replace('<img class="fig__picture" src="/illustrations/L00.jpg" alt="A line drawing of a door." />', "")
            .replace("</svg>", "</svg>\n    <img class=\"fig__picture\" src=\"/illustrations/L00.jpg\" alt=\"A line drawing of a door.\" />")),
    ("the figure has no motion",
     GOOD.replace('class="m-draw" style="--m-length: 120;"', 'style="--m-length: 120;"')),
    ("a drawing element draws itself without saying how long it is",
     GOOD.replace('style="--m-length: 120;"', "")),
    ("the figure uses a gradient",
     GOOD.replace("<path", '<linearGradient id="g"></linearGradient><path')),
    ("the figure uses a filter",
     GOOD.replace("<svg", '<svg filter="drop-shadow(1px 1px 1px #000)"')),
    ("the figure uses a rounded corner",
     GOOD.replace("<svg", '<svg style="rx: 8"')),
    ("the figure carries an inline event handler",
     GOOD.replace("<svg", '<svg onclick="alert(1)"')),
    ("the figure has its own keyframes but no reduced-motion rule",
     GOOD.replace("</figure>", "@keyframes spin { from { opacity: 0; } to { opacity: 1; } }</figure>")),
]


def main() -> int:
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        good_path = os.path.join(tmp, "good.astro")
        with open(good_path, "w", encoding="utf-8") as f:
            f.write(GOOD)
        problems = gate.check_figure("L00", good_path)
        if problems:
            print("FAIL the good figure is rejected: %s" % "; ".join(problems))
            failures += 1
        else:
            print("ok   the good figure passes")

        for name, source in CASES:
            path = os.path.join(tmp, "broken.astro")
            with open(path, "w", encoding="utf-8") as f:
                f.write(source)
            problems = gate.check_figure("L00", path)
            if problems:
                print("ok   caught: %s" % name)
            else:
                print("FAIL missed: %s" % name)
                failures += 1

    print()
    if failures:
        print("%d case(s) failed." % failures)
        return 1
    print("all %d cases behave as expected." % (len(CASES) + 1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
