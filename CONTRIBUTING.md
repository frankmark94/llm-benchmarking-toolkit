# Contributing to OpenAI vs Local LM Benchmarking

Thank you for your interest in contributing! This project welcomes contributions from the community.

## How to Contribute

### 🐛 Bug Reports
- Use GitHub Issues to report bugs
- Include system information (OS, Python version, hardware)
- Provide steps to reproduce the issue
- Include error messages and logs

### 💡 Feature Requests
- Suggest new models to benchmark
- Propose additional evaluation metrics
- Request new prompt categories
- Share hardware configuration results

### 🔧 Code Contributions
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Development Setup

```bash
git clone <your-fork>
cd openai-vs-local-lm
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

## Areas for Contribution

### 🎯 High Priority
- Additional model integrations (Llama, Mistral, Claude)
- Hardware performance benchmarks (Apple Silicon, Intel, AMD)
- Quality scoring automation
- Streaming response comparisons

### 📊 Analysis & Visualization
- New chart types and visualizations
- Statistical significance testing
- Cost optimization algorithms
- Response quality metrics

### 🛠️ Infrastructure
- Docker containerization
- CI/CD pipeline improvements
- Cross-platform compatibility
- Performance optimizations

## Code Style
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings to functions
- Keep line length under 100 characters

## Testing
- Run existing tests before submitting PR
- Add tests for new functionality
- Ensure notebooks run without errors

## Documentation
- Update README.md for new features
- Add docstrings to new functions
- Update CLAUDE.md for development guidance

## Questions?
Open an issue or start a discussion. We're here to help!

Happy contributing! 🚀