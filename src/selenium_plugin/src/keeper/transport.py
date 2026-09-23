"""
Capa keeper: transporte local
=============================

Transporte in-process basado en dos colas (requests/responses). El mismo
contrato podria implementarse sobre sockets/named pipes para un keeper
en otro proceso, sin tocar al cliente ni al servidor.
"""

import queue
from typing import Any, Optional


class LocalTransport:
    """Canal request/response entre cliente y keeper en el mismo proceso."""

    def __init__(self):
        self._requests: 'queue.Queue[dict]' = queue.Queue()
        self._responses: 'queue.Queue[dict]' = queue.Queue()

    def send_request(self, message: dict) -> None:
        self._requests.put(message)

    def next_request(self, timeout: Optional[float] = None) -> dict:
        return self._requests.get(timeout=timeout)

    def send_response(self, message: dict) -> None:
        self._responses.put(message)

    def next_response(self, timeout: Optional[float] = None) -> dict:
        return self._responses.get(timeout=timeout)
