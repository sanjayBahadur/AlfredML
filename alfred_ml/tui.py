import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import print as rprint

from .config import AlfredConfig
from .ingest import ingest_all
from .rag import ask
from .llm import list_models, check_connection

console = Console()

def clear_screen():
    console.clear()

def header():
    console.print(Panel.fit("[bold blue]Alfred ML[/bold blue]\n[italic]Your Local RAG Assistant[/italic]", border_style="blue"))

def manage_models(cfg: AlfredConfig):
    clear_screen()
    header()
    
    rprint(f"\n[bold]Current Model:[/bold] {cfg.ollama_model}")
    rprint(f"[bold]Ollama Host:[/bold]   {cfg.ollama_host}\n")

    if not check_connection(cfg.ollama_host):
        rprint(f"[bold red]Error:[/bold red] Cannot connect to Ollama at {cfg.ollama_host}")
        Prompt.ask("Press Enter to return")
        return

    models = list_models(cfg.ollama_host)
    if not models:
        rprint("[yellow]No models found or error listing models.[/yellow]")
        Prompt.ask("Press Enter to return")
        return

    table = Table(title="Available Models")
    table.add_column("Index", justify="right", style="cyan")
    table.add_column("Model Name", style="magenta")

    for idx, m in enumerate(models):
        table.add_row(str(idx + 1), m)

    console.print(table)

    choice = Prompt.ask("Select model number (or Enter to cancel)", default="")
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(models):
            new_model = models[idx]
            cfg.ollama_model = new_model
            cfg.save()  # Persist change
            rprint(f"[green]Switched to {new_model}![/green]")
        else:
            rprint("[red]Invalid selection[/red]")
    
    Prompt.ask("\nPress Enter to continue")

def sync_docs(cfg: AlfredConfig):
    clear_screen()
    header()
    rprint("\n[bold]Synchronizing Documents...[/bold]")
    stats = ingest_all(cfg)
    
    rprint("\n[bold green]Sync Complete![/bold green]")
    rprint(f"Added Chunks:  {stats['added_chunks']}")
    rprint(f"Skipped Files: {stats['skipped_files']}")
    if "deleted_files" in stats:
        rprint(f"Deleted Files: {stats['deleted_files']}")
    
    Prompt.ask("\nPress Enter to return")

def chat_mode(cfg: AlfredConfig):
    clear_screen()
    header()
    rprint(f"[dim]Model: {cfg.ollama_model} | Type 'exit' to return[/dim]\n")
    
    while True:
        question = Prompt.ask("[bold green]alfred>[/bold green]")
        if question.lower() in ("exit", "quit", ":q"):
            break
        if not question.strip():
            continue
            
        with console.status("[bold green]Thinking...[/bold green]"):
            try:
                out = ask(cfg, question)
                rprint("\n[bold]Answer:[/bold]")
                rprint(out["answer"])
                rprint("\n[dim]Sources:[/dim]")
                for s in out["sources"]:
                    rprint(f"- {s['file_path']} (chunk {s['chunk_index']})")
                rprint()
            except Exception as e:
                rprint(f"[red]Error:[/red] {e}")

def main_menu(cfg: AlfredConfig):
    while True:
        clear_screen()
        header()
        
        rprint(f"\n[dim]Active Model: {cfg.ollama_model}[/dim]\n")
        
        rprint("1. [bold green]Chat[/bold green]")
        rprint("2. [bold cyan]Sync Documents[/bold cyan]")
        rprint("3. [bold magenta]Manage Models[/bold magenta]")
        rprint("4. [bold red]Exit[/bold red]")
        
        choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4"], default="1")
        
        if choice == "1":
            chat_mode(cfg)
        elif choice == "2":
            sync_docs(cfg)
        elif choice == "3":
            manage_models(cfg)
        elif choice == "4":
            rprint("Goodbye!")
            sys.exit(0)
