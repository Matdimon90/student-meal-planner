# How we work

Short rules the three of us follow so the repository stays readable.

## One issue, one branch, one pull request

1. Every piece of work starts as a GitHub issue that says what and why.
2. Create a branch from an up-to-date `main`:
   ```
   git switch main
   git pull
   git switch -c feature/short-description
   ```
3. Commit in small steps, push, open a pull request that ends with `Closes #<issue number>`.
4. A teammate reviews it. Nobody merges their own pull request without a review.
5. Fixes requested in review go on the same branch. The pull request updates by itself.
6. After the merge, delete the branch on GitHub.

Nobody commits directly to `main` (the three kickoff commits were the only exception).

## Branch names

| Prefix | Used for | Example |
| --- | --- | --- |
| `feature/` | new behaviour | `feature/shopping-maths` |
| `prompt/` | a new prompt version or experiment | `prompt/v2-structured-output` |
| `docs/` | documentation only | `docs/ai-approach` |
| `fix/` | bug fixes | `fix/package-rounding` |

## Commit messages

- One line, no body.
- Imperative mood, as if finishing the sentence "This commit will...": `Add budget check`, not `Added` or `Adding`.
- Say what changed. If the message needs "and", it is probably two commits.
- Never `update`, `fix`, `wip`, `stuff`.

## Review comments

Anchor the comment to a line and give three parts:

- **Observation**: what you see.
- **Concern**: why it matters.
- **Suggestion**: a concrete next step, marked **Blocking** or **Optional**.

## Before opening a pull request

- `python3 -m pytest` passes.
- `git status` shows nothing unexpected, and no `.env` file is staged.
- If a prompt changed: the new version is a new file in `prompts/`, and the result of testing it is written in `docs/prompt-log.md`.

## Using AI to write code

We use Claude as a coding assistant. The rule: the person who opens the pull request must be able to explain every file in it, and the reviewer must actually read it.
