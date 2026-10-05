"""Componente Text: campo de texto de una linea."""
from ncurses_ui.components.base import FieldComponent
from ncurses_ui.kernel.input import is_backspace, is_enter, is_escape, is_printable
from ncurses_ui.kernel.renderer import safe_addstr


class Text(FieldComponent):
    """Campo de texto editable."""

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.value = "" if self.value is None else str(self.value)
        self.max_length = int(self.config.get("max_length", 80))

    def display(self):
        if self.value == "" and self.config.get("placeholder"):
            return self.config["placeholder"]
        return self.value

    def render(self, window, region):
        label = self.config.get("label", "")
        text = f"{label}: {self.display()}" if label else self.display()
        safe_addstr(window, region.y, region.x, text, 0, region.width)

    def handle_key(self, key):
        if is_enter(key):
            return "done"
        if is_escape(key):
            return "cancel"
        if is_backspace(key):
            self.value = self.value[:-1]
            return None
        if is_printable(key) and len(self.value) < self.max_length:
            self.value += chr(key)
        return None
