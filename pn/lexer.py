
from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    type: str
    value: str
    line: int


TAGS = {
    "[python]": "PYTHON_START",
    "[/python]": "PYTHON_END",
    "[js]": "JS_START",
    "[/js]": "JS_END",
}


def tokenize(source: str) -> list[Token]:
    """Tokenize Pynode's outer block tags and preserve code sections."""
    tokens = []
    position = 0
    line = 1

    while position < len(source):
        matched_tag = None

        for tag, token_type in TAGS.items():
            if source.startswith(tag, position):
                matched_tag = (tag, token_type)
                break

        if matched_tag:
            tag, token_type = matched_tag
            tokens.append(Token(token_type, tag, line))
            line += tag.count("\n")
            position += len(tag)
            continue

        next_tag_positions = [
            source.find(tag, position) for tag in TAGS
        ]
        next_tag_positions = [
            p for p in next_tag_positions if p != -1
        ]

        end = min(next_tag_positions) if next_tag_positions else len(source)
        text = source[position:end]

        if text:
            tokens.append(Token("TEXT", text, line))
            line += text.count("\n")

        position = end

    return tokens
