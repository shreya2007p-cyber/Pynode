
from dataclasses import dataclass
import ast as python_ast


@dataclass(frozen=True)
class Module:
    """AST node representing a complete Pynode program."""

    python_code: str
    javascript_code: str

    def __iter__(self):
        """Preserve compatibility with the original parser API."""
        yield python_ast.parse(self.python_code)
        yield self.javascript_code
