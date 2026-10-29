import sys
from pn.parser import parse
from pn.executor import execute
from pn.runtime import RuntimeContext
from pathlib import Path


from pn.js_executor import execute_js

VERSION = "0.1.0"


def show_help():
    print("Pynode - Polyglot Runtime")
    print()
    print("Usage:")
    print("  pn <command>")
    print()
    print("Commands:")
    print("  run <file>    Run a .pn file")
    print("  --version     Show Pynode version")
    print("  --help        Show this help message")


def main():
    if len(sys.argv) >= 2:
        command = sys.argv[1]

        if command == "--version":
            print(f"Pynode {VERSION}")
            return

        if command == "--help":
            show_help()
            return

        if command == "run":
            if len(sys.argv) < 3:
                print("Error: Please provide a .pn file")
                return

            file_path = sys.argv[2]
            if Path(file_path).suffix.lower() != ".pn":
                print("Pynode File Error: Only .pn files are supported")
                return


            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    source_code = file.read()
            except OSError as error:
                print(f"Pynode File Error: {error}")
                return


            print("Pynode: source code loaded")

            try:
                python_program, js_code = parse(source_code)
            except Exception as error:
                print(f"Pynode Error: {error}")
                return

            print("Pynode: source code parsed")


            context = RuntimeContext()

            try:
                execute(python_program, context)
            except Exception as error:
                print(f"Pynode Python Error: {error}")
                return


            try:
                context.data.update(execute_js(js_code, context.data))
            except RuntimeError as error:
                print(f"Pynode JS Error: {error}")
                return

            print("Pynode: execution completed")

            return
    print("Pynode CLI is working!")


if __name__ == "__main__":
    main()
