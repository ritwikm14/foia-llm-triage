from typing import Dict, List, Tuple

DEPT_RULES: List[Tuple[str, List[str]]] = [
    ("Mayor's Office", ["mayor", "mayor's office"]),
    ("Police Department", ["police", "incident report", "case #", "case#", "report"]),
    ("Records Office", ["fee waiver", "fees", "foia policy", "deadline", "exemption"]),
]

TYPE_RULES: List[Tuple[str, List[str]]] = [
    ("Email Records", ["email", "emails", "communications"]),
    ("Incident Reports", ["incident", "report", "case #", "case#"]),
    ("Policy Inquiry", ["policy", "waiver", "deadline", "exemption"]),
]


def score(text: str, keywords: List[str]) -> int:
    t = text.lower()
    return sum(1 for k in keywords if k in t)


def route(text: str) -> Dict:
    best_dept, best_d = None, -1
    for dept, kws in DEPT_RULES:
        s = score(text, kws)
        if s > best_d:
            best_dept, best_d = dept, s

    best_type, best_t = None, -1
    for tname, kws in TYPE_RULES:
        s = score(text, kws)
        if s > best_t:
            best_type, best_t = tname, s

    conf = min(1.0, (best_d + best_t) / 4.0)

    if best_d <= 0 and best_t <= 0:
        return {
            "department": "REVIEW",
            "type": "REVIEW",
            "confidence": 0.0,
            "rationale": "No keyword match.",
        }

    return {
        "department": best_dept,
        "type": best_type,
        "confidence": round(conf, 2),
        "rationale": "Keyword routing demo.",
    }
