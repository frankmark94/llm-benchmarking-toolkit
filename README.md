# OpenAI vs Local LM: Comprehensive AI Model Comparison

[![CI](https://github.com/username/openai-vs-local-lm/workflows/CI/badge.svg)](https://github.com/username/openai-vs-local-lm/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A systematic benchmarking framework for comparing any OpenAI model with any local model running via LM Studio. Compare performance across latency, cost, output quality, and response characteristics.

**📊 [View Latest Results →](RESULTS.md)**

## 🎯 Project Overview

This project provides a rigorous, data-driven comparison between:
- **Any OpenAI Model** (via API) - Cloud-based commercial models (GPT-4, GPT-4o, GPT-3.5-turbo, etc.)
- **Any Local Model** (via LM Studio) - Local inference with open-source or custom models

### Supported Models

**OpenAI Models** (via API):
- GPT-4, GPT-4o, GPT-4-turbo
- GPT-3.5-turbo and variants
- Any current or future OpenAI chat completion model

**Local Models** (via LM Studio):
- Llama 3.1, Llama 2 (any size)
- Mistral 7B, Mixtral 8x7B
- Qwen, CodeLlama, Phi-3
- Any GGUF-format model supported by LM Studio

### Key Evaluation Areas
- **Instruction Following**: Task completion and format adherence
- **Reasoning**: Logic, mathematics, and problem-solving
- **Creative Writing**: Storytelling, poetry, and imaginative content
- **Coding Assistance**: Programming problems and debugging

## 📁 Project Structure

```
openai-vs-local-lm/
├── data/
│   └── prompts/                 # Standardized prompt datasets (48 total)
│       ├── instruction.json     # Task-following prompts
│       ├── reasoning.json       # Logic and math problems
│       ├── creative.json        # Creative writing tasks
│       └── coding.json          # Programming challenges
├── scripts/
│   ├── run_prompts_openai.py    # OpenAI API client (any model)
│   ├── run_prompts_local.py     # LM Studio client (any model)
│   ├── compare_outputs.py       # Side-by-side analysis
│   └── utils.py                 # Shared utilities
├── notebooks/
│   ├── output_analysis.ipynb    # Response quality analysis
│   └── performance_charts.ipynb # Performance visualizations
├── results/                     # Generated benchmark data
├── assets/                      # Charts and documentation
├── requirements.txt             # Python dependencies
├── .env.example                 # Configuration template
└── CLAUDE.md                    # Development guidance
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** with pip
2. **OpenAI API key** (for any OpenAI model comparison)
3. **LM Studio** with any local model loaded (GGUF format recommended)

### Installation

1. Clone and setup:
```bash
git clone <repository-url>
cd gpt-o4-vs-gpt-oss
pip install -r requirements.txt
```

2. Configure API access:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

3. Setup LM Studio:
   - Download and install [LM Studio](https://lmstudio.ai/)
   - Load any GGUF model (Llama, Mistral, GPT-OSS, etc.)
   - Start local server (default: `http://127.0.0.1:1234`)

### Running Benchmarks

1. **Run OpenAI model evaluation:**
```bash
cd scripts
python run_prompts_openai.py --api-key YOUR_OPENAI_KEY --model gpt-4
# Or use any other OpenAI model: gpt-4o, gpt-3.5-turbo, etc.
```

2. **Run local model evaluation:**
```bash
python run_prompts_local.py --model your-local-model-name
# Model name should match what's loaded in LM Studio
```

3. **Generate comparison analysis:**
```bash
python compare_outputs.py --export-csv
```

4. **View results in Jupyter:**
```bash
jupyter notebook ../notebooks/
```

## 📊 Analysis Features

### Performance Metrics
- **Latency**: Response time from request to completion
- **Token Usage**: Input/output token consumption (where available)
- **Cost Efficiency**: Per-response and total cost analysis
- **Response Quality**: Length, structure, and content characteristics

### Visualization Suite
- Interactive scatter plots (latency vs. response length)
- Performance radar charts by category
- Cost projection analysis
- Statistical distribution comparisons

### Quality Analysis Framework
- Response length and word count analysis
- Content structure metrics (sentences, code blocks, formatting)
- Category-specific performance breakdowns
- Manual quality scoring templates

## 🔧 Command Line Options

### OpenAI Client (`run_prompts_openai.py`)
```bash
python run_prompts_openai.py \
  --api-key YOUR_KEY \
  --model gpt-4o \
  --categories instruction reasoning creative coding \
  --output-dir ../results

# Supported models: gpt-4, gpt-4o, gpt-4-turbo, gpt-3.5-turbo, etc.
```

### Local Client (`run_prompts_local.py`)
```bash
python run_prompts_local.py \
  --url http://127.0.0.1:1234 \
  --model llama-3.1-8b-instruct \
  --categories instruction reasoning creative coding \
  --output-dir ../results

# Model name must match what's loaded in LM Studio
# Works with any GGUF model: Llama, Mistral, Qwen, etc.
```

### Comparison Tool (`compare_outputs.py`)
```bash
python compare_outputs.py \
  --openai-results ../results/openai_outputs.json \
  --local-results ../results/local_outputs.json \
  --output-dir ../results \
  --export-csv
```

## 📈 Expected Outputs

### JSON Results
- `openai_outputs.json`: Raw OpenAI model responses with performance metrics
- `local_outputs.json`: Raw local model responses with performance metrics
- `detailed_comparison.json`: Side-by-side prompt comparisons
- `performance_analysis.json`: Aggregate statistics and insights

### CSV Export
- `comparison_data.csv`: Flattened data for external analysis tools

### Visualizations
- Performance dashboards with latency, cost, and quality metrics
- Interactive charts for detailed exploration
- Category-specific analysis breakdowns

## 🔍 Key Insights Framework

The analysis focuses on:

1. **Speed vs. Quality Trade-offs**: How local inference latency compares to cloud API speed
2. **Cost Efficiency**: Total cost savings with local deployment vs. API pricing
3. **Response Characteristics**: Differences in output style, length, and structure
4. **Category Performance**: Which model type excels in specific task types
5. **Model Capabilities**: Comparative analysis across different model sizes and architectures

## 🛠️ Technical Architecture

### API Integration
Both models use OpenAI-compatible `/v1/chat/completions` endpoints:
- **OpenAI**: Standard API with usage tracking and cost calculation
- **LM Studio**: Local server API with connection testing and error handling

### Data Pipeline
1. **Prompt Loading**: Structured JSON datasets with consistent formatting
2. **Parallel Execution**: Independent API clients for fair comparison
3. **Metrics Collection**: Comprehensive performance and quality data capture
4. **Analysis Generation**: Statistical comparison and visualization creation

### Error Handling
- Connection testing before batch execution
- Individual prompt error logging without batch interruption
- Graceful degradation for partial results
- Comprehensive error reporting and debugging information

## 📝 Customization

### Adding New Prompts
1. Edit appropriate JSON file in `data/prompts/`
2. Follow existing format: `{\"id\": \"category-##\", \"role\": \"user\", \"content\": \"...\"}}`
3. Maintain consistent prompt numbering and quality standards

### Custom Analysis
- Extend `utils.py` with additional metrics functions
- Modify notebook templates for specific analysis needs
- Add new visualization types in performance charts

### Model Configuration
- **OpenAI Models**: Update model names (gpt-4, gpt-4o, gpt-3.5-turbo) and adjust pricing
- **Local Models**: Ensure model names match what's loaded in LM Studio
- **Cross-Platform**: Configure URLs for remote LM Studio instances (Windows ↔ WSL, etc.)
- **Timeout Settings**: Adjust for different model sizes and hardware capabilities

## 🔒 Security and Best Practices

- API keys stored in environment variables (never committed)
- Local model inference has no external data transmission
- Results contain no sensitive information beyond prompt responses
- All outputs are safe for sharing and publication

## 📊 Sample Results Structure

```json
{
  \"prompt_id\": \"instruction-01\",
  \"model\": \"gpt-4o\",
  \"response\": \"...\",
  \"latency_seconds\": 1.234,
  \"input_tokens\": 45,
  \"output_tokens\": 123,
  \"cost_usd\": 0.0068,
  \"timestamp\": \"2024-01-15T10:30:45\",
  \"response_length\": 456,
  \"words_count\": 78,
  \"category\": \"instruction\"
}
```

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Additional model integrations
- New prompt categories or evaluation metrics
- Enhanced visualization and analysis tools
- Performance optimization and scaling improvements

## 📄 License

This project is designed for research and educational purposes. Please respect the terms of service for OpenAI API and ensure proper licensing for any models used.

---

## 🚀 Getting Started Checklist

- [ ] Install Python dependencies
- [ ] Configure OpenAI API key
- [ ] Set up LM Studio with GPT-OSS-20B
- [ ] Run initial benchmark (small subset)
- [ ] Verify results generation
- [ ] Explore analysis notebooks
- [ ] Run full benchmark suite
- [ ] Generate comparison report

**Ready to compare AI models? Start with the Quick Start guide above!** 🎉