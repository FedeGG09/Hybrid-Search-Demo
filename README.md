# Demo Hybrid Search RAG

Proyecto minimalista para explicar en clase:

- búsqueda keyword con BM25
- búsqueda semántica con embeddings
- fusión de señales
- re-ranking heurístico
- chunking semántico

## Ejecutar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Archivos

- `app.py`: interfaz y demostración
- `hybrid_search.py`: motor híbrido
- `sample_docs.py`: corpus de ejemplo
