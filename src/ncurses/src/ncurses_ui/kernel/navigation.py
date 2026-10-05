"""Pila de navegacion entre vistas (inline)."""


class ViewStack:
    """Pila LIFO de vistas (configs inline)."""

    def __init__(self):
        self.stack = []

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        return self.stack.pop() if self.stack else None

    def current(self):
        return self.stack[-1] if self.stack else None

    def reset(self):
        self.stack.clear()

    def __len__(self):
        return len(self.stack)
