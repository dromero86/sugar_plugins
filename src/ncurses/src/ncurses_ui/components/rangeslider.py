"""Componente RangeSlider: rango numerico con dos handles."""
import curses

from ncurses_ui.components.slider import Slider
from ncurses_ui.kernel.input import is_enter, is_escape


class RangeSlider(Slider):
    """Rango `[lo, hi]` con dos handles (Tab alterna el activo)."""

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        value = self.config.get("value") or [self.min, self.max]
        self.value = [value[0], value[1]]
        self.active = 0

    def bar(self):
        span = self.max - self.min
        if span <= 0:
            return "[" + "-" * self.bar_width + "]"
        low = round(self.bar_width * (self.value[0] - self.min) / span)
        high = round(self.bar_width * (self.value[1] - self.min) / span)
        cells = ["-"] * self.bar_width
        for i in range(max(0, low), min(self.bar_width, high + 1)):
            cells[i] = "#"
        return "[" + "".join(cells) + "]"

    def handle_key(self, key):
        if is_enter(key):
            return "done"
        if is_escape(key):
            return "cancel"
        if key in (curses.KEY_UP, ord("k"), 9):
            self.active = (self.active + 1) % 2
        elif key in (curses.KEY_LEFT, ord("-")):
            self.value[self.active] = max(self.min, self.value[self.active] - self.step)
            if self.active == 0 and self.value[0] > self.value[1]:
                self.value[0] = self.value[1]
        elif key in (curses.KEY_RIGHT, ord("+"), ord("=")):
            self.value[self.active] = min(self.max, self.value[self.active] + self.step)
            if self.active == 1 and self.value[1] < self.value[0]:
                self.value[1] = self.value[0]
        return None
