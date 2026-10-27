# The hook library

The hook is the first two lines of the post. It is the only part most people
read, so it is the only part that has to be good.

## The four hook shapes

### 1. The number

A specific figure that means something.

> 46 lessons. 158 concepts. One battery run against four decision models.
>
> Every vendor publishes a benchmark where they win.

Why it works: a number is checkable, so the reader trusts the rest.

### 2. The contradiction

Two true things that should not both be true.

> A model scored 0.93 on prose and 0.00 on the same question as JSON.
>
> Same model. Same question. Different shape of the answer.

Why it works: the brain has to resolve the contradiction, so it keeps reading.

### 3. The scene

One concrete moment, in the present tense.

> The refund question scored 0.93 as prose and 0.33 as JSON.
>
> Nobody changed the model. Nobody changed the question.

Why it works: specificity reads as honesty.

### 4. The permission

Give the reader a reason to stop scrolling - a promise of what they get.

> If your AI feature is one prompt away from breaking, the bug is in your
> prompt, not your model.
>
> I built a harness that measures exactly that. Here is how it works.

Why it works: it names the reader's problem before the post talks about itself.

## The rewrite loop

Draft the hook, then rewrite it until one of these is true:

- it contains a number, a contradiction, or a named place in the work
- it would still make sense with every mention of the project deleted
- it does not contain "excited to announce", "delighted", "game-changer",
  "revolutionary", "unlock", "leverage", "seamless", or "delve"
- reading only the hook and the CTA makes sense - they are not two different
  posts

Delete any hook that needs a second line to explain its first line. That
second line belongs in the body.

## Length

Under 200 characters. Count it - `tools/linkedin_post.py` will fail the build
if the hook is longer, because a long hook is a hook the feed eats.

## What not to do

- **The announcement.** "I am excited to announce..." The reader has seen
  four of these today.
- **The humble brag.** "This is a small project but..."
- **The fake question.** "Curious what you think?" nobody is curious.
- **The emoji opener.** One emoji is a style. Three is a signal that there is
  no signal.
- **The self-referential opener.** "I've been heads-down on a project..." The
  reader does not care about your heads.
