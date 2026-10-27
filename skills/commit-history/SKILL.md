---
name: commit-history
description: >
  The house rule for how work becomes history in this repository, and especially
  how work done by several agents in parallel becomes history. Use when you are
  about to commit, when another agent has finished and its files are in the
  working tree, when a commit has grown fat enough to be unreadable, or when a
  developer asks why the history looks the way it does. One commit per
  workstream, one owner per file, a message that says what changed, why, whose
  work it was and which gates proved it.
---

# Commit history - the house rule

The history is documentation. A developer who opens `git log` six months from
now should be able to read what was built, in what order, by which piece of
work, and what proved it. That only happens if the commits are made one piece
of work at a time.

This repository builds a lot in parallel. Seven agents wrote the illustrated
course at once. The failure mode is not that agents write bad code - it is
that their work lands in the tree and then gets swept into whatever commit
happens to be made next. A 176-file commit with a two-line subject is not
history; it is a receipt.

## The rules

1. **One commit per workstream.** A workstream is a bounded piece of work with
   an owner: a phase of the course, one agent's figures, one fix from one
   audit. Its files go in one commit, with one message.
2. **One writer per file.** A commit contains only the files its author
   owned. If you need a file another workstream owns, say so in your report
   instead of editing it.
3. **Never sweep.** When other agents' files are in the working tree, do not
   `git add -A`. Stage the paths you own, by name.
4. **The subject is prose.** A sentence that says what changed, in under 72
   characters, with no filler: not "WIP", not "fix", not "update files".
5. **The body is the documentation.** What changed, why it matters, whose
   work it was, how many files, and which gates proved it.
6. **The gates are named.** A commit that changed code says how you know it
   works: the command and what it printed.
7. **Do not commit what you did not prove.** A claim in a message must have a
   gate, a file or a number behind it.

## The message format

```
<Prose subject, under 72 characters, no trailing period>

<One paragraph: what changed and why a reader would care.>

Workstream: <name> - <the bounded piece of work>
Files: <n> files, <what they are>

Gates:
  - <command> -> <what it printed>
```

Full detail and worked examples: `references/message-format.md`.

## The hook

The repository ships a `commit-msg` hook that checks the message before git
accepts it. Enable it once per clone:

```bash
git config core.hooksPath .githooks
```

The hook runs `tools/check_commit.py`, which rejects a subject that is too
long, a placeholder subject, a commit that touches another workstream's files
without saying whose work it is, and a large commit whose body does not name
the gates that proved it. It never rewrites your message; it tells you what is
missing.

Check a message without committing:

```bash
python tools/check_commit.py <path-to-message-file> --staged
```

## When a commit has already grown fat

Sometimes the work is done and the commit is already made, and the commit has
176 files in it. Splitting it is allowed and is the right thing to do: a
developer reading the history is owed the breakdown.

The procedure, in order:

1. Make a backup branch: `git branch backup-before-split`.
2. Note the tree you must end at: `git diff <fat-commit> HEAD` must be empty
   when you are done.
3. Reset to the commit before the fat one: `git reset --hard <base>`.
4. For each group, in order, take its files out of the fat commit and commit
   them with their own message:
   `git checkout <fat-commit> -- <paths>` then `git commit -F <message>`.
5. Take the files that the fat commit deleted out with `git rm`.
6. Check the tree: `git diff <fat-commit> HEAD` must print nothing.
7. Move the branch and force-push:
   `git branch -f main HEAD` and `git push --force-with-lease origin main`.

The one rule while splitting: the final tree must be **byte-identical** to the
fat commit's tree. A history that reads better is not worth changing what the
code says.

## What this is not

- **Not a way to make the contribution graph greener.** GitHub counts days,
  not commits. This is about the history being readable.
- **Not a licence to commit anything.** The gates in the message are the
  point: a future reader must be able to re-run them.
