# Decision Arena Academy

The course. A beginner with zero LLM knowledge ends up able to explain, from
first principles, why this harness reports what it reports - and to publish a
finding somebody else can check.

Everything here is in the repo on purpose: the course, the progress state, the
skills, and the gate that keeps them honest.

## The three paths

| Path | For | Length |
|---|---|---|
| `beginner` | you know nothing about LLMs | every lesson, in phase order |
| `foundations` | you want the maths under the model | the maths and the measurement phases |
| `provider-live` | you want to run real providers and publish | the hands-on, experiment and publish phases |

Start with `/learn`. It places you, teaches one lesson at a time, hands you
the exercise, quizzes you, and tracks what you have actually learned.

## The ten phases

| Phase | Title | What you will be able to do |
|---|---|---|
| 0 | Orientation - what is this thing? | Explain what a decision model is and is not, handle the data shapes, and read the wire protocol |
| 1 | The numbers under the model | Take logits to probabilities and back, and know why temperature works |
| 2 | How a model actually decides | Explain tokens, embeddings, attention and a transformer block without notes |
| 3 | Learning - how models get their answers | Derive a gradient, run gradient descent, and know what calibration means |
| 4 | Talking to a real model | Write a provider adapter and call Jev, Clef or a local Laya |
| 5 | Measuring - accuracy is not enough | Compute accuracy, Brier score, ECE, agreement and action-change rate |
| 6 | Running experiments | Run the format-friction, injection and determinism experiments |
| 7 | Building your own harness | Design cases, label gold answers, run a battery, read the report |
| 8 | Engineering the product | Choose a provider, do the cost arithmetic, ship it |
| 9 | Capstone - publish a finding | Run an experiment and publish something checkable |

### The order inside Phase 0

Phase 0 is not in id order, and that is deliberate: you learn the shapes of
the data (lists, dicts, floats) **before** the wire protocol, because you
cannot read a JSON contract before you know what a dict is. Lessons sort by
`(phase, order, filename)`, and Phase 0 sets an explicit `order` on each
lesson to say so.

## The loop

Every lesson is the same six steps, and the steps are the point:

1. **Read** the brief in `course/lessons/`.
2. **Explain it back** - in your own words, one sentence, no jargon. This is
   the real assessment.
3. **Write** one micro-exercise yourself. The agent never writes it for you.
4. **Quiz** yourself - every question, before any answer is revealed.
5. **Log** what you wrote and what you got wrong.
6. **Publish** one artifact.

Ten minutes of writing something you can explain beats two hours of reading.

## Where things live

| Thing | Path |
|---|---|
| Lesson briefs (source of truth) | `course/lessons/` |
| Quizzes and the answer key | `course/quizzes/` |
| The placement quiz | `course/placement.json` |
| The generated index | `course/curriculum.json` |
| The authoring contract | `course/FORMAT.md` |
| Your progress | `learning/progress.json` |
| Your build log (append-only) | `learning/build_log.md` |
| The progress engine | `tools/learn_state.py` |
| The gate | `tools/course_check.py` |
| The skills | `skills/learn/`, `skills/arena-coach/`, `skills/course-author/` |

## The gate

```bash
python tools/course_check.py --index   # regenerate course/curriculum.json
python tools/course_check.py --check   # validate everything
```

The gate fails on a missing section, an out-of-order section, a quiz without
an explanation, a prereq that does not exist, an `exercise_file` pointing at
nothing, or a stale index. A broken lesson is a build failure, not a warning.

## The rules that keep it honest

1. **The learner writes the exercise.** The agent may scaffold, explain,
   review, quiz and log. It may not write the exercise.
2. **The mock is not evidence.** `MockProvider` tests the harness. It never
   evaluates a model.
3. **Evidence before claims.** A number without its raw `runs/*.jsonl` behind
   it is marketing.
4. **Never delete.** Archive only - in the course and in the repo.
5. **Fundamentals are never cut.** If a day runs short, the course extends.

## Editing the course

Read `course/FORMAT.md`, then use the `course-author` skill. The short version:
the lesson files are the source of truth, `curriculum.json` is generated, and
the gate decides whether your change is allowed in.
