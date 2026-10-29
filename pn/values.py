
"""Pynode's shared value model.

Initially supported values:
None, bool, int, float, str, list, and dict with string keys.
"""

import math


def validate_value(value, path="value"):
    """Validate a value recursively for Python-JavaScript exchange."""

    # Check bool before int because bool is a subclass of int in Python.
    if value is None or isinstance(value, (bool, str)):
        return

    if isinstance(value, int):
        return

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(
                f"{path} contains a non-finite number: {value!r}"
            )
        return

    if isinstance(value, list):
        for index, item in enumerate(value):
            validate_value(item, f"{path}[{index}]")
        return

    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(
                    f"{path} contains a non-string dictionary key: "
                    f"{key!r}"
                )
            validate_value(item, f"{path}.{key}")
        return

    raise TypeError(
        f"{path} contains an unsupported value type: "
        f"{type(value).__name__}"
    )


def validate_context(context):
    """Validate a shared context dictionary."""
    if not isinstance(context, dict):
        raise TypeError("Pynode context must be a dictionary")

    validate_value(context, "context")
