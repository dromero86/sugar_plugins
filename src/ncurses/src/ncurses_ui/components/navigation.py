"""Componentes de navegacion: menu, contextmenu, toolbar, sidebar, hint."""
import curses

from ncurses_ui.components.base import Component, StaticComponent
from ncurses_ui.kernel.input import is_enter, is_escape
from ncurses_ui.kernel.renderer import Region, safe_addstr
from ncurses_ui.kernel.screen import TerminalScreen


class Menu(Component):
    """Lista de items seleccionables."""

    focusable = True

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.items = self.config.get("items", self.config.get("data", []))
        self.cursor = 0

    def label(self, item):
        if isinstance(item, dict):
            return str(item.get("value", item.get("label", item.get("id", ""))))
        return str(item)

    def render(self, window, region, first=0):
        for i, item in enumerate(self.items[first:first + region.height]):
            index = first + i
            marker = ">" if index == self.cursor else " "
            safe_addstr(window, region.y + i, region.x, f"{marker} {self.label(item)}", 0, region.width)

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
        return None

    def handle_mouse(self, x, y, region):
        if not (region.x <= x < region.x + region.width and region.y <= y < region.y + region.height):
            return None
        row = y - region.y
        if 0 <= row < len(self.items):
            self.cursor = row
            return "done"
        return None

    def draw(self, window, region):
        self.render(window, region)

    def run(self):
        with TerminalScreen(self.manager) as screen:
            while True:
                height, width = screen.getmaxyx()
                self.render(screen, Region(0, 0, height, width))
                screen.refresh()
                if self.handle_key(screen.getch()) in ("done", "quit"):
                    break
        return self.result()

    def result(self):
        if not self.items:
            return {"status": "ok", "selected": None}
        return {"status": "ok", "selected": self.items[self.cursor]}


class ContextMenu(Menu):
    """Menu contextual (popup)."""


class Sidebar(Menu):
    """Menu lateral."""


class Toolbar(StaticComponent):
    """Barra horizontal de items."""

    def render(self, window, region):
        x = region.x
        for item in self.config.get("items", []):
            label = str(item.get("value", item.get("label", ""))) if isinstance(item, dict) else str(item)
            text = f"[{label}]"
            if x + len(text) > region.x + region.width:
                break
            safe_addstr(window, region.y, x, text, 0, region.width)
            x += len(text) + 1

    def handle_mouse(self, x, y, region):
        if not (region.x <= x < region.x + region.width and region.y <= y < region.y + region.height):
            return None
        cursor = region.x
        for item in self.config.get("items", []):
            label = str(item.get("value", item.get("label", ""))) if isinstance(item, dict) else str(item)
            width = len(f"[{label}]") + 1
            if cursor <= x < cursor + width:
                return "done"
            cursor += width
        return None


class Hint(StaticComponent):
    """Linea de ayuda / tooltip."""

    def render(self, window, region):
        text = self.config.get("text", self.config.get("content", ""))
        safe_addstr(window, region.y, region.x, str(text), 0, region.width)


class MainBar(StaticComponent):
    """Barra superior: nombre de app + toggle de sidebar (izq) y menu de usuario (der)."""

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.collapsed = False
        self.user_open = False

    def app_name(self):
        return str(self.config.get("name", self.config.get("title", "")))

    def toggle_x(self, region):
        return region.x + len(self.app_name()) + 1

    def render(self, window, region):
        name = self.app_name()
        safe_addstr(window, region.y, region.x, name, 0, region.width)
        toggle_x = self.toggle_x(region)
        safe_addstr(window, region.y, toggle_x, "[=]", 0, max(0, region.width - (toggle_x - region.x)))
        user = "[...]"
        user_x = max(region.x, region.x + region.width - len(user) - 1)
        safe_addstr(window, region.y, user_x, user, 0, len(user))

    def handle_key(self, key):
        if key in (ord("="), 9):
            self.collapsed = not self.collapsed
            return {"action": "toggle_sidebar"}
        if key in (ord("u"), ord("U")):
            self.user_open = not self.user_open
            return {"action": "user_menu"}
        return None

    def handle_mouse(self, x, y, region):
        if not (region.x <= x < region.x + region.width and region.y <= y < region.y + region.height):
            return None
        toggle_x = self.toggle_x(region)
        if toggle_x <= x < toggle_x + 3:
            self.collapsed = not self.collapsed
            return {"action": "toggle_sidebar"}
        if region.x + region.width - 4 <= x < region.x + region.width:
            self.user_open = not self.user_open
            return {"action": "user_menu"}
        return None

    def result(self):
        return {"status": "ok", "collapsed": self.collapsed}
