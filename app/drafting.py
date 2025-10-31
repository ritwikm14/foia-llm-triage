from typing import Dict, List
from .utils import prompt_hash

TEMPLATE = """Dear Requester,

Thank you for your public records request. Based on your description, we have initiated triage and routed your request to: **{department}** (type: **{rtype}**).

Next steps:
- We will search the relevant records and apply applicable exemptions where required.
- If fees or fee waivers apply, we will notify you.
- Our standard response timeline is governed by policy.

Evidence consulted:
{citations}

If additional clarification is needed, we will contact you.

Regards,
City Records Office
"""

def make_citations(results: List[Dict]) -> str:
    lines = []
    for r in results:
        lines.append(f"- [{r['doc_id']}] score={r['score']:.3f}: {r['snippet'][:160].strip()}...")
    return "\n".join(lines) if lines else "- No supporting passages found."

def draft_grounded(request_text: str, route_info: Dict, retrieved: List[Dict]) -> Dict:
    if not retrieved or all(r["score"] < 0.05 for r in retrieved):
        return {"status": "needs_review", "reason": "Insufficient evidence for grounded draft.", "draft": ""}

    citations = make_citations(retrieved)
    draft = TEMPLATE.format(department=route_info["department"], rtype=route_info["type"], citations=citations)
    phash = prompt_hash(request_text + citations)
    return {"status": "ok", "prompt_hash": phash, "draft": draft, "citations": [r["doc_id"] for r in retrieved]}
