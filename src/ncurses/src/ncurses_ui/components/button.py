"""Componente Button: boton clickable."""
from ncurses_ui.components.base import StaticComponent
from ncurses_ui.kernel.renderer import safe_addstr


class Button(StaticComponent):
    """Dibuja `[Texto]`; al activarse devuelve su `action`."""

    def label(self):
        return str(self.config.get("text", self.config.get("label", self.config.get("value", ""))))

    def render(self, window, region):
        safe_addstr(window, region.y, region.x, f"[{self.label()}]", 0, region.width)

    def handle_mouse(self, x, y, region):
        if region.x <= x < region.x + region.width and region.y <= y < region.y + region.height:
            return "done"
        return None

    def result(self):
        return {"status": "ok", "action": self.config.get("action")}
