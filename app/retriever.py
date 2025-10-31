from typing import List, Dict
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Retriever:
    def __init__(self, corpus_dir: str):
        self.paths = sorted(Path(corpus_dir).glob("*.*"))
        self.docs = [p.read_text(encoding="utf-8") for p in self.paths]
        self.ids = [p.name for p in self.paths]
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.X = self.vectorizer.fit_transform(self.docs) if self.docs else None

    def search(self, query: str, k: int = 3) -> List[Dict]:
        if not self.docs:
            return []
        qv = self.vectorizer.transform([query])
        sims = cosine_similarity(qv, self.X).ravel()
        idxs = sims.argsort()[::-1][:k]
        return [{"doc_id": self.ids[i], "score": float(sims[i]), "snippet": self.docs[i][:240]} for i in idxs]
