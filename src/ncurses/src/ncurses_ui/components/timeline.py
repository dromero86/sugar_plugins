"""Componente TimeLine: lista ordenada cronologicamente."""
from ncurses_ui.components.list import List


class TimeLine(List):
    """Como List, pero ordena los items por un campo de tiempo."""

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        field = self.config.get("sort_by", self.config.get("time", "time"))
        if field:
            self.items.sort(key=lambda item: str(item.get(field, "") if isinstance(item, dict) else item))
