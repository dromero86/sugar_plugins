"""Componente Pager: controles de paginacion."""
import curses

from ncurses_ui.components.base import FieldComponent
from ncurses_ui.kernel.input import is_enter, is_escape
from ncurses_ui.kernel.renderer import safe_addstr


class Pager(FieldComponent):
    """Navegacion de paginas `[<] N/M [>]`."""

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.total = int(self.config.get("total", 0))
        self.per_page = int(self.config.get("per_page", self.config.get("size", 20))) or 20
        self.pages = max(1, (self.total + self.per_page - 1) // self.per_page)
        self.page = max(1, int(self.config.get("page", 1)))

    def render(self, window, region):
        safe_addstr(window, region.y, region.x, f"[<] Pagina {self.page}/{self.pages} [>]", 0, region.width)

    def handle_key(self, key):
        if is_enter(key):
            return "done"
        if is_escape(key):
            return "cancel"
        if key in (curses.KEY_LEFT, ord("<"), ord("h")):
            self.page = max(1, self.page - 1)
        elif key in (curses.KEY_RIGHT, ord(">"), ord("l")):
            self.page = min(self.pages, self.page + 1)
        return None

    def result(self):
        return {"status": "ok", "page": self.page, "pages": self.pages}
