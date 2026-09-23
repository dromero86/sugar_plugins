"""
Capa keeper: registry
=====================

Registro in-process de keepers vivos, indexado por la identidad de la
sesion (SessionSpec.cache_key). Permite reattach: una corrida nueva con
el mismo meta reutiliza el navegador que quedo detacheado.
"""

import os
import sys
import threading
from typing import Dict, List

# Bootstrap: ver BrowserFactory.
_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from kernel.contract import SessionSpec
from keeper.KeeperServer import KeeperServer
from keeper.KeeperClient import KeeperClient


_LOCK = threading.Lock()
_KEEPERS: Dict[str, KeeperClient] = {}


def get_or_create(spec: SessionSpec, plugin_name: str = 'SeleniumKeeper') -> KeeperClient:
    """Devuelve el keeper existente para el spec, o crea uno nuevo."""
    key = spec.cache_key()
    with _LOCK:
        client = _KEEPERS.get(key)
        if client is not None:
            return client

        server = KeeperServer(spec, plugin_name)
        server.start()
        server.wait_ready(timeout=60)
        client = KeeperClient(server)
        _KEEPERS[key] = client
        return client


def remove(spec: SessionSpec) -> None:
    with _LOCK:
        _KEEPERS.pop(spec.cache_key(), None)


def active_keys() -> List[str]:
    with _LOCK:
        return list(_KEEPERS.keys())
