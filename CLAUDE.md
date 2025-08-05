# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a benchmarking project that compares OpenAI's GPT-4 with a local GPT-OSS-20B model running via LM Studio. The architecture consists of parallel API clients, standardized prompt datasets, and comprehensive analysis tools.

## Core Architecture

### Data Layer (`data/prompts/`)
- **Prompt Categories**: Four JSON files containing 12 structured prompts each
  - `instruction.json`: Task-following and format compliance
  - `reasoning.json`: Logic and mathematical problem solving  
  - `creative.json`: Creative writing and imagination tasks
  - `coding.json`: Programming problems and debugging challenges
- **Format**: Each prompt has `id`, `role`, `content` fields for consistency

### API Client Layer (`scripts/`)
- **Dual Client Architecture**: Parallel implementations for fair comparison
  - `run_prompts_openai.py`: OpenAI API client with cost tracking
  - `run_prompts_local.py`: LM Studio client with connection testing
  - Both use OpenAI-compatible `/v1/chat/completions` endpoint
- **Shared Utilities** (`utils.py`): Common functions for data handling, cost calculation, and statistics

### Analysis Layer
- **Comparison Engine** (`compare_outputs.py`): Side-by-side analysis with performance metrics
  - Latency ratio calculations
  - Response quality comparisons  
  - Cost efficiency analysis
  - Category-specific breakdowns
- **Export Capabilities**: JSON detailed comparisons and CSV data exports

## Common Commands

### Running Benchmarks
```bash
# Run OpenAI GPT-4 evaluation (requires API key)
cd scripts
python run_prompts_openai.py --api-key YOUR_KEY --categories instruction reasoning

# Run local LM Studio evaluation (requires running LM Studio server)
python run_prompts_local.py --url http://127.0.0.1:1234 --model gpt-oss-20b

# Run all categories for both models
python run_prompts_openai.py --api-key YOUR_KEY
python run_prompts_local.py
```

### Analysis and Comparison
```bash
# Generate side-by-side comparison analysis
python compare_outputs.py --export-csv

# Custom result file locations
python compare_outputs.py --openai-results ../results/custom_openai.json --local-results ../results/custom_local.json
```

### LM Studio Setup Requirements
1. Start LM Studio application
2. Navigate to "Local Server" tab
3. Load GPT-OSS-20B GGUF model
4. Start server on `http://127.0.0.1:1234`
5. Verify connection before running scripts

## Data Flow Architecture

1. **Prompt Loading**: JSON files → `load_prompts()` → structured prompt lists
2. **API Execution**: Prompts → API clients → response data with metrics
3. **Result Storage**: Response data → JSON files in `results/` directory
4. **Comparison Analysis**: Result files → `compare_outputs.py` → performance analysis
5. **Export Options**: Analysis → JSON detailed reports + CSV data export

## Key Integration Points

### Token and Cost Tracking
- OpenAI: Real token counts and pricing from API response
- Local: Estimated tokens if available from LM Studio API
- Cost calculation uses model-specific pricing in `utils.py`

### Error Handling Strategy
- Connection testing for LM Studio before batch processing
- Individual prompt error logging without stopping batch execution
- Graceful degradation when partial results are available

### Performance Metrics
- **Latency**: Time from request to complete response
- **Token Efficiency**: Input/output token usage comparison
- **Response Quality**: Length, word count, and format adherence
- **Cost Analysis**: Per-prompt and aggregate cost tracking

## Result File Structure

### Primary Outputs
- `results/openai_outputs.json`: Raw OpenAI API responses with metrics
- `results/local_outputs.json`: Raw local model responses with metrics  
- `results/detailed_comparison.json`: Side-by-side prompt comparisons
- `results/performance_analysis.json`: Aggregate statistics and insights
- `results/comparison_data.csv`: Flattened data for external analysis

### Response Data Schema
Each response includes: `prompt_id`, `model`, `response`, `latency_seconds`, `input_tokens`, `output_tokens`, `cost_usd`, `timestamp`, `response_length`, `words_count`

## Development Workflow

1. **Adding New Prompts**: Extend JSON files with consistent `id` naming pattern
2. **Model Testing**: Use connection testing before full batch runs
3. **Result Analysis**: Run comparison script after collecting both model results
4. **Performance Monitoring**: Check latency ratios and success rates in analysis output