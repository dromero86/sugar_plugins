"""Componente Checkbox: casilla de dos estados."""
from ncurses_ui.components.base import FieldComponent
from ncurses_ui.kernel.input import is_enter, is_escape
from ncurses_ui.kernel.renderer import safe_addstr


class Checkbox(FieldComponent):
    """Casilla booleana `[X]`/`[ ]`."""

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.value = bool(self.config.get("value", False))

    def box(self):
        return "[X]" if self.value else "[ ]"

    def render(self, window, region):
        label = self.config.get("label", "")
        safe_addstr(window, region.y, region.x, f"{self.box()} {label}".rstrip(), 0, region.width)

    def handle_key(self, key):
        if is_enter(key):
            return "done"
        if is_escape(key):
            return "cancel"
        if key in (ord(" "), ord("x")):
            self.value = not self.value
        return None
