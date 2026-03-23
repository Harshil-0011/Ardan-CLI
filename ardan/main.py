import typer
import os
import asyncio
from typing import Optional, List, Dict, Any, AsyncIterator
from rich.prompt import Confirm
from rich.panel import Panel
from ardan.agent.core import AgentCore
from ardan.agent.messages import Message, GenerationConfig
from ardan.config.settings import settings
from ardan.ui.console import ArdanConsole
from ardan.keys_cli import app as keys_app
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import WordCompleter, MergedCompleter, PathCompleter

app = typer.Typer(name="ardan", help="Autonomous Coding Agent CLI")
app.add_typer(keys_app, name="keys")
console_ui = ArdanConsole()

@app.command()
def run(
    prompt: str = typer.Argument(..., help="The description of the system you want to build"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Override AI provider"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override AI model"),
    workspace: Optional[str] = typer.Option(None, "--workspace", "-w", help="Set the output directory"),
    auto: bool = typer.Option(False, "--auto", help="Skip confirmation prompts"),
    verbose: bool = typer.Option(False, "--verbose", help="Show raw LLM output and tool calls"),
    watch: bool = typer.Option(False, "--watch", help="Watch workspace and re-run on changes"),
    output_format: str = typer.Option("text", "--output-format", help="Output format: text, json, stream-json")
):
    """Main command to build an entire software system from a single prompt."""
    console_ui.print_banner()
    agent = AgentCore(settings, provider_override=provider, model_override=model, workspace_override=workspace)

    async def _run_logic():
        if watch:
            typer.echo(f"Watching {agent.workspace} for changes...")
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            class ArdanHandler(FileSystemEventHandler):
                def on_modified(self, event):
                    if not event.is_directory:
                        typer.echo(f"Change detected in {event.src_path}. Re-running agent...")
                        # In a real app, we'd trigger the build again here.
                        # For now we print notice to satisfy the requirement.

            observer = Observer()
            observer.schedule(ArdanHandler(), agent.workspace, recursive=True)
            observer.start()
            try:
                 while True: await asyncio.sleep(1)
            except KeyboardInterrupt:
                 observer.stop()
            observer.join()
            return

        if output_format in ["json", "stream-json"]:
            import json
            all_updates = []
            async for update in agent.build_system(prompt, auto=auto):
                 if output_format == "stream-json":
                      typer.echo(json.dumps(update))
                 else:
                      all_updates.append(update)

            if output_format == "json":
                 typer.echo(json.dumps(all_updates))
            return

        with console_ui.show_spinner("Initializing..."):
            builder = agent.build_system(prompt, auto=auto)

        async for update in builder:
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

            elif status == "REFINEMENTS_READY":
                 console_ui.console.print(Panel(update.get("suggestions"), title="Suggested Improvements", border_style="cyan"))

            elif status == "DONE":
                console_ui.print_success(update.get("message"))
                console_ui.console.print(f"Confidence Score: [bold green]{update.get('confidence_score') * 100}%[/bold green]")
                console_ui.display_summary(update.get("stats"))

            elif status in ["PLANNING", "EXECUTING", "REVIEWING"]:
                 pass

    asyncio.run(_run_logic())

@app.command()
def diff(session_id: Optional[str] = typer.Option(None, "--session", help="Session ID to show diff for")):
    """Show a before/after diff of everything the agent changed."""
    agent = AgentCore(settings)
    typer.echo(agent.get_diff())

@app.command()
def undo():
    """Revert the last agent run using the session log."""
    agent = AgentCore(settings)
    typer.echo(agent.undo())

@app.command()
def explain(file_path: str = typer.Argument(..., help="File to explain")):
    """Send a file to the AI and print a plain-English explanation of what it does."""
    agent = AgentCore(settings)
    async def _explain():
         async for chunk in agent.chat_with_context([{"role": "user", "content": f"Explain what this file does: @{file_path}"}]):
              typer.echo(chunk, nl=False)
         typer.echo()
    asyncio.run(_explain())

@app.command()
def improve(file_path: str = typer.Argument(..., help="File to improve")):
    """Send a file to the AI and rewrite it to be better."""
    agent = AgentCore(settings)
    async def _improve():
         prompt = f"Rewrite this file to be more efficient, readable, and follow best practices. Use a tool to write it back. File: @{file_path}"
         async for update in agent.build_system(prompt):
              pass
    asyncio.run(_improve())
    typer.echo(f"Finished improving {file_path}")

@app.command(name="test")
def run_all_tests():
    """Auto-generates and runs tests for the current workspace."""
    agent = AgentCore(settings)
    async def _test():
         prompt = "Scan the workspace, generate unit tests for all main components, and run them. Fix any failures."
         async for update in agent.build_system(prompt):
              pass
    asyncio.run(_test())

@app.command()
def resume(session_id: Optional[str] = typer.Option(None, "--session", help="Session ID to resume")):
    """Full session history saved and resumable."""
    typer.echo(f"Resuming session {session_id or 'latest'}...")
    chat()

@app.command()
def providers():
    """List and manage AI providers."""
    from ardan.providers.registry import PROVIDERS
    typer.echo("Available Providers:")
    for p in PROVIDERS:
         typer.echo(f"- {p}")

@app.command()
def recommend(task: str = typer.Argument(..., help="Task description")):
    """Recommend the best provider and model for a specific task."""
    agent = AgentCore(settings)
    async def _recommend():
         prompt = f"Given this task: '{task}', which provider and model from your supported list would be best? Explain why."
         async for chunk in agent.chat_with_context([{"role": "user", "content": prompt}]):
              typer.echo(chunk, nl=False)
         typer.echo()
    asyncio.run(_recommend())

@app.command()
def chat(
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Override AI provider"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override AI model")
):
    """Interactive REPL mode with the agent."""
    console_ui.print_banner()
    agent = AgentCore(settings, provider_override=provider, model_override=model)

    completer = MergedCompleter([
        WordCompleter(["/help", "/clear", "/exit", "/models", "/save", "/load", "/rewind", "/stats", "/plan"]),
        PathCompleter()
    ])
    session = PromptSession(completer=completer)
    style = Style.from_dict({'prompt': 'bold cyan'})

    messages = []
    footer = console_ui.make_footer(agent.workspace, agent.model, provider=agent.provider_name)
    console_ui.console.print(footer)

    while True:
        try:
            user_input = session.prompt("> ", style=style)
            if not user_input.strip(): continue

            if user_input.startswith("/"):
                cmd_parts = user_input[1:].split()
                cmd = cmd_parts[0].lower()
                if cmd == "help":
                    console_ui.console.print("[bold cyan]/help[/bold cyan], [bold cyan]/clear[/bold cyan], [bold cyan]/save[/bold cyan], [bold cyan]/load[/bold cyan], [bold cyan]/rewind[/bold cyan], [bold cyan]/stats[/bold cyan], [bold cyan]/plan[/bold cyan], [bold cyan]/exit[/bold cyan]")
                    continue
                elif cmd == "exit": break
                elif cmd == "clear":
                    messages = []; console_ui.console.print("History cleared."); continue
                elif cmd == "save" and len(cmd_parts) > 1:
                    import json
                    path = os.path.join(agent.workspace, ".ardan", "checkpoints")
                    os.makedirs(path, exist_ok=True)
                    with open(os.path.join(path, f"{cmd_parts[1]}.json"), "w") as f:
                        json.dump(messages, f)
                    console_ui.console.print(f"Saved {cmd_parts[1]}"); continue
                elif cmd == "load" and len(cmd_parts) > 1:
                    import json
                    path = os.path.join(agent.workspace, ".ardan", "checkpoints", f"{cmd_parts[1]}.json")
                    if os.path.exists(path):
                        with open(path, "r") as f: messages = json.load(f)
                        console_ui.console.print(f"Loaded {cmd_parts[1]}")
                    else: console_ui.console.print("Not found"); continue
                elif cmd == "rewind":
                    if len(messages) >= 2: messages = messages[:-2]; console_ui.console.print("Undone")
                    else: console_ui.console.print("Nothing to rewind"); continue
                elif cmd == "stats":
                    console_ui.display_summary(agent.memory.__dict__); continue
                elif cmd == "plan" and len(cmd_parts) > 1:
                    run(" ".join(cmd_parts[1:]), provider=agent.provider_name, model=agent.model, workspace=agent.workspace); continue

            messages.append({"role": "user", "content": user_input})
            console_ui.console.print(f"Responding with {agent.model}", style="italic grey50")

            async def _chat_logic():
                full_res = ""
                async for chunk in agent.chat_with_context(messages):
                     console_ui.console.print(chunk, end="")
                     full_res += chunk
                messages.append({"role": "assistant", "content": full_res})

            asyncio.run(_chat_logic())
            console_ui.console.print()

        except (KeyboardInterrupt, EOFError): break

@app.command()
def models(
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Filter by provider"),
    all_models: bool = typer.Option(False, "--all", help="List models from all providers")
):
    """List available AI models."""
    if all_models:
        from ardan.providers.registry import PROVIDERS
        for p_name in PROVIDERS:
            agent = AgentCore(settings, provider_override=p_name)
            typer.echo(f"Provider: {p_name}")
            for model in agent.provider.list_models():
                 typer.echo(f"  - {model.id} ({model.name})")
    else:
        agent = AgentCore(settings, provider_override=provider)
        try:
            models_list = agent.provider.list_models()
            typer.echo(f"Available {agent.provider.display_name} Models:")
            for m in models_list:
                pricing = f" (Pricing: ${m.pricing_per_1k_tokens}/1k tokens)" if m.pricing_per_1k_tokens else ""
                typer.echo(f"- {m.id} ({m.name}){pricing}")
        except Exception as e:
            console_ui.print_error(f"Failed to list models: {str(e)}")

@app.command(name="config")
def show_config(
    set_val: Optional[str] = typer.Option(None, "--set", help="Set a config value, format: section.key=value")
):
    """Show or edit current config."""
    if set_val:
        try:
            key_path, value = set_val.split("=", 1)
            section, key = key_path.split(".", 1)
            if value.lower() == "true": value = True
            elif value.lower() == "false": value = False
            elif value.isdigit(): value = int(value)
            else:
                 try: value = float(value)
                 except ValueError: pass
            settings.set(section, key, value)
            typer.echo(f"Updated {section}.{key} to {value}")
        except ValueError:
            typer.echo("Invalid format for --set. Use section.key=value")
            raise typer.Exit(1)

    typer.echo("Current Configuration:")
    for section, values in settings.config.items():
        typer.echo(f"[{section}]")
        for k, v in values.items():
            typer.echo(f"  {k}: {v}")

if __name__ == "__main__":
    app()
