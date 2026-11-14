"""MCP stdio server, independent of upstream server globals."""
import os
import threading
from pathlib import Path
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from .backend import Backend
from .engine import Engine

server = MCPServer("mcplaya", version="0.1.0")
backend = Backend()
_engine = None
_lock = threading.Lock()


def engine():
    global _engine
    with _lock:
        if _engine is None:
            root = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state")))
            _engine = Engine(Path(os.environ.get("MCPLAYA_DB", str(root / "mcplaya/sequences.sqlite3"))), backend)
    return _engine


def call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except ValueError as exc:
        raise ToolError(str(exc)) from exc
    except Exception as exc:
        raise ToolError("Laya or storage unavailable; inspect the local installation and model cache before retrying") from exc


@server.tool()
def laya_status() -> dict:
    """Report initialized models and device preference without downloading checkpoints."""
    return backend.status()


@server.tool()
def laya_predict(state: dict, questions: dict, model: str = "auto") -> dict:
    """Delegate independent typed decisions: choice (<=20 labels), score (ordered levels), noul (P(true)). No text generation. Dependent decisions need separate fresh observations."""
    return call(backend.predict, state, questions, model)


@server.tool()
def laya_choose_action(goal: str, observation: str, actions: list[dict], min_confidence: float = 0.7, model: str = "auto") -> dict:
    """Choose one of 2-20 concrete actions without executing. Each action has id and description. requires_review blocks automatic recommendation on missing/low confidence. For repeated decisions use sequence tools."""
    return call(lambda: engine().choose(goal, observation, actions, min_confidence, model))


@server.tool()
def laya_start_sequence(goal: str, max_steps: int = 20, min_confidence: float = 0.7, model: str = "auto") -> dict:
    """Start durable observe-decide-act loop. Use when multiple dependent decisions advance one goal. Returns sequence_id and revision; never executes or preplans future actions."""
    return call(lambda: engine().start(goal, max_steps, min_confidence, model))


@server.tool()
def laya_next_decision(sequence_id: str, revision: int, observation: str, actions: list[dict]) -> dict:
    """Select next action from a fresh textual observation and 2-20 concrete candidates. Record prior outcome first. Pass current revision. Do not execute a requires_review result automatically."""
    return call(lambda: engine().next(sequence_id, revision, observation, actions))


@server.tool()
def laya_record_outcome(sequence_id: str, revision: int, decision_id: str, outcome: str, observation: str) -> dict:
    """After acting with agent tools, record succeeded/failed/skipped and post-action evidence. Use skipped for rejected proposals. Three consecutive failures block the sequence."""
    return call(lambda: engine().record(sequence_id, revision, decision_id, outcome, observation))


@server.tool()
def laya_get_sequence(sequence_id: str) -> dict:
    """Recover goal, revision, pending decision and observed history after reconnect. Inspect the actual environment before retrying any pending action."""
    return call(lambda: engine().get(sequence_id))


@server.tool()
def laya_close_sequence(sequence_id: str, revision: int, reason: str) -> dict:
    """Close a completed, cancelled or blocked sequence with an evidence-based reason."""
    return call(lambda: engine().close(sequence_id, revision, reason))


def main():
    server.run()


if __name__ == "__main__":
    main()
