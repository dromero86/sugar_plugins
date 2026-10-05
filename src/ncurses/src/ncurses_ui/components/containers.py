"""Contenedores: proxy, scrollview, align, abslayout, gridlayout, headerlayout, portlet, dashboard, accordion."""
from ncurses_ui.components.base import StaticComponent, draw_child
from ncurses_ui.kernel.layout import split
from ncurses_ui.kernel.renderer import Region, safe_addstr


class Proxy(StaticComponent):
    """Wrapper que dibuja su `body`."""

    def render(self, window, region):
        child = self._create_child(self.config.get("body"))
        if child is not None:
            draw_child(child, window, region)


class ScrollView(Proxy):
    """Contenedor con scroll (el scroll lo maneja el terminal)."""


class Align(StaticComponent):
    """Centra su `body` en la region."""

    def render(self, window, region):
        child = self._create_child(self.config.get("body"))
        if child is None:
            return
        width = min(int(self.config.get("width", region.width)), region.width)
        height = min(int(self.config.get("height", region.height)), region.height)
        y = region.y + max(0, (region.height - height) // 2)
        x = region.x + max(0, (region.width - width) // 2)
        draw_child(child, window, Region(y, x, height, width))


class AbsLayout(StaticComponent):
    """Hijos posicionados por coordenadas absolutas."""

    def render(self, window, region):
        for child_config in self.config.get("cells", []):
            x = region.x + int(child_config.get("x", 0))
            y = region.y + int(child_config.get("y", 0))
            width = int(child_config.get("width", region.width))
            height = int(child_config.get("height", 1))
            child = self._create_child(child_config)
            if child is not None:
                draw_child(child, window, Region(y, x, height, width))


class GridLayout(StaticComponent):
    """Grilla de celdas en `cols` columnas."""

    def render(self, window, region):
        cols = int(self.config.get("cols", 1)) or 1
        cells = self.config.get("cells", [])
        if not cells:
            return
        gap = self.config.get("gap", 0)
        rows = (len(cells) + cols - 1) // cols
        row_regions = split(region, [{"weight": 1}] * rows, horizontal=False, gap=gap)
        for r, row_region in enumerate(row_regions):
            row_cells = cells[r * cols:(r + 1) * cols]
            col_regions = split(row_region, [{"weight": 1}] * len(row_cells), horizontal=True, gap=gap)
            for child_config, child_region in zip(row_cells, col_regions):
                child = self._create_child(child_config)
                if child is not None:
                    draw_child(child, window, child_region)


class HeaderLayout(StaticComponent):
    """Header arriba + body abajo."""

    def render(self, window, region):
        header_height = int(self.config.get("header_height", 1))
        regions = split(region, [{"size": header_height}, {"weight": 1}], horizontal=False)
        header_child = self._create_child(self.config.get("header")) if self.config.get("header") else None
        if header_child is not None:
            draw_child(header_child, window, regions[0])
        body_child = self._create_child(self.config.get("body")) if self.config.get("body") else None
        if body_child is not None:
            draw_child(body_child, window, regions[1])


class Portlet(StaticComponent):
    """Panel con titulo y body."""

    def render(self, window, region):
        title = self.config.get("title")
        if title and region.height:
            safe_addstr(window, region.y, region.x, f"[{title}]", 0, region.width)
        child = self._create_child(self.config.get("body"))
        if child is not None and region.height > 1:
            draw_child(child, window, Region(region.y + 1, region.x, region.height - 1, region.width))


class Accordion(StaticComponent):
    """Secciones colapsables segun `expanded`."""

    def render(self, window, region):
        sections = self.config.get("sections", self.config.get("cells", []))
        expanded = set(self.config.get("expanded", []))
        y = region.y
        for i, section in enumerate(sections):
            if y >= region.y + region.height:
                break
            header = str(section.get("header", i)) if isinstance(section, dict) else str(section)
            safe_addstr(window, y, region.x, f"{'v' if i in expanded else '>'} {header}", 0, region.width)
            y += 1
            if i in expanded and isinstance(section, dict) and section.get("body") and y < region.y + region.height:
                child = self._create_child(section["body"])
                if child is not None:
                    draw_child(child, window, Region(y, region.x, region.y + region.height - y, region.width))
