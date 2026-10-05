"""Componentes de visualizacion: gage, bullet, chart."""
from ncurses_ui.components.base import StaticComponent
from ncurses_ui.kernel.renderer import safe_addstr


class Gage(StaticComponent):
    """Barra de progreso con valor."""

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.min = self.config.get("min", 0)
        self.max = self.config.get("max", 100)
        self.value = self.config.get("value", self.min)
        self.bar_width = int(self.config.get("bar_width", 20))

    def bar(self):
        span = self.max - self.min
        filled = 0 if span <= 0 else round(self.bar_width * (self.value - self.min) / span)
        return "[" + "#" * filled + "-" * (self.bar_width - filled) + "]"

    def render(self, window, region):
        label = self.config.get("label", "")
        body = f"{self.bar()} {self.value}"
        safe_addstr(window, region.y, region.x, f"{label}: {body}" if label else body, 0, region.width)


class Bullet(Gage):
    """Barra con marcador de target."""

    def bar(self):
        span = self.max - self.min
        filled = 0 if span <= 0 else round(self.bar_width * (self.value - self.min) / span)
        cells = ["-"] * self.bar_width
        for i in range(min(filled, self.bar_width)):
            cells[i] = "="
        target = self.config.get("target")
        if target is not None and span > 0:
            position = min(self.bar_width - 1, max(0, round(self.bar_width * (target - self.min) / span)))
            cells[position] = "|"
        return "[" + "".join(cells) + "]"


class Chart(StaticComponent):
    """Grafico de barras horizontal degradado."""

    def render(self, window, region):
        series = self.config.get("data", self.config.get("values", []))
        if not series:
            return
        values = [item.get("value", 0) if isinstance(item, dict) else item for item in series]
        labels = [item.get("label", "") if isinstance(item, dict) else "" for item in series]
        maximum = max(values) or 1
        width = max(1, int(self.config.get("bar_width", 20)))
        for i, value in enumerate(values[:region.height]):
            length = round(width * value / maximum)
            bar = "#" * length + " " * (width - length)
            label = f" {labels[i]}" if labels[i] else ""
            safe_addstr(window, region.y + i, region.x, f"{bar}{label}", 0, region.width)


class Card(StaticComponent):
    """Tarjeta de metrica: icono + valor + label."""

    def render(self, window, region):
        icon = str(self.config.get("icon", ""))
        value = self.config.get("value", 0)
        label = str(self.config.get("label", ""))
        body = f"{icon} {value} - {label}".strip(" -")
        safe_addstr(window, region.y, region.x, f"[ {body} ]", 0, region.width)
