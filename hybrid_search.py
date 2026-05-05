from __future__ import annotations

import io
import math
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Optional, Sequence

import numpy as np
from rank_bm25 import BM25Okapi

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover
    SentenceTransformer = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import normalize
except Exception:  # pragma: no cover
    TfidfVectorizer = None
    normalize = None

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None


_WORD_RE = re.compile(r"[a-záéíóúüñ0-9]+", re.IGNORECASE)


def tokenize(text: str) -> List[str]:
    """Tokenización simple y robusta para español."""
    return _WORD_RE.findall(text.lower())


def normalize_min_max(values: np.ndarray) -> np.ndarray:
    if values.size == 0:
        return values
    vmin = float(np.min(values))
    vmax = float(np.max(values))
    if math.isclose(vmin, vmax):
        return np.zeros_like(values, dtype=float)
    return (values - vmin) / (vmax - vmin)


def split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[\.\!\?])\s+|\n+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def semantic_chunk_text(text: str, max_words: int = 120, overlap_words: int = 20) -> List[str]:
    """
    Divide el texto en chunks semánticos simples:
    - primero respeta párrafos
    - luego, si un bloque es demasiado largo, lo parte por oraciones
    - agrega solapamiento para no cortar ideas abruptamente
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: List[str] = []

    def flush_buffer(buffer: List[str]) -> List[str]:
        if not buffer:
            return []
        chunk = " ".join(buffer).strip()
        if chunk:
            chunks.append(chunk)
        if overlap_words <= 0:
            return []
        words = tokenize(chunk)
        tail = words[-overlap_words:] if len(words) > overlap_words else words
        return [" ".join(tail)] if tail else []

    buffer: List[str] = []
    buffer_words = 0

    for paragraph in paragraphs:
        p_words = tokenize(paragraph)

        if len(p_words) > max_words:
            buffer = flush_buffer(buffer)
            buffer_words = len(tokenize(" ".join(buffer))) if buffer else 0

            sentences = split_sentences(paragraph)
            sent_buffer: List[str] = []
            sent_words = 0

            for sent in sentences:
                n = len(tokenize(sent))
                if sent_buffer and sent_words + n > max_words:
                    chunks.append(" ".join(sent_buffer).strip())
                    if overlap_words > 0:
                        tail_words = tokenize(chunks[-1])[-overlap_words:]
                        sent_buffer = [" ".join(tail_words)] if tail_words else []
                        sent_words = len(tokenize(" ".join(sent_buffer)))
                    else:
                        sent_buffer = []
                        sent_words = 0
                sent_buffer.append(sent)
                sent_words += n

            if sent_buffer:
                chunks.append(" ".join(sent_buffer).strip())
            continue

        if buffer_words + len(p_words) <= max_words:
            buffer.append(paragraph)
            buffer_words += len(p_words)
        else:
            buffer = flush_buffer(buffer)
            buffer_words = len(tokenize(" ".join(buffer))) if buffer else 0
            buffer.append(paragraph)
            buffer_words += len(p_words)

    if buffer:
        chunks.extend(flush_buffer(buffer) or [])

    return [c for c in chunks if c.strip()]


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Extrae texto de un PDF cargado en memoria.
    Si el PDF es escaneado/imágen, esto no hará OCR.
    """
    if PdfReader is None:
        raise RuntimeError(
            "No está instalada la librería 'pypdf'. Instalá con: pip install pypdf"
        )

    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages: List[str] = []

    for page in reader.pages:
        try:
            txt = page.extract_text() or ""
        except Exception:
            txt = ""
        if txt.strip():
            pages.append(txt)

    return "\n\n".join(pages).strip()


def pdf_bytes_to_document(pdf_bytes: bytes, filename: str) -> Dict[str, str]:
    """Convierte un PDF en un documento compatible con el motor."""
    content = extract_text_from_pdf_bytes(pdf_bytes)
    return {
        "id": f"pdf::{filename}",
        "title": filename,
        "content": content,
    }


@lru_cache(maxsize=2)
def get_sentence_transformer(model_name: str):
    if SentenceTransformer is None:
        return None
    return SentenceTransformer(model_name)


@dataclass
class Chunk:
    chunk_id: int
    doc_id: str
    title: str
    text: str


@dataclass
class SearchResult:
    chunk_id: int
    doc_id: str
    title: str
    text: str
    keyword_score: float
    semantic_score: float
    fused_score: float
    rerank_score: float
    keyword_rank: int
    semantic_rank: int
    fused_rank: int


class HybridSearchEngine:
    """
    Demo didáctica de Hybrid Search:
    keyword (BM25) + semantic search (embeddings) + reranking heurístico.
    """

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2") -> None:
        self.model_name = model_name
        self.chunks: List[Chunk] = []
        self.bm25: Optional[BM25Okapi] = None
        self.keyword_corpus: List[List[str]] = []
        self.semantic_mode: str = "sentence_transformers"
        self.model = None
        self.vectorizer = None
        self.semantic_matrix = None

    def fit(
        self,
        documents: Sequence[Dict[str, str]],
        max_words: int = 120,
        overlap_words: int = 20,
    ) -> "HybridSearchEngine":
        self.chunks = []

        for doc in documents:
            content = doc.get("content", "").strip()
            if not content:
                continue

            raw_chunks = semantic_chunk_text(
                content,
                max_words=max_words,
                overlap_words=overlap_words,
            )

            for raw in raw_chunks:
                self.chunks.append(
                    Chunk(
                        chunk_id=len(self.chunks),
                        doc_id=doc.get("id", f"doc_{len(self.chunks)}"),
                        title=doc.get("title", "Sin título"),
                        text=raw,
                    )
                )

        self.keyword_corpus = [tokenize(c.text) for c in self.chunks]
        self.bm25 = BM25Okapi(self.keyword_corpus) if self.keyword_corpus else None

        texts = [c.text for c in self.chunks]
        self.semantic_matrix = None

        model = get_sentence_transformer(self.model_name)
        if model is not None:
            try:
                self.model = model
                self.semantic_matrix = self.model.encode(
                    texts,
                    normalize_embeddings=True,
                    show_progress_bar=False,
                )
                self.semantic_mode = "sentence_transformers"
                return self
            except Exception:
                self.model = None

        if TfidfVectorizer is None:
            raise RuntimeError(
                "No se pudo inicializar un backend de embeddings. "
                "Instala sentence-transformers o scikit-learn."
            )

        self.semantic_mode = "tfidf_fallback"
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), lowercase=True)
        self.semantic_matrix = self.vectorizer.fit_transform(texts)
        if normalize is not None:
            self.semantic_matrix = normalize(self.semantic_matrix)

        return self

    def _semantic_scores(self, query: str) -> np.ndarray:
        if not self.chunks:
            return np.array([], dtype=float)

        if self.semantic_mode == "sentence_transformers" and self.model is not None:
            q = self.model.encode([query], normalize_embeddings=True, show_progress_bar=False)[0]
            return np.asarray(np.dot(self.semantic_matrix, q), dtype=float)

        q = self.vectorizer.transform([query])
        if normalize is not None:
            q = normalize(q)
        scores = (self.semantic_matrix @ q.T).toarray().ravel()
        return np.asarray(scores, dtype=float)

    def search(
        self,
        query: str,
        top_k: int = 5,
        candidate_pool: int = 8,
        keyword_weight: float = 0.45,
        semantic_weight: float = 0.45,
        overlap_weight: float = 0.10,
    ) -> List[SearchResult]:
        if not self.chunks or self.bm25 is None:
            return []

        q_tokens = tokenize(query)
        bm25_scores = np.asarray(self.bm25.get_scores(q_tokens), dtype=float)
        semantic_scores = self._semantic_scores(query)

        keyword_norm = normalize_min_max(bm25_scores)
        semantic_norm = normalize_min_max(semantic_scores)

        fused = (keyword_weight * keyword_norm) + (semantic_weight * semantic_norm)

        kw_order = np.argsort(-keyword_norm)
        sem_order = np.argsort(-semantic_norm)
        fused_order = np.argsort(-fused)

        candidate_indices = list(
            dict.fromkeys(
                list(fused_order[:candidate_pool])
                + list(kw_order[:candidate_pool])
                + list(sem_order[:candidate_pool])
            )
        )

        q_set = set(q_tokens)
        results: List[SearchResult] = []

        kw_rank_map = {idx: rank + 1 for rank, idx in enumerate(kw_order)}
        sem_rank_map = {idx: rank + 1 for rank, idx in enumerate(sem_order)}
        fused_rank_map = {idx: rank + 1 for rank, idx in enumerate(fused_order)}

        for idx in candidate_indices:
            chunk = self.chunks[idx]
            chunk_tokens = tokenize(chunk.text)
            overlap = len(q_set.intersection(chunk_tokens))
            overlap_score = overlap / max(len(q_set), 1)

            length = len(chunk_tokens)
            length_bonus = 1.0 if 45 <= length <= 180 else 0.92

            rerank_score = float(
                0.72 * fused[idx]
                + overlap_weight * overlap_score
                + 0.08 * length_bonus
            )

            results.append(
                SearchResult(
                    chunk_id=chunk.chunk_id,
                    doc_id=chunk.doc_id,
                    title=chunk.title,
                    text=chunk.text,
                    keyword_score=float(keyword_norm[idx]),
                    semantic_score=float(semantic_norm[idx]),
                    fused_score=float(fused[idx]),
                    rerank_score=rerank_score,
                    keyword_rank=kw_rank_map.get(idx, -1),
                    semantic_rank=sem_rank_map.get(idx, -1),
                    fused_rank=fused_rank_map.get(idx, -1),
                )
            )

        results.sort(key=lambda r: r.rerank_score, reverse=True)
        return results[:top_k]

    def explain(self, query: str) -> Dict[str, object]:
        """Devuelve datos útiles para mostrar en clase."""
        if not self.chunks:
            return {"query": query, "message": "El índice está vacío."}

        return {
            "query": query,
            "documents": len({c.doc_id for c in self.chunks}),
            "chunks": len(self.chunks),
            "backend": self.semantic_mode,
            "query_tokens": tokenize(query),
        }