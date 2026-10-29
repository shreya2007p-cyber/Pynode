
class RuntimeContext:
    """Stores variables shared between Pynode language blocks."""

    def __init__(self):
        self.data = {}

    def set(self, name, value):
        """Store a value in the shared context."""
        self.data[name] = value

    def get(self, name, default=None):
        """Read a value from the shared context."""
        return self.data.get(name, default)

    def update(self, values):
        """Merge multiple values into the shared context."""
        self.data.update(values)

    def snapshot(self):
        """Return a copy of the current runtime data."""
        return self.data.copy()
