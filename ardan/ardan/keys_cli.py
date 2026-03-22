import typer
import os
from ardan.config.credentials import credentials_manager
from ardan.providers.registry import PROVIDERS

app = typer.Typer(name="keys", help="Manage AI provider API keys")

@app.command()
def set(provider: str, api_key: str):
    """Securely store an API key for a provider."""
    if provider.lower() not in PROVIDERS and provider.lower() not in ["anthropic", "google", "openai", "mistral", "groq", "openrouter"]:
        typer.echo(f"Warning: Unknown provider '{provider}'.")

    credentials_manager.set(provider, api_key)
    typer.echo(f"API key for {provider} stored securely.")

@app.command()
def list():
    """List stored API keys (masked)."""
    keys = credentials_manager.list()
    if not keys:
        typer.echo("No API keys stored.")
        return

    typer.echo("Stored API Keys:")
    for p, k in keys.items():
        typer.echo(f"  {p}: {k}")

@app.command()
def remove(provider: str):
    """Remove a stored API key."""
    if credentials_manager.remove(provider):
        typer.echo(f"API key for {provider} removed.")
    else:
        typer.echo(f"No API key found for {provider}.")

@app.command()
def test(provider: str):
    """Test if the API key for a provider is valid."""
    from ardan.agent.core import AgentCore
    from ardan.config.settings import settings

    agent = AgentCore(settings, provider_override=provider)
    health = agent.provider.health_check()
    if health.status == "healthy":
        typer.echo(f"SUCCESS: {provider} is correctly configured and reachable.")
    else:
        typer.echo(f"FAILURE: {health.message}")

if __name__ == "__main__":
    app()
