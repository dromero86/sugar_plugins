"""Componente Layout: compone hijos en filas o columnas y rutea teclas."""
import curses

from ncurses_ui.components.base import Component, draw_child
from ncurses_ui.kernel.layout import split


class Layout(Component):
    """Divide su region entre hijos y delega las teclas al hijo enfocado."""

    focusable = True

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.children = []
        self.focus_index = 0

    def orientation(self):
        if "rows" in self.config:
            return self.config["rows"], False
        return self.config.get("cols", []), True

    @staticmethod
    def child_spec(child, horizontal):
        size = child.get("width") if horizontal else child.get("height")
        if size is None:
            return {"weight": child.get("weight", 1)}
        return {"size": int(size)}

    def regions(self, region):
        children, horizontal = self.orientation()
        specs = [self.child_spec(child, horizontal) for child in children]
        return children, split(region, specs, horizontal=horizontal, gap=self.config.get("gap", 0))

    def _sync_children(self):
        children, _ = self.orientation()
        if len(self.children) != len(children):
            self.children = [self._create_child(child) for child in children]

    def draw(self, window, region):
        self._sync_children()
        _, regions = self.regions(region)
        for child, child_region in zip(self.children, regions):
            draw_child(child, window, child_region)

    def _focusable(self):
        return [i for i, child in enumerate(self.children) if child is not None and getattr(child, "focusable", False)]

    def handle_key(self, key):
        focusable = self._focusable()
        if not focusable:
            return "quit" if key in (ord("q"), ord("Q"), 27) else None
        if self.focus_index not in focusable:
            self.focus_index = focusable[0]
        if key in (9, curses.KEY_BTAB):
            position = focusable.index(self.focus_index)
            self.focus_index = focusable[(position + 1) % len(focusable)]
            return None
        return self.children[self.focus_index].handle_key(key)

    def handle_mouse(self, x, y, region):
        _, regions = self.regions(region)
        for index, (child, child_region) in enumerate(zip(self.children, regions)):
            if child is None or not hasattr(child, "handle_mouse"):
                continue
            inside = (child_region.x <= x < child_region.x + child_region.width
                      and child_region.y <= y < child_region.y + child_region.height)
            if inside:
                self.focus_index = index
                return child.handle_mouse(x, y, child_region)
        return None

    def result(self):
        children = {}
        for i, child in enumerate(self.children):
            if child is not None:
                children[str(i)] = child.result()
        return {"status": "ok", "children": children}
