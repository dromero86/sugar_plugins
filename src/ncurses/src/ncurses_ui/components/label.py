"""Componente Label: texto no editable."""
from ncurses_ui.components.template import Template


class Label(Template):
    """Como Template, pero toma el texto de `label`/`value`/`content`."""

    def text(self):
        return self.config.get("label", self.config.get("value", self.config.get("content", "")))
