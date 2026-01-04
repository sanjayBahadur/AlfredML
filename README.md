# Alfred ML

Alfred ML is a local RAG (Retrieval-Augmented Generation) CLI tool that uses [Ollama](https://ollama.com/) to answer questions based on your personal documents.

## Prerequisites

1.  **Python 3.10+**
2.  **[Ollama](https://ollama.com/)**: Must be installed and running.
    -   Host: `http://localhost:11434`
    -   Default Model: `llama3.2:1b-instruct-q4_K_M` (can be changed in `alfred_ml/config.py`)

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/alfred-ml.git
    cd alfred-ml
    ```

2.  **Create a virtual environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Alternatively, strictly follow the script's check:*
    ```bash
    pip install chromadb sentence-transformers watchdog rich requests
    ```

## Usage

The project includes a convenience script `./alfred` to manage interactions.

### 1. Ingest Documents
Place your markdown (`.md`) or text (`.txt`) files in the `alfred_docs/` directory.

Then, build the vector database:
```bash
./alfred ingest
```

### 2. Chat
Start an interactive chat session:
```bash
./alfred chat
```

### Other Commands
-   **Ask a single question**: `./alfred ask "What is in the notes?"`
-   **Watch for changes**: `./alfred watch` (auto-reindexes when you add/edit files in `alfred_docs/`)
-   **Help**: `./alfred --help`

## Configuration
You can modify `alfred_ml/config.py` to change:
-   The embedding model
-   The Ollama model (ensure you have pulled the model via `ollama pull <model_name>`)
-   Chunk sizes and overlap

## Troubleshooting
-   **Ollama Connection Error**: Ensure Ollama is running (`systemctl start ollama` or just `ollama serve`).
-   **Model Not Found**: If the configured model isn't found, run `ollama list` to see what you have, and update `alfred_ml/config.py` or `ollama pull` the missing model.
