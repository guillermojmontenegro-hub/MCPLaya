"""Lazy adapter using Laya public APIs; never downloads at import time."""
import math
import os
import threading

WARNING = "General Laya checkpoints are not validated for arbitrary action sequences. Confidence is not a guarantee of correctness."

class Backend:
    def __init__(self):
        self.router = None
        self.agent = None
        self.lock = threading.RLock()

    def predict(self, state, questions, model="auto"):
        if model not in ("auto", "english", "multilingual", "typed-decisions"):
            raise ValueError("unknown model")
        if not isinstance(state, dict) or not state:
            raise ValueError("state must be a nonempty object")
        from laya.mcp.tools import validate_questions
        questions = validate_questions(questions)
        for q in questions.values():
            if q["type"] == "choice" and len(q["criteria"]) > 20:
                raise ValueError("limit choice questions to 20 options")
        with self.lock:
            from laya import Router, load
            if os.environ.get("LAYA_ACTION_MODEL"):
                if self.agent is None:
                    self.agent = load(os.environ["LAYA_ACTION_MODEL"], device=os.environ.get("LAYA_DEVICE") or "cpu")
                result = self.agent.predict(state, questions)
            else:
                if self.router is None:
                    self.router = Router(device=os.environ.get("LAYA_DEVICE") or "cpu")
                result = self.router.predict(state, questions, model=None if model == "auto" else model)
        return {"answers": result["answers"], "warning": WARNING}

    def choose(self, goal, observation, actions, history, model):
        criteria = {a["id"]: a["description"] for a in actions}
        result = self.predict(
            {"goal": goal, "observation": observation, "recent_outcomes": history},
            {"next_action": {"type": "choice", "instructions":
                "Select the available next action that best advances the goal using observed facts and prior outcomes.",
                "criteria": criteria}}, model)
        answer = result["answers"]["next_action"]
        action_id = answer.get("choice")
        if action_id not in criteria:
            raise ValueError("Laya returned an unknown action id")
        confidence = answer.get("answer_confidence", answer.get("confidence"))
        if confidence is not None:
            if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not math.isfinite(confidence) or not 0 <= confidence <= 1:
                raise ValueError("Laya returned an invalid confidence")
        return {"action_id": action_id, "confidence": confidence, "warning": WARNING}

    def status(self):
        return {"device_preference": os.environ.get("LAYA_DEVICE") or "cpu",
                "router_initialized": self.router is not None,
                "loaded": list(self.router.loaded) if self.router else [],
                "custom_checkpoint_loaded": self.agent is not None, "warning": WARNING}
