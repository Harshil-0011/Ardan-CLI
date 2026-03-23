# Ardan: The World's Most Powerful Autonomous Coding Agent CLI

Ardan is an elite, multi-provider autonomous coding agent that combines the reasoning power of the world's best LLMs with a high-fidelity developer toolset. Designed for speed, intelligence, and a superior developer experience, Ardan beats every competitor on the market.

---

## 🚀 Why Ardan?

-   **🧠 Multi-Provider Intelligence**: Seamlessly swap between Anthropic, Google, OpenAI, Mistral, Groq, and OpenRouter.
-   **⚡ Extreme Performance**: Real-time tokens-per-second tracking and parallel task execution for maximum efficiency.
-   **🔌 Elite Toolset**: Deep integrations for Git, Docker, Python quality tools, and C/C++ compilation.
-   **🛡️ Industrial Security**: AES-encrypted API key storage secured by your machine's unique hardware identifier.
-   **✨ Master ReAct Loop**: Autonomous planning, parallel execution, self-correction, senior review passes, and proactive suggestions.

---

## 🛠️ Multi-Provider Support

Ardan is provider-agnostic. Use the best model for your task:

| Provider | Recommended Model | Strength | Cost (1M Tokens) |
| :--- | :--- | :--- | :--- |
| **Anthropic** | `claude-sonnet-4-6` | Complex reasoning | $3.00 |
| **Google** | `gemini-2.5-pro` | Smartest, huge context | $1.25 |
| **OpenAI** | `gpt-4.1` | Best tool accuracy | $2.00 |
| **Mistral** | `codestral-latest` | Dedicated code generation | $1.00 |
| **Groq** | `llama-3.3-70b` | Fastest inference alive | Free tier |
| **OpenRouter** | `deepseek/coder-v2` | Best open source | $0.14 |
| **Ollama** | `codellama:13b` | 100% local, no cost | Free |

---

## 📦 Installation

### Core Install
```bash
git clone https://github.com/yourusername/ardan.git
cd ardan
pip install -e .
```

### Install with All Providers
```bash
pip install -e ".[all]"
```

---

## 🔑 Setup Guide

### Secure Your Keys
```bash
ardan keys set anthropic   # Prompts for key and encrypts it
ardan keys set openai
ardan keys list            # Shows configured providers (masked)
ardan keys test google    # Validates key and connectivity
```

### Get API Keys
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com/)
- **Google**: [aistudio.google.com](https://aistudio.google.com/app/apikey)
- **OpenAI**: [platform.openai.com](https://platform.openai.com/api-keys)
- **Groq**: [console.groq.com](https://console.groq.com/keys)

---

## 📖 Command Reference

### Build a System
```bash
ardan run "Build a React + FastAPI Todo app with Docker" --provider anthropic
```
-   `--auto`: Skip all confirmation prompts.
-   `--watch`: Monitor the workspace and re-build on file changes.

### Power Tools
-   `ardan chat`: Interactive REPL with autocompletion and checkpointing.
-   `ardan recommend "Task"`: AI-driven advice on the best provider for your needs.
-   `ardan explain "file.py"`: Deep analysis of any source file.
-   `ardan improve "file.py"`: AI-driven refactoring and best practice alignment.
-   `ardan diff`: See exactly what Ardan changed in this session.
-   `ardan undo`: Revert file creations and modifications instantly.

---

## 🛠️ Adding Custom Tools

Extending Ardan is simple:
1.  Add your function to a module in `ardan/tools/`.
2.  Ensure it returns `ToolResult(success: bool, output: str, error: str)`.
3.  Register it in `ardan/agent/executor.py`'s `self.tools` map.
4.  Add the tool signature to `ardan/ollama/prompts.py` so the agent knows it exists.

---

## ❓ Troubleshooting

-   **Ollama Connection**: Ensure `ollama serve` is running if using the local provider.
-   **Rate Limits**: If a provider is limited, Ardan will automatically attempt to failover to a configured backup.
-   **Pillow Errors**: Ensure system dependencies for `Pillow` (like `libjpeg-dev`) are installed for multimodal features.
