# Alfred ML

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Ollama](https://img.shields.io/badge/Ollama-Offline%20LLM-black.svg)](https://ollama.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-orange.svg)](https://www.trychroma.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Alfred ML** is a local, privacy-focused Retrieval-Augmented Generation (RAG) assistant. It indexes your personal documents, research PDFs, and source code using local vector embeddings, and answers queries via [Ollama](https://ollama.com/)—**100% offline, zero cloud leakage.**

Available as an interactive Terminal UI (TUI), a command-line utility, and a **FastAPI REST API**.

---

## Architecture

```
                             [ Local Documents & Code ]
                       (.pdf, .md, .txt, .py, .ts, .json, etc.)
                                         │
                                         ▼
                               [ Text Chunker ]
                                         │
                                         ▼
                      [ sentence-transformers (Local) ]
                                         │
                                         ▼
                          [ ChromaDB Vector Store ]
                                         ▲
                                         │ Semantic Search (Top-K)
                                         │
[ User Query ] ──► [ Query Embedding ] ──┴──► [ Grounded Prompt ]
                                                     │
                                                     ▼
                                          [ Ollama LLM (Local) ]
                                          (llama3.2:1b-instruct)
                                                     │
                                                     ▼
                                           [ Answer + Sources ]
```

---

## Features

* **Multi-Format Ingestion:** Indexes Markdown (`.md`), plain text (`.txt`), research papers / books (`.pdf`), and codebases (`.py`, `.ts`, `.js`, `.json`, etc.).
* **100% Local & Private:** Embeddings (`sentence-transformers/all-MiniLM-L6-v2`) and generative models (`llama3.2`) run strictly on your hardware.
* **Three Flexible Interfaces:**
  * **Interactive TUI:** Rich terminal menus with model switching and live chat.
  * **FastAPI REST API:** Full OpenAPI / Swagger documentation at `/docs` with `/ask`, `/ingest`, and `/health` endpoints.
  * **CLI Commands:** Fast one-off queries and background file-system watching.
* **Automated Sync:** Watches `alfred_docs/` via `watchdog` and updates changed or deleted documents in real-time.

---

## Prerequisites

1. **Python 3.10+**
2. **[Ollama](https://ollama.com/)** running locally:
   ```bash
   # Start the Ollama daemon
   ollama serve

   # Pull default lightweight model
   ollama pull llama3.2:1b-instruct-q4_K_M
   ```

---

## Quick Start

### 1. Clone & Set Up

```bash
git clone https://github.com/sanjayBahadur/AlfredML.git
cd AlfredML

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Add Documents

Place any documents or code you want Alfred to analyze into `alfred_docs/`:

```bash
cp /path/to/my_notes.md alfred_docs/
cp /path/to/research_paper.pdf alfred_docs/
cp /path/to/main.py alfred_docs/
```

### 3. Ingest Documents

```bash
./alfred ingest
```

---

## Usage Modes

### 1. Interactive TUI (Recommended)
Launch the visual terminal dashboard:

```bash
./alfred
```
* **Chat:** Ask questions interactively with live source citation.
* **Sync Documents:** Re-index files on demand.
* **Manage Models:** Inspect and switch between installed Ollama models on the fly.

### 2. FastAPI REST Server
Start the production-ready HTTP server:

```bash
./alfred serve --port 8000
```
Open **`http://localhost:8000/docs`** in your browser for the interactive Swagger UI.

**Example Query via `curl`:**
```bash
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "What are the main findings in my notes?", "top_k": 4}'
```

**Response:**
```json
{
  "answer": "Based on your notes, the primary conclusions are...",
  "sources": [
    {"file_path": "alfred_docs/my_notes.md", "chunk_index": 0}
  ]
}
```

### 3. Command Line Interface (CLI)

* **Direct Ask:**
  ```bash
  ./alfred ask "Explain the architecture described in my docs"
  ```
* **Live Directory Watcher:**
  ```bash
  ./alfred watch
  ```
* **Directory Locations:**
  ```bash
  ./alfred where
  ```

---

## Running Tests

Alfred ML includes a test suite covering text chunking edge cases, document ingestion, and FastAPI endpoints:

```bash
pytest
```

---

## Project Structure

```
AlfredML/
├── alfred                  # Executable launcher script
├── alfred_ml/              # Core application package
│   ├── chunking.py         # Overlapping text chunker (infinite-loop safe)
│   ├── cli.py              # CLI subcommands & argument parsing
│   ├── config.py           # Dataclass configuration loader
│   ├── ingest.py           # Document parser (.pdf, .md, .py, etc.) & vector indexing
│   ├── llm.py              # Ollama API client & model management
│   ├── rag.py              # Semantic search & prompt synthesis
│   ├── server.py           # FastAPI REST endpoints
│   ├── store.py            # ChromaDB persistent client
│   ├── tui.py              # Rich terminal dashboard
│   └── watch.py            # File system event observer
├── alfred_docs/            # Default indexed document directory
├── pyproject.toml          # Package metadata & build configuration
├── requirements.txt        # Production dependencies
└── tests/                  # Unit and integration test suite
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
