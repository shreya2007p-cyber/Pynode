# Pynode

**Pynode** is an experimental polyglot runtime that lets you write Python and JavaScript in a single `.pn` file.

The current implementation executes the Python block first, passes its variables to JavaScript through a JSON-based context bridge, and returns updated JavaScript context data to Python's runtime context.

> **Project status:** Early development - version 0.1.0.

## Features

- Execute Python and JavaScript from a single `.pn` file.
- Parse and validate Python and JavaScript block boundaries.
- Share JSON-serializable data between Python and JavaScript.
- Return updated JavaScript context data to Python.
- Report file, parsing, Python execution, and JavaScript execution errors.
- Run `.pn` files through a command-line interface.
- Automated regression tests for parser, execution, and data-bridge behaviour.

## Requirements

- Python 3.14 or a compatible Python version.
- Node.js installed and available on your system's `PATH`.
- A terminal such as PowerShell, Command Prompt, or a Unix shell.

## Project Structure

```text
pynode/
â”œâ”€â”€ examples/
â”‚   â”œâ”€â”€ hello.pn
â”‚   â”œâ”€â”€ hello_polyglot.pn
â”‚   â”œâ”€â”€ invalid.pn
â”‚   â”œâ”€â”€ invalid_js.pn
â”‚   â”œâ”€â”€ js_error.pn
â”‚   â””â”€â”€ python_error.pn
â”œâ”€â”€ pn/
â”‚   â”œâ”€â”€ cli.py
â”‚   â”œâ”€â”€ parser.py
â”‚   â”œâ”€â”€ ast.py
â”‚   â”œâ”€â”€ executor.py
â”‚   â”œâ”€â”€ runtime.py
â”‚   â””â”€â”€ js_executor.py
â”œâ”€â”€ tests/
â”‚   â””â”€â”€ test_runtime.py
â”œâ”€â”€ README.md
â””â”€â”€ pyproject.toml
```

## Writing a `.pn` File

A Pynode source file contains a Python block followed by a JavaScript block.

```text
[python]
name = "Shreya"
[/python]

[js]
console.log("Hello,", pynode.name)
pynode.score = 95
[/js]
```

### How It Works

1. Pynode reads the `.pn` file.
2. The parser validates the block structure and Python syntax.
3. The Python block executes first.
4. Python variables are passed to JavaScript through a JSON-based context.
5. JavaScript executes and may update the shared context.
6. Updated JavaScript context data is returned to the Python runtime context.

The current CLI reports successful completion after both blocks execute without a handled error.

## Running Pynode

Activate your virtual environment if you use one, then run a sample file from the project root:

```powershell
python -m pn.cli run examples/hello_polyglot.pn
```

Display help:

```powershell
python -m pn.cli --help
```

Display the version:

```powershell
python -m pn.cli --version
```

## Running Tests

Run the automated test suite from the project root:

```powershell
python -m unittest discover -s tests -v
```

The current regression suite covers parsing, invalid block structures, Python execution, JavaScript execution, context exchange, serialization errors, and related edge cases.

## Current Limitations

- Pynode is an experimental project and is not production-ready.
- Python and JavaScript exchange context data through JSON serialization, so arbitrary Python objects and non-JSON-serializable values are not supported by the bridge.
- Python and JavaScript execute in separate execution environments; this is a data bridge, not direct access to the same native runtime objects.
- The language syntax and CLI are still evolving.

## Goals

The project aims to explore a practical polyglot runtime where Python logic and JavaScript logic can coexist in one source file with an explicit, understandable data bridge.

## License

No license has been specified yet. Check the repository for licensing information before reusing or redistributing this project.
