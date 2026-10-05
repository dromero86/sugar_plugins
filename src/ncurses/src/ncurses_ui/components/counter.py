"""Componente Counter: spin box numerico."""
import curses

from ncurses_ui.components.base import FieldComponent
from ncurses_ui.kernel.input import is_enter, is_escape
from ncurses_ui.kernel.renderer import safe_addstr


class Counter(FieldComponent):
    """Valor numerico ajustable con limites y paso."""

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.min = self.config.get("min")
        self.max = self.config.get("max")
        self.step = self.config.get("step", 1)
        if self.value is None:
            self.value = self.min if self.min is not None else 0

    def clamp(self, value):
        if self.min is not None:
            value = max(self.min, value)
        if self.max is not None:
            value = min(self.max, value)
        return value

    def render(self, window, region):
        label = self.config.get("label", "")
        body = f"[ - ] {self.value} [ + ]"
        text = f"{label}: {body}" if label else body
        safe_addstr(window, region.y, region.x, text, 0, region.width)

    def handle_key(self, key):
        if is_enter(key):
            return "done"
        if is_escape(key):
            return "cancel"
        if key in (curses.KEY_LEFT, ord("-")):
            self.value = self.clamp(self.value - self.step)
        elif key in (curses.KEY_RIGHT, ord("+"), ord("=")):
            self.value = self.clamp(self.value + self.step)
        return None
