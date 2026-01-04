import argparse
from rich import print

from .config import AlfredConfig
from .ingest import ingest_all
from .rag import ask
from .watch import watch

def main():
    cfg = AlfredConfig()

    p = argparse.ArgumentParser(prog="alfred")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("ingest")
    sub.add_parser("watch")

    q = sub.add_parser("ask")
    q.add_argument("question", nargs="+")
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

if __name__ == "__main__":
    main()
