import json

import pandas as pd
import streamlit as st

from hybrid_search import (
    HybridSearchEngine,
    extract_text_from_pdf_bytes,
    pdf_bytes_to_document,
)
from sample_docs import DOCUMENTS


st.set_page_config(
    page_title="Hybrid Search RAG",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 Hybrid Search, Chunking y Re-ranking")
st.write(
    "Una app pequeña para probar cómo se combinan búsqueda keyword, búsqueda semántica "
    "y re-ranking en un pipeline RAG."
)

with st.sidebar:
    st.header("Parámetros de la demo")
    max_words = st.slider("Tamaño máximo del chunk (palabras)", 50, 220, 120, 10)
    overlap_words = st.slider("Overlap entre chunks (palabras)", 0, 40, 20, 5)
    top_k = st.slider("Resultados finales", 1, 8, 5, 1)

    st.subheader("Pesos de fusión")
    keyword_weight = st.slider("Peso keyword", 0.0, 1.0, 0.45, 0.05)
    semantic_weight = st.slider("Peso semántico", 0.0, 1.0, 0.45, 0.05)
    overlap_weight = st.slider("Peso overlap en reranking", 0.0, 0.5, 0.10, 0.01)

    st.subheader("PDF")
    uploaded_pdf = st.file_uploader("Subí un PDF para indexarlo", type=["pdf"])

    pdf_doc = None
    pdf_text = ""

    if uploaded_pdf is not None:
        try:
            pdf_bytes = uploaded_pdf.getvalue()
            pdf_text = extract_text_from_pdf_bytes(pdf_bytes)

            if pdf_text.strip():
                pdf_doc = pdf_bytes_to_document(pdf_bytes, uploaded_pdf.name)
                st.success("PDF cargado y texto extraído correctamente.")
            else:
                st.warning(
                    "El PDF fue cargado, pero no se pudo extraer texto. "
                    "Si es un PDF escaneado, vas a necesitar OCR."
                )
        except Exception as e:
            st.error(f"No se pudo procesar el PDF: {e}")

    if keyword_weight + semantic_weight == 0:
        st.warning("Activa al menos un peso de recuperación.")
    else:
        total = keyword_weight + semantic_weight
        st.caption(f"Suma keyword+semántico: {total:.2f}")

    if uploaded_pdf is None:
        corpus_mode = "Solo documentos de ejemplo"
    else:
        corpus_mode = st.radio(
            "Corpus de consulta",
            ["Solo documentos de ejemplo", "Solo PDF subido", "Ejemplos + PDF"],
            index=2,
        )

if pdf_doc is not None:
    with st.expander("Ver texto extraído del PDF"):
        st.text_area("Contenido extraído", pdf_text[:20000], height=300)

if corpus_mode == "Solo PDF subido" and pdf_doc is not None:
    docs = [pdf_doc]
elif corpus_mode == "Ejemplos + PDF" and pdf_doc is not None:
    docs = DOCUMENTS + [pdf_doc]
else:
    docs = DOCUMENTS


@st.cache_resource(show_spinner=True)
def build_engine(docs_json: str, max_words: int, overlap_words: int) -> HybridSearchEngine:
    engine = HybridSearchEngine()
    docs_local = json.loads(docs_json)
    engine.fit(docs_local, max_words=max_words, overlap_words=overlap_words)
    return engine


docs_json = json.dumps(docs, ensure_ascii=False)
engine = build_engine(docs_json, max_words, overlap_words)


def search_and_show(
    engine: HybridSearchEngine,
    query: str,
    top_k: int,
    candidate_pool: int,
    keyword_weight: float,
    semantic_weight: float,
    overlap_weight: float,
):
    results = engine.search(
        query=query,
        top_k=top_k,
        candidate_pool=candidate_pool,
        keyword_weight=keyword_weight,
        semantic_weight=semantic_weight,
        overlap_weight=overlap_weight,
    )

    st.subheader("Resultados priorizados")

    if not results:
        st.info("No se encontraron resultados.")
        return results

    rows = []
    for r in results:
        rows.append(
            {
                "Documento": r.title,
                "Keyword": round(r.keyword_score, 3),
                "Semántico": round(r.semantic_score, 3),
                "Fused": round(r.fused_score, 3),
                "Rerank": round(r.rerank_score, 3),
                "Chunk": r.chunk_id,
            }
        )

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    for i, r in enumerate(results, start=1):
        with st.expander(f"{i}. {r.title}  |  score final: {r.rerank_score:.3f}", expanded=(i == 1)):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Keyword", f"{r.keyword_score:.3f}")
            c2.metric("Semántico", f"{r.semantic_score:.3f}")
            c3.metric("Fused", f"{r.fused_score:.3f}")
            c4.metric("Rerank", f"{r.rerank_score:.3f}")

            st.write(r.text)
            st.caption(
                f"doc_id={r.doc_id} | chunk_id={r.chunk_id} | "
                f"ranks -> keyword:{r.keyword_rank}, semantic:{r.semantic_rank}, fused:{r.fused_rank}"
            )

    return results


col_a, col_b = st.columns([1.2, 0.8], gap="large")

with col_a:
    query = st.text_input(
        "Escribí una consulta de negocio o soporte técnico",
        value="La VPN no conecta desde casa y aparece un error de túnel seguro",
    )

    st.caption(
        "Ejemplos: cambio de contraseña, impresora en cola, backup, factura con CUIT incorrecto, VPN caída."
    )

    if st.button("Buscar", type="primary"):
        with st.spinner("Recuperando y reordenando contexto..."):
            search_and_show(
                engine=engine,
                query=query,
                top_k=top_k,
                candidate_pool=max(top_k * 3, 8),
                keyword_weight=keyword_weight,
                semantic_weight=semantic_weight,
                overlap_weight=overlap_weight,
            )

with col_b:
    st.subheader("Cómo se ve la arquitectura")
    st.code(
        """
Consulta del usuario
      ├──► Motor keyword (BM25)
      ├──► Motor semántico (embeddings)
      │
      └──► Fusión de scores
               │
               └──► Re-ranking heurístico
                        │
                        └──► Contexto final para RAG
        """.strip(),
        language="text",
    )

    info = engine.explain(query)
    st.subheader("Estado del índice")
    st.json(info)

    st.subheader("Qué muestra esta demo")
    st.markdown(
        """
- **Hybrid Search**: combina dos señales distintas.
- **Chunking semántico**: fragmenta por bloques con sentido.
- **Re-ranking**: reordena los resultados más prometedores antes de pasar al LLM.
        """
    )

st.divider()
st.subheader("Documentos cargados")
for d in docs:
    with st.expander(d["title"]):
        st.write(d["content"][:4000] + ("..." if len(d["content"]) > 4000 else ""))