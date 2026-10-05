"""Componente Toggle/Switch: estado on/off."""
from ncurses_ui.components.checkbox import Checkbox


class Toggle(Checkbox):
    """Como Checkbox, renderizado como ON/OFF."""

    def box(self):
        return "[ON ]" if self.value else "[OFF]"
