"""
Selenium Plugin Implementation v2.1
==================================

Capa de adaptador Sugar (L4). Solo se encarga de:
- Leer la configuracion y el meta del contexto.
- Interpolar variables {{variable}} de Sugar.
- Validar el operador y delegar en la capa de sesion (L1/L2).

La logica de navegador vive en src/session/ (BrowserFactory/BrowserSession)
y el contrato en src/kernel/contract.py.
"""

import os
import sys
from typing import Any, Dict, List, Optional

from Sugar.Lang.Plugins.PluginBase import PluginBase
from Sugar.Lang.Utils.Output import Output

# Bootstrap: permite importar 'kernel'/'session' tanto si el plugin se
# carga como paquete (selenium_plugin.src.*) como si se carga como modulo
# top-level (tests con src/ en sys.path).
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from kernel.contract import SessionSpec
from session.BrowserSession import BrowserSession
from session.SessionController import SessionController
from session.BrowserFactory import SUPPORTED_BROWSERS
from session import Humanize, Logging


class SeleniumPlugin(BrowserSession, PluginBase):
    """
    Plugin de automatización Selenium para Sugar v2.1.

    Sintaxis soportada:
    {
      "selenium": {
        "operator": "command",
        ...
      }
    }
    """

    VERSION = "2.1.0"
    DESCRIPTION = "Plugin Selenium para Sugar con sintaxis {\"selenium\": {\"operator\": ...}}"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = ["selenium>=4.0.0", "webdriver-manager>=3.8.0"]

    SUPPORTED_BROWSERS = SUPPORTED_BROWSERS

    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """Inicializa el plugin de Selenium."""
        PluginBase.__init__(self, context, plugin_config)
        BrowserSession.__init__(self, plugin_name=self.plugin_name)
        self._controller = SessionController(self, self.plugin_name)

    def get_available_commands(self) -> List[str]:
        """Retorna la lista de comandos disponibles del plugin."""
        return [
            "selenium"
        ]

    def execute(self, operator: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta un operador de Selenium.

        Args:
            operator: El operador a ejecutar (siempre 'selenium')
            config: Configuración del operador

        Returns:
            Dict con el resultado de la operación
        """
        spec = None
        try:
            Output.Console(self.plugin_name, f"DEBUG: Ejecutando plugin Selenium con operator: {operator}")
            Output.Console(self.plugin_name, f"DEBUG: Config recibida: {config}")

            if operator != 'selenium':
                raise ValueError(f"Operador no soportado: {operator}")

            selenium_config = config.get('selenium', config)
            command = selenium_config.get('operator')

            Output.Console(self.plugin_name, f"DEBUG: Comando a ejecutar: {command}")
            Output.Console(self.plugin_name, f"DEBUG: Config selenium: {selenium_config}")

            if not command:
                raise ValueError("Operador 'operator' requerido en configuración selenium")

            # Construir el spec y asegurar la sesion (in-process o keeper
            # segun meta.detach).
            spec = self._build_spec()
            self.log_file = spec.log_file
            self._controller.configure(spec)
            self._controller.ensure(spec)

            self._debug_context_state()

            # Interpolar variables de Sugar ANTES de delegar: la capa de
            # sesion/keeper recibe la config ya resuelta.
            interpolated_config = self._interpolate_config(selenium_config)
            self._log_interpolation_summary(selenium_config)

            Output.Console(self.plugin_name, f"DEBUG: Ejecutando comando: {command}")
            if spec.humanize:
                Humanize.sleep_between_operators(spec.humanize)
            result = self._controller.execute(command, interpolated_config)

            Output.Console(self.plugin_name, f"DEBUG: Resultado del comando: {result}")
            return result

        except Exception as e:
            log_file = getattr(spec, 'log_file', None)
            Logging.log_failure(self.plugin_name, f"plugin Selenium (operator='{operator}')", e, log_file)
            return {"error": str(e), "success": False}

    def _build_spec(self) -> SessionSpec:
        """Construye el SessionSpec desde el meta del contexto."""
        if not hasattr(self, 'context') or not self.context:
            raise ValueError("Contexto no disponible para inicializar driver")
        meta = getattr(self.context, 'meta', {})
        spec = SessionSpec.from_meta(meta)
        Output.Console(self.plugin_name, f"DEBUG: Browser configurado: {spec.browser} (detach={spec.detach})")
        return spec

    def cleanup(self):
        """Limpia recursos. Con detach activo, la sesion del keeper queda viva."""
        try:
            self._controller.cleanup()
        except Exception as e:
            log_file = getattr(self, 'log_file', None)
            Logging.log_failure(self.plugin_name, "cleanup", e, log_file)

    def _interpolate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Interpola variables en la configuración usando el sistema de Sugar."""
        if not isinstance(config, dict):
            return config

        Output.Console(self.plugin_name, f"DEBUG: Interpolando configuración: {config}")

        interpolated = {}
        failed_interpolations = []

        for key, value in config.items():
            if isinstance(value, str):
                original_value = value
                try:
                    interpolated_value = self.interpolate_variables(value)
                    interpolated[key] = interpolated_value

                    if "{{" in interpolated_value and "}}" in interpolated_value:
                        failed_interpolations.append(f"{key}: {interpolated_value}")

                    if original_value != interpolated_value:
                        Output.Console(self.plugin_name, f"DEBUG: Interpolado '{key}': '{original_value}' -> '{interpolated_value}'")
                    else:
                        Output.Console(self.plugin_name, f"DEBUG: No se detectaron variables para interpolar en '{key}': '{original_value}'")

                except Exception as e:
                    Output.Console(self.plugin_name, f"ERROR interpolando '{key}': {str(e)}")
                    interpolated[key] = original_value

            elif isinstance(value, dict):
                interpolated[key] = self._interpolate_config(value)
            elif isinstance(value, list):
                interpolated[key] = [
                    self._interpolate_config(item) if isinstance(item, dict)
                    else self.interpolate_variables(item) if isinstance(item, str)
                    else item for item in value
                ]
            else:
                interpolated[key] = value

        if failed_interpolations:
            Output.Console(self.plugin_name, f"ADVERTENCIA: Interpolaciones fallidas detectadas: {failed_interpolations}")

        Output.Console(self.plugin_name, f"DEBUG: Configuración interpolada: {interpolated}")
        return interpolated

    def _log_interpolation_summary(self, config: Dict[str, Any]) -> None:
        """Registra un resumen de las interpolaciones realizadas."""
        interpolation_count = 0
        interpolated_fields = []

        def count_interpolations(obj, path=""):
            nonlocal interpolation_count
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, str) and "{{" in value and "}}" in value:
                        interpolation_count += 1
                        interpolated_fields.append(current_path)
                    elif isinstance(value, (dict, list)):
                        count_interpolations(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]"
                    count_interpolations(item, current_path)

        count_interpolations(config)

        if interpolation_count > 0:
            Output.Console(self.plugin_name, f"RESUMEN: {interpolation_count} campos interpolados: {interpolated_fields}")
        else:
            Output.Console(self.plugin_name, "RESUMEN: No se detectaron interpolaciones")

    def _debug_context_state(self):
        """Depura el estado del contexto y las variables disponibles."""
        try:
            if not self.context:
                Output.Console(self.plugin_name, "DEBUG: Contexto no disponible")
                return

            Output.Console(self.plugin_name, "DEBUG: === ESTADO DEL CONTEXTO ===")

            if hasattr(self.context, 'memory_handler'):
                Output.Console(self.plugin_name, "memory_handler disponible")

                if hasattr(self.context.memory_handler, 'get'):
                    current_vars = self.context.memory_handler.get()
                    if current_vars:
                        Output.Console(self.plugin_name, f"DEBUG: Variables en scope actual: {list(current_vars[-1].keys()) if current_vars[-1] else '{}'}")
                    else:
                        Output.Console(self.plugin_name, "DEBUG: No hay variables en scope actual")

                if hasattr(self.context.memory_handler, 'vars'):
                    global_vars = self.context.memory_handler.vars
                    if global_vars:
                        Output.Console(self.plugin_name, f"DEBUG: Variables globales: {list(global_vars.keys())}")
                    else:
                        Output.Console(self.plugin_name, "DEBUG: No hay variables globales")

                if hasattr(self.context.memory_handler, 'current_loop'):
                    current_loop = self.context.memory_handler.current_loop
                    if current_loop:
                        Output.Console(self.plugin_name, f"DEBUG: Loop actual: {current_loop}")
                    else:
                        Output.Console(self.plugin_name, "DEBUG: No hay loop activo")
            else:
                Output.Console(self.plugin_name, "memory_handler no disponible")

            Output.Console(self.plugin_name, "DEBUG: === FIN ESTADO DEL CONTEXTO ===")

        except Exception as e:
            Output.Console(self.plugin_name, f"ERROR en _debug_context_state: {str(e)}")
