"""Componente Search: campo de busqueda."""
from ncurses_ui.components.text import Text


class Search(Text):
    """Como Text, pero orientado a busqueda incremental."""

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        if "placeholder" not in self.config:
            self.config["placeholder"] = "Buscar"

    def result(self):
        return {"status": "ok", "query": self.value, "value": self.value}
