# Claude Code mechanics and session hygiene

Reference detail behind the core rules in SKILL.md: versions, settings, env
vars and per-provider differences. Load it when configuring Claude Code,
debugging why a dispatch ran on the wrong model, or chasing a cache miss.
Checked 19 October 2026 against Claude Code v2.1.303.

## Claude Code mechanics

- Always pass `model` and `effort` when dispatching; the Agent tool takes a
  per-call `effort` from v2.1.292 (it overrides frontmatter, persists across
  resumes, and loses only to `CLAUDE_CODE_EFFORT_LEVEL`). Model resolution
  order (v2.1.251+):
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
- Aliases resolve per provider. Bedrock and Vertex: `sonnet` is Sonnet 4.5,
  `haiku` Haiku 4.5. Foundry: `opus` is Opus 4.6, `sonnet` Sonnet 4.5,
  `haiku` Haiku 4.5. Claude Platform on AWS: `sonnet` is Sonnet 4.6. The
  Build and Fallback rows are a weaker model there; check before trusting them.
- Effort values: `low`, `medium`, `high`, `xhigh`, `max` on Fable 5.1/5, Opus
  5.5/5/4.8/4.7, Sonnet 5.5/5, Haiku 5.5. Opus 4.6 and Sonnet 4.6 take only
  low, medium, high, max; an unsupported level falls back to the highest
  supported one below it. Levels are calibrated per model, so `medium` on
  Opus 5.5 is not `medium` on Sonnet 5.5. Effort in agent frontmatter
  overrides the session `/effort` while that agent runs, but not
  `CLAUDE_CODE_EFFORT_LEVEL`. A top-level `effortLevel` in user settings does
  not count for Opus 5.5; set per-model levels under `modelSettings`. `max`
  is not a valid `effortLevel`.
- Thinking is always on for Opus 5.5, Sonnet 5.5, Haiku 5.5 and the Fable
  models; effort is the only dial. Haiku 4.5 (still the `haiku` target on
  Bedrock, Vertex and Foundry) has no effort dial; do not set `effort` on a
  Haiku agent there, and drop `effort: low` from the bundled `scan` and
  `Explore` agents on those providers.
- Built-in `Explore` runs on the session model. Only when the session is on
  Fable, and only on a subscription, Console account or `ANTHROPIC_BASE_URL`
  gateway, does it drop to the `opus` alias; on Bedrock, Vertex and Foundry it
  stays on Fable. A user or project agent named `Explore` replaces it and
  keeps its own `model`; define one with `model: haiku`, `effort: low`.
- Workflow agents inherit the session model unless told otherwise. Set
  `CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL=sonnet` (v2.1.296+), or plan on Fable,
  then `/model sonnet` before launching the build. Start a dynamic workflow on
  a scoped task; they fan out fast.
- Safety nets: `CLAUDE_CODE_SUBAGENT_MODEL=sonnet` catches subagents with no
  model set. `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` (v2.1.257+) pins every subagent to
  it regardless of frontmatter or invocation; use only for a cost-locked session,
  since it also flattens the tiers above.
- Agent frontmatter also takes `maxTurns` (hard cap per dispatch, output comes
  back marked partial and can be resumed), `isolation: worktree` (parallel
  edits without collisions), `skills` (preload so the agent does not spend
  turns discovering them), and `tools` (read-only sets for Scan tier).
- A fork (`context: fork` skill, or a forked subagent) reuses the parent's
  prompt cache; a fresh subagent pays for its context again. For a task that
  needs the same context the parent already has, fork. Forks are on by
  default in `-p`, the SDK, desktop and VS Code from v2.1.303
  (`CLAUDE_CODE_FORK_SUBAGENT=0` turns them off).
- Subagents get a five-minute cache even on a subscription. A Build agent
  that waits on tests or long tool calls re-writes its cache every gap; set
  `subagentPromptCacheTtl: "1h"` (or `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL`)
  when its turns are routinely more than five minutes apart.
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
  conversation uncached. Effort can move mid-session on Opus 5.5, Fable 5.1
  (v2.1.260+), Sonnet 5.5 and Haiku 5.5 without a cache miss (API key or
  subscription; not on Bedrock, Vertex, a gateway, or HIPAA orgs). On every
  other model an effort change is a cache miss.
- The cache lives one hour on a subscription, five minutes on an API key or
  once usage credits kick in; pin it with `promptCacheTtl` or
  `CLAUDE_CODE_PROMPT_CACHE_TTL` (`5m` or `1h`). A six-minute break on the API
  turns the next cache read into a full cache write.
- Idle compaction (v2.1.299+, terminal only) compacts a 200K+ token session
  after about 54 idle minutes, just before the hour-long cache expires, so
  resuming pays for the summary, not the whole history. Leave it on; tune the
  threshold with `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS`. On the API's
  five-minute cache it fires too late, so compact by hand before a break
  there.
- `/clear` between unrelated tasks; it is free. `/compact` costs about one
  request (roughly $0.25 at 150K context on Opus 5.5) and pays back in about
  ten turns, so never compact right before finishing. `/rewind` truncates to an
  already-cached prefix.
- Usage limits: session and weekly limits are shared across models. "You've
  hit your Opus limit" is family-specific; switch to Sonnet or Haiku with
  `/model` and keep working (the switch itself is a cache miss).
- Fast mode (`/fast`) is Opus-only (5.5, 5, 4.8), up to 2.5x faster at
  $8/$40 per MTok on Opus 5.5, billed to usage credits on a subscription and
  per token on Console; not offered on Bedrock, Vertex, Foundry or Claude
  Platform on AWS. Skip it unless latency matters more than money.
- Agent teams run each teammate as a separate Claude instance with its own
  context, roughly 7x the tokens of a normal session. Prefer one level of
  subagents.
- Context bands: under 70% full, carry on. 70-80%, finish what is open and
  prefer batched dispatches over new inline reads. Over 80%, start nothing
  new: commit verified work, write the handoff, then `/compact` with a note on
  what to keep.
- After a model release, run `/doctor prompt-audit` on CLAUDE.md, skills and agents. Instructions written for an
  older model make the new one write more and repeat tool calls; Anthropic's
  own migration example cut cost 18% by moving to Opus 5.5 at low and a
  further 9% by removing stale rituals.
