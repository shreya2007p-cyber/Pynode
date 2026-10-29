
import ast
import unittest

from pn.executor import execute
from pn.runtime import RuntimeContext
from pn.js_executor import execute_js
from pn.parser import parse


class TestRuntime(unittest.TestCase):
    
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

if __name__ == "__main__":
    unittest.main()
