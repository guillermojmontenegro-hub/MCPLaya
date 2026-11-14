"""Durable decision protocol. Only the caller executes actions."""
import copy
import json
import math
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path


def text(value, name):
    if not isinstance(value, str) or not value.strip() or len(value) > 16000:
        raise ValueError(f"{name} must be nonempty text of at most 16000 characters")
    return value


def candidates(actions):
    if not isinstance(actions, list) or not 2 <= len(actions) <= 20:
        raise ValueError("provide 2 to 20 actions; shortlist larger sets using observed relevance")
    ids = set()
    for a in actions:
        if not isinstance(a, dict):
            raise ValueError("actions must be objects")
        text(a.get("id"), "action id")
        text(a.get("description"), "action description")
        if a["id"] in ids:
            raise ValueError("duplicate action id")
        ids.add(a["id"])
    return copy.deepcopy(actions)


def threshold(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("min_confidence must be in [0,1]")
    return value


class Engine:
    def __init__(self, path, backend):
        self.path = str(path)
        self.backend = backend
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS sequences (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")

    def connect(self):
        return sqlite3.connect(self.path, timeout=300)

    @contextmanager
    def session(self, sequence_id):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT payload FROM sequences WHERE id=?", (sequence_id,)).fetchone()
            if row is None:
                raise ValueError("unknown sequence_id")
            state = json.loads(row[0])
            yield state
            db.execute("UPDATE sequences SET payload=? WHERE id=?", (json.dumps(state), sequence_id))

    def start(self, goal, max_steps=20, min_confidence=0.7, model="auto"):
        text(goal, "goal")
        if isinstance(max_steps, bool) or not isinstance(max_steps, int) or not 1 <= max_steps <= 100:
            raise ValueError("max_steps must be an integer in [1,100]")
        threshold(min_confidence)
        if model not in ("auto", "english", "multilingual", "typed-decisions"):
            raise ValueError("unknown model")
        sid = str(uuid.uuid4())
        state = dict(sequence_id=sid, goal=goal, max_steps=max_steps, min_confidence=min_confidence,
                     model=model, revision=0, status="active", history=[], pending=None)
        with self.connect() as db:
            db.execute("INSERT INTO sequences VALUES (?, ?)", (sid, json.dumps(state)))
        return state

    def choose(self, goal, observation, actions, min_confidence=0.7, model="auto", history=None):
        text(goal, "goal")
        text(observation, "observation")
        actions = candidates(actions)
        threshold(min_confidence)
        result = self.backend.choose(goal, observation, actions, history or [], model)
        if result.get("action_id") not in {a["id"] for a in actions}:
            raise ValueError("unknown predicted action")
        confidence = result.get("confidence")
        if confidence is not None:
            threshold(confidence)
        review = confidence is None or confidence < min_confidence
        return {**result, "requires_review": review, "recommended_action_id": None if review else result["action_id"]}

    def next(self, sequence_id, revision, observation, actions):
        with self.session(sequence_id) as s:
            self.active(s, revision)
            if s["pending"]:
                raise ValueError("record the pending outcome before requesting another decision")
            if len(s["history"]) >= s["max_steps"]:
                raise ValueError("step budget exhausted; close this sequence")
            result = self.choose(s["goal"], observation, actions, s["min_confidence"], s["model"], s["history"][-5:])
            decision = dict(result, decision_id=str(uuid.uuid4()), observation=observation,
                            actions=actions)
            s["pending"] = decision
            s["revision"] += 1
            return dict(result, decision_id=decision["decision_id"], revision=s["revision"],
                        sequence_id=sequence_id, step=len(s["history"]) + 1)

    @staticmethod
    def active(s, revision):
        if s["status"] != "active":
            raise ValueError("sequence is closed")
        if isinstance(revision, bool) or revision != s["revision"]:
            raise ValueError("stale revision; fetch sequence before retrying")

    def record(self, sequence_id, revision, decision_id, outcome, observation):
        if outcome not in ("succeeded", "failed", "skipped"):
            raise ValueError("outcome must be succeeded, failed or skipped")
        text(observation, "post-action observation")
        with self.session(sequence_id) as s:
            self.active(s, revision)
            pending = s["pending"]
            if not pending or pending["decision_id"] != decision_id:
                raise ValueError("decision_id does not match the pending decision")
            s["history"].append(dict(decision_id=decision_id, action_id=pending["action_id"],
                                      proposed_action=next(a for a in pending["actions"] if a["id"] == pending["action_id"]),
                                      outcome=outcome, observation=observation,
                                      requires_review=pending["requires_review"]))
            s["pending"] = None
            s["revision"] += 1
            if len(s["history"]) >= 3 and all(h["outcome"] == "failed" for h in s["history"][-3:]):
                s["status"] = "blocked"
            return {"sequence_id": sequence_id, "revision": s["revision"], "status": s["status"],
                    "remaining_steps": s["max_steps"] - len(s["history"])}

    def get(self, sequence_id):
        with self.session(sequence_id) as s:
            return s

    def close(self, sequence_id, revision, reason):
        text(reason, "reason")
        with self.session(sequence_id) as s:
            if s["revision"] != revision:
                raise ValueError("stale revision")
            if s["status"] == "closed":
                raise ValueError("already closed")
            s["status"] = "closed"
            s["close_reason"] = reason
            s["pending"] = None
            s["revision"] += 1
            return s
