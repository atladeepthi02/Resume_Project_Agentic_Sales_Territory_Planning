from __future__ import annotations

import math
from typing import Any, Dict, List


class SimpleVectorStore:
    """Local fallback retrieval implementation without a heavy dependency."""

    def __init__(self):
        self._documents: List[Dict[str, Any]] = []

    def add_documents(self, documents: List[Dict[str, Any]]):
        self._documents.extend(documents)

    def search(self, query: str, filters: Dict[str, Any] | None = None, limit: int = 5) -> List[Dict[str, Any]]:
        query_tokens = {token.lower() for token in query.replace("/", " ").split() if token}
        if not query_tokens:
            return []

        results = []
        for document in self._documents:
            if filters:
                match = True
                for key, value in filters.items():
                    if document.get(key) != value:
                        match = False
                        break
                if not match:
                    continue
            score = 0.0
            text = f"{document.get('title','')} {document.get('content','')}".lower()
            for token in query_tokens:
                if token in text:
                    score += 1.0
            if score > 0:
                results.append({**document, "score": score})

        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:limit]


class SalesKnowledgeRAG:
    def __init__(self, vector_store: SimpleVectorStore | None = None):
        self.vector_store = vector_store or SimpleVectorStore()

    def ingest_documents(self, documents: List[Dict[str, Any]]):
        self.vector_store.add_documents(documents)

    def search(self, query: str, filters: Dict[str, Any] | None = None, limit: int = 5) -> List[Dict[str, Any]]:
        return self.vector_store.search(query=query, filters=filters, limit=limit)

    def retrieve_with_citations(self, query: str, filters: Dict[str, Any] | None = None, limit: int = 5) -> List[Dict[str, Any]]:
        results = self.search(query=query, filters=filters, limit=limit)
        for item in results:
            item["citation"] = f"{item.get('source', 'Unknown')}#section-{item.get('title', 'doc')}"
        return results
