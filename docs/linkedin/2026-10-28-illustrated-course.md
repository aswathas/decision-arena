---
slug: illustrated-course
date: 2026-10-28
format: teaching-post
status: ready
---

# The illustrated course - 46 lessons, each with a story, a moving diagram and a picture

## The post

One ticket. Three shapes. One decision that flips.

I have reproduced that shape offline. I have not yet measured it on a real model.

What a decision model actually receives is a state, not a sentence. Send the same support ticket three ways - prose, flat key-value JSON, nested JSON with headers - and the words are identical while the shape is not. A key called refund_requested carries emphasis the sentence never had, and a threshold at 0.5 turns that emphasis into an action.

That is the finding the course is built around: if only the serialisation changes and the decision moves anyway, then a benchmark that uses one shape is partly measuring the author's taste. The lesson diagram in this post carries the published spread - 0.90, 0.86, 0.09 - from an independent harness the lesson cites by name.

The friction plot in this post is my own run, and it is a simulator: the format shift is built into it on purpose, so the pipeline can be exercised without credentials. It reads 0.93 as prose, 0.33 as flat JSON, 0.00 as nested, and on four of the nine questions the decision flips at the 0.5 threshold. That proves the harness works, not that any model is shape-sensitive. The live provider runs are still waiting on keys.

That experiment is lesson 61 in a 46-lesson course I built to learn AI/ML properly: 46 lessons, 46 quizzes, 154 concepts asked about across those quizzes, ten phases, 26 hours of reading. This week every lesson got the same three parts - a story of 120 to 220 words that starts from something physical, a hand-authored diagram with a single idea of motion, and a generated line-art picture of the same idea in a human scene.

The hard part was not drawing them. It was that a beginner cannot learn a definition from a definition. Every lesson had to start from something you can picture - a support desk, a queue, a threshold - and only then earn the vocabulary. And the site builds those lessons straight from the markdown in the repository, so the course cannot drift away from the code that made it.

Start at L00, 25 minutes, no assumptions. Every lesson ends with a small exercise you write yourself and a quiz you answer before the key opens.

Read the course: https://aswathas.github.io/decision-arena/course/

#decisionmodels #machinelearning #evals #learninpublic

## First comment

The link, in case the post swallowed it: https://aswathas.github.io/decision-arena/course/

The course is also in the repo, if you would rather read the markdown: https://github.com/aswathas/decision-arena

## Attachments

- `../media/01-hook.jpg` - The friction finding figure from the site: on the left, three small drawings of the same support ticket - a wavy line for prose, a row of five squares for flat JSON, three stacked rectangles for nested JSON - each with a line running right to a vertical probability scale where a black marker sits at 0.93, a grey marker sits at 0.33 below a dashed 0.5 decision threshold, and a third sits at 0.0. The caption under the figure reads that the ticket never changed, only its shape did, and that this is the offline simulator reproducing the shape of the result, not a measurement of a model.
  - caption: One ticket, three shapes, one threshold. The finding the course is built around - and the figure that says on its face that these numbers came from the offline simulator.
- `../media/02-lesson.jpg` - Lesson L61 on the site: a generated line-art picture of a desk with a hand writing on a sheet of paper beside a clipboard and a printer, and below it the lesson's own diagram in which three small drawings labelled prose, flat and nested each send an arrow to a vertical probability scale, where two markers sit high at 0.90 and 0.86 above a dashed 0.5 line and a third sits low at 0.09, with the caption 'The same ticket in three serialisations moves the probability from 0.90 to 0.09, and only the one that crosses the 0.5 line changes a decision.'
  - caption: Every lesson now carries the same three parts: a story, a diagram with one idea of motion, and a picture.
- `../media/03-course.jpg` - The top of the course index page: the heading 'The whole course, in order.', a stat row reading 46 lessons, 46 quizzes, 10 phases, 3 paths and 26 h of reading time, a 'Start here' card pointing at lesson L00, a course map of ten phases drawn as vertical ticks of different heights above the first phase, which lists L00, L10, L01, L02 and L03 with their reading times.
  - caption: The whole course, in one page: 46 lessons, ten phases, one reading order.

## Links

- Decision Arena Academy - the course index - https://aswathas.github.io/decision-arena/course/

## Evidence

- 46 lesson files under course/lessons/, 46 quiz files under course/quizzes/, 154 unique concepts asked about across the quizzes
- 46 figure components under site/src/figures/ and 46 illustrations under site/public/illustrations/; python tools/check_course_figures.py reports 46 lessons checked, 0 with problems
- The friction numbers are the mock simulator run runs/20261027-212313-friction-mock.jsonl: fmt-001-refund is_urgent reads 0.9271 prose, 0.3278 flat, 0.0 nested, and the run file records 9 questions measured with 4 flips at 0.5
- The published spread the lesson diagram draws is the independent harness rmax-ai/jev-vs-clef, recorded in course/lessons/L61-format-friction.md and AI-CONTEXT.md
- Ten phases and 26 hours of reading: course/curriculum.json and the minutes field in the 46 lesson files under course/lessons/ (1560 minutes in total)
- Live site, rebuilt and re-checked on every push to main: https://aswathas.github.io/decision-arena/ - the course index and lesson L00 both return 200

## Checks

- all checks pass (2306 chars, 4 tags, 3 images)
