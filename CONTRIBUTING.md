# Contributing to GenAI Platform

Thank you for your interest in contributing to GenAI Platform! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/GenerativeAIProjects.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `make test`
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

```bash
# Install dependencies
make dev-install

# Run tests
make test

# Format code
make format

# Run linters
make lint

# Start local environment
make docker-up
```

## Code Style

- Follow PEP 8 for Python code
- Use Black for formatting
- Use type hints
- Write docstrings for public APIs
- Keep functions focused and small

## Testing

- Write unit tests for new features
- Maintain test coverage above 80%
- Test edge cases
- Use pytest fixtures for setup

## Pull Request Guidelines

1. **Title**: Use descriptive titles (e.g., "Add support for Claude 3 model")
2. **Description**: Explain what and why
3. **Tests**: Include tests for new features
4. **Documentation**: Update docs if needed
5. **Changelog**: Add entry to CHANGELOG.md

## Commit Messages

Use conventional commits format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

Example: `feat: add support for Google Gemini Pro`

## Adding New Features

### New Model Provider

1. Create provider class in `src/models/`
2. Extend `BaseModelProvider`
3. Implement all required methods
4. Register in `ProviderFactory`
5. Add tests
6. Update documentation

### New Vector Store

1. Create store class in `src/infrastructure/vector_stores/`
2. Extend `BaseVectorStore`
3. Implement all required methods
4. Add configuration options
5. Add tests
6. Update documentation

### New API Endpoint

1. Create route in `src/api/routes/`
2. Add request/response models
3. Implement business logic
4. Add error handling
5. Add tests
6. Update API documentation

## Documentation

- Update README.md for major features
- Update docs/ for detailed documentation
- Add code examples
- Keep API documentation in sync

## Questions?

- Open an issue for bugs
- Start a discussion for feature ideas
- Check existing issues first

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the project

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
