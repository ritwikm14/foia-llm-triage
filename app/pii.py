import re
from typing import List, Dict
PATTERNS = [
    ("EMAIL", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("PHONE", re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b")),
    ("SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
]
def suggest_pii(text: str) -> List[Dict]:
    out = []
    for label, pat in PATTERNS:
        for m in pat.finditer(text):
            out.append({"label":label,"start":m.start(),"end":m.end(),"text":m.group(0),
                        "confidence":0.95 if label!="PHONE" else 0.85,"reason":f"Regex match for {label}"})
    return out
