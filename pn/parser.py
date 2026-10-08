import ast


def parse(source_code):
    python_start_tag = "[python]"
    python_end_tag = "[/python]"

    js_start_tag = "[js]"
    js_end_tag = "[/js]"

    python_start = source_code.find(python_start_tag)
    python_end = source_code.find(python_end_tag)

    if python_start == -1:
        raise SyntaxError("Missing [python] block")

    if python_end == -1:
        raise SyntaxError("Missing [/python] block")

    if python_end < python_start:
        raise SyntaxError("[/python] appears before [python]")

    js_start = source_code.find(js_start_tag)
    js_end = source_code.find(js_end_tag)

    if js_start == -1:
        raise SyntaxError("Missing [js] block")

    if js_end == -1:
        raise SyntaxError("Missing [/js] block")

    if js_end < js_start:
        raise SyntaxError("[/js] appears before [js]")

    python_start += len(python_start_tag)
    js_start += len(js_start_tag)

    python_code = source_code[python_start:python_end].strip()
    js_code = source_code[js_start:js_end].strip()

    if not python_code:
        raise SyntaxError("Empty [python] block")

    if not js_code:
        raise SyntaxError("Empty [js] block")

    python_program = ast.parse(python_code)

    return python_program, js_code