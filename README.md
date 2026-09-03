# efficient-claude

An agent skill that routes every delegated task to the cheapest Claude model and effort level that can still do it right, and escalates only on evidence.

Default: Sonnet at medium. Scan work drops to Haiku. Judgment work goes to Fable at low effort. Fable high/max is a budgeted consult, not a default.

[![skills.sh](https://skills.sh/b/thevrus/efficient-claude)](https://skills.sh/thevrus/efficient-claude)

## Install

```bash
npx skills add thevrus/efficient-claude
```

Works with Claude Code, Codex, Cursor, OpenCode and every other agent the `skills` CLI supports. Add `-g` to install globally.

## What you get

`skills/efficient-claude/SKILL.md` covers:

- A routing table: Scan / Build / Reason / Frontier / Fallback / Visual tiers with the model and effort for each.
- An escalation rule that moves one dial at a time: model when it did not know enough, effort when it did not try hard enough.
- Fable-specific budgeting rules for subscription plans.
- Claude Code mapping: per-invocation `model`, agent `effort` frontmatter, resolution order, `CLAUDE_CODE_SUBAGENT_MODEL` safety net.
- Session hygiene, delegation rules, and a handoff-packet template for subagent prompts.

## Optional: pre-routed Claude Code agents

`skills/efficient-claude/agents/` holds five agent definitions already pinned to the right tier:

| Agent | Model | Effort | Use |
| --- | --- | --- | --- |
| `scan` | haiku | low | grep, inventory, find-where |
| `Explore` | haiku | low | overrides the built-in Explore so it stops inheriting the session model |
| `build` | sonnet | default | bounded edits from a clear spec |
| `reason` | fable | low | root cause, refactor design, tradeoffs |
| `frontier-review` | fable | medium | final clean-context review before shipping risky changes |

Copy them into `~/.claude/agents/` (global) or `.claude/agents/` (project) to use them from the `Agent` tool. The `skills` CLI does not register agents automatically.

Also recommended in `~/.claude/settings.json`:

```json
{ "env": { "CLAUDE_CODE_SUBAGENT_MODEL": "sonnet" } }
```

so an unrouted subagent never inherits an expensive session model.

## Why

Effort moves cost more than model choice: Fable 5.1 spans roughly 11x output tokens from low to max, Opus about 8x, while model price gaps are 2.5-5x. Most "Fable burned my limits" reports come from running high or max by default. The skill encodes the measured routing so the agent starts at the floor.

Model behavior shifts between releases. Keep a handful of personal tasks you know the answer to, re-run them when a model ships, and re-rank the table from that.

## License

MIT
