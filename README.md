<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/icon-dark.svg">
    <img src="assets/icon.svg" alt="efficient-claude" width="72">
  </picture>
</p>

# efficient-claude

### Your Claude Code subagents are running on your most expensive model. Fix it in one command.

Every file search, log read and grep your subagents do is billed at your session's model price. On Opus, that is the same rate as your hardest design question, spent on work a model 40x cheaper handles fine. It drains your usage limit and your token budget for nothing.

efficient-claude makes Claude pick the right model for every subagent task, automatically.

- **Cheaper:** search and logs go to Haiku, edits to Sonnet, Opus and Fable only where they earn it.
- **Same quality:** it starts cheap, moves up one tier only when a cheaper model actually misses, and a stronger model that never saw the work reviews it before it ships.
- **Zero effort:** no new workflow. Work as usual; Claude states each route in one line.

```
Routing to scan/haiku: pure grep across the repo, spec fully determines output.
```

## Install (30 seconds)

```bash
claude plugin install model-router --marketplace thevrus/efficient-claude
```

Needs Claude Code 2.1.292+. Adds the skill, routing agents, and a hook that blocks any subagent call with no model set, so nothing slips through on the expensive default.

Codex, Cursor, OpenCode or other agents (skill only):

```bash
npx skills add thevrus/efficient-claude -g
```

## What you save

One session, 10 subagent tasks, list prices (illustrative math on an assumed mix, [not a benchmark](docs/comparison.md)):

| Task | Count | All on Opus | Routed |
| --- | --- | --- | --- |
| Search / logs | 6 | $2.16 | $0.05 (Haiku) |
| Edits from a plan | 3 | $1.08 | $0.54 (Sonnet) |
| Debug unknown cause | 1 | $0.60 | $0.60 (Opus) |
| **Total** | 10 | **$3.84** | **$1.19** (-69%) |

The hard task costs the same either way. The savings come from everything that never needed Opus.

## How it routes

| Job | Model | Effort |
| --- | --- | --- |
| Search, logs, summaries | Haiku | low |
| Edits and tests from a clear plan | Sonnet | medium |
| Debugging, refactors, reviews | Opus | medium |
| Must be right the first time | Fable | medium |

Anything touching security or money never routes below Opus. Updated for Fable 5.2.

To route a specific task: `/efficient-claude refactor auth, use subagents for search and tests`

Full rules: [SKILL.md](skills/efficient-claude/SKILL.md). Prices, benchmarks and sources: [rationale.md](skills/efficient-claude/references/rationale.md).

If it saves you tokens, a star helps others find it.

[![skills.sh](https://skills.sh/b/thevrus/efficient-claude)](https://skills.sh/thevrus/efficient-claude)

MIT
