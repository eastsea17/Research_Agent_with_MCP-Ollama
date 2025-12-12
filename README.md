# Multi-agent based Research Topic Ideation System 🔬

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-Cloud%20Supported-orange.svg)](https://ollama.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Version 1.0**
>
> **Multi-Agent Research Ideation System: Generator → Critic → Refiner Loop**

An automated system that leverages **OpenAlex API** for real-time literature review and utilizes **Advanced LLMs (DeepSeek V3, GPT-OSS)** via Ollama Cloud to generate, critique, and refine **top-tier journal-quality** research proposals.

## ✨ Key Features

- **📚 Real-time Literature Review**: Automatically fetches the latest papers from **OpenAlex** based on keywords (Strict config validation).
- **🔄 Iterative Refinement Loop**:
  - **Generator**: Uses **DeepSeek V3 (671B)** for high-level idea generation using Chain of Thought.
  - **Critic**: Uses **GPT-OSS (120B)** to evaluate ideas on Novelty, Feasibility, Specificity, and Impact.
  - **Refiner**: Uses **GPT-OSS (120B)** to improve ideas based on specific critique feedback.
- **☁️ Hybrid Operation**: Supports both **Local Ollama** (privacy/cost) and **Ollama Cloud** (performance).
- **📊 Rich Reports**: Auto-generates detailed **Markdown** and **HTML** reports with evolution history.

## 🏗️ System Architecture

```mermaid
graph LR
    A[Keyword] -->|Fetch Limit| B[OpenAlex API]
    B -->|Top-K Selection| C[Context]
    C --> D[Generator Agent]
    D --> E[Draft Ideas]
    E --> F[Critic Agent]
    F --> G{Score >= Threshold?}
    G -->|Yes| H[Accepted]
    G -->|No, >= Drop| I[Refiner Agent]
    G -->|No, < Drop| J[Rejected]
    I --> E
    H --> K[Markdown Report]
    K --> L[HTML Report]
```

## 📁 Project Structure

```text
├── agents/                     # Agent Modules
│   ├── base_agent.py           # Base agent class
│   ├── generator.py            # Idea generation (OpenAlex integrated)
│   ├── critic.py               # Evaluation logic
│   └── refiner.py              # Refinement logic
├── core/                       # Core Infrastructure
│   ├── model_manager.py        # Model loading & Cloud/Local management
│   ├── mcp_client.py           # OpenAlex context fetching
│   └── types.py                # Data types (IdeaObject, etc.)
├── prompts/                    # System Prompts
│   ├── generator.txt           # CoT + Critic-Solution Prompt
│   ├── critic.txt              # Evaluation Rubric
│   └── refiner.txt             # Improvement Instructions
├── utils/                      # Utilities
│   ├── parser.py               # Robust JSON parsing
│   ├── report_generator.py     # Markdown generation
│   └── html_generator.py       # HTML styling
├── results/                    # Output Directory
├── config.yaml                 # System Configuration
├── main.py                     # Entry Point
└── LICENSE                     # MIT License
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.ai/) (Local or Cloud endpoint)

### Installation

```bash
git clone <repository-url>
cd 251212_Research_Ideation_Agent_with_MCP

pip install pyyaml requests
```

### Configuration

The system is fully configurable via `config.yaml`.
**Note:** `openalex` settings are strictly enforced.

```yaml
project:
  name: "Multi-agent based Research Topic Ideation System"
  version: "1.0"

ollama:
  base_url: "http://localhost:11434"  # Local Ollama
  cloud_url: "http://localhost:11434" # Ollama Cloud endpoint

openalex:
  fetch_limit: 200        # REQUIRED: Number of papers to fetch
  top_k_papers: 10        # REQUIRED: Top papers for context

agent_models:
  generator:
    provider: "ollama-cloud"
    model: "deepseek-v3.1:671b-cloud"
    temperature: 0.8
    system_prompt_path: "./prompts/generator.txt"

  critic:
    provider: "ollama-cloud"
    model: "gpt-oss:120b-cloud"
    temperature: 0.3
    system_prompt_path: "./prompts/critic.txt"

  refiner:
    provider: "ollama-cloud"
    model: "gpt-oss:120b-cloud"
    temperature: 0.3
    system_prompt_path: "./prompts/refiner.txt"

loop_settings:
  max_iterations: 2
  num_ideas: 3
  score_threshold: 3.0
  drop_threshold: 2.0
```

### Usage

Run the agent with a research keyword:

```bash
python main.py --keyword "AI based technology intelligence"
```

Override iteration count:

```bash
python main.py --keyword "Generative Design in Architecture" --loops 5
```

## 📊 Output

Results are saved in the `results/` directory:

1. **`research_results.json`**: Complete structured data including evolution history.
2. **`research_report_DATE.md`**: Readable report with scores and feedback.
3. **`research_report_DATE.html`**: Professional HTML report for sharing.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Powered by DeepSeek V3 & GPT-OSS*
