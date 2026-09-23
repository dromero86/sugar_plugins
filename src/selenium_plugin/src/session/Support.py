"""
Capa de sesion: soporte
=======================

Politica de capacidades no soportadas por el navegador elegido
(meta.on_unsupported: warn | error | ignore).
"""

import os
import sys
from typing import Any

# Bootstrap: ver BrowserFactory.
_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from session import Logging


def unsupported(spec: Any, plugin_name: str, message: str) -> None:
    """Reporta una capacidad sin equivalente en el driver elegido."""
    level = (getattr(spec, 'on_unsupported', 'warn') or 'warn').lower()
    if level == 'ignore':
        return
    if level == 'error':
        raise ValueError(message)
    Logging.log_warning(plugin_name, 'capacidad no soportada', message, getattr(spec, 'log_file', None))
