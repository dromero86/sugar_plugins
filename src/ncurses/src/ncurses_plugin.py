"""
Plugin Ncurses para Sugar Language
==================================

Interfaces de terminal (TUI) con un modelo de componentes estilo Webix:
`{"ncurses": {"operator": "<view>", ...}}`. El adaptador resuelve el operador
en el `ViewRegistry`, corre el componente y binea el resultado. El kernel y los
componentes viven en el paquete `ncurses_ui`.
"""

import os
import sys
from typing import Any, Dict, List, Optional

from Sugar.Lang.Plugins.PluginBase import PluginBase
from Sugar.Lang.Utils.Output import Output

# Bootstrap: permite importar 'ncurses_ui' tanto si el plugin se carga como
# modulo top-level (loader) como si se carga por path (tests).
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from ncurses_ui.errors import NcursesError
from ncurses_ui.components import register_defaults
from ncurses_ui.kernel.registry import ViewRegistry
from ncurses_ui.kernel.session import Session


class NcursesPlugin(PluginBase):
    """Plugin Ncurses: resuelve operadores-componente y binea el resultado."""

    VERSION = "2.0.0"
    DESCRIPTION = "Plugin Ncurses para Sugar - Interfaces de terminal interactivas (TUI)"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = []
    REQUIREMENTS = []

    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        super().__init__(context, plugin_config)
        self.manager = Session()
        self.registry = ViewRegistry()
        register_defaults(self.registry)
        self.manager.registry = self.registry
        self.manager.call_function = self.call_function
        self.manager.register_function = self.register_function
        self.manager.invoke_anonymous = self.invoke_anonymous

    def execute(self, operator: str, config: Dict[str, Any]) -> Any:
        """Ejecuta un componente y guarda el resultado en `id` (si hay)."""
        op = config.get("operator") or operator

        if not self.registry.has(op):
            raise NcursesError(f"Comando no reconocido: {op}")

        try:
            interpolated_config = self.interpolate_variables(config)

            if getattr(self, "_ui_active", False):
                raise NcursesError("Reentrancia de UI: un callback no puede abrir otra vista")
            self._ui_active = True
            try:
                component = self.registry.create(op, interpolated_config, self.context, self.manager)
                result = component.run()
            finally:
                self._ui_active = False

            result_key = config.get("id")
            if result_key and self.context:
                self.set_variable(result_key, result)

            return result

        except NcursesError:
            raise
        except Exception as e:
            Output.Console(self.plugin_name, f"Error ejecutando {op}: {str(e)}")
            raise NcursesError(f"Error ejecutando {op}: {str(e)}")

    def get_available_commands(self) -> List[str]:
        """El core registra el nodo `{"ncurses": {...}}` a partir de esta lista."""
        return ["ncurses"]
