import typer
import os
from typing import Optional
from rich.prompt import Confirm
from ardan.agent.core import AgentCore
from ardan.config.settings import settings
from ardan.ui.console import ArdanConsole

app = typer.Typer(name="ardan", help="Autonomous Coding Agent CLI")
console_ui = ArdanConsole()

@app.command()
def run(
    prompt: str = typer.Argument(..., help="The description of the system you want to build"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override the default Ollama model"),
    workspace: Optional[str] = typer.Option(None, "--workspace", "-w", help="Set the output directory"),
    auto: bool = typer.Option(False, "--auto", help="Skip confirmation prompts"),
    verbose: bool = typer.Option(False, "--verbose", help="Show raw LLM output and tool calls")
):
    """Main command to build an entire software system from a single prompt."""
    console_ui.print_banner()
    agent = AgentCore(settings, model_override=model, workspace_override=workspace)

    with console_ui.show_spinner("Initializing..."):
        builder = agent.build_system(prompt, auto=auto)

    for update in builder:
        status = update.get("status")

        if status == "PLAN_READY":
            plan = update.get("plan")
            console_ui.display_plan(plan)
            if not auto:
                if not Confirm.ask("Do you want to proceed with this plan?"):
                    typer.echo("Aborted.")
                    raise typer.Exit()

        elif status == "STEP_START":
            console_ui.print_step_start(update.get("step"))

        elif status == "STEP_PROGRESS":
            if verbose:
                console_ui.print_progress(update.get("chunk"))

        elif status == "STEP_COMPLETE":
            console_ui.print_step_complete(update.get("step"))

        elif status == "DONE":
            console_ui.print_success(update.get("message"))
            console_ui.display_summary(update.get("stats"))

        elif status in ["PLANNING", "EXECUTING", "REVIEWING"]:
             # Spinner updates could go here
             pass

@app.command()
def chat():
    """Interactive REPL mode with the agent."""
    console_ui.print_banner()
    agent = AgentCore(settings)
    typer.echo("Entering interactive chat mode. Type 'exit' to quit.")

    while True:
        user_input = typer.prompt("You")
        if user_input.lower() in ["exit", "quit"]:
            break

        typer.echo("Ardan: ", nl=False)
        for chunk in agent.chat(user_input):
             typer.echo(chunk, nl=False)
        typer.echo()

@app.command()
def models():
    """List available Ollama models."""
    agent = AgentCore(settings)
    try:
        models = agent.client.list_models()
        table = typer.echo("Available Ollama Models:")
        for model in models:
            typer.echo(f"- {model['name']}")
    except Exception as e:
        console_ui.print_error(f"Failed to list models: {str(e)}")

@app.command()
def config():
    """Show current config."""
    typer.echo("Current Configuration:")
    for section, values in settings.config.items():
        typer.echo(f"[{section}]")
        for k, v in values.items():
            typer.echo(f"  {k}: {v}")

if __name__ == "__main__":
    app()
