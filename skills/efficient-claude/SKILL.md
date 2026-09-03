---
name: "efficient-claude"
description: "Use whenever spawning a subagent, creating a routine, or choosing model/effort for a delegated task in Claude Code. Routes each task to the cheapest Claude model and effort level that can still do it right; escalates only on evidence. Companion to efficient-fable (which says WHAT to delegate; this says WHICH model)."
---

# Efficient Claude

Bias: speed and value, not maximum capability. The vendor default (biggest
model, high effort) is tuned to spend tokens. Start at the floor and escalate
only when a concrete failure proves the floor was too low. One step up per
failure. Never pre-emptively "use the big one just in case."

## Routing table

| Tier | `model` | Effort | Route here when |
| --- | --- | --- | --- |
| Scan | `haiku` | low | Grep/search, file inventory, log reduction, list extraction, "does X exist", summarizing one page, formatting, renames. Outcome fully determined by the instruction. |
| Build | `sonnet` | medium | Bounded edits from a clear spec, writing tests, running/reporting test output, browser flows with known steps, drafting from a template, data transforms. |
| Reason | `fable` | **low** | Ambiguous scope, multi-file refactor, root-cause debugging, comparing conflicting reports, architecture/tradeoff decisions, anything with security or money consequences. |
| Frontier | `fable` | medium | Top-level session only. After Fable low failed with full context, or a multi-hour autonomous run. Never xhigh/max: 8-11x the tokens of low, 1.5x quota burn. |
| Fallback | `opus` | medium | When the Fable weekly cap (~50% of plan quota) is hit, or via `opusplan` (Opus plans, Sonnet executes). |
| Visual | (inherit) | default | Reading screenshots, charts, UI diffs, image-heavy pages. |

Defaults when unsure: `sonnet` at **medium** effort. Raise to high only
after it visibly under-tried.
"Execute this plan" tasks go to Build/`sonnet` even when Opus wrote the plan;
several practitioners find Sonnet beats Opus there on quality, cost, and speed. Drop to Scan
after two routine tasks in a row succeed. Escalate one tier after one clear
failure with adequate context.

## Why this table (measured, Sep 2026)

- Effort moves cost more than model: Fable 5.1 spans 11x output tokens from
  low to max, Opus 5 about 8x. Model price gaps are only 2.5-5x.
- Fable 5.1 cache reads cost $0.25/MTok vs Sonnet $0.20, and agent sessions
  are mostly cache reads, so Fable at low effort lands near Sonnet cost per
  task while out-scoring Opus (Snorkel: 58% fewer output tokens and 36% less
  wall-clock than Opus 5 on matched runs; CursorBench: Fable 5.1 low = Fable 5
  high at a third of the cost).
- On subscriptions Fable is capped at roughly half the weekly quota, so Sonnet
  still carries the volume. Most "Fable burned my limits" reports come from
  people running high or max by default.
- Sonnet at medium matches or beats Opus on "execute this plan" work per
  several independent practitioners; one production fleet pins 17 of 18
  subagents to `effort: medium`.

## Escalation rule (inverted from Anthropic's guidance)

Start low. Escalate only on a concrete miss, and only one dial at a time:

Ask two questions after a miss:

- **Did it not know enough?** It had the files, clearly tried, and was still
  confidently wrong. Move up one model tier.
- **Did it not try hard enough?** It skipped a file, didn't run tests, bailed
  mid-refactor. Raise effort one notch, keep the model.

- **Did it get worse with more effort, or game the check?** That is
  over-optimization. Lower effort and sharpen the spec; do not escalate model.
- **Fix loop?** Rounds 1-3: resume the same worker with the findings. Round 4:
  a fresh worker one tier up. A loop that survives three resumes usually means
  the worker cannot see its own problem.

If neither applies, the fix is upstream: sharpen the prompt, scope, or context.
Never bump both model and effort at once; you learn nothing about what worked.

## Fable-specific rules

- Fable is the orchestrator, architect, and final judge, not the typist. Keep
  its own token volume low: emit specs and verdicts, delegate volume.
- Run Fable at **low effort** by default. On API pricing it can come out
  cheaper than Sonnet on coding evals while still beating Opus; `max` effort
  overthinks. Raise to high only for the final review or a stuck problem.
- That "cheaper than Sonnet" claim is per-token API math. On a subscription,
  Fable still drains the 5-hour window in a handful of prompts, so plan users
  should budget Fable turns, not treat them as free.
- Every Fable turn on a subscription plan is expensive; several people burn a
  5-hour Max window in under an hour. Treat each Fable call as a budgeted
  consult, not a chat.
- If the account has no Fable access, `opus` takes the Frontier role and
  `sonnet` takes Reason. Same table, shifted down.

## Claude Code mapping

- Scheduled routines (cron): monitors and daily digests are Scan; anything
  that drafts a message for the user or touches money is Build; research
  routines with judgment calls are Reason.
- Browser work that only needs snapshots/clicking on a known flow is Build
  tier. Anything that must interpret a page it has never seen is Reason tier.

- Per-invocation: pass `model` and rely on the subagent's `effort` frontmatter.
  Resolution order: per-invocation `model` > agent frontmatter > 
  `CLAUDE_CODE_SUBAGENT_MODEL` env > session model.
- Aliases: `haiku`, `sonnet`, `opus`, `fable` (resolves to Fable 5.1), `best`
  (Fable if available else Opus). Pin with full IDs only when reproducibility
  matters.
- Effort in agent frontmatter overrides the session `/effort`, so a
  `model: haiku` + `effort: low` Explore agent stays cheap even in a Fable
  session. Built-in Explore inherits the session model (capped at Opus), so
  define your own `Explore` with `model: haiku` to keep scans cheap.
- Set `CLAUDE_CODE_SUBAGENT_MODEL=sonnet` (without `_FORCE`) as a safety net
  so an unrouted subagent never inherits Fable by accident.
- Keep the installed skill count small. One user went from ~250 skills to
  under 25 and got measurably smarter agents and more headroom on limits.

## The table goes stale

Model behavior shifts between releases, so this routing is a starting point,
not a law. Keep 5-10 personal tasks you know the right answer to (one per
tier) and re-run them when a model ships. Re-rank tiers from that, not from
launch-day benchmarks or X sentiment.

## Session hygiene (cheap wins)

- Set model and effort once at session start. Switching either mid-session
  invalidates the prompt cache (Fable 5.1 allows per-message effort changes
  without a cache miss; others do not).
- `/clear` between unrelated tasks. `/rewind` instead of `/compact` to undo
  bad turns; compact always costs, rewind is free.
- Run `/claude-api prompt-audit` on skills after a model release to strip
  stale verification rituals and emphasis boosters the new model no longer
  needs. Fewer skills loaded beats more.
- Fast mode (`/fast`) bills usage credits, not plan quota. Skip it on a
  subscription unless latency matters more than money.

## Delegation rules

- Always name the model when dispatching. An omitted model silently inherits
  the session model, which is usually the priciest one.
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
"Routing to fast/haiku: pure grep across the repo, spec fully determines
output." That makes the routing auditable and teaches the pattern.
