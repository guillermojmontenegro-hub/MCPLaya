# Local installation and compatibility

MCPLaya runs inference and stores decision history on the user's computer.
The MCP client launches the server over stdio. The eight MCP tools work with
any compatible local client, without a hosted inference service or an API key.

## Supported installation paths

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) using the
instructions for your operating system. Download and extract this repository
or clone it, then open a terminal in its directory:

```sh
uv tool install --python 3.12 .
mcplaya doctor
mcplaya config
```

The same commands work in Windows PowerShell, macOS Terminal and Linux shells.
uv installs an isolated environment and can download Python automatically.
If the executable is not found, run `uv tool update-shell` and reopen the
terminal. Keep the installed uv tool environment; generated configuration points
to its Python interpreter. The source checkout can be removed after installation.
To update from a newer extracted checkout, run
`uv tool install --force --python 3.12 .` and regenerate the configuration.
`uv tool uninstall mcplaya` removes the server environment, leaving history and
model caches available for a later reinstall.

A built wheel is another installation source:

```sh
uv tool install --python 3.12 ./dist/mcplaya-0.1.0-py3-none-any.whl
```

The wrapper wheel is platform independent. Its native inference dependencies
are resolved for the installing computer. This repository does not assume that
`mcplaya` has been published to PyPI.

For development with the committed dependency lock:

```sh
uv sync --frozen --extra dev --python 3.12
uv run --frozen --extra dev python -m pytest
uv run --frozen mcplaya doctor
uv run --frozen mcplaya config
```

Do not copy a virtual environment between computers or operating systems.
Reinstall it at the target location. Tool/wheel installation resolves the
package's requirements; checkout installation with `--frozen` uses `uv.lock`.

### Without uv

Install Python 3.12 for the machine's architecture. In the extracted repository,
create an isolated environment and install with pip. On Windows:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install .
.venv\Scripts\python.exe -m mcplaya doctor
.venv\Scripts\python.exe -m mcplaya config
```

On macOS or Linux:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/python -m mcplaya doctor
.venv/bin/python -m mcplaya config
```

Keep that environment and its parent directory at the same location. No shell
activation is needed. The generated configuration uses its absolute interpreter
path, including proper JSON escaping for Windows paths and spaces.

## Platform targets and limits

| Platform | Architecture | Installation target |
|---|---|---|
| Windows | x64 | Native Python and PyTorch, CPU by default |
| Linux with glibc | x64, ARM64 | Native Python and PyTorch, CPU by default |
| macOS | Apple Silicon ARM64 | Native ARM64 Python and PyTorch; optional MPS |
| macOS | Intel x64 | Python 3.10–3.12, PyTorch 2.2.2, NumPy <2, Transformers 4.48–4.49 |

Supported Python versions are 3.10 through 3.12. Python 3.12 is the common
installation target. Each dependency's minimum OS version still applies; for
example, the current locked Apple Silicon PyTorch wheels require macOS 14 or
newer. Intel macOS dependencies are constrained separately because newer
PyTorch releases do not ship Intel Mac wheels. This legacy stack needs native
and real-checkpoint validation before a release is claimed to support it.

32-bit systems, Windows ARM64, Alpine/musl, mobile operating systems and other
architectures are not validated targets. Available RAM, disk, CPU instructions
and selected model size limit inference; the wrapper cannot make every computer
capable of running every checkpoint. No measured minimum RAM or latency is
claimed. Installation can download several GB of dependencies even in CPU mode.

The CI workflow is configured for Windows x64, Linux x64, Apple Silicon macOS
and Intel macOS with Python 3.10 and 3.12. It runs unit and stdio protocol tests,
checks native imports, and installs the wheel in a separate environment. Adding
this matrix does not establish a passing result until CI runs. Linux ARM64 and
real client/model combinations still require native validation. No model weights
are downloaded by these checks.

## Connecting agents

Use `mcplaya config` for clients with an `mcpServers` configuration object.
Use `mcplaya config --format vscode` for VS Code's `servers` object and
`type: "stdio"`. Use `mcplaya config --format opencode` for OpenCode v2's
`mcp.servers` object, or `--format opencode-v1` for the older format.
These commands print configuration; they do not modify any client files.
Merge the `mcplaya` entry into the client's existing settings, then reload
the connection and check that `laya_status` and the other seven tools appear.

For a client with a different schema, reuse the generated `command`, `args`
and environment in its local MCP connection UI. It must support spawning a
stdio subprocess and MCP tool calls. The protocol is agent independent;
configuration formats, tool permissions and timeouts are client specific.
Allow enough time for the first checkpoint download and CPU inference.
The stdio stream contains only MCP protocol messages; management commands
such as `config` are separate processes and must not be used as the server
launch command.

Agents running in a container, VM, remote SSH session or cloud environment
launch subprocesses there. To run inference on the user's physical computer,
the MCP client/connector must also run there or provide its own local bridge.
Clients that accept only remote MCP URLs cannot launch this stdio server
directly. MCPLaya does not currently supply an HTTP transport or bridge.

## Device, storage and offline use

CPU is the default and requires no GPU. Set `LAYA_DEVICE=cuda` for a compatible
PyTorch/CUDA installation, or `LAYA_DEVICE=mps` on a compatible Apple Silicon
Mac. Run `mcplaya doctor` after setting the variable, then regenerate the
configuration so the agent receives it. Diagnostics check installed package
versions, inference imports, Torch/NumPy conversion and a device allocation;
they do not load a checkpoint, measure model accuracy, or verify history-directory
write permissions. A failed diagnostic exits with status 1 and a JSON error.

Set variables in PowerShell with `$env:LAYA_DEVICE = "cpu"`, or in macOS/Linux
shells with `export LAYA_DEVICE=cpu`. The configuration generator preserves
`LAYA_DEVICE`, `MCPLAYA_DB`, `LAYA_ACTION_MODEL`, `HF_HOME` and `HF_HUB_OFFLINE`
when set. Relative storage/checkpoint/cache paths are converted to absolute
paths so an agent's working directory does not change their meaning.

| System | Default history database |
|---|---|
| Windows | `%LOCALAPPDATA%\mcplaya\sequences.sqlite3` (fallback: `~\AppData\Local`) |
| macOS | `~/Library/Application Support/mcplaya/sequences.sqlite3` |
| Linux | `$XDG_STATE_HOME/mcplaya/sequences.sqlite3`, or `~/.local/state/mcplaya/sequences.sqlite3` |

`MCPLAYA_DB` overrides the history database on every platform. If a database
already exists at the legacy XDG/Linux path and none exists at the native
location, it remains in use. No database is automatically moved or deleted.

Weights use the Hugging Face cache; `HF_HOME` selects a cache directory.
Initial installation and checkpoint acquisition need internet access. Once
the selected checkpoint and tokenizer files are fully cached, set
`HF_HUB_OFFLINE=1` for offline inference. Alternatively, use `LAYA_ACTION_MODEL`
with a complete compatible local checkpoint directory. Models needing uncached
files will fail offline. Startup and `laya_status` stay lazy and do not download
weights. `doctor` imports dependencies but does not download weights either.

## References

- [MCP stdio transport](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports#stdio)
- [uv tool installation](https://docs.astral.sh/uv/guides/tools/)
- [PyTorch native installation](https://pytorch.org/get-started/locally/)
- [VS Code MCP configuration](https://code.visualstudio.com/docs/agent-customization/mcp-servers)
- [OpenCode MCP configuration](https://opencode.ai/docs/mcp-servers/)
