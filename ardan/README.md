# Ardan: Autonomous Coding Agent CLI

Ardan is a powerful, local-first coding agent that leverages [Ollama](https://ollama.com/) to build complete software systems from simple natural language prompts. It handles the entire lifecycle: planning, execution, and review, all while keeping you in the loop with a beautiful, real-time terminal interface.

---

## 🚀 Key Features

-   **🧠 Autonomous Problem Solving**: Uses a ReAct (Reasoning + Acting) loop to break down complex tasks into actionable steps.
-   **🔌 Deep Tool Integration**: Can read/write files, execute shell commands, lint/format code, and search the web.
-   **🔌 MCP Support**: Extend capabilities with Model Context Protocol (MCP) servers.
-   **🏠 100% Local & Private**: Powered by Ollama. Your code never leaves your machine. No API keys, no subscriptions.
-   **✨ Rich Terminal UI**: Experience real-time progress with syntax-highlighted code previews, spinners, and task tables.
-   **♻️ Self-Correction**: Includes a reviewer phase that identifies bugs and missing features, triggering an automatic fix cycle.
-   **📂 Context Management**: Automatically summarizes long history to maintain coherence within LLM context windows.

---

## 🏛️ Project Architecture

Ardan is built with a modular, extensible architecture:

-   `agent/`: The brain. Orchestrates the **Planner**, **Executor**, **Reviewer**, and **Memory** modules.
-   `tools/`: The hands. A growing collection of specialized utilities:
    -   `file_tools`: Robust file operations (read, write, append, search/replace).
    -   `shell_tools`: Secure command execution and temporary script running.
    -   `code_tools`: Python-specific linting (ruff/py_compile) and formatting (black).
    -   `web_tools`: Real-time web search via DuckDuckGo scraping (no API needed).
-   `ollama/`: The bridge. Handles communication with your local Ollama instance with streaming and retry logic.
-   `ui/`: The face. A `rich`-powered console interface for a professional CLI experience.
-   `config/`: The control center. Manage models, workspaces, and agent behavior via `config.yaml` or env vars.

---

## 🛠️ Installation

1.  **Prerequisites**:
    -   Python 3.11+
    -   [Ollama](https://ollama.com/) installed and running.
2.  **Clone and Install**:
    ```bash
    git clone https://github.com/yourusername/ardan.git
    cd ardan
    pip install -e .
    ```
3.  **Pull the Recommended Model**:
    ```bash
    ollama pull codellama:13b
    ```

---

## 📖 Usage Examples

### Build a Full-Stack Application
```bash
ardan run "Build a FastAPI backend with SQLite and JWT auth, plus a React frontend with Tailwind CSS. Include a docker-compose.yml to run both."
```

### Create a CLI Tool
```bash
ardan run "Create a Python CLI tool that monitors a folder and auto-compresses new images using Pillow. Add a --verbose flag."
```

### override Defaults
```bash
# Use a different model
ardan run "Build a simple snake game in Python" --model llama3

# specify a custom workspace
ardan run "Create a web scraper for news sites" --workspace ./my-scrapers

# Fully autonomous mode (skip confirmations)
ardan run "Refactor the current project to use async/await" --auto
```

### Interactive Chat Mode
Ardan features a powerful interactive REPL built with `prompt_toolkit`:
```bash
ardan chat
```
- **Slash Commands**: `/help`, `/clear`, `/save`, `/load`, `/rewind`, `/stats`, `/plan`, `/exit`.
- **Autocompletion**: Tab-complete commands and file paths.
- **Context Injection**: Use `@path/to/file` or `@path/to/image.png` directly in your chat.
- **Checkpointing**: Save and resume complex sessions.

### Plan Mode
Break down complex tasks and execute them systematically:
```bash
> /plan "Implement a distributed task queue with Redis and Python"
```

---

## 🔧 Advanced Features

- **Multimodal capabilities**: Ardan can "see" images. Just mention them with `@image.png`.
- **Project Context (ARDAN.md)**: Add a `ARDAN.md` file to your project root to provide persistent, project-specific instructions to the agent.
- **Codebase Investigation**: Ardan can perform deep analysis of your project structure using the `investigate_codebase` tool.
- **Non-Interactive Scripting**: Integrate Ardan into your workflows with `--output-format json` or `stream-json`.

---

## ⚙️ Configuration

Ardan looks for `config.yaml` in its project root. You can also use environment variables:

| Variable | Config Key | Default |
| :--- | :--- | :--- |
| `ARDAN_MODEL` | `ollama.model` | `codellama:13b` |
| `ARDAN_WORKSPACE` | `agent.workspace` | `./ardan-output` |
| `ARDAN_MAX_STEPS` | `agent.max_steps` | `50` |
| `ARDAN_OLLAMA_BASE_URL` | `ollama.base_url` | `http://localhost:11434` |

---

## 🛠️ Adding Custom Tools

Extending Ardan is easy:
1.  Add your function in a new or existing file in `ardan/tools/`.
2.  Ensure it returns a `ToolResult(success: bool, output: str, error: str)`.
3.  Register the tool in `ardan/agent/executor.py` within the `self.tools` dictionary.
4.  Update the `EXECUTOR_SYSTEM` prompt in `ardan/ollama/prompts.py` so the agent knows how to use it.

---

## ❓ Troubleshooting

-   **Ollama Connection Refused**: Ensure Ollama is running (`ollama serve`).
-   **Model Not Found**: Ardan will try to use `codellama:13b` by default. If you don't have it, run `ollama pull codellama:13b` or override it with `--model`.
-   **Tool Failures**: If a command fails (e.g., `ruff` not found), Ardan will attempt to use a fallback or report the error and try a different approach.
