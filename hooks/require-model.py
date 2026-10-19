#!/usr/bin/env python3
"""PreToolUse hook: block Agent dispatches that would silently inherit the
session model. Allows a call when it passes `model` explicitly or names a
subagent_type whose definition pins one. Exit 2 blocks and shows stderr to
Claude. Claude Code hooks contract: https://code.claude.com/docs/en/hooks
"""
import json
import sys

PINNED = {"scan", "Explore", "build", "reason", "frontier-review"}

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

if data.get("tool_name") not in ("Agent", "Task"):
    sys.exit(0)

inp = data.get("tool_input") or {}
# Plugin installs namespace agents as "model-router:scan".
st = inp.get("subagent_type") or ""
agent = st[len("model-router:"):] if st.startswith("model-router:") else st
if inp.get("model") or agent in PINNED:
    sys.exit(0)

sys.stderr.write(
    "efficient-claude: this Agent call has no `model` and its subagent_type "
    "is not one of the pinned agents (" + ", ".join(sorted(PINNED)) + "). "
    "It would inherit the session model. Pass model: haiku | sonnet | opus | "
    "fable per the routing table, or use a pinned subagent_type.\n"
)
sys.exit(2)
