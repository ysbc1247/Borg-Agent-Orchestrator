# Repository Instructions

These instructions apply to work performed in this repository.

## Workflow Defaults

- Continue to the next logical engineering step unless the user explicitly tells you to stop or redirect.
- Make code changes directly rather than stopping at analysis when the next implementation step is clear.
- Keep momentum through implementation, verification, commit, and push.
- Preserve working conventions across sessions by recording durable workflow, reporting, and handoff rules in repository files rather than keeping them only in transient context.

## Git Workflow

- Always commit after making meaningful changes in this repository.
- Always push committed changes to the remote branch for this repository.
- Do not ask the user for permission before committing or pushing.
- Split changes into small, specific, logically separated commits.
- Split commits more aggressively than usual: when practical, separate Python code, documentation, handoff files, config/examples, and workflow-policy changes into different commits.
- Do not bundle unrelated file classes together in one commit just because they were edited in the same session.
- If one session touches multiple concerns, stage and commit each concern independently in the order they were validated.
- Prefer the smallest defensible commit that leaves the repository in a coherent state.
- When working in a single file, still shard commits by function, feature slice, or behavior change where practical.
- Use clear commit messages that describe the specific unit of work.

## Continuity And Memory

- When a session establishes a new durable working convention, store it in `Agents.md`, `NEXT_STEPS.md`, `README.md`, or another appropriate tracked file before ending the work.
- Keep `NEXT_STEPS.md` current enough that a new Codex session can resume with the same operational assumptions and current priorities.
- Keep user-facing workflow changes in `README.md` when they affect how the repository should be used.
- Use timestamp-prefixed report filenames in KST format `YYYYMMDDHHMM_*` for report artifacts stored in the repository.
- If the user types `milestone`, treat that as an instruction to record the current state for the next Codex context.
- On `milestone`, update the relevant tracked memory files for the work that was completed, especially `NEXT_STEPS.md`, `README.md`, `Agents.md`, and report files when applicable.
- On `milestone`, commit and push those updates using the repository's split-commit policy instead of bundling all persistence changes together.

## Data Layout

- Prefer keeping large Borg data outside the repository under `~/Documents`.
- Treat `~/Documents/borg_data` as the default raw data location.
- Treat `~/Documents/borg_processed` as the default processed data location.
- Do not commit generated datasets or large external data files into git.
- When a new parquet type or artifact directory is created under the external processed-data tree, add a schema or artifact explanation file in that same directory describing what the files mean and what the important columns represent.
- Do not rely only on repository docs for parquet meanings; keep a local README-style explanation beside the actual generated outputs.

## Cluster Defaults

- Default processing targets are clusters `b`, `c`, `d`, `e`, `f`, and `g`.
- Exclude clusters `a` and `h` by default unless the user explicitly asks to include them.

## Approval Behavior

- Do not ask the user for approval for routine repository workflow actions such as commits and pushes.
- If the runtime or sandbox requires an approval flow outside repository policy, comply with the runtime requirement, but do not ask for git workflow approval on your own initiative.
