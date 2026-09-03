# Why the routing table looks like this

Last checked: September 2026. Two kinds of evidence are mixed here; they are
labeled so you know which can be trusted after the next model release.

## Documented by Anthropic

- Cache-read pricing per MTok: Fable 5.1 $0.25, Opus 5 $0.50, Sonnet 5 $0.20,
  Haiku 4.5 $0.10. Input/output: Fable 5.1 $10/$50, Opus 5 $5/$25, Sonnet 5
  $2/$10, Haiku 4.5 $1/$5. Agent sessions are mostly cache reads, which is why
  Fable at low effort lands near Sonnet cost per task.
  https://platform.claude.com/docs/en/about-claude/pricing
- On Max, Team Premium and Enterprise seats, Fable usage may take at most 50%
  of the weekly limit; it is the same limit, not extra quota.
  https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan
- Anthropic's own default is `high` effort on every current model, with `low`
  reserved for "short, scoped, latency-sensitive tasks that are not
  intelligence-sensitive". The skill inverts this on purpose.
  https://code.claude.com/docs/en/model-config
- Anthropic's cost guide: Sonnet handles most coding tasks; reserve Opus for
  complex architectural decisions; `model: haiku` for simple subagent tasks.
  Agent teams cost roughly 7x a standard session.
  https://code.claude.com/docs/en/costs
- Subagent model resolution order, `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`, Explore
  inheriting the session model since v2.1.198, frontmatter `effort` overriding
  session effort. https://code.claude.com/docs/en/sub-agents
- `/rewind` restores to an already-cached prefix; `/compact` builds a new one
  and is the most expensive way to resume.
  https://code.claude.com/docs/en/checkpointing

## Third-party and practitioner reports (re-verify after each release)

- Effort moves cost more than model choice: Fable 5.1 spans roughly 11x output
  tokens from low to max, Opus 5 about 8x, while model price gaps are 2.5-5x.
- Snorkel matched runs: Fable 5.1 used 58% fewer output tokens and 36% less
  wall-clock than Opus 5. CursorBench: Fable 5.1 at low effort scored level
  with Fable 5 at high effort for about a third of the cost.
- Several independent practitioners report Sonnet at medium matching or
  beating Opus on "execute this plan" work. One production fleet pins 17 of 18
  subagents to `effort: medium`.
- Most "Fable burned my limits" reports trace to running high or max by
  default; several users drained a 5-hour Max window in under an hour that way.
- One user went from roughly 250 installed skills to under 25 and reported
  measurably better agent behavior and more headroom on limits.

## How to re-rank

Keep 5-10 tasks you know the right answer to, one per tier. When a model
ships, run each at the tier the table prescribes and one tier below. Move the
tier boundary only when the cheaper run fails the same way twice.
