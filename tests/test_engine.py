import pytest
from mcplaya.engine import Engine

ACTIONS = [{"id": "inspect", "description": "Read current status"}, {"id": "stop", "description": "Stop and report"}]

class Fake:
    def __init__(self, confidence=0.9):
        self.confidence = confidence
        self.calls = []
    def choose(self, goal, observation, actions, history, model):
        self.calls.append((observation, history))
        return {"action_id": "inspect", "confidence": self.confidence}

@pytest.fixture
def engine(tmp_path):
    return Engine(tmp_path / "state.sqlite3", Fake())

def test_observe_act_record_restart(engine):
    s = engine.start("Diagnose failure")
    d = engine.next(s["sequence_id"], 0, "Test failed", ACTIONS)
    assert d["recommended_action_id"] == "inspect"
    with pytest.raises(ValueError, match="pending"):
        engine.next(s["sequence_id"], 1, "Still failed", ACTIONS)
    with pytest.raises(ValueError, match="decision_id"):
        engine.record(s["sequence_id"], 1, "wrong", "succeeded", "Read status")
    engine.record(s["sequence_id"], 1, d["decision_id"], "succeeded", "Missing schema")
    other = Engine(engine.path, Fake())
    assert other.get(s["sequence_id"])["history"][0]["observation"] == "Missing schema"
    other.next(s["sequence_id"], 2, "Schema missing", ACTIONS)
    assert other.backend.calls[0][1][0]["proposed_action"]["description"] == "Read current status"
    with pytest.raises(ValueError, match="stale"):
        other.record(s["sequence_id"], 2, d["decision_id"], "failed", "Old call")

@pytest.mark.parametrize("confidence", [None, 0.1])
def test_uncertain_never_recommends(tmp_path, confidence):
    e = Engine(tmp_path / "s.db", Fake(confidence))
    r = e.choose("Goal", "Facts", ACTIONS)
    assert r["requires_review"] is True
    assert r["recommended_action_id"] is None

@pytest.mark.parametrize("confidence", [float("nan"), float("inf"), -0.1, 1.1, True, "0.8"])
def test_invalid_model_confidence(tmp_path, confidence):
    e = Engine(tmp_path / "s.db", Fake(confidence))
    with pytest.raises(ValueError):
        e.choose("Goal", "Facts", ACTIONS)

def test_budget_and_close(engine):
    s = engine.start("Goal", max_steps=1)
    sid = s["sequence_id"]
    d = engine.next(sid, 0, "Observed", ACTIONS)
    engine.record(sid, 1, d["decision_id"], "skipped", "Rejected")
    with pytest.raises(ValueError, match="budget"):
        engine.next(sid, 2, "New facts", ACTIONS)
    engine.close(sid, 2, "Budget ended")
    with pytest.raises(ValueError, match="closed"):
        engine.next(sid, 3, "New facts", ACTIONS)

def test_failures_block(engine):
    sid = engine.start("Goal")["sequence_id"]
    for rev in (0, 2, 4):
        d = engine.next(sid, rev, "Fresh facts", ACTIONS)
        r = engine.record(sid, rev + 1, d["decision_id"], "failed", "Failure verified")
    assert r["status"] == "blocked"
    with pytest.raises(ValueError, match="closed"):
        engine.next(sid, 6, "Fresh facts", ACTIONS)
    engine.close(sid, 6, "Three failures")

@pytest.mark.parametrize("actions", [[], ACTIONS[:1], ACTIONS * 2, [{"id":"x"}], [{}], "bad"])
def test_bad_candidates_do_not_advance(engine, actions):
    sid = engine.start("Goal")["sequence_id"]
    with pytest.raises(ValueError):
        engine.next(sid, 0, "Observed", actions)
    assert engine.get(sid)["revision"] == 0
    assert engine.backend.calls == []

def test_inference_failure_rolls_back(engine):
    def fail(*args):
        raise RuntimeError("offline")
    engine.backend.choose = fail
    sid = engine.start("Goal")["sequence_id"]
    with pytest.raises(RuntimeError):
        engine.next(sid, 0, "Observed", ACTIONS)
    assert engine.get(sid)["pending"] is None
    assert engine.get(sid)["revision"] == 0

def test_two_connections_cannot_both_decide(engine):
    from concurrent.futures import ThreadPoolExecutor
    sid = engine.start("Goal")["sequence_id"]
    other = Engine(engine.path, Fake())
    def attempt(e):
        try:
            e.next(sid, 0, "Observed", ACTIONS)
            return True
        except ValueError:
            return False
    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(attempt, [engine, other]))
    assert sorted(results) == [False, True]
