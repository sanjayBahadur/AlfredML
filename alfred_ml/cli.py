import argparse
import sys
from rich import print

from .config import AlfredConfig
from .ingest import ingest_all
from .rag import ask
from .tui import main_menu
from .watch import watch


def main():
    cfg = AlfredConfig.load()

    p = argparse.ArgumentParser(prog="alfred", description="Alfred ML - Your local RAG assistant")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("ingest", help="Index all documents in alfred_docs")
    sub.add_parser("watch", help="Watch alfred_docs and automatically re-index on change")
    sub.add_parser("chat", help="Launch interactive chat session")

    srv = sub.add_parser("serve", help="Start FastAPI REST API server")
    srv.add_argument("--host", default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    srv.add_argument("--port", type=int, default=8000, help="Port number (default: 8000)")
    srv.add_argument("--reload", action="store_true", help="Enable dev reload mode")

    q = sub.add_parser("ask", help="Ask a single question and print the answer with sources")
    q.add_argument("question", nargs="+", help="Question to ask")

    # If no args, launch TUI
    if len(sys.argv) == 1:
        try:
            main_menu(cfg)
        except KeyboardInterrupt:
            sys.exit(0)
        return

    args = p.parse_args()

    if args.cmd == "ingest":
        stats = ingest_all(cfg)
        print(stats)
    elif args.cmd == "watch":
        print(f"Watching {cfg.docs_dir} for changes…")
        watch(cfg)
    elif args.cmd == "ask":
        question = " ".join(args.question)
        out = ask(cfg, question)
        print("\n[bold]Answer:[/bold]\n", out["answer"])
        print("\n[bold]Sources:[/bold]\n", out["sources"])
    elif args.cmd == "chat":
        from .tui import chat_mode

        try:
            chat_mode(cfg)
        except KeyboardInterrupt:
            pass
    elif args.cmd == "serve":
        import uvicorn

        print(f"[bold green]Starting Alfred ML API server on http://{args.host}:{args.port}[/bold green]")
        print(f"[dim]Interactive API documentation at http://{args.host}:{args.port}/docs[/dim]")
        uvicorn.run("alfred_ml.server:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
