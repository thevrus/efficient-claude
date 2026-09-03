# efficient-claude

An agent skill that routes every delegated task to the cheapest Claude model and effort level that can still do it right, and escalates only on evidence.

Default: Sonnet at medium. Scan work drops to Haiku. Judgment work goes to Fable at low effort. Fable high/max is a budgeted consult, not a default.

[![skills.sh](https://skills.sh/b/thevrus/efficient-claude)](https://skills.sh/thevrus/efficient-claude)

## Install

```bash
npx skills add thevrus/efficient-claude
```

Works with Claude Code, Codex, Cursor, OpenCode and every other agent the `skills` CLI supports. Add `-g` to install globally.

## How it works

Claude Code loads a skill's `SKILL.md` into context when its description matches what you asked for, or when you invoke it by name with `/efficient-claude`. Once loaded, it changes one decision the agent makes constantly: which `model` and `effort` to pass when it spawns a subagent with the `Agent` tool.

Without the skill, an omitted `model` inherits the session model, so a Fable or Opus session runs every grep and every file rename on the most expensive model. With the skill:

1. Every delegated task is classified into a tier: Scan, Build, Reason, Frontier, Fallback, Visual.
2. The tier fixes the model and effort. Scan is `haiku` low, Build is `sonnet` medium, Reason is `fable` low, and so on.
3. The agent states the route in one line before dispatching, so you can audit it: "Routing to scan/haiku: pure grep, spec fully determines output."
4. On a miss it escalates one dial at a time. Wrong despite having the files: move up one model tier. Skipped a file or did not run tests: raise effort one notch, keep the model. Never both at once.
5. The prompt it writes for the subagent follows a handoff-packet template: objective, scope, evidence format, verification steps, stop conditions. A tight spec is what keeps a Sonnet task from needing Opus.

The optional `agents/` definitions make the routing mechanical: each agent has `model` and `effort` pinned in its frontmatter, so `Agent(subagent_type: "scan")` is always Haiku at low effort regardless of the session model.

## How to use it

Install once:

```bash
npx skills add thevrus/efficient-claude -g
```

Then work normally. The skill applies itself whenever Claude Code is about to delegate. To apply it explicitly to a task:

```
/efficient-claude refactor the auth module, use subagents for the file scan and the tests
```

What you should see: a one-line route per delegation, cheap models on lookups, Sonnet on implementation, Fable or Opus only where judgment is needed, and an explicit reason each time it escalates.

For the mechanical version, copy the agent definitions and set the safety net:

```bash
cp -R ~/.claude/skills/efficient-claude/agents/* ~/.claude/agents/
```

In `~/.claude/settings.json`:

```json
{ "env": { "CLAUDE_CODE_SUBAGENT_MODEL": "sonnet" } }
```

Now `scan`, `Explore`, `build`, `reason` and `frontier-review` show up as `subagent_type` options with their tier pre-set, and any subagent the skill did not route falls back to Sonnet instead of the session model.

Session-level habits the skill also nudges: set `/model` and `/effort` once at session start (switching mid-session drops the prompt cache), `/clear` between unrelated tasks, `/rewind` instead of `/compact` to undo a bad turn.

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

The `skills` CLI installs the skill only; it does not register agents. Copy them into `~/.claude/agents/` (global) or `.claude/agents/` (project) as shown above.

## Why

Effort moves cost more than model choice: Fable 5.1 spans roughly 11x output tokens from low to max, Opus about 8x, while model price gaps are 2.5-5x. Most "Fable burned my limits" reports come from running high or max by default. The skill encodes the measured routing so the agent starts at the floor.

Model behavior shifts between releases. Keep a handful of personal tasks you know the answer to, re-run them when a model ships, and re-rank the table from that.

## License

MIT
