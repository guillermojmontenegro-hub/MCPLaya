# MCPLaya

A standalone stdio MCP server and Agensi-ready skill for delegating structured
choices to [Laya](https://github.com/NandhaKishorM/laya). Its main workflow is a
sequence of decisions: observe → ask Laya → execute one action with the agent →
record real outcome → observe again. It never executes actions itself.

Created independently alongside LayaTUI-MCP; no TUI or upstream server monkey-patching.
Laya 0.3.20 is installed from PyPI; model weights are not included.

## Install and connect

```sh
git clone https://github.com/guillermojmontenegro-hub/MCPLaya.git
cd MCPLaya
uv sync --frozen
uv run --frozen mcplaya
```

Python >=3.10; `uv` must already be installed. The last command is a stdio server,
so a client normally launches it as a subprocess. First inference can download
large checkpoints and take time; startup and status are lazy. CPU is supported;
set `LAYA_DEVICE=cuda` for a compatible GPU installation.

For Claude Code, Cursor and other `mcpServers` clients:

```json
{"mcpServers":{"mcplaya":{"command":"uv","args":["--directory","/ABSOLUTE/PATH/MCPLaya","run","--frozen","mcplaya"],"env":{"LAYA_DEVICE":"cpu"}}}}
```

For VS Code Copilot, use `.vscode/mcp.json`, the key `servers`, and `type: "stdio"`.
Use your client's MCP connection UI for other formats. This project does not
change global agent configuration. See the skill's [tool reference](skills/laya-decisions/references/usage.md)
for schemas and a complete request/outcome example.

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
`MCPLAYA_DB` (SQLite path). Default DB: `$XDG_STATE_HOME/mcplaya/sequences.sqlite3`
or `~/.local/state/mcplaya/sequences.sqlite3`. History is local plaintext; it
contains only what the caller supplies. Users can remove the DB to erase all
history while the server is stopped. No telemetry or paid API dependency.

## Skill and Agensi

The skill is [skills/laya-decisions/SKILL.md](skills/laya-decisions/SKILL.md).
Install it in your agent's supported skill directory, or submit
`dist/laya-decisions.zip` to Agensi. Installing/loading the skill does not install
the separate MCP server. Agensi distributes instructions through its connector;
local Laya inference still runs on the buyer's machine.

```sh
uv run --frozen --extra dev pytest
uv run --frozen --extra dev python scripts/package_skill.py
uv run --frozen --extra dev python -m build
```

See [docs/AGENSI.md](docs/AGENSI.md) for listing text, current platform requirements
and remaining manual validation. No Agensi account, listing or price is configured
by this repository. The skill and wrapper are Apache-2.0; publication as a paid
product does not remove recipients' open-source rights.

## License

Laya's code and the three official checkpoint cards declare Apache-2.0, allowing
commercial use and redistribution with conditions. See [docs/LICENSING.md](docs/LICENSING.md)
for sources, obligations and the distinction between this wrapper and dependencies.
This repository redistributes neither Laya code nor model weights.
