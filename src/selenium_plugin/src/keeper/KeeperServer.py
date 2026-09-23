"""
Capa keeper: servidor
=====================

Corre en un thread (daemon) del host y es el dueno real de la
BrowserSession. Aplica el detach por software: al recibir 'detach' deja
de atender al cliente pero NO cierra la sesion, de modo que el navegador
sigue vivo y puede reattacharse via registry.
"""

import os
import queue
import sys
import threading
from typing import Any, Optional

# Bootstrap: ver BrowserFactory.
_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from kernel.contract import SessionSpec
from session.BrowserSession import BrowserSession
from keeper.transport import LocalTransport
from keeper import protocol


class KeeperServer(threading.Thread):
    """Thread que posee una BrowserSession y atiende comandos del cliente."""

    def __init__(self, spec: SessionSpec, plugin_name: str = 'SeleniumKeeper',
                 session: Optional[BrowserSession] = None):
        super().__init__(name='selenium-keeper', daemon=True)
        self.spec = spec
        self.plugin_name = plugin_name
        self.session = session or BrowserSession(plugin_name)
        self.transport = LocalTransport()
        self._running = True
        self._ready = threading.Event()
        self._error: Optional[BaseException] = None

    def run(self) -> None:
        try:
            self.session.ensure_driver(self.spec)
        except BaseException as e:  # noqa: BLE001 - se propaga al cliente
            self._error = e
            self._ready.set()
            return

        self._ready.set()
        while self._running:
            try:
                message = self.transport.next_request(timeout=0.5)
            except queue.Empty:
                continue
            self._handle(message)

    def wait_ready(self, timeout: float = 60) -> None:
        if not self._ready.wait(timeout):
            raise TimeoutError("El keeper no inicializo la sesion a tiempo")
        if self._error is not None:
            raise self._error

    def _handle(self, message: dict) -> None:
        op = message.get('op')
        request_id = message.get('id')
        try:
            if op == protocol.OP_EXECUTE:
                result = self.session.execute_command(message['command'], message['config'])
                self._reply(request_id, True, result=result)
            elif op == protocol.OP_DETACH:
                # No se cierra la sesion: el browser queda vivo.
                self._reply(request_id, True)
            elif op == protocol.OP_QUIT:
                self.session.quit()
                self._running = False
                self._reply(request_id, True)
            elif op == protocol.OP_PING:
                self._reply(request_id, True)
            else:
                self._reply(request_id, False, error=f"Operacion de keeper no soportada: {op}")
        except Exception as e:  # noqa: BLE001 - se devuelve como error al cliente
            self._reply(request_id, False, error=str(e))

    def _reply(self, request_id: Any, ok: bool, result: Any = None, error: Optional[str] = None) -> None:
        self.transport.send_response(protocol.make_response(request_id, ok, result=result, error=error))
