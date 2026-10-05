"""Registro de componentes de UI por operador."""
from ncurses_ui.errors import NcursesError


class ViewRegistry:
    """Mapea `operator` -> fabrica de componentes."""

    def __init__(self):
        self._factories = {}

    def register(self, operator, factory):
        self._factories[operator] = factory

    def has(self, operator):
        return operator in self._factories

    def operators(self):
        return sorted(self._factories)

    def create(self, operator, config, context, manager):
        factory = self._factories.get(operator)
        if factory is None:
            raise NcursesError(f"Componente no registrado: {operator}")
        return factory(config, context, manager)
