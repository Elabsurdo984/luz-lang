# Contributing to Luz

Thank you for your interest in contributing to Luz! This document explains how to get started.

## Getting started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/luz-lang.git
   cd luz-lang
   ```
3. Create a branch for your change:
   ```bash
   git checkout -b feature/my-feature
   ```

## Project structure

```
luz-lang/
├── main.py               # Entry point: REPL, file execution, --check mode
├── luz/
│   ├── tokens.py         # TokenType enum and Token class
│   ├── lexer.py          # Lexer: text → tokens
│   ├── parser.py         # Parser: tokens → AST + all AST node classes
│   ├── interpreter.py    # Interpreter: executes the AST
│   └── exceptions.py     # Error class hierarchy
├── ray.py                # Ray package manager
├── libs/                 # Standard library (bundled with installer)
│   └── luz-math/         # Math library
├── tests/
│   └── test_suite.py     # Test suite
├── installer/
│   └── luz_installer.iss # Inno Setup installer script
├── vscode-luz/           # VS Code extension
└── docs/                 # MkDocs documentation
```

## Running the tests

```bash
pip install pytest
pytest tests/test_suite.py -v
```

All tests must pass before opening a pull request.

## Lint

```bash
pip install pylint
pylint luz/ --fail-under=9.0
```

The CI enforces a minimum pylint score of **9.0/10**. Your PR will not be merged if it drops below that. The project ships a `.pylintrc` that already silences false positives from wildcard imports and intentional style decisions, so you only need to worry about real issues.

## Making changes to the language

The interpreter pipeline has three stages. Depending on what you want to add:

| What | Where to change |
|---|---|
| New keyword | `tokens.py` → `lexer.py` (KEYWORDS dict) |
| New syntax | `parser.py` (add node class + parse method) |
| New behavior | `interpreter.py` (add `visit_YourNode` method) |
| New built-in function | `interpreter.py` (`self.builtins` dict) |
| New error type | `exceptions.py` |
| New stdlib module | `libs/` (new folder with `luz.json` + `.luz` files) |

## Code style

- Follow the existing style in each file
- Add comments for non-obvious logic
- Keep functions focused and small

## Opening a pull request

1. Make sure all tests pass: `pytest tests/test_suite.py -v`
2. Make sure lint passes: `pylint luz/ --fail-under=9.0`
3. Push your branch to your fork
4. Open a pull request against `master`
5. Describe what you changed and why

## Reporting bugs

Open an issue at [github.com/Elabsurdo984/luz-lang/issues](https://github.com/Elabsurdo984/luz-lang/issues) with:
- A minimal code example that reproduces the bug
- The expected behavior
- The actual behavior (including the full error message)

## Ideas and feature requests

Open an issue with the `enhancement` label. Good areas to contribute:

- New standard library modules (`luz-string`, `luz-random`, etc.)
- HTTP client / server built-ins
- More test coverage
- Improvements to the VS Code extension
- Linux and macOS builds
