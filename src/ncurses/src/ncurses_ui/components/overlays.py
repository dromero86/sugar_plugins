"""Componentes de ventanas y popups (overlays)."""
from ncurses_ui.components.base import StaticComponent, draw_child
from ncurses_ui.kernel.renderer import Region, safe_addstr


class Window(StaticComponent):
    """Ventana con borde, titulo y body."""

    def box_region(self, region):
        width = min(int(self.config.get("width", 60)), region.width)
        height = min(int(self.config.get("height", 20)), region.height)
        y = region.y + max(0, (region.height - height) // 2)
        x = region.x + max(0, (region.width - width) // 2)
        return Region(y, x, height, width)

    @staticmethod
    def draw_border(window, box):
        if box.width < 2 or box.height < 2:
            return
        safe_addstr(window, box.y, box.x, "+" + "-" * (box.width - 2) + "+", 0, box.width)
        for i in range(1, box.height - 1):
            safe_addstr(window, box.y + i, box.x, "|", 0, 1)
            safe_addstr(window, box.y + i, box.x + box.width - 1, "|", 0, 1)
        safe_addstr(window, box.y + box.height - 1, box.x, "+" + "-" * (box.width - 2) + "+", 0, box.width)

    def render(self, window, region):
        box = self.box_region(region)
        if self.config.get("border", True):
            self.draw_border(window, box)
        title = self.config.get("title")
        if title and box.width > 4:
            safe_addstr(window, box.y, box.x + 2, f" {title} ", 0, box.width - 4)
        body = self.config.get("body")
        child = self._create_child(body) if body else None
        if child is not None:
            draw_child(child, window, Region(box.y + 1, box.x + 1, max(0, box.height - 2), max(0, box.width - 2)))


class Popup(Window):
    """Ventana sin borde por defecto."""

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.config.setdefault("border", False)


class Tooltip(Window):
    """Recuadro pequeno anclado a la esquina de la region."""

    def box_region(self, region):
        width = min(int(self.config.get("width", 30)), region.width)
        height = min(int(self.config.get("height", 3)), region.height)
        return Region(region.y, region.x, height, width)


class Context(Window):
    """Popup posicionado por `position` {x, y}."""

    def box_region(self, region):
        position = self.config.get("position") or {}
        width = min(int(self.config.get("width", 40)), region.width)
        height = min(int(self.config.get("height", 10)), region.height)
        y = min(region.y + int(position.get("y", 0)), region.y + max(0, region.height - height))
        x = min(region.x + int(position.get("x", 0)), region.x + max(0, region.width - width))
        return Region(y, x, height, width)
