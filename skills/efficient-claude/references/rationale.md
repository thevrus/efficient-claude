# Why the routing table looks like this

Last checked: 24 September 2026, two days after Opus 5.5 shipped. Two kinds
of evidence are mixed here and labeled so you know which to trust after the
next release.

## Documented by Anthropic

- Pricing per MTok (input / output / cache read): Fable 5.1 $10 / $50 / $0.25;
  Opus 5.5 $4 / $20 / $0.20; Opus 5 $5 / $25 / $0.50 (legacy); Sonnet 5 $2 /
  $10 / $0.20; Haiku 4.5 $1 / $5 / $0.10. Cache reads are 2.5% of input on
  Fable 5.1, 5% on Opus 5.5, 10% elsewhere. Agent sessions are mostly cache
  reads, which is why Opus 5.5 and Sonnet 5 cost the same per cached token.
  https://platform.claude.com/docs/en/about-claude/pricing
- Opus 5.5 default effort is `medium`; Fable 5.1, Sonnet 5 and the rest
  default to `high`. Anthropic's model guide: "start with Claude Opus 5.5 for
  most workloads. Use Claude Fable 5.1 for demanding reasoning and
  long-horizon agentic work, or when your evals on Claude Opus 5.5 at higher
  effort still fall short."
  https://platform.claude.com/docs/en/about-claude/models/overview
- Claude Code effort ladder as Anthropic states it: medium for well-scoped
  daily work, high when medium stalls, low for mechanical edits; "if high
  hits the same problem twice, switch to Fable 5.1." Three models a day: a
  small one for lookups, Opus 5.5 for supervised work, Fable for the hardest.
  Keep code edits on Opus 5.5; send search and log reading down to Sonnet or
  Haiku. Effort math: high adds ~20K thinking tokens, about $0.40 on Opus
  5.5, roughly one ten-turn retry loop at 100K context.
  https://claude.com/blog/what-a-task-costs-on-opus-5-5
- Anthropic's escalation heuristic ("did it not know enough, or not try hard
  enough") and its advice to check context and tools before turning either
  dial. https://claude.com/blog/claude-model-and-effort-level-in-claude-code
- `default` is Opus 5.5 on Pro, Max, Team, Enterprise, the API, AWS, Bedrock
  and Vertex from v2.1.280 (Pro and Team Standard were Sonnet 5 before).
  `opus` resolves to Opus 5.5 from v2.1.280. Effort levels per model and the
  per-model saved-effort rule. https://code.claude.com/docs/en/model-config
- Effort changes keep the cache on Opus 5.5 and Fable 5.1 with an API key or
  subscription (v2.1.260+ for Fable); a model switch never does. Forks reuse
  the parent's cache; fresh subagents do not. Cache lifetime is one hour on a
  subscription, five minutes on the API or on usage credits.
  https://code.claude.com/docs/en/prompt-caching
- Fable on plans: up to 50% of the weekly limit on Max, Team Premium and
  Enterprise premium seats, drawn from the same limit. Not included on Pro,
  Team Standard or Enterprise standard seats; usage credits only. The Fable 5
  promotion for those plans ended 19 July 2026 and never covered Fable 5.1.
  https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan
- "You've hit your Opus limit" is a family-specific limit; session and weekly
  limits are shared across models. https://code.claude.com/docs/en/errors
- Subagent model resolution order, `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`, Explore
  inheriting the session model since v2.1.198, frontmatter `effort` overriding
  session effort, `maxTurns` partial output.
  https://code.claude.com/docs/en/sub-agents
- Fast mode: Opus 5.5 at $8 / $40, up to 2.5x faster, usage credits only on a
  subscription. https://code.claude.com/docs/en/fast-mode
- Cost guide: Sonnet handles most coding tasks; `model: haiku` for simple
  subagents; agent teams cost roughly 7x a standard session; CLAUDE.md under
  200 lines. https://code.claude.com/docs/en/costs

## Anthropic launch-day benchmarks (vendor-run, re-verify)

- "Performs at the level of Claude Fable 5.1 on most work and costs 40% less
  to run than Opus 5." CursorBench 4.0: Opus 5.5 at medium 52.5% vs Fable 5.1
  at max 51.8% vs Opus 5 at max 46.6%. HAProxy C-to-Rust rewrite: Opus 5.5
  finished in 9.5 hours vs 12 for Fable 5.1 at 51% less cost. Output more
  than 30% faster than Opus 5. https://www.anthropic.com/news/claude-opus-5-5
- Customer quotes in the same post: Opus 5.5 at lowest effort beat Opus 5 at
  high on Deloitte code review (72% vs 56% of known bugs) and on Rogo's
  finance bench with ~60% fewer output tokens; Optiver saw Opus 5 quality in
  about half the turns and tokens.
- Migration example: Opus 4.8 default effort to Opus 5.5 at low cut a
  44-ticket support benchmark 18%; `/claude-api prompt-audit` cut a further
  9%. https://claude.com/blog/what-a-task-costs-on-opus-5-5

## Third-party and practitioner reports (pre-Opus 5.5, re-verify)

- Effort moves cost more than model choice: Fable 5.1 spans roughly 11x output
  tokens from low to max, Opus 5 about 8x, while model price gaps are 2.5-5x.
- Snorkel matched runs: Fable 5.1 used 58% fewer output tokens and 36% less
  wall-clock than Opus 5. Superseded for routing purposes by Opus 5.5.
- Several independent practitioners report Sonnet at medium matching or
  beating Opus 5 on "execute this plan" work. One production fleet pins 17 of
  18 subagents to `effort: medium`. Not yet re-measured against Opus 5.5.
- Most "Fable burned my limits" reports trace to running high or max by
  default; several users drained a 5-hour Max window in under an hour.
- One user went from roughly 250 installed skills to under 25 and reported
  measurably better agent behavior and more headroom on limits.

## Why Reason moved from Fable low to Opus 5.5 medium

Fable 5.1 at low was the Reason tier because its cache reads ($0.25) were
close to Sonnet's and it out-scored Opus 5. Opus 5.5 now matches Fable 5.1 on
the vendor's own coding benchmarks at $20 output instead of $50 and $0.20
cache reads, is included in every paid plan instead of capped at 50% or
billed to credits, and defaults to medium. Fable keeps the Frontier row for
the cases Anthropic itself names: unsupervised long runs, no pattern in the
codebase, many coordinated subagents, or Opus at high failing twice.

## How to re-rank

Keep 5-10 tasks you know the right answer to, one per tier. When a model
ships, run each at the tier the table prescribes and one tier below. Move the
tier boundary only when the cheaper run fails the same way twice. Sonnet 5.5
and Haiku 5.5 are due within weeks of Opus 5.5; the Build and Scan rows are
the next to move.
