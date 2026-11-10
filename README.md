# efficient-claude

**Stop paying Opus prices for grep.** A Claude Code skill that sends each subagent task to the cheapest Claude model and effort that can still do it right.

Claude Code subagents inherit your session's model, so a file search costs the same as your hardest design question. This makes Claude pick per task, start cheap, and move up only when a cheaper model actually misses:

| Job | Model | Effort |
| --- | --- | --- |
| Search, logs, summaries | Haiku | low |
| Edits and tests from a clear plan | Sonnet | medium |
| Debugging, refactors, reviews | Opus | medium |
| Must be right the first time | Fable | medium |

Before anything ships, a stronger model that never saw the work reviews it.

## Savings

One session, 10 subagent tasks, list prices (illustrative math on an assumed mix, [not a benchmark](docs/comparison.md)):

| Task | Count | All on Opus | Routed |
| --- | --- | --- | --- |
| Search / logs | 6 | $2.16 | $0.05 (Haiku) |
| Edits from a plan | 3 | $1.08 | $0.54 (Sonnet) |
| Debug unknown cause | 1 | $0.60 | $0.60 (Opus) |
| **Total** | 10 | **$3.84** | **$1.19** (-69%) |

The gap comes from search and log reading. Hard tasks cost the same either way.

## Install

One command, in your terminal (Claude Code 2.1.292+):

```bash
claude plugin install model-router --marketplace thevrus/efficient-claude
```

Or inside Claude Code: `/plugin install model-router --marketplace thevrus/efficient-claude`

You get the skill, routing agents, and a hook that blocks subagent calls with no model.

Skill only, for Codex, Cursor, OpenCode and others:

```bash
npx skills add thevrus/efficient-claude -g
```

## Use

Work as usual. Before each subagent call, Claude states the route:

```
Routing to scan/haiku: pure grep across the repo, spec fully determines output.
```

Or invoke it: `/efficient-claude refactor auth, use subagents for search and tests`

Rules in [SKILL.md](skills/efficient-claude/SKILL.md); prices, benchmarks and sources in [rationale.md](skills/efficient-claude/references/rationale.md) (checked 10 Nov 2026, Fable 5.2).

[![skills.sh](https://skills.sh/b/thevrus/efficient-claude)](https://skills.sh/thevrus/efficient-claude)

MIT
