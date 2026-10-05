"""Componente DataTable (config estilo Webix) para ncurses."""
from ncurses_ui.components.base import Component
from ncurses_ui.components.datatable_state import DataTableStateMixin
from ncurses_ui.components.datatable_view import DataTableViewMixin
from ncurses_ui.kernel.contract import normalize_config


class DataTable(DataTableStateMixin, DataTableViewMixin, Component):
    """Frontend puro sobre una lista de filas (no accede a datos)."""

    focusable = True

    def run(self):
        normalize_config(self.config)
        self._ensure_state()
        return super().run()

    def _ensure_state(self):
        if not hasattr(self, "state"):
            self.items = self._source_items(self.config)
            self.state = self._datatable_state(self.config, self.items)
            self.title = self.config.get("title", "Tabla")
            self.page_size = 10

    def draw(self, window, region):
        self._ensure_state()
        self.page_size = max(1, region.height - 7 - (1 if self.state["show_header"] else 0))
        if self.state["dirty"]:
            self._datatable_reload(self.state, self.page_size)
        self._draw_datatable(window, self.state, self.title, self.page_size, region)

    def handle_key(self, key):
        self._ensure_state()
        action = self._datatable_handle_key(key, self.state, self.page_size)
        if isinstance(action, dict):
            return action
        if action == "quit":
            return "quit"
        if action == "detail":
            self._open_detail(self.state, self.title)
        elif action == "reload":
            self.state["dirty"] = True
        return None

    def handle_mouse(self, x, y, region):
        self._ensure_state()
        inside = (region.x <= x < region.x + region.width and region.y <= y < region.y + region.height)
        if not inside:
            return None
        first_row = region.y + (5 if self.state["show_header"] else 4)
        page_row = y - first_row
        if 0 <= page_row < len(self.state["rows"]):
            self.state["cursor"] = page_row
            return "done"
        return None

    def result(self):
        self._ensure_state()
        result = {"status": "ok", "selected": self._selected_rows(self.state), "query": self.state["query"]}
        if self.state.get("editable_cols"):
            result["rows"] = self.state["items"]
        return result
