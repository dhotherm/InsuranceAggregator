#!/usr/bin/env python3
"""
Command-line interface for the Insurance Aggregator PoC.
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agents import InsuranceOrchestrator

console = Console()


def main():
    console.print(Panel.fit(
        "[bold blue]Insurance Aggregator PoC[/bold blue]\n"
        "[dim]AI-powered comparison across Sun Life, Manulife, Canada Life[/dim]",
        border_style="blue"
    ))

    console.print("\n[yellow]Initializing...[/yellow]")
    orchestrator = InsuranceOrchestrator(data_dir="./data")
    console.print("[green]Ready![/green]\n")

    console.print("[dim]Type your questions about insurance. Type 'quit' to exit.[/dim]\n")

    while True:
        try:
            user_input = console.input("[bold cyan]You:[/bold cyan] ")

            if user_input.lower() in ['quit', 'exit', 'q']:
                console.print("\n[yellow]Goodbye![/yellow]")
                break

            if not user_input.strip():
                continue

            console.print("\n[dim]Thinking...[/dim]")

            response = orchestrator.process(user_input)

            console.print("\n[bold green]Assistant:[/bold green]")
            console.print(Markdown(response))
            console.print()

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]\n")


if __name__ == "__main__":
    main()
