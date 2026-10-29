
import unittest

from pn.lexer import tokenize


class TestLexer(unittest.TestCase):

    def test_recognizes_all_block_tags(self):
        source = "[python]\nx = 10\n[/python]\n[js]\ny = 20\n[/js]"
        tokens = tokenize(source)

        self.assertEqual(
            [t.type for t in tokens if t.type != "TEXT"],
            [
                "PYTHON_START",
                "PYTHON_END",
                "JS_START",
                "JS_END",
            ],
        )

    def test_preserves_source_code(self):
        source = "[python]\nx = 10\n[/python]"
        tokens = tokenize(source)

        text = "".join(t.value for t in tokens if t.type == "TEXT")
        self.assertEqual(text, "\nx = 10\n")

    def test_tracks_tag_line_numbers(self):
        source = "[python]\nx = 10\n[/python]"
        tokens = tokenize(source)

        self.assertEqual(tokens[0].line, 1)
        self.assertEqual(tokens[2].line, 3)

    def test_empty_source_returns_no_tokens(self):
        self.assertEqual(tokenize(""), [])

    def test_plain_text_is_preserved(self):
        source = "x = 10"
        tokens = tokenize(source)

        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, "TEXT")
        self.assertEqual(tokens[0].value, source)


if __name__ == "__main__":
    unittest.main()

