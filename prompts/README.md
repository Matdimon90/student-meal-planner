# Prompts

One file per prompt version. The app loads these files at run time, so a prompt change is a normal Git diff that can be reviewed on its own.

Each file has two parts separated by the line `---USER---`: the system prompt, then the user message template. `{{placeholders}}` are filled in by `src/prompting.py`.

| Version | Technique added | What we expected it to fix |
| --- | --- | --- |
| `v1_zero_shot.md` | Zero-shot, one loose instruction | Baseline |
| `v2_structured_output.md` | Exact JSON format, unit rules | Replies that cannot be parsed, wrong units |
| `v3_constraints_and_roles.md` | Explicit constraints, package prices, honesty rule, role separation for user notes | Over-budget plans, wasted packages, pretending an impossible budget works, prompt injection through the notes field |
| `v4_few_shot.md` | Two worked examples (one feasible, one infeasible) | Weak ingredient reuse, vague refusals |
| `x1_model_total.md` | Experiment: v4 plus "add up the packages yourself and write the total" | Tested whether the pricing code could be dropped. It cannot: see the log, the model writes a number just under the budget instead of adding |
| `v5_varied_menu.md` | Written by us from the v4 results: gram equivalents for produce, a vegetable per meal, reuse target, "do not copy the examples" | Fruit in pieces, menus that copy the examples, leftovers. Scored lower than v4 (see the log) |

Measured results for each version are in [`docs/prompt-log.md`](../docs/prompt-log.md). Expectations above are hypotheses; the log says what actually happened.

The version used by the app is set in `src/planner.py` (`DEFAULT_PROMPT_VERSION`).
