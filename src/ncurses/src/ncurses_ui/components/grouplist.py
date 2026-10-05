"""Componente GroupList: lista agrupada por un campo."""
import curses

from ncurses_ui.components.list import List
from ncurses_ui.kernel.input import is_enter, is_escape
from ncurses_ui.kernel.renderer import safe_addstr


class GroupList(List):
    """Lista con headers de grupo insertados por `group_by`."""

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.rows = self._build_rows()

    def _build_rows(self):
        group_by = self.config.get("group_by")
        rows = []
        current = object()
        for index, item in enumerate(self.items):
            if group_by and isinstance(item, dict):
                key = item.get(group_by)
                if key != current:
                    current = key
                    rows.append({"kind": "group", "label": str(key)})
            rows.append({"kind": "item", "index": index})
        return rows

    def _row_for_item(self, item_index):
        for position, row in enumerate(self.rows):
            if row["kind"] == "item" and row["index"] == item_index:
                return position
        return 0

    def render(self, window, region, first=0):
        for i, row in enumerate(self.rows[first:first + region.height]):
            if row["kind"] == "group":
                safe_addstr(window, region.y + i, region.x, f"[{row['label']}]", 0, region.width)
            else:
                item = self.items[row["index"]]
                marker = ">" if row["index"] == self.cursor else " "
                safe_addstr(window, region.y + i, region.x, f"{marker} {self.text(item)}", 0, region.width)

    def handle_key(self, key):
        if is_escape(key) or key in (ord("q"), ord("Q")):
            return "quit"
        if is_enter(key):
            return "done"
        if key in (curses.KEY_UP, ord("k")):
            self._move(-1)
        elif key in (curses.KEY_DOWN, ord("j")):
            self._move(1)
        return None

    def _move(self, delta):
        position = self._row_for_item(self.cursor) + delta
        while 0 <= position < len(self.rows) and self.rows[position]["kind"] != "item":
            position += delta
        if 0 <= position < len(self.rows):
            self.cursor = self.rows[position]["index"]

    def _visible_offset(self, height):
        position = self._row_for_item(self.cursor)
        if position < self.offset:
            return position
        if position >= self.offset + height:
            return position - height + 1
        return self.offset
