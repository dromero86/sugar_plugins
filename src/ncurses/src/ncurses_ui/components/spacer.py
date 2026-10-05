"""Componente Spacer: vista vacia que solo ocupa espacio."""
from ncurses_ui.components.base import StaticComponent


class Spacer(StaticComponent):
    """No dibuja nada; reserva una region del layout."""

    def render(self, window, region):
        pass
