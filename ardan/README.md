# Ardan: The World's Most Powerful Autonomous Coding Agent CLI

Ardan is a high-performance, multi-provider coding agent that outperforms all competitors in intelligence, flexibility, and developer experience.

---

## 🚀 Why Ardan?

-   **🧠 Multi-Provider Intelligence**: Seamlessly switch between Anthropic (Claude), Google (Gemini), OpenAI (GPT-4o), Mistral, Groq, and OpenRouter.
-   **⚡ Unmatched Speed**: Real-time tokens-per-second display, especially on Groq.
-   **🔌 Elite Toolset**: Full control over Git, Docker, Testing, Dependencies, and Architecture Diagrams.
-   **🛡️ Secure Credentials**: API keys are stored encrypted at rest with machine-derived keys.
-   **✨ Master-Level Agent Loop**: Autonomous planning, execution with self-correction, and senior-level code review.

---

## 🛠️ Multi-Provider Support

Ardan is provider-agnostic. Use the best model for your task:

| Provider | Recommended Model | Best For... |
| :--- | :--- | :--- |
| **Anthropic** | `claude-3-5-sonnet` | Complex logic, reasoning |
| **Google** | `gemini-2.0-flash` | Speed, large context (1M+ tokens) |
| **OpenAI** | `gpt-4o` | General purpose, tool accuracy |
| **Mistral** | `codestral-latest` | Dedicated code generation |
| **Groq** | `llama-3.3-70b` | Extreme performance, real-time TPS |
| **Ollama** | `codellama:13b` | 100% local, no-cost experimentation |

---

## 📋 Installation

1.  **Prerequisites**: Python 3.11+
2.  **Install Ardan**:
    ```bash
    git clone https://github.com/yourusername/ardan.git
    cd ardan
    pip install -e .
    ```
3.  **Optional: Install Provider SDKs**:
    ```bash
    pip install "ardan[all]"  # Installs all provider SDKs
    ```

---

## 🔐 Credentials Setup

Securely store your API keys:
```bash
ardan keys set anthropic YOUR_API_KEY
ardan keys set openai YOUR_API_KEY
ardan keys test google
```

---

## 📖 Power Usage

### Run with Specific Provider
```bash
ardan run "Build a React + FastAPI app" --provider anthropic --model claude-3-5-sonnet
```

### Advanced Chat Mode
```bash
ardan chat --provider groq --model llama-3.3-70b-versatile
```

### New Advanced Tools
-   **Git**: `git_init`, `git_commit`, `git_branch`
-   **Docker**: `docker_build`, `docker_run`, `generate_dockerfile`
-   **Quality**: `run_tests`, `scan_deps`, `auto_install_deps`
-   **Architecture**: `generate_ascii_diagram`

---

## ❓ FAQ

-   **Failover**: If your primary provider is rate-limited, Ardan can automatically failover to a backup.
-   **Security**: Keys are encrypted using your machine's unique identifier.
-   **Plan Mode**: Use `/plan` in chat to break down massive features into structured execution steps.
