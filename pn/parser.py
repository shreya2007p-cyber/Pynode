import ast



def parse(source_code):
    python_start_tag = "[python]"
    python_end_tag = "[/python]"

    js_start_tag = "[js]"
    js_end_tag = "[/js]"

    if source_code.count(python_start_tag) > 1:
        raise SyntaxError("Duplicate [python] block")

    if source_code.count(js_start_tag) > 1:
        raise SyntaxError("Duplicate [js] block")

    if source_code.count(python_end_tag) > 1:
        raise SyntaxError("Duplicate [/python] block")

    if source_code.count(js_end_tag) > 1:
        raise SyntaxError("Duplicate [/js] block")

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


    if js_start < python_end and python_start < js_end:
        raise SyntaxError("[python] and [js] blocks overlap")

    if js_start < python_start:
        raise SyntaxError("[js] block must come after [python] block")


    # Reject non-whitespace text outside the two blocks.
    before_python = source_code[:python_start]
    between_blocks = source_code[python_end + len(python_end_tag):js_start]
    after_javascript = source_code[js_end + len(js_end_tag):]

    if before_python.strip():
        raise SyntaxError("Unexpected text before [python] block")

    if between_blocks.strip():
        raise SyntaxError("Unexpected text between [python] and [js] blocks")

    if after_javascript.strip():
        raise SyntaxError("Unexpected text after [/js] block")

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
