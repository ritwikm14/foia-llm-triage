<!-- TITLE & BADGES -->
<h1 align="center">FOIA Auto-Triage & Grounded Drafting (MVP)</h1>

<p align="center">
  <em>Routes public-records requests → retrieves evidence → drafts grounded replies with citations → flags PII</em>
</p>

<p align="center">
  <a href="https://www.python.org/"><img alt="Python" src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white"></a>
  <a href="./LICENSE"><img alt="License" src="https://img.shields.io/badge/License-MIT-000?logo=opensourceinitiative&logoColor=white"></a>
  <a href="https://scikit-learn.org/"><img alt="scikit-learn" src="https://img.shields.io/badge/scikit--learn-1.7+-F89939?logo=scikitlearn&logoColor=white"></a>
  <a href="https://numpy.org/"><img alt="NumPy" src="https://img.shields.io/badge/NumPy-2.x-013243?logo=numpy&logoColor=white"></a>
  <a href="https://code.visualstudio.com/"><img alt="VS Code" src="https://img.shields.io/badge/Editor-VS%20Code-007ACC?logo=visualstudiocode&logoColor=white"></a>
</p>

---

## ✨ Overview

This repo implements a minimal, production-lean baseline for public-records workflows:

- **Routing** — Rule-based mapping of request text to `{ department, type, confidence }` in [`app/routing.py`](app/routing.py)  
- **Retrieval** — TF-IDF + cosine similarity over a small corpus in [`data/corpus/`](data/corpus/) via [`app/retriever.py`](app/retriever.py)  
- **Grounded drafting** — Response templating with explicit citations and a refusal path when evidence is weak in [`app/drafting.py`](app/drafting.py)  
- **PII hints** — Lightweight regex detectors for emails/phones/SSNs in [`app/pii.py`](app/pii.py)  
- **CLI** — Single or batch JSONL entry points in [`app/main.py`](app/main.py); JSONL reader is BOM-tolerant for Windows editors

Outputs are **auditable by default** and include `citations`, `retrieved_ids`, a reproducible `prompt_hash`, and a `grounded` flag to gate downstream automation.

---

## 🧠 Techniques (with docs)

- **TF-IDF vectorization with n-grams** for sparse retrieval  
  → scikit-learn [`TfidfVectorizer`](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html) with `stop_words="english"`, `ngram_range=(1, 2)`
- **Cosine similarity on sparse matrices** for ranking  
  → scikit-learn [`cosine_similarity`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html)
- **Deterministic rule-based routing** with simple keyword scoring  
  → Transparent, easy to test/extend (see [`app/routing.py`](app/routing.py))
- **BOM-tolerant JSONL ingestion** for Windows-saved files  
  → Open with `encoding="utf-8-sig"`; MDN: [Byte order mark (BOM)](https://developer.mozilla.org/docs/Glossary/Byte_order_mark), [JSON](https://developer.mozilla.org/docs/Web/JavaScript/Reference/Global_Objects/JSON)
- **Refusal on weak evidence**  
  → Drafting short-circuits to `needs_review` if all retrieval scores fall below a threshold (see [`app/drafting.py`](app/drafting.py))
- **Auditable output contract**  
  → `prompt_hash`, `citations`, `retrieved_ids`, `grounded` (see [`app/utils.py`](app/utils.py), [`app/main.py`](app/main.py))

> **Why this design?** Start deterministic for safety and auditability; keep seams clean for later upgrades (BM25/FAISS, style-only LLM pass that preserves citations).

---

## 🧰 Notable Tooling & Libraries

- **[scikit-learn](https://scikit-learn.org/)** — TF-IDF & cosine similarity for lightweight retrieval  
- **[NumPy](https://numpy.org/)** — numeric underpinnings used by scikit-learn  
- **[Rich](https://rich.readthedocs.io/)** — readable CLI diagnostics (optional; code falls back gracefully)  
- **Conda** — reproducible Python envs across Windows/macOS/Linux  
- **VS Code launch/tasks** — one-click run/debug (see [`.vscode/launch.json`](.vscode/launch.json), [`.vscode/tasks.json`](.vscode/tasks.json))

> Fonts: N/A — CLI/library project (no web UI)

---

## 📂 Project Structure

```text
D:.
|   requirements.txt
|   results.jsonl
|
+---.vscode
|       launch.json
|       settings.json
|       tasks.json
|
+---app
|   |   drafting.py
|   |   init.py
|   |   main.py
|   |   pii.py
|   |   retriever.py
|   |   routing.py
|   |   utils.py
|   |   __init__.py
|   |
|   \---__pycache__
|           ...
|
\---data
    |   requests_sample.jsonl
    |
    \---corpus
            policy_foia.md
            prior_response_1.md
            prior_response_2.md
Directory notes

app/ — single-responsibility modules with stable interfaces
↪ Note: __init__.py is the package marker; init.py is not required and can be removed if unused

data/corpus/ — small grounding set; add .md/.txt files to strengthen citations

.vscode/ — optional one-click run/debug and reproducible tasks

⚙️ Setup
bash
Copy code
# 1) Create and activate a clean environment
conda create -y -n llm-mvp python=3.11
conda activate llm-mvp

# 2) Install dependencies
pip install -r requirements.txt

# 3) Sanity check
python -c "import sklearn, numpy; print('ok', sklearn.__version__, numpy.__version__)"

# 4) Run a single request
python -m app.main --text "I am requesting emails between the Mayor's office and ACME Corp from Jan 2023."

# 5) Batch run (writes results.jsonl)
python -m app.main --jsonl data/requests_sample.jsonl --out results.jsonl
Windows note: Batch reader accepts utf-8-sig (BOM). JSONL saved from Notepad/VS Code works out of the box.

VS Code one-click

Run & Debug ▶️ via .vscode/launch.json

Or Tasks via .vscode/tasks.json which use conda run -n llm-mvp …

🧪 Sample Output (trimmed)
json
Copy code
{
  "routing": {"department": "Mayor's Office", "type": "Email Records", "confidence": 1.0},
  "retrieval": [
    {"doc_id": "prior_response_1.md", "score": 0.45, "snippet": "..."},
    {"doc_id": "policy_foia.md", "score": 0.04, "snippet": "..."}
  ],
  "drafting": {
    "status": "ok",
    "draft": "Dear Requester, ...",
    "citations": ["prior_response_1.md", "policy_foia.md"]
  },
  "pii_suggestions": [],
  "audit": {"retrieved_ids": ["prior_response_1.md","policy_foia.md"], "grounded": true}
}
🔭 Extensibility Roadmap
Hybrid retrieval (BM25 + dense/FAISS) to improve recall on varied policy corpora

Router v2 with department/type dictionaries, softmax scoring, and fallbacks

Style-only LLM pass that preserves citations and still refuses on weak evidence

Privacy: expand PII detectors (names/addresses), masking modes, policy-aware exemptions

Quality gates: unit tests for routing/retrieval/thresholds; golden outputs

Metrics: calibration curves (score → refusal), reviewer accept/reject analytics

✅ Design Tenets
Deterministic baseline first (safer than immediate generation)

Grounded or refused; never ungrounded prose

Auditable by default (provenance + flags)

Small modules; easy to replace parts without churn

📜 License
MIT — use freely for demos and internal pilots. Validate outputs and keep a human in the loop for production use.


