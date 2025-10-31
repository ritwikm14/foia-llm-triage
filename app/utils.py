import hashlib
import json
import time
from typing import Any

def now_ms() -> int:
    return int(time.time() * 1000)

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def to_json(o: Any) -> str:
    return json.dumps(o, ensure_ascii=False, indent=2)

def prompt_hash(prompt: str) -> str:
    return sha256(prompt)[:12]
