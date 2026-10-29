
def execute(program, context=None):
    if context is None:
        context = {}

    variables = context.data if hasattr(context, "data") else context

    # Keep Python's internal variables out of the shared data.
    exec_globals = {"__builtins__": __builtins__}
    exec_globals.update(variables)

    compiled_program = compile(program, "<pynode>", "exec")
    exec(compiled_program, exec_globals, exec_globals)

    variables.update({
        key: value
        for key, value in exec_globals.items()
        if not key.startswith("__")
    })

    return context
