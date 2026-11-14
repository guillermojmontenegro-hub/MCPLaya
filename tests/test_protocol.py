"""Real stdio protocol handshake; no model download or fake protocol server."""
import json
import os
import subprocess
import sys
from pathlib import Path
import pytest


@pytest.mark.parametrize("launch", [["-m", "mcplaya.server"], ["-m", "mcplaya"], ["-m", "mcplaya", "serve"]])
def test_stdio_tools_and_errors(tmp_path, launch):
    requests = [
        {"jsonrpc":"2.0", "id":1, "method":"initialize", "params":{"protocolVersion":"2025-11-25", "capabilities":{}, "clientInfo":{"name":"test", "version":"1"}}},
        {"jsonrpc":"2.0", "method":"notifications/initialized"},
        {"jsonrpc":"2.0", "id":2, "method":"tools/list", "params":{}},
        {"jsonrpc":"2.0", "id":3, "method":"tools/call", "params":{"name":"laya_status", "arguments":{}}},
        {"jsonrpc":"2.0", "id":4, "method":"tools/call", "params":{"name":"laya_start_sequence", "arguments":{"goal":"Inspect local state"}}},
        {"jsonrpc":"2.0", "id":5, "method":"tools/call", "params":{"name":"laya_get_sequence", "arguments":{"sequence_id":"unknown"}}},
    ]
    env = dict(os.environ, MCPLAYA_DB=str(tmp_path / "Zoë Data/protocol.db"), HF_HUB_OFFLINE="1", PYTHONUTF8="1")
    proc = subprocess.Popen([sys.executable, *launch], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", env=env)
    # Keep stdin open until responses arrive: EOF can cancel in-flight tool calls.
    import queue
    import threading
    q = queue.Queue()
    def read():
        for line in proc.stdout:
            q.put(line)
    threading.Thread(target=read, daemon=True).start()
    try:
        for request in requests:
            proc.stdin.write(json.dumps(request) + "\n")
            proc.stdin.flush()
            if "id" in request:
                response = json.loads(q.get(timeout=30))
                assert response["id"] == request["id"]
                if request["id"] == 2:
                    names = {t["name"] for t in response["result"]["tools"]}
                    assert len(names) == 8
                    assert "laya_next_decision" in names
                elif request["id"] in (3, 4):
                    assert not response["result"].get("isError")
                    payload = json.loads(response["result"]["content"][0]["text"])
                    if request["id"] == 3:
                        assert payload["router_initialized"] is False
                    else:
                        assert payload["revision"] == 0
                elif request["id"] == 5:
                    assert response["result"]["isError"] is True
    finally:
        proc.stdin.close()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
    assert proc.returncode == 0, proc.stderr.read()
