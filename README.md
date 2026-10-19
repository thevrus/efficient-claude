# efficient-claude

Get the best results from Claude Code while spending fewer tokens.

efficient-claude is a model routing skill and Claude Code plugin. It sends each subagent task to the cheapest Claude model (Haiku, Sonnet, Opus or Fable) and effort level that can still do the job, so you cut token costs without lowering quality.

When Claude Code hands work to a subagent, it uses your session's model by
default, so a quick file search runs on the same expensive model as your
hardest design question. This skill makes Claude pick the right model for each
job:

| Job | Model | Effort |
| --- | --- | --- |
| Search, find files, read logs | Haiku | low |
| Edits and tests from a clear plan | Sonnet | medium |
| Debugging, refactors, reviews | Opus | medium |
| Work that must be right the first time | Fable | low |

It starts cheap and moves up only when a cheaper model actually misses. Before
anything ships, a stronger model that never saw the work reviews it.

## Install

As a Claude Code plugin (skill, routing agents and a guard hook in one step):

```
/plugin install model-router --marketplace thevrus/efficient-claude
```

Plugin commands are prefixed: `/model-router:efficient-claude`.

Or just the skill, in Claude Code, Codex, Cursor and other agents:

```bash
npx skills add thevrus/efficient-claude -g
```

## Use

Work as usual. Before each subagent dispatch, Claude states the route in one
line:

```
Routing to scan/haiku: pure grep across the repo, spec fully determines output.
```

To apply it to a specific task, name it:

```
/efficient-claude refactor the auth module, use subagents for the search and the tests
```

The plugin also adds agents with their models pre-set: `model-router:scan`,
`:build`, `:reason` and `:frontier-review`. Its hook stops any
subagent call that names no model, so nothing slips through on the expensive
default.

## FAQ

**How do I reduce Claude Code token costs?**

Stop running subagents on your session's model. By default a subagent inherits it, so on an Opus session every file search is billed at Opus prices. This skill sends search and log reading to Haiku, bounded edits to Sonnet, and keeps Opus and Fable for the work that needs them.

**Which Claude model should a subagent use?**

Use the table above as the default: Haiku for search and summaries, Sonnet for edits with a clear spec, Opus for debugging and reviews, and Fable for work that must be right the first time. A task moves up a tier only when a cheaper model misses.

**Does it work with Codex, Cursor or OpenCode?**

Yes. The skill installs with `npx skills add` and works in Claude Code, Codex, Cursor, OpenCode and other agents. The plugin, with its routing agents and guard hook, is for Claude Code.

## Learn more

- [SKILL.md](skills/efficient-claude/SKILL.md): the full routing rules.
- [rationale.md](skills/efficient-claude/references/rationale.md): prices,
  benchmarks and sources behind the table, updated 19 October 2026.

[![skills.sh](https://skills.sh/b/thevrus/efficient-claude)](https://skills.sh/thevrus/efficient-claude)

MIT license.
