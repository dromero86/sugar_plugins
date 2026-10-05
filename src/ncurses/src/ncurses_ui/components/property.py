"""Componente Property: tabla de pares nombre:valor."""
from ncurses_ui.components.base import StaticComponent
from ncurses_ui.kernel.renderer import safe_addstr


class Property(StaticComponent):
    """Muestra un dict como `Header: valor`, campo por linea."""

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.data = self._data()
        self.fields = self._fields()

    def _data(self):
        data = self.config.get("data")
        if isinstance(data, dict):
            return data
        if isinstance(data, str) and self.context is not None:
            handler = getattr(self.context, "memory_handler", None)
            value = handler.get_variable(data) if handler else None
            if isinstance(value, dict):
                return value
        return {}

    def _fields(self):
        fields = self.config.get("fields")
        if not fields:
            return [{"id": key, "header": key} for key in self.data]
        out = []
        for field in fields:
            if isinstance(field, dict):
                field_id = field.get("id") or field.get("field")
                out.append({"id": field_id, "header": field.get("header", field_id)})
            else:
                out.append({"id": field, "header": field})
        return out

    def set_data(self, data):
        """Actualiza los datos; si no se configuraron `fields`, los deriva."""
        self.data = data or {}
        if not self.config.get("fields"):
            self.fields = [{"id": key, "header": key} for key in self.data]

    def lines(self):
        return [f"{field['header']}: {self.data.get(field['id'], '')}" for field in self.fields]

    def render(self, window, region):
        for i, line in enumerate(self.lines()[:region.height]):
            safe_addstr(window, region.y + i, region.x, line, 0, region.width)

    def result(self):
        return {"status": "ok", "values": dict(self.data)}
