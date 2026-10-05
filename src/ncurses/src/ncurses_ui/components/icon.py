"""Componente Icon: glifo con label opcional."""
from ncurses_ui.components.base import StaticComponent
from ncurses_ui.kernel.renderer import safe_addstr


class Icon(StaticComponent):
    """Dibuja `glyph`/`icon` y, si hay, su `label`."""

    def content(self):
        glyph = str(self.config.get("glyph", self.config.get("icon", "")))
        label = self.config.get("label")
        return f"{glyph} {label}".strip() if label else glyph

    def render(self, window, region):
        safe_addstr(window, region.y, region.x, self.content(), 0, region.width)

    def result(self):
        return {"status": "ok", "content": self.content()}
