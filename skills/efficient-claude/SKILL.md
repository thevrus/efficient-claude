---
name: efficient-claude
description: "Use whenever spawning a subagent, creating a routine, or choosing model/effort for a delegated task in Claude Code. Routes each task to the cheapest Claude model and effort level that can still do it right; escalates only on evidence. Companion to efficient-fable (which says WHAT to delegate; this says WHICH model)."
license: MIT
metadata:
  author: thevrus
  version: "1.1"
---

# Efficient Claude

Bias: speed and value, not maximum capability. The vendor default (biggest
model, high effort) is tuned to spend tokens. Start at the floor and escalate
only when a concrete failure proves the floor was too low. One step up per
failure. Never pre-emptively "use the big one just in case."

Rationale and the measurements behind the table live in
[references/rationale.md](references/rationale.md). Load it only when someone
asks why, or when re-ranking after a model release.

## Routing table

| Tier | `model` | Effort | `maxTurns` | Route here when |
| --- | --- | --- | --- | --- |
| Scan | `haiku` | low | 10 | Grep/search, file inventory, log reduction, list extraction, "does X exist", summarizing one page, formatting, renames. Outcome fully determined by the instruction. |
| Build | `sonnet` | medium | 40 | Bounded edits from a clear spec, writing tests, running/reporting test output, browser flows with known steps, drafting from a template, data transforms. |
| Reason | `fable` | **low** | 40 | Ambiguous scope, multi-file refactor, root-cause debugging, comparing conflicting reports, architecture/tradeoff decisions, anything with security or money consequences. |
| Frontier | `fable` | medium | - | Top-level session only. After Fable low failed with full context, or a multi-hour autonomous run. Never xhigh/max. |
| Fallback | `opus` | medium | 40 | When the Fable weekly cap (50% of plan quota on Max, Team Premium, Enterprise) is hit, or via `opusplan` (Opus plans, Sonnet executes). |
| Visual | (inherit) | default | 20 | Reading screenshots, charts, UI diffs, image-heavy pages. |

Defaults when unsure: `sonnet` at **medium** effort. Raise to high only after
it visibly under-tried. "Execute this plan" tasks go to Build/`sonnet` even
when a bigger model wrote the plan. Drop to Scan after two routine tasks in a
row succeed. Escalate one tier after one clear failure with adequate context.

If the account has no Fable access: `opus` takes Frontier, `sonnet` takes
Reason. Same table, shifted down.

## Escalation rule

Start low. Escalate only on a concrete miss, one dial at a time. After a miss
ask:

- **Did it not know enough?** It had the files, clearly tried, and was still
  confidently wrong. Move up one model tier.
- **Did it not try hard enough?** It skipped a file, didn't run tests, bailed
  mid-refactor. Raise effort one notch, keep the model.
- **Did it get worse with more effort, or game the check?** Over-optimization.
  Lower effort and sharpen the spec; do not escalate model.
- **Fix loop?** Rounds 1-3: resume the same worker with the findings. Round 4:
  a fresh worker one tier up. A loop that survives three resumes usually means
  the worker cannot see its own problem.

If none applies, the fix is upstream: sharpen the prompt, scope, or context.
Never bump both model and effort at once; you learn nothing about what worked.

This is deliberately inverted from Anthropic's published guidance (default
`high`, use `low` only for latency-sensitive tasks). The inversion is the
point of the skill; see the rationale file for the numbers.

## Fable rules

- Fable is the orchestrator, architect, and final judge, not the typist. Keep
  its own token volume low: emit specs and verdicts, delegate volume.
- Run Fable at **low effort** by default. Raise to high only for the final
  review or a stuck problem; `max` overthinks.
- On a subscription every Fable turn is a budgeted consult, not a chat. Fable
  usage is capped at 50% of the weekly limit on Max, Team Premium and
  Enterprise seats; Sonnet carries the volume.

## Claude Code mechanics

- Always pass `model` when dispatching. Resolution order (v2.1.251+):
  per-invocation `model` > agent frontmatter `model` >
  `CLAUDE_CODE_SUBAGENT_MODEL` env > session model. Before v2.1.251 the env var
  came first and overrode everything.
- An omitted `model` inherits the session model. The `default` alias is Opus 5
  on Max, Team Premium, Enterprise and API, Sonnet 5 on Pro and Team Standard,
  so "inherit" is usually the priciest option.
- Aliases: `haiku`, `sonnet`, `opus`, `fable` (Fable 5.1), `best` (Fable if
  available, else Opus), `opusplan`, `default`. Pin full IDs only when
  reproducibility matters.
- Effort values: `low`, `medium`, `high`, `xhigh`, `max` on Fable 5.1/5, Opus
  5/4.8/4.7, Sonnet 5. Effort in agent frontmatter overrides the session
  `/effort` while that agent runs, but not the effort env var.
- Built-in `Explore` inherits the session model (capped at Opus) since
  v2.1.198. A user or project agent named `Explore` replaces it and keeps its
  own `model`; define one with `model: haiku`, `effort: low`.
- Safety nets: `CLAUDE_CODE_SUBAGENT_MODEL=sonnet` catches subagents with no
  model set. `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` pins every subagent to it
  regardless of frontmatter or invocation; use only for a cost-locked session,
  since it also flattens the tiers above.
- Agent frontmatter also takes `maxTurns` (hard cap per dispatch, use the
  table values), `isolation: worktree` (parallel edits without collisions),
  `skills` (preload so the agent does not spend turns discovering them), and
  `tools` (read-only sets for Scan tier).
- Scheduled routines: monitors and digests are Scan; anything that drafts a
  message for the user or touches money is Build; research with judgment is
  Reason.
- Browser work on a known flow is Build. Interpreting a page never seen before
  is Reason.
- Keep installed skills few. Each loaded skill stays in context for the whole
  session.

## Session hygiene

- Set `/model` and `/effort` once at session start. Claude Code warns on a
  mid-session switch because it invalidates the prompt cache.
- `/clear` between unrelated tasks. `/rewind` instead of `/compact` to undo bad
  turns: rewind truncates to an already-cached prefix, compact rebuilds one.
- Fast mode (`/fast`) needs usage credits enabled and bills them, not plan
  quota; first-party API only. Skip on a subscription unless latency matters
  more than money.
- Agent teams run each teammate as a separate Claude instance with its own
  context, roughly 7x the tokens of a normal session. Prefer one level of
  subagents.

## Delegation rules

- One level deep. A subagent that spawns its own reviewer or subagent is a
  defect, not extra rigor. Duplicate review seats are the most common waste.
- Turn count beats token price. Cheap models often take 2-3x the turns on
  multi-step work, so a Scan-tier model on a multi-step task can cost more in
  total and in wall-clock than one Build-tier call. Scan is for single-shot
  lookups.
- If the output is mechanically checkable (schema, tests, counts, diff
  applies), build the check and a retry-or-escalate loop instead of an
  example-heavy prompt. Spend effort on the verifier, not on prompt polish.
- Never let a cheap model re-improve its own output in a loop without an
  outside judge. It returns the same answer nearly every time, and the rare
  change is a regression. Score each pass, keep the best, stop at the first
  regression.
- A stage with no failable check must be labeled unverified. "I reviewed it
  and it looks right" is not a check.

## Handoff packet for any delegated task

Write the prompt as if the recipient has zero chat context: objective, exact
scope and out-of-scope, evidence format to return (files, line refs, commands,
diffs, uncertainties), verification steps, and stop conditions. Lower-tier
models need a tighter spec; a vague spec is what pushes a Sonnet task into
needing Opus.

## Report the route

When you delegate, say the tier you chose and why in one line, e.g.
"Routing to scan/haiku: pure grep across the repo, spec fully determines
output." That makes the routing auditable and teaches the pattern.

## The table goes stale

Model behavior shifts between releases. Keep 5-10 personal tasks you know the
right answer to (one per tier) and re-run them when a model ships. Re-rank
tiers from that, not from launch-day benchmarks or social sentiment.
