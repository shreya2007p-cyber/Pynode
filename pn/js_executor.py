
import json
import os
import subprocess
import tempfile
from pathlib import Path
from pn.values import validate_context


def execute_js(js_code, context=None):
    if context is None:
        context = {}

    try:
        validate_context(context)
        context_json = json.dumps(context, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise RuntimeError(
            f"Python context is not JSON-serializable: {error}"
        ) from error

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".json",
        delete=False
    ) as result_file:
        result_path = result_file.name

    try:
        wrapped_js = f"""
const fs = require("node:fs");
const pynode = {context_json};

{js_code}

try {{
    const returnedJson = JSON.stringify(pynode);

    if (returnedJson === undefined) {{
        throw new Error("JSON.stringify returned undefined");
    }}

    fs.writeFileSync(
        process.env.PYNODE_RESULT_FILE,
        returnedJson,
        "utf8"
    );
}} catch (error) {{
    process.stderr.write(
        "__PYNODE_SERIALIZATION_ERROR__" + error.message + "\\n"
    );
    process.exitCode = 1;
}}
"""

        env = os.environ.copy()
        env["PYNODE_RESULT_FILE"] = result_path

        result = subprocess.run(
            ["node", "-e", wrapped_js],
            capture_output=True,
            text=True,
            env=env
        )

        if result.returncode != 0:
            marker = "__PYNODE_SERIALIZATION_ERROR__"

            for line in result.stderr.splitlines():
                if line.startswith(marker):
                    message = line[len(marker):]
                    raise RuntimeError(
                        "JavaScript context is not JSON-serializable: "
                        f"{message}"
                    )

            raise RuntimeError(
                f"JavaScript execution failed:\n{result.stderr}"
            )

        print(result.stdout, end="")

        try:
            returned_json = Path(result_path).read_text(
                encoding="utf-8"
            )
            return json.loads(returned_json)

        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError(
                "JavaScript did not return a valid context"
            ) from error

    finally:
        try:
            os.remove(result_path)
        except FileNotFoundError:
            pass
