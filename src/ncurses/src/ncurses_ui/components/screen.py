"""Componente Screen: hospeda la vista actual y la pila de navegacion.

Navegacion inline (sin registro de nombres): un evento `navigate` lleva la
vista destino en `view`; `back` vuelve a la anterior. El hijo devuelve un dict
`{"action": "navigate"|"back", ...}` desde `handle_key` y el screen lo aplica.
"""
from ncurses_ui.components.base import Component, draw_child
from ncurses_ui.kernel.navigation import ViewStack


class Screen(Component):
    focusable = True

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.view = config.get("view") if config else None
        self.stack = ViewStack()
        self.child = None

    def _ensure_child(self):
        if self.child is None and self.view is not None:
            self.child = self._create_child(self.view)
        return self.child

    def draw(self, window, region):
        draw_child(self._ensure_child(), window, region)

    def handle_key(self, key):
        child = self._ensure_child()
        if child is None:
            return "quit"
        action = child.handle_key(key)
        if isinstance(action, dict):
            return self._navigate(action)
        if action is None and key in (ord("q"), ord("Q"), 27):
            return "quit"
        return action

    def handle_mouse(self, x, y, region):
        child = self._ensure_child()
        if child is None or not hasattr(child, "handle_mouse"):
            return None
        action = child.handle_mouse(x, y, region)
        if isinstance(action, dict):
            return self._navigate(action)
        return action

    def _navigate(self, action):
        kind = action.get("action")
        if kind == "navigate" and action.get("view"):
            self.stack.push(self.view)
            self.view = action["view"]
            self.child = None
        elif kind == "back":
            previous = self.stack.pop()
            if previous is not None:
                self.view = previous
                self.child = None
        return None

    def result(self):
        child = self._ensure_child()
        return child.result() if child is not None else {"status": "ok"}
