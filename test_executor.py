import ast

from pn.executor import execute


program = ast.parse("""
name = "Shreya"
age = 20
""")

ctx = execute(program)

print(ctx["name"])
print(ctx["age"])