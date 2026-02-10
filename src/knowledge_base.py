import logging
import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src import db
from src.config import CHUNK_SIZE, TOP_K

logger = logging.getLogger(__name__)


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """Split text into chunks at sentence boundaries."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) > chunk_size and current:
            chunks.append(current.strip())
            current = sentence
        else:
            current = f"{current} {sentence}" if current else sentence
    if current.strip():
        chunks.append(current.strip())
    return chunks if chunks else [text]


class KnowledgeBase:
    """TF-IDF based knowledge retrieval."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.chunks: list[str] = []
        self.matrix = None
        self._build_index()

    def _build_index(self):
        entries = db.get_all_knowledge()
        self.chunks = []
        for entry in entries:
            title = entry["title"]
            for chunk in _chunk_text(entry["content"]):
                self.chunks.append(f"{title}: {chunk}")

        if self.chunks:
            self.matrix = self.vectorizer.fit_transform(self.chunks)
            logger.info("Knowledge index built with %d chunks", len(self.chunks))
        else:
            self.matrix = None
            logger.info("Knowledge base is empty")

    def rebuild(self):
        """Rebuild the index after knowledge base changes."""
        self._build_index()

    def search(self, query: str, top_k: int = TOP_K) -> list[str]:
        """Return the top-k most relevant chunks for a query."""
        if not self.chunks or self.matrix is None:
            return []
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).flatten()
        top_indices = np.argsort(scores)[-top_k:][::-1]
        return [self.chunks[i] for i in top_indices if scores[i] > 0.05]
