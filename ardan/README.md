# Ardan CLI

Ardan is a fully functional coding agent CLI that uses Ollama as its LLM backend to autonomously build entire software systems from a single prompt.

## Features
- **Autonomous System Building**: From planning to execution and review.
- **Ollama Backend**: Uses local LLMs, no API keys required.
- **Rich Terminal UI**: Beautiful status updates, code highlighting, and progress bars.
- **Comprehensive Toolset**: File operations, shell commands, code linting/formatting, and web search.
- **ReAct Agent Loop**: Reason and Act cycle for complex problem solving.

## Installation

1.  **Prerequisites**:
    - Python 3.11+
    - [Ollama](https://ollama.com/) installed and running.
2.  **Clone and Install**:
    ```bash
    git clone <repository-url>
    cd ardan
    pip install -e .
    ```
3.  **Pull Required Model**:
    ```bash
    ollama pull codellama:13b
    ```

## Usage

### Build a Project
```bash
ardan run "Build a FastAPI app with SQLite, user auth (JWT), and CRUD endpoints for a todo list. Include Dockerfile and tests."
```

### Options
- `--model <model_name>`: Override the default Ollama model.
- `--workspace <path>`: Set the output directory for the project.
- `--auto`: Skip confirmation prompts (fully autonomous mode).
- `--verbose`: Show raw LLM output and tool calls.

### Interactive Mode
```bash
ardan chat
```

### Other Commands
- `ardan models`: List available Ollama models.
- `ardan config`: Show or edit current configuration.

## Troubleshooting

- **Ollama not running**: Ensure Ollama is started (`ollama serve`).
- **Model not found**: Run `ollama pull <model_name>` for the model specified in your config or command.
- **Connection Errors**: Check if Ollama is accessible at `http://localhost:11434`.

## Customization
You can modify `config.yaml` to change default models, workspace directories, and agent behavior.
