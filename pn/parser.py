
import ast as python_ast

from pn.ast import Module
from pn.lexer import tokenize


def parse(source_code: str) -> Module:
    tokens = tokenize(source_code)

    python_starts = [t for t in tokens if t.type == "PYTHON_START"]
    python_ends = [t for t in tokens if t.type == "PYTHON_END"]
    js_starts = [t for t in tokens if t.type == "JS_START"]
    js_ends = [t for t in tokens if t.type == "JS_END"]

    if len(python_starts) > 1:
        raise SyntaxError("Duplicate [python] block")
    if len(js_starts) > 1:
        raise SyntaxError("Duplicate [js] block")
    if len(python_ends) > 1:
        raise SyntaxError("Duplicate [/python] block")
    if len(js_ends) > 1:
        raise SyntaxError("Duplicate [/js] block")

    if not python_starts:
        raise SyntaxError("Missing [python] block")
    if not python_ends:
        raise SyntaxError("Missing [/python] block")
    if not js_starts:
        raise SyntaxError("Missing [js] block")
    if not js_ends:
        raise SyntaxError("Missing [/js] block")

    ps, pe = python_starts[0], python_ends[0]
    js, je = js_starts[0], js_ends[0]

    if pe.line < ps.line:
        raise SyntaxError("[/python] appears before [python]")
    if je.line < js.line:
        raise SyntaxError("[/js] appears before [js]")

    # Use token positions to preserve the exact source between tags.
    tag_tokens = [
        t for t in tokens
        if t.type in {
            "PYTHON_START", "PYTHON_END", "JS_START", "JS_END"
        }
    ]

    positions = []
    cursor = 0
    for token in tokens:
        positions.append((token, cursor))
        cursor += len(token.value)

    offsets = {id(token): pos for token, pos in positions}

    ps_pos = offsets[id(ps)]
    pe_pos = offsets[id(pe)]
    js_pos = offsets[id(js)]
    je_pos = offsets[id(je)]

    if js_pos < ps_pos:
        raise SyntaxError("[js] block must come after [python] block")

    if ps_pos < js_pos < pe_pos:
        raise SyntaxError("[python] and [js] blocks overlap")

    before_python = source_code[:ps_pos]
    python_code = source_code[ps_pos + len("[python]"):pe_pos].strip()
    between_blocks = source_code[pe_pos + len("[/python]"):js_pos]
    js_code = source_code[js_pos + len("[js]"):je_pos].strip()
    after_javascript = source_code[je_pos + len("[/js]"):]

    if before_python.strip():
        raise SyntaxError("Unexpected text before [python] block")
    if between_blocks.strip():
        raise SyntaxError(
            "Unexpected text between [python] and [js] blocks"
        )
    if after_javascript.strip():
        raise SyntaxError("Unexpected text after [/js] block")
    if not python_code:
        raise SyntaxError("Empty [python] block")
    if not js_code:
        raise SyntaxError("Empty [js] block")

    try:
        python_ast.parse(python_code)
    except SyntaxError as exc:
        raise SyntaxError(f"Invalid Python syntax: {exc.msg}") from exc

    return Module(
        python_code=python_code,
        javascript_code=js_code,
    )
