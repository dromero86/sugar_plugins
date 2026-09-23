"""
Capa keeper: cliente
====================

Lado del adaptador que habla con un KeeperServer. Encola un request y
espera la response con el id correspondiente (ignora responses ajenas).
"""

from typing import Any, Optional

from keeper import protocol
from keeper.KeeperServer import KeeperServer


class KeeperClient:
    """Handle de comunicacion con un KeeperServer."""

    def __init__(self, server: KeeperServer):
        self._server = server
        self._transport = server.transport
        self._counter = 0

    def _call(self, op: str, timeout: Optional[float] = 300, **payload: Any) -> Any:
        self._counter += 1
        request_id = self._counter
        self._transport.send_request(protocol.make_request(request_id, op, **payload))
        while True:
            response = self._transport.next_response(timeout=timeout)
            if response.get('id') != request_id:
                continue
            if response.get('ok'):
                return response.get('result')
            raise RuntimeError(response.get('error'))

    def execute(self, command: str, config: dict) -> dict:
        return self._call(protocol.OP_EXECUTE, command=command, config=config)

    def detach(self) -> None:
        self._call(protocol.OP_DETACH)

    def quit(self) -> None:
        self._call(protocol.OP_QUIT)

    def ping(self) -> None:
        self._call(protocol.OP_PING)
