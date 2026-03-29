import typer
import asyncio
from typing import Optional
from ardan.agent.core import AgentCore
from ardan.config.settings import settings
from ardan.ui.console import ArdanConsole
from ardan.config.credentials import credentials_manager
from rich.prompt import Confirm

app = typer.Typer(name="ardan", help="Ardan — a CLI that flows like divine love, dancing in soft light with every command.")
console_ui = ArdanConsole()


@app.command()
def run(
    prompt: str = typer.Argument(..., help="What do you want to build?"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p"),
    model: Optional[str] = typer.Option(None, "--model", "-m"),
    workspace: Optional[str] = typer.Option(None, "--workspace", "-w"),
    auto: bool = typer.Option(False, "--auto"),
    watch: bool = typer.Option(False, "--watch"),
):
    """Main entrypoint for building software systems."""
    agent = AgentCore(
        settings,
        provider_override=provider,
        model_override=model,
        workspace_override=workspace,
    )

    async def _run():
        if watch:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            class BuildHandler(FileSystemEventHandler):
                def __init__(self, agent_instance, prompt_text):
                    self.agent = agent_instance
                    self.prompt = prompt_text

                def on_modified(self, event):
                    if not event.is_directory:
                        typer.echo(
                            f"Change detected in {event.src_path}. Re-building..."
                        )
                        # Trigger non-recursive build logic
                        asyncio.run(self._trigger_build())

                async def _trigger_build(self):
                    async for update in self.agent.build_system(self.prompt):
                        pass

            observer = Observer()
            observer.schedule(
                BuildHandler(agent, prompt), agent.workspace, recursive=True
            )
            observer.start()
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()
            return

        console_ui.print_banner()
        console_ui.print_provider_badge(agent.provider_name, agent.model)

        with console_ui.show_spinner("Building system..."):
            async for update in agent.build_system(prompt, auto=auto):
                status = update.get("status")
                if status == "PLAN_READY":
                    console_ui.display_plan(update["plan"])
                    if not auto and not Confirm.ask("Proceed?"):
                        return
                elif status == "STEP_START":
                    console_ui.print_step_start(update["step"])
                elif status == "STEP_PROGRESS":
                    console_ui.console.print(update["chunk"], end="")
                elif status == "WARNING":
                    console_ui.console.print(update["message"])
                elif status == "DONE":
                    console_ui.print_success(update["message"])
                    console_ui.display_summary(update)
                    console_ui.print_next_steps(agent.workspace)

    asyncio.run(_run())


@app.command()
def chat():
    """Interactive AI developer REPL."""
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import PathCompleter, WordCompleter, MergedCompleter
    from prompt_toolkit.styles import Style

    async def _chat():
        console_ui.print_banner()
        agent = AgentCore(settings)
        console_ui.print_provider_badge(agent.provider_name, agent.model)

        completer = MergedCompleter([
            PathCompleter(),
            WordCompleter(["/exit", "/quit", "/help", "/save", "/load", "/rewind", "/stats", "/plan", "/clear"], ignore_case=True)
        ])

        style = Style.from_dict({
            "prompt": "ansicyan bold",
        })

        session = PromptSession(completer=completer, style=style)

        while True:
            try:
                user_input = await session.prompt_async("ardan > ")
                if not user_input.strip():
                    continue
                if user_input.lower() in ["/exit", "/quit"]:
                    break
                if user_input.lower() == "/help":
                    console_ui.console.print("[bold cyan]Commands:[/bold cyan]")
                    console_ui.console.print("  /exit, /quit - Exit the chat")
                    console_ui.console.print("  /help        - Show this help message")
                    console_ui.console.print("  /clear       - Clear the screen")
                    console_ui.console.print("  /stats       - Show session stats")
                    continue
                if user_input.lower() == "/clear":
                    console_ui.console.clear()
                    continue
                if user_input.lower() == "/stats":
                    console_ui.display_summary({"stats": {"files_created": agent.memory.files_created, "commands_run": agent.memory.commands_run}, "confidence": 1.0})
                    continue

                async for chunk in agent.chat(user_input):
                    console_ui.console.print(chunk, end="")
                console_ui.console.print()
            except KeyboardInterrupt:
                continue
            except EOFError:
                break

    asyncio.run(_chat())


@app.command()
def models(provider: Optional[str] = None, all: bool = False):
    """List available AI models."""

    async def _models():
        if all:
            from ardan.providers.registry import PROVIDERS

            for p_name in PROVIDERS:
                agent = AgentCore(settings, provider_override=p_name)
                models_list = await agent.provider.list_models()
                if models_list:
                    console_ui.display_models_table(p_name, models_list)
        else:
            agent = AgentCore(settings, provider_override=provider)
            try:
                models_list = await agent.provider.list_models()
                if models_list:
                    console_ui.display_models_table(agent.provider_name, models_list)
                else:
                    console_ui.console.print(
                        f"[yellow]No models found for {agent.provider_name}.[/yellow]"
                    )
            except Exception as e:
                console_ui.print_error(f"Failed to list models: {str(e)}")

    asyncio.run(_models())


@app.command()
def keys(
    action: str = typer.Argument(..., help="Action: set, list, remove, test"),
    provider: Optional[str] = typer.Argument(None, help="The AI provider"),
    value: Optional[str] = typer.Option(None, "--value", help="Directly provide the key value"),
):
    """Manage AI provider API keys securely."""
    if action == "set":
        if not provider:
            typer.echo("Error: 'set' requires a provider.")
            raise typer.Exit(1)
        credentials_manager.set(
            provider,
            value or typer.prompt(f"Enter key for {provider}", hide_input=True),
        )
        typer.echo(f"Key for {provider} stored successfully.")
    elif action == "list":
        typer.echo("Stored API Keys (Masked):")
        for p, k in credentials_manager.list_masked().items():
            typer.echo(f"- {p}: {k}")
    elif action == "remove":
        if not provider:
            typer.echo("Error: 'remove' requires a provider.")
            raise typer.Exit(1)
        credentials_manager.remove(provider)
        typer.echo(f"Key for {provider} removed.")
    elif action == "test":
        if not provider:
            typer.echo("Error: 'test' requires a provider.")
            raise typer.Exit(1)

        async def _test():
            agent = AgentCore(settings, provider_override=provider)
            health = await agent.provider.health_check()
            if health.status == "healthy":
                console_ui.print_success(f"{provider} is healthy: {health.message}")
            else:
                console_ui.print_error(f"{provider} check failed: {health.message}")

        asyncio.run(_test())


@app.command()
def recommend(task: str):
    """Recommend the best provider and model for a specific task."""

    async def _rec():
        agent = AgentCore(settings)
        prompt = f"Recommend the best AI provider and model for this task: '{task}'. Consider Anthropic, Google, OpenAI, Mistral, Groq, OpenRouter, and Ollama. Format as a table with columns: Provider, Model, Strength, Cost."
        async for chunk in agent.chat(prompt):
            console_ui.console.print(chunk, end="")
        console_ui.console.print()

    asyncio.run(_rec())


@app.command()
def diff():
    """Show session diff."""
    agent = AgentCore(settings)
    typer.echo(agent.memory.get_diff())


@app.command()
def undo():
    """Undo file changes."""
    agent = AgentCore(settings)
    count = agent.memory.undo_last_run()
    typer.echo(f"Reverted {count} files.")


@app.command()
def resume():
    """Resume the latest session."""
    agent = AgentCore(settings)
    console_ui.print_success(f"Resuming session {agent.memory.session_id}")
    # Transition to chat
    chat()


@app.command()
def explain(file: str):
    """Explain a file's contents."""

    async def _explain():
        agent = AgentCore(settings)
        async for chunk in agent.chat(f"Explain this file: @{file}"):
            console_ui.console.print(chunk, end="")
        console_ui.console.print()

    asyncio.run(_explain())


@app.command()
def improve(file: str):
    """Improve a file's code."""

    async def _improve():
        agent = AgentCore(settings)
        async for update in agent.build_system(f"Improve this file: @{file}"):
            pass

    asyncio.run(_improve())


@app.command()
def test():
    """Run tests for the project."""

    async def _test():
        agent = AgentCore(settings)
        async for update in agent.build_system("Run all tests and fix failures."):
            pass

    asyncio.run(_test())


@app.command()
def config(edit: bool = typer.Option(False, "--edit", "-e")):
    """Show or edit current configuration."""
    if edit:
        config_path = os.path.join(os.getcwd(), "config.yaml")
        if not os.path.exists(config_path):
            typer.echo(f"Config file not found at {config_path}")
            raise typer.Exit(1)
        typer.edit(filename=config_path)
    else:
        typer.echo(settings.config)


@app.command()
def providers():
    """List available providers."""
    from ardan.providers.registry import PROVIDERS

    for p in PROVIDERS:
        typer.echo(f"- {p}")


if __name__ == "__main__":
    app()
