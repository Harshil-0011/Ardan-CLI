from rich.console import Console
from rich.panel import Panel
from rich.table import Table


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
Ardan — a CLI that flows like divine love,
dancing in soft light with every command.
        """
        self.console.print(Panel(banner, style="bold light_cyan3"))

    def print_provider_badge(self, provider: str, model: str):
        colors = {
            "anthropic": "orange1",
            "google": "dodger_blue1",
            "openai": "spring_green2",
            "mistral": "medium_purple1",
            "groq": "wheat1",
            "openrouter": "light_cyan3",
            "ollama": "grey70",
        }
        color = colors.get(provider.lower(), "grey70")
        local_badge = " [LOCAL]" if provider == "ollama" else ""
        self.console.print(
            f"[bold {color}]● {provider.upper()}[/bold {color}] ({model}){local_badge}"
        )
        self.console.print("Tips for getting started:")
        self.console.print("1. Ask questions, edit files, or run commands.")
        self.console.print(
            "2. Use [bold magenta]@path/to/file[/bold magenta] to include file content in context."
        )
        self.console.print(
            "3. Type [bold cyan]/help[/bold cyan] for more information.\n"
        )

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
                ", ".join(map(str, step.get("depends_on", []))),
            )
        self.console.print(table)

    def print_step_start(self, step: dict):
        self.console.print(
            Panel(
                f"Step {step.get('id')}: {step.get('description')}",
                border_style="yellow",
            )
        )

    def print_step_complete(self, step: dict):
        self.console.print(f"[green]✔ Step {step.get('id')} complete[/green]")

    def print_progress(self, chunk: str):
        self.console.print(chunk, end="")

    def print_error(self, message: str):
        self.console.print(f"[red]ERROR: {message}[/red]")

    def print_success(self, message: str):
        self.console.print(f"[green]SUCCESS: {message}[/green]")

    def make_footer(
        self, workspace: str, model: str, steps: int = 0, provider: str = "ollama"
    ):
        provider_colors = {
            "anthropic": "orange1",
            "google": "blue",
            "openai": "green",
            "mistral": "purple",
            "groq": "yellow",
            "openrouter": "cyan",
            "ollama": "white",
        }
        color = provider_colors.get(provider.lower(), "white")
        badge = f"[{color}]●[/{color}] [bold]{provider.upper()}[/bold]"

        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right", ratio=1)

        grid.add_row(
            f" {badge} | [bold cyan]Workspace:[/bold cyan] {workspace} | [bold yellow]Model:[/bold yellow] {model}",
            f"[bold magenta]Steps:[/bold magenta] {steps} | [bold red]Sandbox:[/bold red] no sandbox (see /docs)",
        )
        return Panel(grid, style="white on blue")

    def display_summary(self, update_data: dict):
        stats = update_data.get("stats", {})
        table = Table(title="Project Summary", border_style="bold green")
        table.add_column("Category", style="cyan")
        table.add_column("Count", style="white")
        table.add_column("Details", style="magenta")

        table.add_row(
            "Files Created",
            str(len(stats.get("files_created", []))),
            ", ".join(stats.get("files_created", [])),
        )
        table.add_row("Commands Run", str(len(stats.get("commands_run", []))), "")
        table.add_row("Confidence", f"{update_data.get('confidence', 0)*100}%", "")

        self.console.print(table)

        if update_data.get("suggestions"):
            self.console.print(
                Panel(
                    "\n".join([f"• {s}" for s in update_data["suggestions"]]),
                    title="Proactive Suggestions",
                    border_style="cyan",
                )
            )

    def display_models_table(self, provider: str, models: list):
        """Displays a formatted table of available models."""
        table = Table(
            title=f"Available Models for [bold]{provider.upper()}[/bold]",
            border_style="bright_blue",
        )
        table.add_column("Model ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Context", justify="right", style="magenta")
        table.add_column("Strength", style="italic yellow")

        for m in models:
            table.add_row(
                m.id,
                m.name,
                f"{m.context_window:,}" if m.context_window else "N/A",
                m.strength or "",
            )
        self.console.print(table)

    def print_next_steps(self, workspace: str):
        """Prints a friendly 'Next Steps' panel to guide the user."""
        next_steps = f"""
[bold green]Build complete![/bold green] What's next?

1. [bold cyan]Inspect:[/bold cyan] Check the generated files in [magenta]{workspace}[/magenta]
2. [bold cyan]Test:[/bold cyan] Run [white]ardan test[/white] to verify functionality
3. [bold cyan]Iterate:[/bold cyan] Use [white]ardan chat[/white] to refine the codebase
4. [bold cyan]Learn:[/bold cyan] Run [white]ardan explain <file>[/white] to understand any module
        """
        self.console.print(
            Panel(
                next_steps.strip(),
                title="🚀 [bold white]NEXT STEPS[/bold white]",
                border_style="bright_blue",
            )
        )
