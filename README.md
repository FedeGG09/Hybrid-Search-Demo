# 🔎 Hybrid Search RAG Demo

Demo didáctica para explicar, en una sola app, cómo funciona un pipeline de **Hybrid Search** aplicado a **RAG**:

- recuperación por palabras clave con **BM25**
- recuperación semántica con **embeddings**
- **fusión de scores**
- **re-ranking heurístico**
- **chunking semántico**
- carga de **PDFs** para consultar sobre documentos reales

**Versión en línea:** https://hybrid-search-d.streamlit.app/

---

## ¿Qué resuelve esta demo?

En muchos sistemas RAG, el problema no está en generar texto, sino en **recuperar el contexto correcto** antes de responder.

Este proyecto muestra cómo combinar:

- **keyword search**, útil para términos exactos, códigos, siglas y nombres técnicos;
- **semantic search**, útil para recuperar ideas similares aunque cambie la redacción;
- **hybrid search**, para equilibrar precisión y cobertura;
- **chunking semántico**, para dividir documentos en fragmentos con sentido;
- **re-ranking**, para priorizar los fragmentos más relevantes antes de enviarlos al modelo generativo.

---

## Funcionalidades principales

- Carga de documentos de ejemplo.
- Subida de un PDF desde la interfaz.
- Extracción automática de texto del PDF.
- Indexación híbrida del contenido.
- Búsqueda con parámetros ajustables:
  - tamaño de chunk
  - overlap
  - top-k
  - peso keyword
  - peso semántico
  - peso de overlap en re-ranking
- Visualización de resultados con métricas por fragmento.
- Explicación del estado del índice y de la arquitectura.

---

## Arquitectura del proyecto

```text
Usuario
  └──► Consulta
          ├──► BM25 / keyword search
          ├──► Semantic search / embeddings
          ├──► Fusión de scores
          ├──► Re-ranking heurístico
          └──► Contexto final para RAG
```

### Módulos del proyecto

#### `app.py`
Interfaz principal en Streamlit.

Responsabilidades:
- mostrar la UI
- permitir subir PDFs
- tomar la consulta del usuario
- llamar al motor híbrido
- mostrar resultados, métricas y contexto recuperado

#### `hybrid_search.py`
Motor de recuperación híbrida.

Responsabilidades:
- tokenización
- chunking semántico
- extracción de texto de PDF
- construcción del índice BM25
- cálculo de embeddings semánticos
- fusión de resultados
- re-ranking heurístico
- explicación del índice

#### `sample_docs.py`
Corpus de ejemplo.

Responsabilidades:
- definir documentos base para demo
- simular contenido empresarial / soporte técnico
- permitir comparar el comportamiento del sistema con y sin PDF

#### `requirements.txt`
Dependencias del proyecto.

Responsabilidades:
- fijar librerías necesarias para ejecutar la app localmente o en Streamlit Cloud

---

## Grupo de funciones del motor `hybrid_search.py`

### 1) Preprocesamiento y tokenización
Funciones:
- `tokenize(text)`
- `normalize_min_max(values)`
- `split_sentences(text)`

Qué hacen:
- limpian y normalizan texto
- separan palabras
- separan oraciones
- preparan el contenido para indexación y scoring

### 2) Chunking semántico
Función:
- `semantic_chunk_text(text, max_words=120, overlap_words=20)`

Qué hace:
- divide el texto en fragmentos con sentido
- prioriza párrafos y oraciones
- aplica overlap para no perder continuidad

### 3) PDF ingestion
Funciones:
- `extract_text_from_pdf_bytes(pdf_bytes)`
- `pdf_bytes_to_document(pdf_bytes, filename)`

Qué hacen:
- leen un PDF cargado por el usuario
- extraen texto
- convierten el archivo a un documento compatible con el motor

### 4) Motor híbrido
Clase:
- `HybridSearchEngine`

Métodos principales:
- `fit(...)`
- `_semantic_scores(query)`
- `search(...)`
- `explain(query)`

Qué hacen:
- construyen el índice
- calculan scores keyword y semánticos
- fusionan resultados
- reordenan por relevancia
- devuelven resultados listos para mostrar en clase

---

## Requisitos

- Python 3.10 o superior
- conexión a internet para instalar dependencias
- navegador web
- opcionalmente: GPU no es necesaria para la demo

---

## Instalación local

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd TU_REPO
```

### 2. Crear y activar un entorno virtual

#### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Linux / macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la app

```bash
streamlit run app.py
```

---

## Cómo usar la app

### Opción A: con los documentos de ejemplo
1. Abrí la app.
2. Escribí una consulta como:
   - `La VPN no conecta desde casa`
   - `No puedo imprimir un documento`
   - `La factura tiene un CUIT incorrecto`
3. Ajustá los sliders de chunking y pesos.
4. Presioná **Buscar**.

### Opción B: con un PDF propio
1. Subí un PDF desde la barra lateral.
2. Elegí el modo de corpus:
   - solo PDF subido
   - ejemplos + PDF
   - solo ejemplos
3. Ejecutá consultas sobre el contenido del documento.

---


---

## Este proyecto está pensado para visualizar:

- por qué un LLM no debería responder “solo con memoria”
- cómo se arma un pipeline RAG
- por qué keyword search y semantic search se complementan
- por qué el chunking afecta la calidad del contexto
- por qué el re-ranking mejora la relevancia final
- cómo se adapta una arquitectura a documentos empresariales reales

---

## Estructura sugerida del repositorio

```text
.
├── app.py
├── hybrid_search.py
├── sample_docs.py
├── requirements.txt
└── README.md
```

---

## Consideraciones técnicas

- Si el PDF es **escaneado** y no contiene texto digital, `pypdf` puede no extraer contenido útil.
- En ese caso se recomienda sumar OCR más adelante.
- La demo incluye fallback semántico para simplificar la ejecución en entornos donde no se cargue `sentence-transformers`.
- Los scores mostrados son útiles para enseñanza, no para producción.


## Licencia

Material educativo para uso en clase.

---

## Federico Guillermo Gravina

Proyecto didáctico preparado para enseñar:
- Hybrid Search
- RAG
- Chunking semántico
- Re-ranking
- Recuperación de contexto en sistemas empresariales

- `sample_docs.py`: corpus de ejemplo
