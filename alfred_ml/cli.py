import argparse
import sys
from rich import print

from .config import AlfredConfig
from .ingest import ingest_all
from .rag import ask
from .watch import watch
from .tui import main_menu

def main():
    cfg = AlfredConfig.load()

    p = argparse.ArgumentParser(prog="alfred")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("ingest")
    sub.add_parser("watch")
    sub.add_parser("chat") # Legacy chat command, now aliases to TUI or simple mode?
                           # Let's keep it but maybe it just launches TUI too or specific chat mode?
                           # Current user request implies "more visual cli interface", so default should be TUI.

    q = sub.add_parser("ask")
    q.add_argument("question", nargs="+")
    
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
        # Launch TUI's chat mode directly? Or main menu?
        # Let's launch main menu for consistent experience, or TUI chat mode
        from .tui import chat_mode
        try:
            chat_mode(cfg)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
