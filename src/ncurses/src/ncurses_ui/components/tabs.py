"""Componentes de pestanas y vistas multiples."""
import curses

from ncurses_ui.components.base import FieldComponent, StaticComponent, draw_child
from ncurses_ui.kernel.input import is_enter, is_escape
from ncurses_ui.kernel.renderer import Region, safe_addstr


class MultiView(StaticComponent):
    """Muestra una celda de N segun `index`."""

    def cells(self):
        return self.config.get("cells", [])

    def index(self):
        cells = self.cells()
        if not cells:
            return 0
        return min(max(0, int(self.config.get("index", 0))), len(cells) - 1)

    def render(self, window, region):
        cells = self.cells()
        if not cells:
            return
        cell = cells[self.index()]
        body = cell.get("body", cell) if isinstance(cell, dict) else cell
        child = self._create_child(body)
        if child is not None:
            draw_child(child, window, region)

    def result(self):
        return {"status": "ok", "index": self.index()}


class Carousel(MultiView):
    """MultiView con navegacion por indice."""


class TabBar(FieldComponent):
    """Barra de pestanas seleccionable."""

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.index = max(0, int(self.config.get("index", 0)))

    def tabs(self):
        return self.config.get("tabs", self.config.get("cells", []))

    def labels(self):
        out = []
        for i, tab in enumerate(self.tabs()):
            if isinstance(tab, dict):
                out.append(str(tab.get("header", tab.get("value", i))))
            else:
                out.append(str(tab))
        return out

    def render(self, window, region):
        labels = self.labels()
        if not labels:
            return
        self.index = min(self.index, len(labels) - 1)
        x = region.x
        for i, label in enumerate(labels):
            text = f"[{label}]" if i == self.index else f" {label} "
            safe_addstr(window, region.y, x, text, 0, region.width)
            x += len(text) + 1

    def handle_key(self, key):
        labels = self.labels()
        if is_escape(key):
            return "cancel"
        if is_enter(key):
            return "done"
        if not labels:
            return None
        if key in (curses.KEY_LEFT, ord("h")):
            self.index = (self.index - 1) % len(labels)
        elif key in (curses.KEY_RIGHT, ord("l")):
            self.index = (self.index + 1) % len(labels)
        return None

    def result(self):
        return {"status": "ok", "index": self.index}


class TabView(StaticComponent):
    """TabBar + celda activa."""

    def render(self, window, region):
        cells = self.config.get("cells", [])
        if not cells:
            return
        index = min(max(0, int(self.config.get("index", 0))), len(cells) - 1)
        x = region.x
        for i, cell in enumerate(cells):
            header = str(cell.get("header", i)) if isinstance(cell, dict) else str(cell)
            text = f"[{header}]" if i == index else f" {header} "
            safe_addstr(window, region.y, x, text, 0, region.width)
            x += len(text) + 1
        active = cells[index]
        body = active.get("body", active) if isinstance(active, dict) else active
        child = self._create_child(body)
        if child is not None and region.height > 1:
            draw_child(child, window, Region(region.y + 1, region.x, region.height - 1, region.width))

    def result(self):
        cells = self.config.get("cells", [])
        index = min(max(0, int(self.config.get("index", 0))), max(0, len(cells) - 1))
        return {"status": "ok", "index": index}
