---
name: efficient-claude
description: "Use whenever spawning a subagent, creating a routine, or choosing model/effort for a delegated task in Claude Code. Routes each task to the cheapest Claude model and effort that still does it right, and straight to Fable when the stakes demand it; escalates on evidence, with a quality gate on every deliverable. Companion to efficient-fable (which says WHAT to delegate; this says WHICH model)."
license: MIT
metadata:
  author: thevrus
  version: "1.2"
---

# Efficient Claude

Two goals, in this order: the best result on work that matters, the cheapest
path on work that does not. Stakes decide the route, not habit. The vendor
default (biggest model, high effort, everywhere) spends tokens on renames;
the miser default (Sonnet everywhere) ships a mediocre migration. Both are
wrong. Start at the floor for routine work and escalate on evidence; go
straight to the top when the deliverable is the thing you will be judged on.

Rationale and the measurements behind the table live in
[references/rationale.md](references/rationale.md). Load it only when someone
asks why, or when re-ranking after a model release.

## Routing table (Claude Code v2.1.280+, Opus 5.5 generation)

| Tier | `model` | Effort | `maxTurns` | Route here when |
| --- | --- | --- | --- | --- |
| Scan | `haiku` | low | 10 | Grep/search, file inventory, log and test-output reduction, "where is X defined", one-page summaries, formatting, renames. Outcome fully determined by the instruction and a mistake is cheap to spot. |
| Build | `sonnet` | medium | 40 | Bounded edits from a clear spec, tests from an existing pattern, data transforms, drafting from a template, browser flows with known steps. |
| Reason | `opus` | medium | 40 | Ambiguous scope, multi-file refactor, root-cause debugging, code review with follow-up edits, reconciling conflicting reports, anything with security or money consequences. |
| Frontier | `fable` | low, then medium | - | Any stakes-override case below (the deliverable itself, no pattern to follow, unsupervised runs, coordination, security or money), or after `opus` at high hit the same problem twice. Never xhigh/max. |
| Fallback | `sonnet` | high | 40 | "You've hit your Opus limit": Reason-tier work continues on Sonnet at high until the reset. |
| Visual | (inherit) | default | 20 | Reading screenshots, charts, UI diffs, image-heavy pages. |

`opus` is Opus 5.5. Its default effort is medium; every other model defaults
to high. Three models cover a day: Haiku for lookups, Opus for the work you
supervise, Fable for the rare task the others cannot finish.

Defaults when unsure: `sonnet` medium for anything with a spec, `opus` medium
for anything without one. "Execute this plan" goes to Build even when a bigger
model wrote the plan. A mechanical edit across many files from a session
already on Opus stays on `opus` at **low** (same model, cheaper turns, no
switch). Drop one tier after two routine tasks in a row succeed.

Score a task on four signals: complexity, blast radius, reversibility,
ambiguity. The tier is the **highest** signal, never the average. Risk floor:
security, auth, money, data integrity, concurrency, and anything irreversible
never route below Reason, even when the diff looks like a one-liner. Scan and
Build only take work where a mistake is cheap to spot.

If the account has no Fable access: `opus` at high takes Frontier. Same table,
shifted down.

## Stakes override: go straight to Fable

Skip the ladder and route to `fable` (low, medium for the final pass) when any
of these hold. A retry here costs more than the model ever will.

- **The output is the deliverable.** Production migration, public API or
  schema design, customer-facing copy or code, anything irreversible or
  expensive to redo. One shot at the right answer beats three cheap tries.
- **No pattern to follow.** Novel problem, ambiguous requirements that need
  taste, or a design with real tradeoffs and no precedent in the codebase.
- **Unsupervised runs.** Anything that runs for more than an hour without you
  reading along, overnight jobs, autonomous loops. Fable finishes jobs the
  others stall on, and nobody is there to catch the stall.
- **Coordination.** One change that spans many repos or subagents; Fable as
  the planner and integrator, cheaper tiers as the hands.
- **Adversarial or high-consequence judgment.** Security review, money
  paths, reconciling conflicting evidence, a decision that is hard to walk
  back.
- **The user says so.** "Best result", "this matters", "do it right", "take
  your time" all mean Fable. Do not negotiate it down to save tokens.

Tripwires that promote a task mid-flight: a design that touches three or more
files or a public interface; more than 50 new lines produced from a plan
nobody reviewed; a migration, a concurrency change, or anything irreversible.
Hitting one means at least Reason for the work and the quality gate before
it ships.

Everything else starts at the floor. When in doubt, ask one question: if this
comes back wrong, is the redo cheap? If yes, start low. If no, start with
Fable.

## Escalation rule

Start low. Escalate only on a concrete miss, one dial at a time. After a miss
ask, in order:

1. **Could it check its own work?** No test, build, or script to run means
   the miss is a missing verifier, not a model problem. Add the check first.
   One test run costs one turn; more effort adds thinking to every turn.
2. **Did it not try hard enough?** Skipped a file, didn't run tests, fixed one
   layer and stopped (updated the handler, not the caller). Raise effort one
   notch, keep the model.
3. **Did it not know enough?** It had the files, clearly tried, and was still
   confidently wrong. Move up one model tier.
4. **Did it get worse with more effort, or game the check?** Over-optimization.
   Lower effort and sharpen the spec; do not escalate model.
5. **Fix loop?** Rounds 1-3: resume the same worker with the findings. Round 4:
   a fresh worker one tier up. Round 5: stop and adjudicate, either park it
   with a written ruling or fix it by hand. A loop that survives three
   resumes usually means the worker cannot see its own problem; a loop that
   survives five is you refusing to decide.

Effort math on Opus 5.5: `high` adds roughly 20K thinking tokens per task,
about $0.40. A ten-turn retry loop at 100K context costs about the same. High
pays for itself when it saves one retry and is wasted when medium would have
finished. If `opus` at high hits the same problem twice, go to Fable; do not
wait for a third failure.

If nothing above applies, the fix is upstream: sharpen the prompt, scope, or
context. Never bump both model and effort at once; you learn nothing about
what worked.

This is deliberately below Anthropic's published guidance (start at the
model's default effort, `high` on most models). The floor-first inversion is
the point of the skill; the rationale file has the numbers.

## Using Fable well

Fable has three jobs, and the price is different for each.

- **Orchestrator (cheap).** A Fable session at low effort that reads, decides,
  writes specs and verdicts, and delegates volume to the tiers below. Its
  turns are mostly cache reads at $0.25/MTok; its output is short. This is
  the default way to run a session when quality matters.
- **Judge (cheap).** A read-only Fable pass over a cheaper worker's output
  before it ships: one verdict, the exact fixes, nothing else. Costs one
  context read and a few hundred output tokens. Use it on every deliverable
  (see the quality gate below) and on any change touching security or money.
- **Worker (expensive).** Fable writing the code itself. Reserve for the
  stakes override and the Frontier row; elsewhere Opus 5.5 does the same
  work at 40% of the output price.

Rules for all three:

- Run Fable at **low effort** first; medium for a final review of a risky
  change or a problem that survived low. `xhigh` and `max` overthink and cost
  8-11x the tokens of low; use them only on a stuck problem with full
  context, for one turn.
- Fable and Opus 5.5 keep the prompt cache across effort changes on an API key
  or subscription, so raise effort for one hard step and drop it again.
- Plans: on Max, Team Premium and Enterprise premium seats, Fable draws from
  the same weekly limit and may use at most 50% of it. On Pro, Team Standard
  and Enterprise standard seats, Fable is not included at all and bills
  usage credits from the first request. Claude Code asks before billing
  credits in an interactive session; with `-p` or the Agent SDK it bills
  without asking.
- Every Fable turn is a budgeted consult, not a chat: emit specs and
  verdicts, delegate volume. Budget it, do not avoid it. Skipping Fable on a
  task that needed it costs more than a week of routine Fable turns.

## Claude Code mechanics

- Always pass `model` when dispatching. Resolution order (v2.1.251+):
  per-invocation `model` > agent frontmatter `model` >
  `CLAUDE_CODE_SUBAGENT_MODEL` env > session model. Before v2.1.251 the env var
  came first and overrode everything.
- An omitted `model` inherits the session model, and `default` is Opus 5.5 on
  every plan (Pro and Team Standard moved from Sonnet in v2.1.280), on the
  API, and on AWS, Bedrock and Vertex. Microsoft Foundry defaults to Sonnet
  4.5. "Inherit" is never the cheap option.
- Aliases: `haiku`, `sonnet`, `opus` (Opus 5.5 from v2.1.280, Opus 5 before),
  `fable` (Fable 5.1), `best` (Fable if available, else Opus), `opusplan`,
  `default`. Pin full IDs such as `claude-opus-5-5` only when reproducibility
  matters. Run `claude update` if `opus` still resolves to Opus 5.
- Effort values: `low`, `medium`, `high`, `xhigh`, `max` on Fable 5.1/5, Opus
  5.5/5/4.8/4.7, Sonnet 5. Levels are calibrated per model, so `medium` on
  Opus 5.5 is not `medium` on Sonnet 5. Effort in agent frontmatter overrides
  the session `/effort` while that agent runs, but not the effort env var. A
  top-level `effortLevel` saved before v2.1.280 does not apply to Opus 5.5.
- Thinking is always on for Opus 5.5 and the Fable models; effort is the only
  dial. Haiku 4.5 has no effort dial at all; do not set `effort` on a Haiku
  agent.
- Built-in `Explore` inherits the session model (capped at Opus) since
  v2.1.198. A user or project agent named `Explore` replaces it and keeps its
  own `model`; define one with `model: haiku`, `effort: low`.
- Safety nets: `CLAUDE_CODE_SUBAGENT_MODEL=sonnet` catches subagents with no
  model set. `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` pins every subagent to it
  regardless of frontmatter or invocation; use only for a cost-locked session,
  since it also flattens the tiers above.
- Agent frontmatter also takes `maxTurns` (hard cap per dispatch, output comes
  back marked partial and can be resumed), `isolation: worktree` (parallel
  edits without collisions), `skills` (preload so the agent does not spend
  turns discovering them), and `tools` (read-only sets for Scan tier).
- A fork (`context: fork` skill, or a forked subagent) reuses the parent's
  prompt cache; a fresh subagent pays for its context again. For a task that
  needs the same context the parent already has, fork.
- A skill with `model:` in its frontmatter that differs from the session model
  is a model switch for that turn and drops the cache. Put the model on a
  forked agent instead.
- Safety classifiers can re-run a flagged Fable or Opus 5.5 request
  (cybersecurity, biology) on a fallback model. That is a model switch and a
  cache reset; expect it on security work.
- Scheduled routines: monitors and digests are Scan; anything that drafts a
  message for the user or touches money is Build; research with judgment is
  Reason.
- Browser work on a known flow is Build. Interpreting a page never seen before
  is Reason.
- Keep installed skills few and CLAUDE.md under 200 lines. Both are resent on
  every turn of every session.

## Session hygiene

- Pick `/model` once at session start; a model switch reads the whole
  conversation uncached. Effort can move mid-session on Opus 5.5 and Fable 5.1
  without a cache miss (API key or subscription; not on Bedrock, Vertex, a
  gateway, or HIPAA orgs). On every other model an effort change is a cache
  miss.
- The cache lives one hour on a subscription, five minutes on an API key or
  once usage credits kick in. A six-minute break on the API turns the next
  cache read into a full cache write. Compact before you step away, not after.
- `/clear` between unrelated tasks; it is free. `/compact` costs about one
  request (roughly $0.25 at 150K context on Opus 5.5) and pays back in about
  ten turns, so never compact right before finishing. `/rewind` truncates to an
  already-cached prefix.
- Usage limits: session and weekly limits are shared across models. "You've
  hit your Opus limit" is family-specific; switch to Sonnet or Haiku with
  `/model` and keep working (the switch itself is a cache miss).
- Fast mode (`/fast`) is Opus-only (5.5, 5, 4.8), up to 2.5x faster at
  $8/$40 per MTok on Opus 5.5, billed to usage credits on a subscription. Skip
  it unless latency matters more than money.
- Agent teams run each teammate as a separate Claude instance with its own
  context, roughly 7x the tokens of a normal session. Prefer one level of
  subagents.
- Context bands: under 70% full, carry on. 70-80%, finish what is open and
  prefer batched dispatches over new inline reads. Over 80%, start nothing
  new: commit verified work, write the handoff, then `/compact` with a note on
  what to keep.
- After a model release, run `/claude-api prompt-audit` on CLAUDE.md and
  skills. Instructions written for an older model make the new one write more
  and repeat tool calls; Anthropic's own migration example cut cost 18% by
  moving to Opus 5.5 at low and a further 9% by removing stale rituals.

## Delegation rules

- One level deep. A subagent that spawns its own reviewer or subagent is a
  defect, not extra rigor. Duplicate review seats are the most common waste.
- Delegation only helps when it changes the tier or isolates context. A
  subagent on the same model and effort as the session, given the same
  context, buys nothing and costs a cache write. Delegate down for volume,
  up for judgment, sideways only to keep noise out of the main context.
- More than three dispatches in one run: print a routing plan first (subtask,
  model, effort, reason), cap fan-out at ten, and keep a ledger file of what
  was dispatched and what returned. Re-dispatching finished work after a
  compaction is the single most expensive failure in long runs; the ledger
  survives compaction, the conversation does not.
- Turn count beats token price. Every turn resends the whole conversation, so
  a cheap model that takes 2-3x the turns costs more than one Build-tier call.
  Scan is for single-shot lookups.
- A small model that misreads a search result sends the main model after the
  wrong file, and the main model pays for the detour. Keep Scan on work where
  a mistake is cheap to spot: finding files, running tests, reading logs.
- Keep code edits and judgment on the main model. `opusplan` puts the edits on
  Sonnet, the opposite of that; measure it on your own tasks before making it
  a default.
- If the output is mechanically checkable (schema, tests, counts, diff
  applies), build the check and a retry-or-escalate loop instead of an
  example-heavy prompt. Spend effort on the verifier, not on prompt polish.
- Never let a cheap model re-improve its own output in a loop without an
  outside judge. It returns the same answer nearly every time, and the rare
  change is a regression. Score each pass, keep the best, stop at the first
  regression.
- A stage with no failable check must be labeled unverified. "I reviewed it
  and it looks right" is not a check.
- **Quality gate.** Anything that will be shipped, sent, or merged gets a
  final pass one tier above the worker that produced it, read-only, verdict
  only: SHIP, FIX-FIRST with the exact fixes, or RETHINK with the reason. For
  Reason-tier and stakes work that pass is Fable (the `frontier-review`
  agent). Cheap draft plus expensive judge beats expensive draft alone on
  both cost and quality.
- **Judge is never the generator.** The context that built the work does not
  grade it; the reviewer is an isolated agent that never saw the build. Hand
  it the bare claim and the diff, not the worker's reasoning, or it inherits
  the worker's blind spot while following the rule to the letter.

## Handoff packet for any delegated task

Write the prompt as if the recipient has zero chat context: objective, exact
scope and out-of-scope, evidence format to return, verification steps, and
stop conditions. Lower-tier models need a tighter spec; a vague spec is what
pushes a Sonnet task into needing Opus.

Require a fixed return shape so results can be checked mechanically:

```
status: DONE | PARTIAL | BLOCKED
completed: [...]        skipped: [...] (with reason)
findings: [{claim, location (file:line), severity, evidence}]
commands_run: [...]     artifacts: [...]
uncertainties: [...]
```

A return with no `status` or no `findings` is a FAIL, not a summary. Anything
truncated by `maxTurns` or a timeout is logged as PARTIAL; a silent cap reads
as full coverage and is the most common way a review lies.

## Report the route

When you delegate, say the tier you chose and why in one line, e.g.
"Routing to scan/haiku: pure grep across the repo, spec fully determines
output." That makes the routing auditable and teaches the pattern.

The label is only true when the work actually runs there. Writing "routing
to scan/haiku" and then doing the grep inline on a Fable session is the
cosmetic-label anti-pattern: the tier is a dispatch, not a caption.

## Rationalizations to refuse

| Excuse | Reality |
| --- | --- |
| "It's a one-liner, Sonnet is fine" | If it touches auth, money, data, or is irreversible, the risk floor is Reason. Size is not stakes. |
| "Fable will burn my limits" | Skipping Fable on a task that needed it costs a redo, which costs more than a week of Fable turns. Budget it, don't avoid it. |
| "I'll just do it myself, faster" | On a Fable session that is the most expensive typist available. Delegate volume; keep judgment. |
| "It looked right, ship it" | Not a check. Unverified stages are labeled unverified; deliverables get the quality gate. |
| "One more effort bump will fix it" | After two misses at high on the same problem, it is a model problem or a spec problem, not an effort problem. |
| "I reviewed my own work" | Judge is never the generator. Isolated reviewer, bare claim, diff. |
| "Sending it to a subagent makes it more rigorous" | Same tier, same context, same blind spot. Delegation changes nothing unless it changes the tier or isolates context. |

## Self-audit

Run when routing feels off, after a Claude Code upgrade, and after a model
release.

- Does `/tasks` show the model and effort you intended on each dispatched
  agent? A pinned `model` in frontmatter that does not appear there means a
  `FORCE` env var or an allowlist is overriding it.
- Is `CLAUDE_CODE_SUBAGENT_MODEL` a deliberate safety net or a stale leak
  in the environment? A forgotten `FORCE=1` flattens every tier.
- Do the `agents/` files still carry `model`, `effort` and `maxTurns`, and is
  a user-level `Explore` defined so the built-in cannot inherit the session
  model?
- At the end of a task, `/usage` shows three tells: cache share should be
  high on a long session; a lot of output on a small change means effort too
  high or a retry loop; total input many times the conversation size means
  too many turns. Read the transcript to find where the loop repeated.
- Is Fable spend tracked against the plan? On Max and premium seats the cap
  is 50% of the weekly limit; on Pro and standard seats it bills credits.
- Re-run the 5-10 personal benchmark tasks; move a tier boundary only when
  the cheaper run fails the same way twice.

## The table goes stale

Sonnet 5.5 and Haiku 5.5 are announced for the weeks after Opus 5.5; the Build
and Scan rows will move when they ship. Keep 5-10 personal tasks you know the
right answer to (one per tier) and re-run them when a model ships. Re-rank
tiers from that, not from launch-day benchmarks or social sentiment.
