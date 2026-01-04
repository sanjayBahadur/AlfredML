# Alfred ML

Alfred ML is your local, privacy-focused RAG (Retrieval-Augmented Generation) assistant. It uses [Ollama](https://ollama.com/) to analyze your personal documents and answer questions about them, all running offline on your machine.

## Prerequisites

Before setting up Alfred ML, ensure you have the following installed:

1.  **Python 3.10 or higher**
2.  **[Ollama](https://ollama.com/)**: This powers the LLM backend.
    -   **Install**: Follow instructions at [ollama.com](https://ollama.com/).
    -   **Run**: Ensure Ollama is running (`ollama serve`).
    -   **Model**: Alfred uses `llama3.2:1b-instruct-q4_K_M` by default. You can pull it via:
        ```bash
        ollama pull llama3.2:1b-instruct-q4_K_M
        ```
    *(Note: You can switch models later within the application)*

## Setup Guide

Follow these steps to set up the project on your local machine.

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/alfred-ml.git
cd alfred-ml
```

### 2. Set Up Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

```bash
# Create the virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate
# On Windows, use: .venv\Scripts\activate
```

### 3. Install Dependencies
Install the required Python packages.

```bash
pip install -r requirements.txt
```

### 4. Organize Your Documents
The repository includes an `alfred_docs/` directory. This is where you put the documents you want Alfred to read.

-   **Action**: Copy your `.md` (Markdown) or `.txt` (Text) files into `alfred_docs/`.
-   **Note**: This directory is tracked (or you may choose to gitignore it if you fork the repo). By default, it may contain sample files. Feel free to remove them.

## Usage

Alfred comes with a convenient wrapper script `./alfred`.

### Interactive Mode (Recommended)
Simply run the script to launch the visual interface (TUI):

```bash
./alfred
```

From here, you can:
-   **Chat**: Interactively ask questions about your documents.
-   **Sync Documents**: Index new or changed files in `alfred_docs/`.
-   **Manage Models**: Switch between available Ollama models.

### Command Line Interface
You can also run specific commands directly:

-   **Ingest/Sync**: Manually trigger the indexing process.
    ```bash
    ./alfred ingest
    ```
-   **Quick Ask**: Ask a single question without entering interactive mode.
    ```bash
    ./alfred ask "What is the summary of project X?"
    ```
-   **Watch**: Automatically sync whenever you save a file in `alfred_docs/`.
    ```bash
    ./alfred watch
    ```

## Configuration

Settings are stored in `alfred_config.json`. This file is automatically created when you change settings (like the model) in the TUI. You can also manually edit `alfred_ml/config.py` to change defaults.

## Files to Know
-   `alfred_docs/`: Drop your documents here.
-   `alfred_db/`: This directory is created automatically to store the vector database. **Do not commit this to version control.** (It is already in `.gitignore`).
-   `.venv/`: Your Python environment. (Ignored by `.gitignore`).

## Troubleshooting

-   **"Ollama isn't reachable"**: Make sure the Ollama server is running (usually on port 11434).
-   **"No module named..."**: Ensure you activated your virtual environment (`source .venv/bin/activate`) and installed requirements.
