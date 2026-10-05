"""Componentes de seleccion: select, richselect, combo, suggest."""
import curses

from ncurses_ui.components.base import FieldComponent
from ncurses_ui.kernel.input import is_backspace, is_enter, is_escape, is_printable
from ncurses_ui.kernel.renderer import render_template, safe_addstr


class Select(FieldComponent):
    """Seleccion unica con `< valor >`."""

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.options = self._normalize(self.config.get("options", []))
        self.index = self._initial_index()
        self.open = False

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

    def label(self):
        if not self.options:
            return ""
        return str(self.options[self.index][1])

    def render(self, window, region):
        label = self.config.get("label", "")
        body = f"< {self.label()} >"
        safe_addstr(window, region.y, region.x, f"{label}: {body}" if label else body, 0, region.width)
        if self.open:
            for i, (_, value) in enumerate(self.options[:max(0, region.height - 1)]):
                marker = ">" if i == self.index else " "
                safe_addstr(window, region.y + 1 + i, region.x, f"{marker} {value}", 0, region.width)

    def handle_key(self, key):
        if self.open:
            if is_escape(key):
                self.open = False
                return None
            if is_enter(key):
                self.open = False
                return "done"
            if key in (curses.KEY_UP, ord("k")):
                self.index = max(0, self.index - 1)
            elif key in (curses.KEY_DOWN, ord("j")) and self.options:
                self.index = min(len(self.options) - 1, self.index + 1)
            return None
        if is_escape(key):
            return "cancel"
        if is_enter(key):
            if self.options:
                self.open = True
                return None
            return "done"
        if not self.options:
            return None
        if key in (curses.KEY_LEFT, ord("h")):
            self.index = (self.index - 1) % len(self.options)
        elif key in (curses.KEY_RIGHT, ord("l")):
            self.index = (self.index + 1) % len(self.options)
        return None

    def result(self):
        if not self.options:
            return {"status": "ok", "value": None}
        return {"status": "ok", "value": self.options[self.index][0]}


class RichSelect(Select):
    """Select con `template` sobre el valor."""

    def label(self):
        if not self.options:
            return ""
        _, value = self.options[self.index]
        template = self.config.get("template")
        if template and isinstance(value, dict):
            return render_template(template, value)
        return str(value)


class Combo(Select):
    """Select editable: texto + popup de opciones filtrado."""

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.text = "" if self.config.get("value") is None else str(self.config.get("value"))
        self.open = False
        self.index = 0

    def label(self):
        return self.text

    def filtered(self):
        query = self.text.lower()
        if not query:
            return list(self.options)
        return [(oid, value) for oid, value in self.options if query in str(value).lower()]

    def render(self, window, region):
        label = self.config.get("label", "")
        body = f"< {self.text} >"
        safe_addstr(window, region.y, region.x, f"{label}: {body}" if label else body, 0, region.width)
        if self.open:
            for i, (_, value) in enumerate(self.filtered()[:max(0, region.height - 1)]):
                marker = ">" if i == self.index else " "
                safe_addstr(window, region.y + 1 + i, region.x, f"{marker} {value}", 0, region.width)

    def handle_key(self, key):
        if self.open:
            options = self.filtered()
            if is_escape(key):
                self.open = False
                return None
            if is_enter(key):
                if options:
                    self.text = str(options[min(self.index, len(options) - 1)][1])
                self.open = False
                return "done"
            if key in (curses.KEY_UP, ord("k")):
                self.index = max(0, self.index - 1)
            elif key in (curses.KEY_DOWN, ord("j")) and options:
                self.index = min(len(options) - 1, self.index + 1)
            elif is_backspace(key):
                self.text = self.text[:-1]
                self.index = 0
            elif is_printable(key):
                self.text += chr(key)
                self.index = 0
            return None
        if is_escape(key):
            return "cancel"
        if is_enter(key):
            if self.options:
                self.open = True
                self.index = 0
                return None
            return "done"
        if is_backspace(key):
            self.text = self.text[:-1]
            return None
        if is_printable(key):
            self.text += chr(key)
        return None

    def result(self):
        return {"status": "ok", "value": self.text}


class Suggest(Combo):
    """Sugerencias: como Combo, filtrando las opciones mientras se tipea."""
