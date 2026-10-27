**Scope.** The course reader - the part of the site that carries the
Decision Arena Academy itself. Two surfaces: the course index at
`site/src/pages/course/index.astro` and one page per lesson at
`site/src/pages/lessons/[id].astro`, forty-six of them. Both are rendered
from the repository's own files: `course/curriculum.json` for the index, and
`course/lessons/*.md` and `course/quizzes/*.json` for each lesson page. The
site holds no copy of the course, so it cannot drift from it.

**Visitor mode.** Read. The visitor here is trying to understand something,
not decide something. A lesson page is a technical document: the lesson's own
words, the numbers it claims, and the answer key kept until they have tried.

**Audience.** Absolute beginners learning AI/ML fundamentals, plus engineers
who want the course as a reference. They are not evaluating vendors here. They
know how to run a terminal, they have never been told what softmax is, and
they will be asked to write a small piece of code before they are told whether
they understood it.

**Job / action.** Understand one concept, and know whether you understood it.
**Action:** answer the lesson's three questions out loud, in your own words,
before opening the key. The page is the reading; the tutor in the repository
is the grading. The page's own job is to make the attempt happen before the
answer arrives.

**Proof and content (all real, nothing invented).** The lesson text is the
file in `course/lessons/` - rendered, not rewritten. The quiz is the file in
`course/quizzes/`, with its concepts, its options and its explanations. The
counts, the phase titles, the minutes, the concepts and the prerequisites come
from `course/curriculum.json`, which `tools/course_check.py --index`
regenerates and whose staleness the course gate fails on. Forty-six lessons,
forty-six quizzes, ten phases, three paths, one passing course gate.

**Constraints.** The reader teaches; it does not keep the record. Mastery is
tracked per concept by the tutor in `learning/progress.json`, and the page
says so rather than pretending a scroll position is understanding. The answer
must not reach the reader before they have answered, so the key sits behind a
disclosure. No third-party runtime request, and no new dependency to render
markdown - the lessons are read with the markdown processor the site already
had. No secret, credential or private path. Apache-2.0.

**Chosen direction.** *The Analysis Chart*, extended. The landing page is a
plot; a lesson page is the same sheet with a longer reading column. The world
does not change - a lesson is a technical document, and the honest form for
one is a spec sheet: a reference strip above the title, one measure, hairline
rules, the section list in the margin, and the answer key boxed at the end.

**Memorable moment.** The key opening. The lesson ends with a quiz, and the
answers are right there - but behind a disclosure that reads as a plus sign in
the margin, so the moment of opening it is the moment the reader decides
whether they were honest. A reader who answers first and opens second gets
something; a reader who opens first gets nothing. The page is built so that
the second kind of reader can feel the difference.

## Direction contract

**THESIS.** A lesson you read is not a concept you own, so a reading surface
that shows the answers is a reading surface that teaches nothing. This reader
is therefore built around the attempt: the lesson's own file, the lesson's
own questions, and the key held shut until the reader has spoken the answer
out loud. The category default for an online course is a video, a progress
bar and a quiz that grades itself against a letter grade nobody earned; this
refuses the progress bar because the honest record of what the learner
understood lives in the repository, tracked per concept, and a page cannot
fake it.

**OWN-WORLD.** The printed technical plot, unchanged from the landing page -
cool plot-paper ground, near-black ink with a blue cast, prussian indigo as
the one committed accent, hairline rules only, no rounded cards, no shadows,
no gradients, no serif. What the lesson pages add is a reading register, not a
new world: a reference strip above the title carrying the phase, the reading
time, the concepts, the paths, the prerequisites and the file the reader is
going to write; one measure for the prose; the lesson's own section list in a
margin rail; a disclosure whose marker is a hairline plus; and a next-lesson
rule at the foot. Every number is tabular monospace. The rail is the one piece
of furniture the landing page did not have, and it is the same furniture a
printed specification has had for a century: the list of sections in the
margin.

**STORY.** The visitor arrives from the landing page's second door, or from a
search result, or from a colleague's link to one lesson. They do not know
what a decision model is, or they know and want the maths. The page meets them
with the facts first - how long this takes, what it assumes, which file they
are going to write - and then with the lesson itself, in the teacher's voice,
in the order the teacher wrote it. At the end the page asks three questions
and keeps the answers behind a plus sign. The visitor leaves having tried, and
the page says where the real record is: the tutor, per concept, in the
repository, because a page can teach and cannot certify.

**FIRST VIEWPORT.** A lesson page opens on the reference strip, not on a
kicker: the phase and its title, then a hairline row of reading time, the
concepts this lesson owns, the paths it sits on, the lessons to read first,
and the file the reader is about to write. Below it the title - the lesson's
own H1, the same words as in the repository, because the page renders the
file rather than restating it - and then the first section of the lesson. In
the margin, a sticky rail lists the lesson's own eight sections, ending in a
link to the whole course. Below 1080px the rail stops being a column and
becomes a single wrapped contents line, so the title still lands near the top
of the screen. No eyebrow label above the title, no progress bar, no video
placeholder, no card grid, and no answer visible anywhere on the first screen.

**FORM.** *The Analysis Chart*, extended rather than replaced. The same
tokens, the same ground, the same one committed colour, the same hairline
grammar, the same mono numerals; the course index is the landing page's
curriculum column drawn out into a table of contents, and a lesson page is the
same sheet with a reading column. The signature interaction of the landing
page - the projection toggle, the only authored motion on the site - is
absent here on purpose: a lesson is read, not operated, and the one motion
that does exist is the reader's own, the disclosure opening.

**FINISH.** unreviewed and undocumented is unfinished; this build ends with
the finish review, the verdict, DESIGN.md, and the detector and the
accessibility check run across all forty-eight built pages, not just the
landing page

## Unresolved decisions

- Whether to add self-scoring quizzes and browser-side progress was declined
  for now: a browser cannot own the per-concept mastery record, and a second
  progress mechanism that disagrees with the real one is worse than none.
- Whether the course reader should ever be the place where the learner writes
  code is unresolved. Today the answer is no - the learner writes in their
  checkout, because the harness, the tutor and the progress file all live
  there.
