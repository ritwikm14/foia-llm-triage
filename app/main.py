import argparse
import json
from pathlib import Path
from typing import Dict

try:
    from rich import print
except Exception:
    # Fallback if rich isn't installed (should be via requirements)
    print = print  # noqa: A001

from .routing import route
from .retriever import Retriever
from .drafting import draft_grounded
from .pii import suggest_pii
from .utils import to_json, now_ms


def process_text(text: str, retriever: Retriever) -> Dict:
    routing = route(text)
    retrieved = retriever.search(text, k=3)
    drafting = draft_grounded(text, routing, retrieved)
    pii = suggest_pii(text)
    return {
        "ts_ms": now_ms(),
        "input": text,
        "routing": routing,
        "retrieval": retrieved,
        "drafting": drafting,
        "pii_suggestions": pii,
        "audit": {
            "retrieved_ids": [r["doc_id"] for r in retrieved],
            "grounded": drafting.get("status") == "ok",
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", type=str, help="Single request text.")
    ap.add_argument("--jsonl", type=str, help="Path to JSONL with {'id','text'} records.")
    ap.add_argument("--out", type=str, help="Output JSONL path for batch.", default=None)
    ap.add_argument(
        "--corpus",
        type=str,
        default=str(Path(__file__).resolve().parents[1] / "data" / "corpus"),
    )
    args = ap.parse_args()

    print("[bold green]main() entered[/bold green]")

    retriever = Retriever(args.corpus)
    print(f"[dim]Loaded corpus from:[/dim] {args.corpus}")

    if args.text:
        result = process_text(args.text, retriever)
        print(to_json(result))
        return

    if args.jsonl:
        # NOTE: accept UTF-8 with BOM to avoid JSONDecodeError from Windows editors
        outfh = open(args.out, "w", encoding="utf-8") if args.out else None
        with open(args.jsonl, "r", encoding="utf-8-sig") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                res = process_text(rec["text"], retriever)
                res["id"] = rec.get("id")
                s = json.dumps(res, ensure_ascii=False)
                if outfh:
                    outfh.write(s + "\n")
                else:
                    print(s)
        if outfh:
            outfh.close()
        return

    ap.print_help()


if __name__ == "__main__":
    main()
