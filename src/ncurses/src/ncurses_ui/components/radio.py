"""Componente Radio: seleccion unica entre opciones."""
import curses

from ncurses_ui.components.base import FieldComponent
from ncurses_ui.kernel.input import is_enter, is_escape
from ncurses_ui.kernel.renderer import safe_addstr


class Radio(FieldComponent):
    """Grupo de opciones mutuamente excluyentes."""

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.options = self._normalize(self.config.get("options", []))
        self.index = self._initial_index()

    @staticmethod
    def _normalize(options):
        out = []
        for i, opt in enumerate(options):
            if isinstance(opt, dict):
                out.append((opt.get("id", i), opt.get("value", opt.get("id", i))))
            else:
                out.append((opt, opt))
        return out

    def _initial_index(self):
        for i, (option_id, _) in enumerate(self.options):
            if option_id == self.config.get("value"):
                return i
        return 0

    def render(self, window, region):
        for i, (_, label) in enumerate(self.options):
            if i >= region.height:
                break
            mark = "(*)" if i == self.index else "( )"
            safe_addstr(window, region.y + i, region.x, f"{mark} {label}", 0, region.width)

    def handle_key(self, key):
        if is_enter(key):
            return "done"
        if is_escape(key):
            return "cancel"
        if not self.options:
            return None
        if key in (curses.KEY_UP, ord("k")):
            self.index = (self.index - 1) % len(self.options)
        elif key in (curses.KEY_DOWN, ord("j")):
            self.index = (self.index + 1) % len(self.options)
        return None

    def result(self):
        if not self.options:
            return {"status": "ok", "value": None}
        return {"status": "ok", "value": self.options[self.index][0]}
