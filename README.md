# 🤖 Ardan — a CLI that flows like divine love, dancing in soft light with every command.

Ardan is a soulful, multi-provider autonomous coding agent that lives in your terminal. It combines master-level reasoning from the world's best LLMs with a high-fidelity developer toolset to build entire software systems from a single prompt.

---

## ⚡ Ardan Terminal Demo

```text
 █████╗ ██████╗ ██████╗  █████╗ ███╗   ██╗
██╔══██╗██╔══██╗██╔══██╗██╔══██╗████╗  ██║
███████║██████╔╝██║  ██║███████║██╔██╗ ██║
██╔══██║██╔══██╗██║  ██║██╔══██║██║╚██╗██║
██║  ██║██║  ██║██████╔╝██║  ██║██║ ╚████║
╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝
Ardan — a CLI that flows like divine love,
dancing in soft light with every command.

 ● ANTHROPIC (claude-sonnet-4-6)

Tips for getting started:
1. Ask questions, edit files, or run commands.
2. Use @path/to/file to include file content in context.
3. Type /help for more information.

> ardan run "Build a FastAPI app with JWT auth and SQLite. Include a Dockerfile."

⠋ [bold yellow]Analyzing request...[/bold yellow]

┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ ID ┃ Description                                                ┃ Tool Hint        ┃ Depends On ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│  1 │ Initialize project structure and requirements.txt          │ write_file       │            │
│  2 │ Create core FastAPI application logic in main.py           │ write_file       │ 1          │
│  3 │ Implement JWT authentication and user routes               │ write_file       │ 2          │
│  4 │ Configure SQLite database and models                       │ write_file       │ 3          │
│  5 │ Generate a production-ready Dockerfile                     │ docker_tools     │ 4          │
│  6 │ Run initial unit tests                                     │ test_tools       │ 5          │
└────┴━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┴━━━━━━━━━━━━━━━━━━┴━━━━━━━━━━━━┘

Proceed? [y/N]: y

[Ardan] Initiating execution...

Step 1: Initialize project structure...
[green]✔[/green] Created requirements.txt

Step 2: Writing main.py...
[blue]Writing to main.py[/blue]
[white]1 from fastapi import FastAPI[/white]
[white]2 app = FastAPI()[/white]
...
[green]✔ Step 2 complete[/green]

[Ardan] Performing senior code review...
[blue]Observation:[/blue] Found missing error handling in auth routes. Fix suggested.

⠋ [bold green]Applying corrections...[/bold green]
[green]✔ Auth logic hardened[/green]

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Category         ┃ Details                                              ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Files Created    │ main.py, auth.py, db.py, Dockerfile, requirements.txt│
│ Commands Run     │ pip install, git init                                │
│ Confidence       │ 96%                                                  │
└━━━━━━━━━━━━━━━━━━┴━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┘

🚀 [bold white]NEXT STEPS[/bold white]
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 1. Inspect: Check generated files in ./ardan-output                    ┃
┃ 2. Test: Run 'ardan test' to verify functionality                      ┃
┃ 3. Iterate: Use 'ardan chat' to refine the codebase                    ┃
┃ 4. Learn: Run 'ardan explain main.py' to understand the architecture   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## 🚀 Why Ardan Beats Every Competitor

Ardan was built to solve the limitations of existing coding agents. It doesn't just generate code; it **engineers systems**.

-   **🧠 Multi-Provider Intelligence**: Native support for **Anthropic (Claude 4.6)**, **OpenAI (GPT-4.1)**, **Google (Gemini 2.5)**, **Mistral**, **Groq**, and **OpenRouter**. Ardan dynamically failover between providers if one is rate-limited.
-   **⚡ Extreme Efficiency**: Parallel tool execution for independent tasks and real-time **Tokens-Per-Second (TPS)** metrics for Groq.
-   **🔌 Professional Toolset**:
    -   **Git**: Full repo lifecycle (init, commit, branch, auto-commit messages).
    -   **Docker**: Intelligent Dockerfile and Compose generation + build/run cycles.
    -   **Performance**: Native **C/C++ compilation** (gcc/g++) and execution for high-speed modules.
    -   **Quality**: Automated dependency scanning, auto-installation, and AI-driven unit test generation.
-   **🛡️ Industrial Security**: Your API keys are **AES-encrypted at rest** using a unique key derived from your hardware. We never store keys in plaintext.
-   **✨ Master-Level ReAct Loop**: Every build includes a **senior reviewer pass** for self-correction and a **proactive suggestion** phase for future iterations.

---

## 🧠 How It Works: The Ardan Cycle

Ardan doesn't just "guess" code. It follows a rigorous engineering cycle designed for accuracy and reliability:

1.  **Plan**: The agent breaks your prompt into a dependency-aware graph of atomic tasks.
2.  **Execute**: Tasks are executed using the most appropriate tools. Independent tasks are run in **parallel** to minimize wait time.
3.  **Observe**: Every tool output (shell logs, file content, web summaries) is fed back into the agent's context.
4.  **Auto-Fix**: If a command fails or a linter catches an error, Ardan analyzes the failure and immediately attempts a fix.
5.  **Review**: A second "Senior Developer" instance of the AI reviews the entire workspace to ensure consistency, security, and performance.
6.  **Refine**: Ardan suggests three high-value follow-up tasks to take your project to the next level.

---

## 🛠️ Provider Matrix

| Provider | Recommended Model | Best For... | Real-time Speed |
| :--- | :--- | :--- | :--- |
| **Anthropic** | `claude-sonnet-4-6` | Master-level reasoning | High |
| **OpenAI** | `gpt-4.1` | Best tool-use accuracy | High |
| **Google** | `gemini-2.5-pro` | Massive context (1M+ tokens) | High |
| **Groq** | `llama-3.3-70b` | Extreme inference performance | **ELITE (500+ TPS)** |
| **Mistral** | `codestral-latest` | Dedicated code generation | High |
| **Ollama** | `codellama:13b` | 100% Local / Zero Cost | Medium |

---

## 📋 Installation

1.  **Core Package**:
    ```bash
    git clone https://github.com/yourusername/ardan.git
    cd ardan
    pip install -e .
    ```
2.  **Unlock All Providers**:
    ```bash
    pip install -e ".[all]"
    ```
3.  **Local Development (Optional)**:
    Ensure [Ollama](https://ollama.ai) is running for the default local experience.

---

## 🔐 Credentials & Security

Ardan protects your keys using `cryptography.fernet` encryption.

```bash
# Securely store a key
ardan keys set anthropic

# Validate connectivity
ardan keys test openai

# List configured providers (masked)
ardan keys list
```

---

## 📖 Power User Guide

### Building a System
```bash
ardan run "Build a React dashboard with a Python backend and PostgreSQL" --provider anthropic
```
-   `--watch`: Monitors your directory. If you change a file, Ardan re-runs its analysis and build.
-   `--auto`: Runs fully autonomously (use with caution in shell environments).

### Interactive REPL (`ardan chat`)
Ardan's REPL is powered by `prompt_toolkit` for a high-performance interactive experience:
-   **Slash Commands**: `/help`, `/save`, `/load`, `/rewind`, `/stats`, `/plan`.
-   **Autocompletion**: Tab-complete file paths and internal commands.
-   **Multimodal**: Reference images via `@path/to/image.png` (supports vision-enabled models).

### Advanced Maintenance
-   `ardan diff`: See a structured diff of everything Ardan changed in the current session.
-   `ardan undo`: Instantly reverts file creations and modifications using session log backups.
-   `ardan recommend`: AI-driven advice on the best model/provider for your specific task.
-   `ardan explain`: Deep-dive analysis into any source file.

---

## 🛠️ Adding Custom Tools

Extending Ardan is simple. Add a function to `ardan/tools/`, register it in `ardan/agent/executor.py`, and update the prompt in `ardan/ollama/prompts.py`. Ardan's architecture is built for infinite extensibility.

---

## ❓ FAQ & Troubleshooting

-   **Ollama not found**: Run `ollama serve` and ensure it's accessible at `http://localhost:11434`.
-   **Rate Limits**: Configure multiple providers to take advantage of Ardan's **Auto-Failover** feature.
-   **Pillow Errors**: If vision features fail, ensure `libjpeg` and `zlib` headers are installed on your OS.
