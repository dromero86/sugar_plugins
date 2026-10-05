"""Componente Textarea: campo de texto multilinea."""
from ncurses_ui.components.text import Text
from ncurses_ui.kernel.input import is_backspace, is_enter, is_escape, is_printable
from ncurses_ui.kernel.renderer import safe_addstr


class Textarea(Text):
    """Campo multilinea: Enter inserta salto de linea, Esc finaliza."""

    def render(self, window, region):
        label = self.config.get("label", "")
        lines = ([f"{label}:"] if label else []) + self.value.split("\n")
        for i, line in enumerate(lines[:region.height]):
            safe_addstr(window, region.y + i, region.x, line, 0, region.width)

    def handle_key(self, key):
        if is_escape(key):
            return "done"
        if is_backspace(key):
            self.value = self.value[:-1]
            return None
        if is_enter(key):
            self.value += "\n"
            return None
        if is_printable(key) and len(self.value) < self.max_length:
            self.value += chr(key)
        return None
