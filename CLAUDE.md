# Elodie Development Guide

## Build & Test Commands
- Run all tests: `python elodie/tests/run_tests.py`
- Run single test file: `python -m nose elodie/tests/specific_test.py`
- Run specific test: `python -m nose elodie/tests/specific_test.py:specific_test_function`

## Code Style Guidelines
- **Linting**: Use flake8 for code quality checks
- **Imports**: Absolute imports preferred, grouped by source (stdlib, third-party, local)
- **Formatting**: 4-space indentation, max line length ~79 chars
- **Types**: Use compatibility layer (six, future) for Python 2/3 support
- **Naming**: 
  - snake_case for functions, variables, modules
  - CamelCase for classes
- **Error Handling**: Use specific exception types in try/except blocks
- **Documentation**: Docstrings for modules, classes, methods
- **Testing**: Follow unittest patterns with setUp/tearDown methods

## Project Structure
- Core functionality in `/elodie` directory
- Tests in `/elodie/tests`
- Web interface in `/app`