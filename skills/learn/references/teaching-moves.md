# Teaching moves - the technique library

This is the reference the `learn` skill draws on. It is a working catalogue of
techniques that actually survive contact with a tired beginner at 11pm, not a
list of names to show off. Each entry says **when to use it** and **what it
looks like in this course**.

The default arc for a lesson is Feynman: **plain words → what breaks → the real
thing → compress**. Everything below is a way to make one of those four steps
land harder.

---

## The spine

### 1. Feynman technique - compress until it hurts (1949)

> Explain it without jargon. If you cannot, you do not understand it yet.
> Then say it in one sentence. The gap between your two attempts is the gap.

**In this course:** after every concept, ask the learner to say it back in one
sentence with no jargon. A one-sentence answer that uses "logit" but not
"score" means the word got memorised and the idea did not. Ask again, with a
different analogy.

### 2. Socratic questioning - the question is the lesson

Instead of giving the answer, ask the question the answer would answer.
"Where does the 0.72 in this dict come from?" is worth more than "the 0.72
comes from softmax over the logits".

**In this course:** never open a lesson with the definition. Open it with the
question the definition answers.

### 3. Concrete before abstract (Piaget)

A beginner cannot generalise from a definition they have not felt. Give one
worked number first; the rule comes second.

**In this course:** every "The real thing" section starts with one number the
learner can check by hand - three scores, one gradient, one probability.

### 4. Advance organiser (Ausubel)

Before new material, give the learner a frame to hang it on.

**In this course:** the "Why this matters" section is the organiser. It tells
them which question this lesson answers before they meet any notation.

### 5. Spiral curriculum (Bruner)

The same idea returns at increasing depth. Confidence vs probability appears
first as intuition (L04) and returns as measurement (L33, L52).

**In this course:** do not introduce a concept once and never revisit it. When
a lesson touches an old concept, say "this is the same idea as L04, but now we
can measure it" - the return is where the learning actually consolidates.

### 6. Mastery learning (Bloom)

A concept is learned when the learner can do it, not when they have heard it.
Move on only after the check passes.

**In this course:** a quiz score under 70% does not advance the lesson. It
routes to the review queue (`tools/learn_state.py review`).

---

## Techniques that make it stick

### 7. Retrieval practice (Roediger & Karpicke)

Re-reading feels like learning and is not. Pulling it out of your head is
learning.

**In this course:** Step 1 (warm-up recall) exists only for this. Also: the
"Check yourself" questions are answered *before* the quiz, from memory, not
by scrolling back up.

### 8. The generation effect (Slamecka & Cuedeck)

A term you produced yourself is remembered far better than one you read.

**In this course:** "## Your turn" always asks the learner to produce
something - a function, a number, a sentence. The artifact is always
produced, never received.

### 9. Elaborative interrogation

Ask "why is that true?" after every step, and answer it - do not let it hang.

**In this course:** when you explain a step, close it with a why. If the
learner asks why and you cannot answer it in one sentence, you have found the
edge of your own understanding too.

### 10. Self-explanation (Chi)

Talking through your own reasoning deepens it.

**In this course:** the build log entry is written in the learner's own words.
That sentence is the assessment of understanding, and the reason for the log
existing at all.

### 11. Dual coding (Paivio)

A picture plus words beats words alone.

**In this course:** print a bar of characters for a distribution, draw the
attention matrix, show the probability as a point on a line. One picture per
lesson is enough.

### 12. Spacing and interleaving (Ebbinghaus)

Massed practice feels better and works worse. Mixing problem types feels
worse and works better.

**In this course:** the review queue brings back weak concepts later instead
of cramming. The "In this repo" pointer deliberately shows the concept in a
*different* file than where it was taught.

### 13. Cognitive load theory (Sweller)

Beginners have a small working memory. Do not make them hold more than they
can.

**In this course:** one concept per turn. One exercise per turn. A worked
example before a task. If a learner is stuck, the fix is almost always
"smaller", never "more explanation".

### 14. Worked examples, then fading (Kalyuga)

Show a complete solution, then a partial one, then none. The steps removed
should be the ones they have earned.

**In this course:** the exemplar lesson shows the maths, the "In this repo"
section shows it in real code, and the exercise removes one more layer each
time. Fade deliberately: leave the easy step, remove the hard one.

### 15. Desirable difficulty (Bjork)

Make it hard enough to be useful and easy enough to be finishable. The right
difficulty is where the learner slows down but keeps going.

**In this course:** do not answer faster than the learner can think. Silence
after a question is not failure - it is the technique working.

### 16. Learning from errors

A wrong prediction, examined, teaches more than a right one that was never in
doubt.

**In this course:** before running anything, ask "what do you think will
happen?". Let them be wrong, run it, and let the output do the correcting.

---

## Reading the learner

Adjust within the turn. These are the signals.

| Signal | What it means | Do this |
|---|---|---|
| Answer is fluent but reuses your words | Memorised, not understood | Ask for an analogy you did not give |
| Long pause, then "I don't know" | The gap is real | Go smaller: one number, one line |
| "Wait, why?" mid-explanation | Best possible outcome | Answer it now, slowly, before continuing |
| Gets it right immediately | Ready for more | Raise the difficulty of the exercise |
| Right answer, wrong reason | Worse than a wrong answer | Ask "how do you know?" - this is the real gap |
| Tries to skip to the code | Wants to skip understanding | Redirect: "predict the output first" |
| Asks for the answer | Blocked, not lazy | Narrow the exercise; give a worked trace |

---

## The four things that ruin a session

1. **Answering the question they did not ask.** They asked "what does this
   do", not "write it for me".
2. **Vague praise.** "Nice work" teaches nothing. "Your `shifted` line
   subtracts the max before the exp - that is the overflow fix" teaches
   something.
3. **Dumping.** Three concepts in one turn because you are in a hurry. The
   learner will remember none of them.
4. **Quizzing before they have built.** A quiz on code they never wrote is
   theatre. Explain, exercise, then quiz.

---

## The Feynman compression test

At the end of every lesson, the learner should be able to say this, with no
jargon, in one or two sentences:

> "I know what <X> is, what it is for, and what it costs me if I get it
> wrong."

If they can only produce the first part, teach the second part next time.
That sentence is the definition of done for a lesson.
