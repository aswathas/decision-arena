# learning/ - the learner's state

Two files, and the difference between them matters.

| File | What it is | Who writes it |
|---|---|---|
| `progress.json` | machine state: what is done, per-concept mastery, the review queue, published artifacts | `tools/learn_state.py` only |
| `build_log.md` | the learner's own record, in their own words | the learner, via `tools/learn_state.py log` |

**`progress.json` is committed on purpose.** It is the evidence of what was
actually learned - not what was read. A course that can show a learner's
concept-by-concept mastery is a course that cannot be quietly gamed.

**`build_log.md` is append-only.** Never edit or delete an earlier entry. The
path the learner took, including the wrong turns, is the most valuable thing
in this folder.

Both are per-learner. Do not reset them to make a demo look tidy - start a
separate path instead (`python tools/learn_state.py init --learner <name>
--path <path>`).

## The commands

```bash
python tools/learn_state.py init --learner aswath --path beginner
python tools/learn_state.py next           # what to learn next, and why
python tools/learn_state.py start L12      # mark a lesson in progress
python tools/learn_state.py grade L12 --answers 1,0,2,1
python tools/learn_state.py record L12 --answers 1,0,2,1 --artifact docs/notes/L12-softmax.md
python tools/learn_state.py review         # what to go back to
python tools/learn_state.py status         # the progress report
python tools/learn_state.py feedback       # the closing note for a session
python tools/learn_state.py log --lesson L12 --summary "..." --concept "..."
```

The **beginner** path is every lesson in phase order. **foundations** is the
maths and measurement phases. **provider-live** is the hands-on, experiment
and publish phases. See `course/README.md`.
