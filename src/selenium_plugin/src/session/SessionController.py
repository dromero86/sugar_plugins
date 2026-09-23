"""
Capa de sesion: controller
==========================

Interfaz unica que usa el adaptador para ejecutar comandos. Elige el
backend:
- InProcessBackend: la BrowserSession local (comportamiento actual).
- DetachedBackend: un keeper que posee la sesion y sobrevive al cliente.
"""

import os
import sys
from typing import Any, Dict, Optional

# Bootstrap: ver BrowserFactory.
_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from kernel.contract import SessionSpec


class InProcessBackend:
    """Backend que usa la BrowserSession local."""

    def __init__(self, session):
        self.session = session

    def ensure(self, spec: SessionSpec) -> None:
        self.session.ensure_driver(spec)

    def execute(self, command: str, config: Dict[str, Any]) -> Dict[str, Any]:
        return self.session.execute_command(command, config)

    def detach(self) -> None:
        pass

    def quit(self) -> None:
        self.session.quit()

    def cleanup(self) -> None:
        self.session.quit()


class DetachedBackend:
    """Backend que delega en un keeper via registry."""

    def __init__(self, spec: SessionSpec, plugin_name: str):
        self.spec = spec
        self.plugin_name = plugin_name
        self.client = None

    def ensure(self, spec: SessionSpec) -> None:
        if self.client is None:
            from keeper import registry
            self.client = registry.get_or_create(spec, self.plugin_name)

    def execute(self, command: str, config: Dict[str, Any]) -> Dict[str, Any]:
        # 'quit' explicito cierra el browser y da de baja el keeper; la
        # proxima operacion levanta una sesion nueva.
        if command == 'quit':
            self._forget()
            result_key = config.get('id', 'quit')
            return {result_key: True, "success": True}
        return self.client.execute(command, config)

    def _forget(self) -> None:
        if self.client is not None:
            from keeper import registry
            self.client.quit()
            registry.remove(self.spec)
            self.client = None

    def detach(self) -> None:
        if self.client is not None:
            self.client.detach()

    def quit(self) -> None:
        self._forget()

    def cleanup(self) -> None:
        # Semantica de detach: al terminar la tarea NO se cierra el browser.
        self.detach()


class SessionController:
    """Punto de entrada de la capa de sesion para el adaptador."""

    def __init__(self, session, plugin_name: str = 'Selenium'):
        self.session = session
        self.plugin_name = plugin_name
        self._backend = InProcessBackend(session)
        self._detached = False

    @property
    def is_detached(self) -> bool:
        return self._detached

    def configure(self, spec: SessionSpec) -> None:
        """Cambia a backend detached si el spec lo pide (idempotente)."""
        if spec.detach and not self._detached:
            self._backend = DetachedBackend(spec, self.plugin_name)
            self._detached = True

    def ensure(self, spec: SessionSpec) -> None:
        self._backend.ensure(spec)

    def execute(self, command: str, config: Dict[str, Any]) -> Dict[str, Any]:
        return self._backend.execute(command, config)

    def detach(self) -> None:
        self._backend.detach()

    def quit(self) -> None:
        self._backend.quit()

    def cleanup(self) -> None:
        self._backend.cleanup()
