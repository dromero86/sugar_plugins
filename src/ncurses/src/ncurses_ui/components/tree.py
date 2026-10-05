"""Componente Tree: estructura jerarquica con expand/collapse."""
import curses

from ncurses_ui.components.base import Component
from ncurses_ui.kernel.input import is_enter, is_escape
from ncurses_ui.kernel.renderer import Region, safe_addstr
from ncurses_ui.kernel.screen import TerminalScreen


class Tree(Component):
    """Arbol navegable a partir de una lista plana con campo padre."""

    focusable = True

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.items = self._items()
        self.id_field = self.config.get("id_field", "id")
        self.parent_field = self.config.get("parent_id", self.config.get("parent", "parent"))
        self.text_field = self.config.get("text", "value")
        self.nodes = self._build_tree()
        self.expanded = set()
        self.cursor = 0
        self.offset = 0

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

    def _build_tree(self):
        by_id = {}
        for item in self.items:
            by_id[item.get(self.id_field)] = {"item": item, "children": []}
        roots = []
        for item in self.items:
            node = by_id.get(item.get(self.id_field))
            parent = item.get(self.parent_field)
            if parent is not None and parent in by_id and parent != item.get(self.id_field):
                by_id[parent]["children"].append(node)
            else:
                roots.append(node)
        return roots

    def visible(self):
        rows = []

        def walk(nodes, depth):
            for node in nodes:
                rows.append((depth, node))
                if node["item"].get(self.id_field) in self.expanded:
                    walk(node["children"], depth + 1)

        walk(self.nodes, 0)
        return rows

    def _label(self, node):
        item = node["item"]
        return str(item.get(self.text_field, item.get(self.id_field, ""))) if isinstance(item, dict) else str(item)

    def render(self, window, region, first=0):
        rows = self.visible()
        for i, (depth, node) in enumerate(rows[first:first + region.height]):
            index = first + i
            marker = ">" if index == self.cursor else " "
            expanded = node["item"].get(self.id_field) in self.expanded
            arrow = ("v" if expanded else ">") if node["children"] else " "
            safe_addstr(window, region.y + i, region.x, f"{marker}{arrow} {'  ' * depth}{self._label(node)}", 0, region.width)

    def _current(self):
        rows = self.visible()
        if not rows or self.cursor >= len(rows):
            return None
        return rows[self.cursor][1]

    def handle_key(self, key):
        rows = self.visible()
        if is_escape(key) or key in (ord("q"), ord("Q")):
            return "quit"
        if is_enter(key):
            return "done"
        if key in (curses.KEY_UP, ord("k")):
            self.cursor = max(0, self.cursor - 1)
        elif key in (curses.KEY_DOWN, ord("j")):
            self.cursor = min(max(0, len(rows) - 1), self.cursor + 1)
        elif key in (curses.KEY_RIGHT, ord("l")):
            node = self._current()
            if node and node["children"]:
                self.expanded.add(node["item"].get(self.id_field))
        elif key in (curses.KEY_LEFT, ord("h")):
            node = self._current()
            if node:
                self.expanded.discard(node["item"].get(self.id_field))
        return None

    def _visible_offset(self, height):
        if self.cursor < self.offset:
            return self.cursor
        if self.cursor >= self.offset + height:
            return self.cursor - height + 1
        return self.offset

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
        rows = self.visible()
        if not rows or self.cursor >= len(rows):
            return {"status": "ok", "selected": None}
        return {"status": "ok", "selected": rows[self.cursor][1]["item"]}
