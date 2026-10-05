"""Componente DataView: grilla de bloques."""
from ncurses_ui.components.list import List
from ncurses_ui.kernel.renderer import safe_addstr


class DataView(List):
    """Como List, pero cada item se dibuja como bloque multilinea."""

    def render(self, window, region, first=0):
        y = region.y
        for i, item in enumerate(self.items[first:]):
            index = first + i
            marker = ">" if index == self.cursor else " "
            for j, line in enumerate(self.text(item).split("\n")):
                if y >= region.y + region.height:
                    return
                prefix = f"{marker} " if j == 0 else "  "
                safe_addstr(window, y, region.x, prefix + line, 0, region.width)
                y += 1
