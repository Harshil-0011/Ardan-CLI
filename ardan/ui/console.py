from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
from rich.layout import Layout
import time

class ArdanConsole:
    def __init__(self):
        self.console = Console()

    def print_banner(self):
        banner = """
 █████╗ ██████╗ ██████╗  █████╗ ███╗   ██╗
██╔══██╗██╔══██╗██╔══██╗██╔══██╗████╗  ██║
███████║██████╔╝██║  ██║███████║██╔██╗ ██║
██╔══██║██╔══██╗██║  ██║██╔══██║██║╚██╗██║
██║  ██║██║  ██║██████╔╝██║  ██║██║ ╚████║
╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝
    THE WORLD'S MOST POWERFUL CODING AGENT
        """
        self.console.print(Panel(banner, style="bold cyan"))

    def print_provider_badge(self, provider: str, model: str):
        colors = {
            "anthropic": "orange1",
            "google": "blue",
            "openai": "green",
            "mistral": "purple",
            "groq": "yellow",
            "openrouter": "cyan",
            "ollama": "white"
        }
        color = colors.get(provider.lower(), "white")
        local_badge = " [LOCAL]" if provider == "ollama" else ""
        self.console.print(f"[bold {color}]● {provider.upper()}[/bold {color}] ({model}){local_badge}")
        self.console.print("Tips for getting started:")
        self.console.print("1. Ask questions, edit files, or run commands.")
        self.console.print("2. Use [bold magenta]@path/to/file[/bold magenta] to include file content in context.")
        self.console.print("3. Type [bold cyan]/help[/bold cyan] for more information.\n")

    def show_spinner(self, message: str):
        return self.console.status(message)

    def display_plan(self, plan: list):
        table = Table(title="Execution Plan")
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Tool Hint", style="magenta")
        table.add_column("Depends On", style="yellow")

        for step in plan:
            table.add_row(
                str(step.get("id")),
                step.get("description"),
                step.get("tool_hint"),
                ", ".join(map(str, step.get("depends_on", [])))
            )
        self.console.print(table)

    def print_step_start(self, step: dict):
        self.console.print(Panel(f"Step {step.get('id')}: {step.get('description')}", border_style="yellow"))

    def print_step_complete(self, step: dict):
        self.console.print(f"[green]✔ Step {step.get('id')} complete[/green]")

    def print_progress(self, chunk: str):
        self.console.print(chunk, end="")

    def print_error(self, message: str):
        self.console.print(f"[red]ERROR: {message}[/red]")

    def print_success(self, message: str):
        self.console.print(f"[green]SUCCESS: {message}[/green]")

    def make_footer(self, workspace: str, model: str, steps: int = 0, provider: str = "ollama"):
        provider_colors = {
            "anthropic": "orange1",
            "google": "blue",
            "openai": "green",
            "mistral": "purple",
            "groq": "yellow",
            "openrouter": "cyan",
            "ollama": "white"
        }
        color = provider_colors.get(provider.lower(), "white")
        badge = f"[{color}]●[/{color}] [bold]{provider.upper()}[/bold]"

        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right", ratio=1)

        grid.add_row(
            f" {badge} | [bold cyan]Workspace:[/bold cyan] {workspace} | [bold yellow]Model:[/bold yellow] {model}",
            f"[bold magenta]Steps:[/bold magenta] {steps} | [bold red]Sandbox:[/bold red] no sandbox (see /docs)"
        )
        return Panel(grid, style="white on blue")

    def display_summary(self, update_data: dict):
        stats = update_data.get("stats", {})
        table = Table(title="Project Summary", border_style="bold green")
        table.add_column("Category", style="cyan")
        table.add_column("Count", style="white")
        table.add_column("Details", style="magenta")

        table.add_row("Files Created", str(len(stats.get("files_created", []))), ", ".join(stats.get("files_created", [])))
        table.add_row("Commands Run", str(len(stats.get("commands_run", []))), "")
        table.add_row("Confidence", f"{update_data.get('confidence', 0)*100}%", "")

        self.console.print(table)

        if update_data.get("suggestions"):
             self.console.print(Panel("\n".join([f"• {s}" for s in update_data["suggestions"]]), title="Proactive Suggestions", border_style="cyan"))
