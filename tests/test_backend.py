"""Exercise the real Laya router API without downloading checkpoint weights."""
import pytest
from laya import Router
from mcplaya.backend import Backend


@pytest.mark.parametrize("model", ["auto", "english", "multilingual", "typed-decisions"])
def test_real_router_api(monkeypatch, model):
    backend = Backend()
    backend.router = Router()
    loaded = []
    class Agent:
        def system_one(self, state, questions, **kwargs):
            return {"answers": {"next_action": {"choice": "read", "answer_confidence": 0.88}}}
    def load(name):
        loaded.append(name)
        return Agent()
    monkeypatch.setattr(backend.router, "load", load)
    result = backend.choose("Diagnose test", "A test failed", [
        {"id": "read", "description": "Read test logs"},
        {"id": "stop", "description": "Stop investigation"}], [], model)
    assert result["action_id"] == "read"
    assert result["confidence"] == 0.88
    assert loaded == ["english" if model == "auto" else model]
