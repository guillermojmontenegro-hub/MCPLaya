# MCPLaya

A local, agent-independent stdio MCP server for delegating structured
choices to [Laya](https://github.com/NandhaKishorM/laya): text categorization,
independent tags, ordinal ratings, statement probabilities and bounded action
selection. For dependent decisions, use observe → ask Laya → execute one action
with the agent → record real outcome → observe again. It never executes actions itself.

Created independently alongside LayaTUI-MCP; no TUI or upstream server monkey-patching.
Laya 0.3.20 is installed from PyPI; model weights are not included.

## Install and connect

Download and extract the repository, or clone it. From its directory, run these
commands in PowerShell, Terminal or a Linux shell with [uv installed](https://docs.astral.sh/uv/getting-started/installation/):

```sh
uv tool install --python 3.12 .
mcplaya doctor
mcplaya config
```

`uv` can install Python 3.12 automatically. If `mcplaya` is not on PATH, run
`uv tool update-shell` and reopen the terminal. The installed server runs outside
the repository and needs no Git, Docker, Node.js, administrator access or API key
at runtime. Python 3.10–3.12 is the supported package range.

Paste the output of `mcplaya config` into a client using `mcpServers`. It contains
the installed Python's absolute path and arguments, avoiding shell and PATH
differences. Merge the entry with existing configuration. Other supported formats:

```sh
mcplaya config --format vscode
mcplaya config --format opencode
mcplaya config --format opencode-v1
```

VS Code uses `.vscode/mcp.json`; OpenCode v2 uses `mcp.servers`, while v1 uses
`mcp` directly. For other agents, configure the executable and arguments from
the generated JSON in their MCP UI. Configuration commands only print text.
The agent launches `mcplaya serve` as a local subprocess; `mcplaya` without
arguments remains equivalent. No network listener is started.

The target platforms are Windows x64, Linux x64/ARM64, and macOS Apple Silicon
and Intel, subject to native dependency and OS requirements. CPU is the default;
CUDA or Apple MPS acceleration is optional. First inference downloads checkpoint
files and can take time; installation and models can require several GB of disk
space. Startup, status, configuration and diagnostics do not download weights.

Compatibility requires an agent that can launch **local stdio MCP servers**.
An agent without MCP support, or a remote-only client, needs its own adapter.
There is no claim of compatibility with every OS, hardware configuration or
agent. See [installation and compatibility](docs/INSTALLATION.md) for offline
use, manual installation, storage paths and validation limits. See the
[tool reference](docs/TOOLS.md) for request examples and the
[decision workflow](docs/WORKFLOW.md) for agent integration guidance.

## Tools and behavior

| Tool | Purpose |
|---|---|
| `laya_status` | Lazy model/device report |
| `laya_predict` | Independent choice, ordered score and P(true) questions |
| `laya_choose_action` | One bounded choice among 2-20 concrete candidates |
| `laya_start_sequence` | Goal, step budget, confidence threshold, model |
| `laya_next_decision` | Fresh observation and candidates → one pending decision |
| `laya_record_outcome` | Record observed succeeded/failed/skipped outcome |
| `laya_get_sequence` | Recover durable state and current revision |
| `laya_close_sequence` | Finish with a reason supported by evidence |

SQLite stores caller-supplied observations and history across restarts. Revision
checks prevent stale updates; one pending decision prevents jumping ahead.
Three consecutive failures block the loop. Skipped proposals consume budget too.
Low or missing confidence returns `requires_review: true` and no automatic
recommendation. Confidence is not authorization or a correctness guarantee.
Callers must review real-world permissions and verify action results themselves.

General checkpoints have not been validated for arbitrary action selection.
Evaluate on your domain; a compatible `LAYA_ACTION_MODEL` local checkpoint can
replace the router for **all inference tools**, including `laya_predict`.
Its supported schemas, license and accuracy are the deployer's responsibility.
The tool sends a short current observation plus five recent outcomes; long
inputs may exceed or be truncated by the checkpoint's context window.

Settings: `LAYA_DEVICE` (torch device), `LAYA_ACTION_MODEL` (checkpoint path),
`MCPLAYA_DB` (SQLite path). Default DB: `%LOCALAPPDATA%/mcplaya/sequences.sqlite3`
on Windows, `~/Library/Application Support/mcplaya/sequences.sqlite3` on macOS,
and `$XDG_STATE_HOME/mcplaya/sequences.sqlite3` or
`~/.local/state/mcplaya/sequences.sqlite3` on Linux. Existing legacy databases
remain in use when no database exists at the native location. History is local plaintext; it
contains only what the caller supplies. Users can remove the DB to erase all
history while the server is stopped. No telemetry or paid API dependency.

## Agent usage skill

[skills/mcplaya-decisions/SKILL.md](skills/mcplaya-decisions/SKILL.md) teaches an
agent how to use the connected MCP. It covers text classification, intent and
email routing, independent tags, urgency and sentiment, screening signals,
retrieval relevance, specialist workflows and bounded action sequences.

The skill includes a researched [use-case catalog](skills/mcplaya-decisions/references/use-cases.md),
[request recipes](skills/mcplaya-decisions/references/recipes.md) and
[performance/model guidance](skills/mcplaya-decisions/references/performance.md).
It explains how to reuse warm models, combine independent questions and handle
uncertainty without assuming measured accuracy or fixed latency.

Load or copy the `skills/mcplaya-decisions` folder using your agent's supported
skill mechanism. Its references are self-contained; optional `agents/openai.yaml`
provides Codex UI metadata. Native-layout export profiles and ZIP packages are
available for Codex, Claude Code, Cursor, GitHub Copilot, OpenCode, Gemini CLI,
Cline and Roo Code. See the [harness guide](docs/HARNESSES.md) for the discovery
paths, official sources and usage instructions.

```sh
uv run --frozen python scripts/export_usage_skill.py --harness all
```

The exporter creates one ZIP per harness under `dist/`, using one shared skill
and its references. It is a usage skill, independent of the separate
installation skill. It does not install, configure or launch the MCP server.
The repository and source distribution include the skill; the Python wheel
installs the server, so load the skill separately into the client.

## Development

```sh
uv sync --frozen --extra dev --python 3.12
uv run --frozen --extra dev python -m pytest
uv run --frozen --extra dev python scripts/validate_usage_skill.py
uv run --frozen --extra dev python scripts/export_usage_skill.py --harness all
uv run --frozen --extra dev python -m build
```

## License

Laya's code and the three official checkpoint cards declare Apache-2.0, allowing
commercial use and redistribution with conditions. See [docs/LICENSING.md](docs/LICENSING.md)
for sources, obligations and the distinction between this wrapper and dependencies.
This repository redistributes neither Laya code nor model weights.
