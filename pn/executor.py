def execute(program, context=None):
    if context is None:
        context = {}

    exec(
        compile(program, "<pynode>", "exec"),
        context,
        context
    )

    return context