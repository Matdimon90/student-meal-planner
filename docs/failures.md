# Problems, failures and what we learned

What happened? Why? What did we try? What did we learn?

## Git would not run: Xcode licence

- **What happened.** The first `git config` on a new Mac printed the whole Apple licence and refused to run.
- **Why.** macOS ships Git inside Apple's developer tools, and the licence had never been accepted. Accepting it needs admin rights.
- **Fix.** `sudo xcodebuild -license accept`.
- **Learned.** Read the last lines of an error before the first ones: the fix was written at the bottom.

## A placeholder email in the Git identity

- **What happened.** `git config --global user.email "your-github-email"` was pasted as it was, placeholder included.
- **Why it matters.** GitHub links commits to an account through the email. With a wrong email, commits are not credited to the author.
- **Fix.** Set the real email again and check with `git config --global user.email` before the first commit.

## A stale `.git/index.lock`

- **What happened.** Git refused to work: "unable to unlink index.lock".
- **Why.** A tool had run `git status` in the folder from a sandbox that was not allowed to delete files, so Git's lock file stayed behind.
- **Fix.** `rm -f .git/index.lock`. Rule since then: only we run Git in this folder.

## The API call crashed on `temperature`

- **What happened.** While writing `src/llm.py` with our coding assistant, the draft passed `temperature=0.2` to get repeatable plans, as the textbook (chapter 6) suggests. The first real call, made before the file was committed, failed: `TypeError: Messages.create() got an unexpected keyword argument 'temperature'`.
- **Why.** Version 1.x of the Anthropic Python SDK no longer has a `temperature` parameter. The textbook was written for an older version.
- **Fix.** Removed the parameter and pinned `anthropic>=1.7` in `requirements.txt` so everybody runs the same SDK.
- **Learned.** Our tests did not catch it, because they replace the model with a fake. A fake model tests our code, not the real API. One real call early would have found it in a minute. Also: we cannot turn randomness down any more, so the same request can give different plans. That makes validating every answer in code even more important.

## "This API key is not scoped to a workspace"

- **What happened.** The key was accepted but every request came back `400 BadRequestError`. The app only showed the error type, so we had to run a bare call in the terminal to read the message.
- **Why.** Anthropic keys created at organisation level are not tied to a workspace, and the API then requires the workspace id on each request.
- **What we tried.** Checked the key for spaces, tried other model names, then read the full error text.
- **Fix.** Optional `ANTHROPIC_WORKSPACE_ID` in `.env`, passed to the SDK. The app now shows the provider's message for bad requests (key masked).
- **Learned.** Show the real error text to the person debugging. "BadRequestError" alone cost us twenty minutes.

## The first real plan took far too long

- **What happened.** With `claude-sonnet-5`, one plan for 2 people and 3 days took long enough to be annoying, and a plan that needed a repair and a cheaper retry tripled that.
- **Why.** Generation time grows with the number of words produced. Six recipes with steps is a lot of JSON, and Sonnet writes slowly.
- **What we tried.** Shorter recipes (4 one-sentence steps, no commentary) and a faster model (`claude-haiku-4-5-20251001`) as the default. Seconds per call are now shown under "Under the hood" and recorded by the evaluation script.
- **Learned.** Since the code validates every answer, a smaller model is an acceptable trade. Measured comparison: see `docs/prompt-log.md`, "Model comparison".

## "Address already in use" when starting the server

- **What happened.** `uvicorn` refused to start, and the browser kept showing an old version of the page.
- **Why.** A server from an earlier terminal session was still running on port 8000.
- **Fix.** `kill $(lsof -ti :8000)` then start again.

## No supermarket API

See [`decisions.md`](decisions.md), point 2. The first plan (call a price API) was abandoned after research.

## Git mistakes

We left these mistakes in the history instead of rewriting `main`: rewriting shared
history would break everyone's copy, and the mistakes are part of what we learned.

### A pull request merged into the wrong branch (#2)

- **What happened.** Pull request #2 (`feature/shopping-maths`) was merged into
`docs/contributing` instead of `main`. The shopping maths only reached `main` later, when
pull request #3 merged `docs/contributing`.
- **Why.** When you open a pull request, GitHub asks for a *base* branch: the branch that
will receive the changes. `docs/contributing` was picked instead of `main`. The line
"wants to merge into ..." is easy to miss, and nobody noticed it before merging either.
- **Fix.** Nothing was lost, because pull request #3 was merged just after, so we left it
as it was. If #3 had been closed, the shopping maths would never have reached `main`.
- **Learned.** Read the base branch before creating a pull request, and again before
approving one. Always start a new branch from an up-to-date `main`.

### Commits pushed straight to main

- **What happened.** Two README edits reached `main` without a pull request. On 21
September, `README.md update` (Oscar) was committed on his local `main` and pushed. On 23
September, `Update README.md` (Tom) was made in GitHub's web editor and changed the title
to "Student Meal Planner for student ". The wrong title stayed until pull request #36
fixed it.
- **Why.** Nothing stopped it: `main` was not protected. In the browser, GitHub's default
choice is "Commit directly to the main branch", with a ready-made message like "Update
README.md". Both messages say which file changed, not what changed, and nobody reviewed
the edits.
- **Fix.** The title was fixed in pull request #36. `main` is now protected: every change
needs a pull request and one approval.
- **Learned.** A written rule is not enough; the tool has to block the wrong path. In the
web editor, choose "Create a new branch for this commit and start a pull request", and
write a message that says what changed.

### Our first merge conflict: two branches, the same table row

- **What happened.** `prompt/experiment-model-total` (the x1 experiment) had been open for a while. Meanwhile v5 was merged into `main`. Bringing `main` back into the branch stopped on `CONFLICT (content): Merge conflict in prompts/README.md`. `docs/prompt-log.md` merged by itself even though both sides had also written in it.
- **Why.** Both branches added a row at the *end* of the same Markdown table, so both sides changed the same line. Git has no idea that two new table rows can simply live next to each other; that is a human decision. `prompt-log.md` was fine because the two sides wrote in different sections of the file, far apart.
- **Fix.** Keep both rows, in the order the versions were written (x1 then v5), delete the `<<<<<<<` / `=======` / `>>>>>>>` markers, check that the table still renders, commit the resolution. It is commit `9c95f9e`, and the resolution is visible with `git show --cc 9c95f9e`.
- **Learned.** Two things. A conflict is not an error, it is Git refusing to guess; the fix took a minute because both changes were small and we understood both. And the real lesson for the way we work: append-only tables and logs conflict every single time two people work in parallel, so it is better to merge `main` into a long-lived branch early and often than to discover four days of divergence at the end. To replay it without touching anything: `git merge-tree --write-tree 8123f4e 6d15add`.

### The course brief was sitting inside the repository

- **What happened.** `[students] DAT32-91_Prompt_Engineering_Git_Project_Guidelines.docx` was saved in the project folder, so `git status` offered to commit it and a `git add -A` staged it into a local commit. We caught it before pushing (`git reset --soft HEAD~1`, unstage the file, commit again), so it never reached the shared history.
- **Why it matters.** The repository is our work; the teacher's brief is not ours to redistribute, and a binary `.docx` in a Git history cannot be diffed or removed cleanly afterwards.
- **Fix.** Added to `.gitignore` (`*.docx`, and the brief by name) so the file can stay in the working folder without ever being staged again.
- **Learned.** Check what `git add -A` is about to stage. An untracked file in the working folder is one careless `git add` away from being in the history for good. main
