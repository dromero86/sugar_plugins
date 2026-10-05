"""Componente Template: texto estatico con placeholders `#campo#`."""
from ncurses_ui.components.base import StaticComponent
from ncurses_ui.kernel.renderer import render_template, safe_addstr


class Template(StaticComponent):
    """Renderiza `content`/`template` contra `data`."""

    def text(self):
        return self.config.get("content", self.config.get("template", ""))

    def content(self):
        return render_template(self.text(), self.config.get("data") or {})

    def render(self, window, region):
        safe_addstr(window, region.y, region.x, self.content(), 0, region.width)

    def result(self):
        return {"status": "ok", "content": self.content()}
