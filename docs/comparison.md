# Cost comparison (illustrative)

List-price arithmetic on an assumed workload. **Not a benchmark**: it shows
what routing changes, not what you will save.

Prices per million tokens, input / output (checked 10 Nov 2026, [pricing](https://platform.claude.com/docs/en/about-claude/pricing)): Haiku 5.5 $0.10 / $0.50, Sonnet 5.5 $2 / $10, Opus 5.5 $4 / $20, Fable 5.2 $8 / $40.

Workload: one session with 10 subagent tasks, run on an Opus 5.5 session.

| Subagent task | Count | Tokens in / out each | Routed to | All on Opus | Routed |
| --- | --- | --- | --- | --- | --- |
| Search / log reading | 6 | 80K / 2K | Haiku | $2.16 | $0.05 |
| Edits from a clear plan | 3 | 60K / 6K | Sonnet | $1.08 | $0.54 |
| Debug an unknown cause | 1 | 100K / 10K | Opus | $0.60 | $0.60 |
| **Total** | 10 | | | **$3.84** | **$1.19** |

Routed is 69% cheaper than all-Opus and 84% cheaper than all-Fable ($7.68) on this mix. Almost all of the gap comes from the six search tasks; the hard task costs the same either way.

## What this leaves out

- Thinking tokens (they bill as output and vary by effort), prompt-cache discounts, and retries when a cheaper model misses.
- Quality. The rule is that a cheaper tier only takes work where a mistake is cheap to spot, and a miss moves the task up one tier.
- Your mix. A session of mostly hard debugging saves little; one heavy on search and log reading saves most.

Measure your own: run `/usage` before and after a session, or compare one task at two tiers.
