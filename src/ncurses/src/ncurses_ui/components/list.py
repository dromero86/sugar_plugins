"""Componente List: lista seleccionable."""
import curses

from ncurses_ui.components.base import Component
from ncurses_ui.kernel.input import is_enter, is_escape
from ncurses_ui.kernel.renderer import Region, render_template, safe_addstr
from ncurses_ui.kernel.screen import TerminalScreen


class List(Component):
    """Lista de items con `template` y seleccion simple o multiple."""

    focusable = True

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.items = self._items()
        self.template = self.config.get("template", "")
        self.select = self.config.get("select", "row")
        self.cursor = 0
        self.offset = 0
        self.marked = set()

    def _items(self):
        data = self.config.get("data")
        if isinstance(data, list):
            return data
        if isinstance(data, str) and self.context is not None:
            handler = getattr(self.context, "memory_handler", None)
            value = handler.get_variable(data) if handler else None
            if isinstance(value, list):
                return value
        return []

    def text(self, item):
        if self.template:
            data = item if isinstance(item, dict) else {"value": item}
            return render_template(self.template, data)
        return str(item)

    def render(self, window, region, first=0):
        for i, item in enumerate(self.items[first:first + region.height]):
            index = first + i
            marker = ">" if index == self.cursor else ("+" if index in self.marked else " ")
            safe_addstr(window, region.y + i, region.x, f"{marker} {self.text(item)}", 0, region.width)

    def handle_key(self, key):
        if is_escape(key) or key in (ord("q"), ord("Q")):
            return "quit"
        if is_enter(key):
            item = self.items[self.cursor] if self.items else None
            action = self.dispatch_event("on_item_click", {"item": item})
            if action and action.get("action") in ("navigate", "back"):
                return action
            return "done"
        if key in (curses.KEY_UP, ord("k")):
            self.cursor = max(0, self.cursor - 1)
        elif key in (curses.KEY_DOWN, ord("j")):
            self.cursor = min(max(0, len(self.items) - 1), self.cursor + 1)
        elif key == ord(" ") and self.select == "multiselect":
            self.marked.symmetric_difference_update({self.cursor})
        return None

    def _visible_offset(self, height):
        if self.cursor < self.offset:
            return self.cursor
        if self.cursor >= self.offset + height:
            return self.cursor - height + 1
        return self.offset

    def handle_mouse(self, x, y, region):
        if not (region.x <= x < region.x + region.width and region.y <= y < region.y + region.height):
            return None
        row = self.offset + (y - region.y)
        if 0 <= row < len(self.items):
            self.cursor = row
            return "done"
        return None

    def draw(self, window, region):
        self.offset = self._visible_offset(region.height)
        self.render(window, region, self.offset)

    def run(self):
        with TerminalScreen(self.manager) as screen:
            while True:
                height, width = screen.getmaxyx()
                self.offset = self._visible_offset(height)
                self.render(screen, Region(0, 0, height, width), self.offset)
                screen.refresh()
                if self.handle_key(screen.getch()) in ("done", "quit"):
                    break
        return self.result()

    def result(self):
        if not self.items:
            return {"status": "ok", "selected": None}
        if self.select == "multiselect":
            selected = [self.items[i] for i in sorted(self.marked)]
            if not selected:
                selected = [self.items[self.cursor]]
            return {"status": "ok", "selected": selected}
        return {"status": "ok", "selected": self.items[self.cursor]}
