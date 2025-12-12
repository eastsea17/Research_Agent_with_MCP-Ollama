# Deep Research Agent 🔬

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-required-orange.svg)](https://ollama.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Multi-Agent Research Ideation System: Generator → Critic → Refiner Loop**

OpenAlex API에서 최신 논문을 검색하고, 멀티 에이전트 시스템을 통해 **Top-tier 저널 수준**의 독창적인 연구 제안서를 자동으로 생성하는 시스템입니다.

## ✨ Key Features

- **📚 OpenAlex Integration**: 키워드 기반으로 최신 논문 100개 자동 수집
- **🔄 Iterative Refinement Loop**: Generator → Critic → Refiner 순환 구조
- **🧠 Multi-Agent System**:
  - **Generator**: 논문 기반 아이디어 생성 (Chain of Thought + Critic-Solution Framework)
  - **Critic**: 4가지 기준으로 평가 (Novelty, Feasibility, Specificity, Impact)
  - **Refiner**: 비평을 반영하여 아이디어 개선
- **💾 Ollama Local/Cloud**: 로컬 및 클라우드 Ollama 모델 지원
- **📊 Rich Reports**: Markdown + HTML 상세 보고서 자동 생성

## 🏗️ System Architecture

```mermaid
graph LR
    A[Keyword] --> B[OpenAlex API]
    B --> C[Top 5 Papers]
    C --> D[Generator Agent]
    D --> E[Draft Ideas]
    E --> F[Critic Agent]
    F --> G{Score >= 3.0?}
    G -->|Yes| H[Accepted]
    G -->|No, >= 2.0| I[Refiner Agent]
    G -->|No, < 2.0| J[Rejected]
    I --> E
    H --> K[Markdown Report]
    K --> L[HTML Report]
```

## 📁 Project Structure

```text
├── agents/                     # Agent Modules
│   ├── base_agent.py           # Base agent class
│   ├── generator.py            # OpenAlex + Idea generation
│   ├── critic.py               # Evaluation (4 criteria)
│   └── refiner.py              # Improvement based on feedback
├── core/                       # Core Infrastructure
│   ├── model_manager.py        # Ollama local/cloud management
│   ├── mcp_client.py           # MCP server client (mock)
│   └── types.py                # Data structures
├── prompts/                    # System Prompts
│   ├── generator_v2.txt
│   ├── critic_v2.txt
│   └── refiner_v2.txt
├── utils/                      # Utilities
│   ├── parser.py               # JSON parsing with fallback
│   ├── report_generator.py     # Markdown report
│   └── html_generator.py       # HTML conversion
├── results/                    # Generated Reports
├── config.yaml                 # Configuration
├── main.py                     # Entry Point
└── LICENSE                     # MIT License
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.ai/)

### Installation

```bash
git clone <repository-url>
cd 251212_Research_Ideation_Agent_with_MCP

pip install pyyaml requests
```

### Configuration

Edit `config.yaml`:

```yaml
ollama:
  base_url: "http://localhost:11434"    # Local Ollama
  cloud_url: "http://your-cloud:11434"  # Cloud Ollama (optional)

agent_models:
  generator:
    provider: "ollama"
    model: "gpt-oss:20b"
    temperature: 0.8

  critic:
    provider: "ollama-cloud"
    model: "deepseek-v3.1:671b-cloud"
    temperature: 0.1

  refiner:
    provider: "ollama-cloud"
    model: "gpt-oss:120b-cloud"
    temperature: 0.3

loop_settings:
  max_iterations: 2
  score_threshold: 3.0   # Minimum score to accept
  drop_threshold: 2.0    # Below this = rejected
```

### Run

```bash
python main.py --keyword "patents network analysis" --loops 3
```

### Output

- `research_results.json`: Full data in JSON format
- `results/research_report_YYYYMMDD_HHMMSS.md`: Markdown report
- `results/research_report_YYYYMMDD_HHMMSS.html`: Styled HTML report

## 📊 Output Example

### Generated Report Structure

```markdown
## 아이디어 1: Quantum-Enhanced Patent Citation Embedding

**Status:** `accepted`
**Total Iterations:** 2

### 진화 과정 (Evolution History)

#### Iteration 0 - DRAFT
**Title:** Quantum-Enhanced Patent Citation Embedding
**Methodology:** Use quantum circuits for similarity computation...

##### 🧐 Critic Agent의 평가
| 평가 항목 | 점수 |
|---|---|
| Novelty | 3/5 |
| Feasibility | 3/5 |
| Specificity | 2/5 |
| Impact | 4/5 |
| **Average** | **3.00** |

#### Iteration 1 - REFINED
**Title:** Quantum-Inspired Contrastive Graph Kernels

##### 🔧 Refiner Agent의 개선 내용
The critic noted vague methodology. Adding specific quantum kernel formulation...
```

## ⚙️ Scoring Rubric

| Score | Novelty | Feasibility | Specificity | Impact |
|---|---|---|---|---|
| **5** | Paradigm shift | Elegant implementation | Math formulas | Top-tier journal |
| **4** | Cross-domain fusion | Clear roadmap | Complete pipeline | Industry applicable |
| **3** | Domain adaptation | Theoretically possible | Standard algorithms | Field interest |
| **2** | Parameter tuning | Cost prohibitive | Missing causality | Niche improvement |
| **1** | Textbook knowledge | Impossible | Vague | Practice level |

### Thresholds

- **≥ 3.0**: Accepted
- **2.0 - 3.0**: Refinement needed
- **< 2.0**: Rejected

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Built with ❤️ for Research Innovation*
