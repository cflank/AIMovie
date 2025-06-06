# Contributing to AIMovie Cloud

Thank you for your interest in contributing to AIMovie Cloud! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git
- Basic knowledge of FastAPI and Streamlit
- Understanding of cloud API services

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/aimovie-cloud.git
   cd aimovie-cloud
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

4. **Configure Environment**
   ```bash
   cp env_template.txt .env
   # Edit .env with your API keys
   ```

5. **Run Tests**
   ```bash
   pytest tests/
   ```

## 📝 Development Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use Black for code formatting: `black src/`
- Use flake8 for linting: `flake8 src/`
- Use mypy for type checking: `mypy src/`

### Commit Messages
Follow conventional commit format:
- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation changes
- `style:` formatting changes
- `refactor:` code refactoring
- `test:` adding tests
- `chore:` maintenance tasks

Example: `feat: add support for new TTS service`

### Branch Naming
- `feature/description` for new features
- `fix/description` for bug fixes
- `docs/description` for documentation
- `refactor/description` for refactoring

## 🔧 Types of Contributions

### 1. Bug Reports
- Use the bug report template
- Include detailed reproduction steps
- Provide error logs and environment info
- Test with minimal configuration

### 2. Feature Requests
- Use the feature request template
- Explain the use case clearly
- Consider implementation complexity
- Discuss API cost implications

### 3. Code Contributions
- Start with an issue discussion
- Follow the development setup
- Write tests for new features
- Update documentation

### 4. Documentation
- Fix typos and improve clarity
- Add examples and use cases
- Update API documentation
- Translate to other languages

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_specific.py
```

### Writing Tests
- Write unit tests for new functions
- Test cloud API integrations with mocks
- Include edge cases and error handling
- Test with different configurations

### Test Structure
```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── fixtures/       # Test data
└── conftest.py     # Pytest configuration
```

## 📚 Documentation

### Code Documentation
- Use docstrings for all functions and classes
- Include parameter types and return values
- Add usage examples for complex functions

### API Documentation
- Update OpenAPI schemas for new endpoints
- Include request/response examples
- Document error codes and messages

### User Documentation
- Update README.md for major changes
- Update USAGE_GUIDE.md for new features
- Include cost implications for new services

## 🌐 Cloud Services

### Adding New Services
1. Create agent in `src/agents/`
2. Add configuration in `src/config/`
3. Update environment template
4. Add tests with mocks
5. Update documentation
6. Consider cost implications

### API Integration Guidelines
- Use async/await for API calls
- Implement proper error handling
- Add retry logic with exponential backoff
- Include rate limiting
- Log API usage for cost tracking

## 🔍 Code Review Process

### Before Submitting PR
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No breaking changes (or clearly marked)
- [ ] API costs considered

### Review Criteria
- Code quality and readability
- Test coverage
- Performance implications
- Security considerations
- API cost impact
- Documentation completeness

## 🚀 Release Process

### Version Numbering
We follow Semantic Versioning (SemVer):
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in pyproject.toml
- [ ] Docker image builds successfully
- [ ] API costs documented

## 💰 Cost Considerations

When contributing features that use cloud APIs:
- Document expected costs
- Provide cost optimization options
- Test with minimal API usage
- Consider free tier limitations
- Update cost estimation tools

## 🤝 Community Guidelines

### Be Respectful
- Use inclusive language
- Be patient with newcomers
- Provide constructive feedback
- Help others learn

### Communication Channels
- GitHub Issues for bugs and features
- GitHub Discussions for questions
- Pull Requests for code contributions

## 📞 Getting Help

- Check existing issues and documentation
- Ask questions in GitHub Discussions
- Join our community chat (if available)
- Contact maintainers for urgent issues

## 🎉 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing to AIMovie Cloud! 🚀 