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

## Install

Claude Code plugin (skill, routing agents, and a hook that blocks subagent calls with no model):

```
/plugin install model-router --marketplace thevrus/efficient-claude
```

Skill only (Claude Code, Codex, Cursor, OpenCode):

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
