
import ast
import unittest

from pn.executor import execute
from pn.runtime import RuntimeContext
from pn.js_executor import execute_js
from pn.parser import parse


class TestRuntime(unittest.TestCase):


    def test_value_model_accepts_supported_values(self):
        from pn.values import validate_context

        context = {
            "none": None,
            "boolean": True,
            "integer": 42,
            "float": 3.14,
            "string": "Pynode",
            "list": [1, "two", False, None],
            "nested": {"score": 95},
        }

        validate_context(context)

    def test_value_model_rejects_set(self):
        from pn.values import validate_context

        with self.assertRaisesRegex(
            TypeError, "unsupported value type: set"
        ):
            validate_context({"items": {1, 2, 3}})

    def test_value_model_rejects_non_string_keys(self):
        from pn.values import validate_context

        with self.assertRaisesRegex(
            TypeError, "non-string dictionary key"
        ):
            validate_context({"metadata": {1: "invalid"}})

    def test_value_model_rejects_non_finite_numbers(self):
        from pn.values import validate_context

        with self.assertRaisesRegex(
            ValueError, "non-finite number"
        ):
            validate_context({"score": float("nan")})


    def test_python_variables_enter_context(self):

        context = RuntimeContext()
        program = ast.parse(
            'name = "Shreya"\nage = 20'
        )

        execute(program, context)

        self.assertEqual(context.data["name"], "Shreya")
        self.assertEqual(context.data["age"], 20)


    def test_execute_without_context(self):
        program = ast.parse('name = "Shreya"')

        context = execute(program)

        self.assertIsInstance(context, dict)
        self.assertEqual(context["name"], "Shreya")



    def test_non_serializable_context_raises_clear_error(self):
        with self.assertRaisesRegex(
            RuntimeError,
            "Python context is not JSON-serializable"
        ):
            execute_js(
                'console.log("This should not run");',
                {"items": {1, 2, 3}}
            )

    def test_non_serializable_javascript_context_raises_clear_error(self):
        with self.assertRaisesRegex(
            RuntimeError,
            "JavaScript context is not JSON-serializable"
        ):
            execute_js(
                "pynode.self = pynode;",
                {}
            )


    def test_javascript_reads_python_data(self):
        context = RuntimeContext()
        context.data["name"] = "Shreya"

        returned = execute_js(
            'console.log(pynode.name);',
            context.data
        )

        self.assertEqual(returned["name"], "Shreya")

    def test_javascript_data_returns_to_python(self):
        context = RuntimeContext()

        returned = execute_js(
            'pynode.score = 95;',
            context.data
        )

        context.data.update(returned)

        self.assertEqual(context.data["score"], 95)

    def test_javascript_error_is_detected(self):
        with self.assertRaises(RuntimeError):
            execute_js(
                'throw new Error("test failure");',
                {}
            )


    def test_javascript_block_before_python_is_rejected(self):
        source_code = """
[js]
console.log("Hello");
[/js]

[python]
name = "Shreya"
[/python]
"""

        with self.assertRaisesRegex(
            SyntaxError,
            r"\[js\] block must come after \[python\] block"
        ):
            parse(source_code)


    def test_missing_python_closing_tag_is_rejected(self):
        source_code = """
[python]
name = "Shreya"

[js]
console.log("Hello");
[/js]
"""

        with self.assertRaisesRegex(
            SyntaxError,
            r"Missing \[/python\] block"
        ):
            parse(source_code)


    def test_missing_javascript_closing_tag_is_rejected(self):
        source_code = """
[python]
name = "Shreya"
[/python]

[js]
console.log("Hello");
"""

        with self.assertRaisesRegex(
            SyntaxError,
            r"Missing \[/js\] block"
        ):
            parse(source_code)


    def test_duplicate_python_block_is_rejected(self):
        source_code = """
[python]
name = "Shreya"
[/python]

[python]
age = 20
[/python]

[js]
console.log("Hello");
[/js]
"""

        with self.assertRaisesRegex(
            SyntaxError,
            r"Duplicate \[python\] block"
        ):
            parse(source_code)


    def test_duplicate_javascript_block_is_rejected(self):
        source_code = """
[python]
name = "Shreya"
[/python]

[js]
console.log("First block");
[/js]

[js]
console.log("Second block");
[/js]
"""

        with self.assertRaisesRegex(
            SyntaxError,
            r"Duplicate \[js\] block"
        ):
            parse(source_code)


    def test_duplicate_python_closing_tag_is_rejected(self):
        source_code = """
[python]
name = "Shreya"
[/python]
[/python]

[js]
console.log("Hello");
[/js]
"""

        with self.assertRaisesRegex(
            SyntaxError,
            r"Duplicate \[/python\] block"
        ):
            parse(source_code)


    def test_duplicate_javascript_closing_tag_is_rejected(self):
        source_code = """
[python]
name = "Shreya"
[/python]

[js]
console.log("Hello");
[/js]
[/js]
"""

        with self.assertRaisesRegex(
            SyntaxError,
            r"Duplicate \[/js\] block"
        ):
            parse(source_code)


    def test_nested_javascript_block_is_rejected(self):
        source_code = """
[python]
name = "Shreya"

[js]
console.log("Hello");
[/js]

[/python]
"""

        with self.assertRaisesRegex(
            SyntaxError,
            r"\[python\] and \[js\] blocks overlap"
        ):
            parse(source_code)


    def test_valid_polyglot_source_is_parsed(self):
        source_code = """
[python]
name = "Shreya"
[/python]

[js]
console.log(pynode.name);
[/js]
"""

        python_program, js_code = parse(source_code)

        self.assertIsInstance(python_program, ast.Module)
        self.assertEqual(
             ast.literal_eval(python_program.body[0].value),
            "Shreya"
      )
        self.assertIn("console.log(pynode.name);", js_code)


    def test_empty_python_block_is_rejected(self):
        source_code = """
[python]
[/python]

[js]
console.log("Hello");
[/js]
"""

        with self.assertRaisesRegex(
            SyntaxError,
            r"Empty \[python\] block"
        ):
            parse(source_code)



    def test_empty_javascript_block_is_rejected(self):
        source_code = """
[python]
name = "Shreya"
[/python]

[js]
[/js]
"""

        with self.assertRaisesRegex(
            SyntaxError,
            r"Empty \[js\] block"
        ):
            parse(source_code)


    def test_invalid_python_syntax_is_rejected(self):
        source_code = """
[python]
if True
    name = "Shreya"
[/python]

[js]
console.log("Hello");
[/js]
"""

        with self.assertRaises(SyntaxError):
            parse(source_code)



    def test_text_before_python_block_is_rejected(self):
        source_code = """
Unexpected text here.

[python]
name = "Shreya"
[/python]

[js]
console.log(pynode.name);
[/js]
"""

        with self.assertRaisesRegex(
            SyntaxError,
            "Unexpected text before"
        ):
            parse(source_code)


    def test_text_between_blocks_is_rejected(self):
        source_code = """
[python]
name = "Shreya"
[/python]

Unexpected text here.

[js]
console.log(pynode.name);
[/js]
"""

        with self.assertRaisesRegex(
            SyntaxError,
            "Unexpected text between"
        ):
            parse(source_code)

    def test_text_after_javascript_block_is_rejected(self):
        source_code = """
[python]
name = "Shreya"
[/python]

[js]
console.log(pynode.name);
[/js]

Unexpected text here.
"""

        with self.assertRaisesRegex(
            SyntaxError,
            "Unexpected text after"
        ):
            parse(source_code)


    def test_execute_with_plain_dictionary_context(self):
        program = ast.parse(
            'name = "Shreya"\nscore = 95'
        )
        context = {}

        returned = execute(program, context)

        self.assertIs(returned, context)
        self.assertEqual(context["name"], "Shreya")
        self.assertEqual(context["score"], 95)


    def test_existing_variable_is_updated(self):
        context = {"score": 80}
        program = ast.parse("score = score + 15")

        execute(program, context)

        self.assertEqual(context["score"], 95)


    def test_python_internal_variables_are_not_shared(self):
        context = {}
        program = ast.parse('name = "Shreya"')

        execute(program, context)

        self.assertNotIn("__builtins__", context)
        self.assertEqual(context["name"], "Shreya")

    def test_empty_and_falsy_values_are_preserved(self):
        context = {
            "empty_string": "",
            "zero": 0,
            "false_value": False,
            "items": [],
        }

        result = execute_js(
            """
            pynode.empty_string = "";
            pynode.zero = 0;
            pynode.false_value = false;
            pynode.items = [];
            """,
            context,
        )

        self.assertEqual(result["empty_string"], "")
        self.assertEqual(result["zero"], 0)
        self.assertIs(result["false_value"], False)
        self.assertEqual(result["items"], [])

    def test_javascript_update_preserves_unrelated_values(self):
        context = {
            "name": "Shreya",
            "score": 80,
            "city": "Lucknow",
        }

        result = execute_js(
            "pynode.score = 95;",
            context,
        )

        self.assertEqual(result["score"], 95)
        self.assertEqual(result["name"], "Shreya")
        self.assertEqual(result["city"], "Lucknow")


    def test_set_and_get(self):
        from pn.runtime import RuntimeContext

        context = RuntimeContext()
        context.set("name", "Shreya")

        self.assertEqual(context.get("name"), "Shreya")

    def test_update_multiple_values(self):
        from pn.runtime import RuntimeContext

        context = RuntimeContext()
        context.update({"score": 95, "level": 4})

        self.assertEqual(context.get("score"), 95)
        self.assertEqual(context.get("level"), 4)

    def test_snapshot_is_independent_copy(self):
        from pn.runtime import RuntimeContext

        context = RuntimeContext()
        context.set("score", 95)

        snapshot = context.snapshot()
        snapshot["score"] = 0

        self.assertEqual(context.get("score"), 95)


    def test_javascript_nested_updates_return_to_python(self):
        from pn.js_executor import execute_js

        context = {
            "student": {
                "name": "Shreya",
                "marks": {"math": 95}
            }
        }

        result = execute_js(
            "pynode.student.marks.math = 99; "
            "pynode.student.marks.science = 92;",
            context
        )

        self.assertEqual(result["student"]["marks"]["math"], 99)
        self.assertEqual(result["student"]["marks"]["science"], 92)
        self.assertEqual(result["student"]["name"], "Shreya")


    def test_javascript_preserves_json_compatible_edge_values(self):
        from pn.js_executor import execute_js

        context = {
            "empty": "",
            "count": 0,
            "enabled": True,
            "disabled": False,
            "nothing": None,
            "items": [1, 2, 3],
        }

        result = execute_js(
            "pynode.empty = pynode.empty + 'ok'; "
            "pynode.count = pynode.count + 1; "
            "pynode.enabled = false; "
            "pynode.disabled = true; "
            "pynode.nothing = 'filled'; "
            "pynode.items.push(4);",
            context
        )

        self.assertEqual(result["empty"], "ok")
        self.assertEqual(result["count"], 1)
        self.assertFalse(result["enabled"])
        self.assertTrue(result["disabled"])
        self.assertEqual(result["nothing"], "filled")
        self.assertEqual(result["items"], [1, 2, 3, 4])


    def test_python_javascript_shared_context_round_trip(self):
        context = RuntimeContext()

        execute(
            'student = {"name": "Shreya", "score": 90}',
            context
        )

        js_result = execute_js(
            "pynode.student.score = 95;",
            context.data
        )

        context.update(js_result)

        self.assertEqual(context.get("student")["score"], 95)
        self.assertEqual(context.get("student")["name"], "Shreya")


    def test_bridge_rejects_non_finite_python_values(self):
        from pn.js_executor import execute_js

        with self.assertRaisesRegex(
            RuntimeError, "non-finite number"
        ):
            execute_js(
                "pynode.checked = true;",
                {"score": float("nan")},
            )

    def test_bridge_rejects_non_string_dictionary_keys(self):
        from pn.js_executor import execute_js

        with self.assertRaisesRegex(
            RuntimeError, "non-string dictionary key"
        ):
            execute_js(
                "pynode.checked = true;",
                {"metadata": {1: "invalid"}},
            )



if __name__ == "__main__":
    unittest.main()
