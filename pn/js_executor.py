import subprocess


def execute_js(js_code):
    result = subprocess.run(
        ["node", "-e", js_code],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"JavaScript execution failed:\n{result.stderr}"
        )

    print(result.stdout, end="")