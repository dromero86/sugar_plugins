"""Componente Slider: seleccion numerica con barra."""
import curses

from ncurses_ui.components.base import FieldComponent
from ncurses_ui.kernel.input import is_enter, is_escape
from ncurses_ui.kernel.renderer import safe_addstr


class Slider(FieldComponent):
    """Valor numerico ajustable con barra visual."""

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.min = self.config.get("min", 0)
        self.max = self.config.get("max", 100)
        self.step = self.config.get("step", 1)
        self.bar_width = int(self.config.get("bar_width", 20))
        if self.value is None:
            self.value = self.min

    def bar(self):
        span = self.max - self.min
        filled = 0 if span <= 0 else round(self.bar_width * (self.value - self.min) / span)
        return "[" + "#" * filled + "-" * (self.bar_width - filled) + "]"

    def clamp(self, value):
        return max(self.min, min(self.max, value))

    def render(self, window, region):
        label = self.config.get("label", "")
        body = f"{self.bar()} {self.value}"
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
