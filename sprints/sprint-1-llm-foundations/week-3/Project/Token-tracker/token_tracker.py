import time
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

class TokenTracker:
    """
    Simple token tracker for monitoring token usage and costs.
    """
    DEFAULT_PRICING = {
        "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},
        "gpt-4": {"prompt": 0.03, "completion": 0.06},
    }

    def __init__(self, model_name: str = "gpt-3.5-turbo", log_path: Optional[str] = None):
        self.model_name = model_name
        self.log_path = log_path
        self.tokens = {"prompt": 0, "completion": 0, "total": 0}
        self.cost = 0.0
        self.start_time = time.time()
        self.interactions = []
        self.pricing = self.DEFAULT_PRICING.copy()

    def count_tokens(self, text: str) -> int:
        if not text:
            return 0
        if TIKTOKEN_AVAILABLE:
            try:
                enc = tiktoken.encoding_for_model(self.model_name)
                return len(enc.encode(text))
            except Exception:
                pass
        return max(1, len(text) // 4)

    def get_price(self, token_type: str) -> float:
        return self.pricing.get(self.model_name, {}).get(token_type, 0.001)

    def log(self, prompt: str, completion: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pt = self.count_tokens(prompt)
        ct = self.count_tokens(completion)
        total = pt + ct
        pcost = (pt / 1000) * self.get_price("prompt")
        ccost = (ct / 1000) * self.get_price("completion")
        tcost = pcost + ccost

        self.tokens["prompt"] += pt
        self.tokens["completion"] += ct
        self.tokens["total"] += total
        self.cost += tcost

        record = {
            "timestamp": datetime.now().isoformat(),
            "model": self.model_name,
            "tokens": {"prompt": pt, "completion": ct, "total": total},
            "cost": {"prompt": pcost, "completion": ccost, "total": tcost},
        }
        if metadata:
            record["metadata"] = metadata
        self.interactions.append(record)
        if self.log_path:
            self._save(record)
        return record

    def _save(self, record: Dict[str, Any]):
        try:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            with open(self.log_path, "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception:
            pass

    def summary(self) -> Dict[str, Any]:
        return {
            "model": self.model_name,
            "tokens": self.tokens,
            "cost": self.cost,
            "duration_seconds": time.time() - self.start_time,
            "interactions": len(self.interactions),
        }

    def reset(self):
        self.tokens = {"prompt": 0, "completion": 0, "total": 0}
        self.cost = 0.0
        self.start_time = time.time()
        self.interactions = []

    def export(self, path: str) -> str:
        data = {"summary": self.summary(), "interactions": self.interactions}
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            return path
        except Exception:
            return ""
