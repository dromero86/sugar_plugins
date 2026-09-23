"""
Capa de sesion: logging de fallos
=================================

Centraliza el registro de errores para documentarlos (archivo + consola)
y permitir que el plugin siga funcionando ante fallos de features
opcionales (best-effort).
"""

import logging
import os
import sys
import traceback
from typing import Optional

# Bootstrap: ver BrowserFactory.
_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from Sugar.Lang.Utils.Output import Output


_LOGGERS = {}


def _get_logger(log_file: Optional[str]) -> Optional[logging.Logger]:
    if not log_file:
        return None
    if log_file in _LOGGERS:
        return _LOGGERS[log_file]
    logger = logging.getLogger(f"sugar.selenium.failures.{log_file}")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    if not logger.handlers:
        try:
            directory = os.path.dirname(os.path.abspath(log_file))
            os.makedirs(directory, exist_ok=True)
            handler = logging.FileHandler(log_file, encoding='utf-8')
            handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
            logger.addHandler(handler)
        except Exception as e:  # noqa: BLE001 - no romper por el log
            Output.Console('SeleniumLog', f"ADVERTENCIA: no se pudo abrir el log '{log_file}': {e}")
            return None
    _LOGGERS[log_file] = logger
    return logger


def log_failure(plugin_name: str, context: str, exc: BaseException, log_file: Optional[str] = None) -> str:
    """Registra un fallo en consola y (si hay log_file) en archivo con traceback."""
    message = f"FALLO en {context}: {type(exc).__name__}: {exc}"
    try:
        Output.Console(plugin_name, message)
    except Exception:
        pass
    logger = _get_logger(log_file)
    if logger is not None:
        logger.error(message)
        logger.error(''.join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
    return message


def log_warning(plugin_name: str, context: str, message: str, log_file: Optional[str] = None) -> None:
    """Registra una advertencia (best-effort) en consola y archivo."""
    try:
        Output.Console(plugin_name, f"ADVERTENCIA en {context}: {message}")
    except Exception:
        pass
    logger = _get_logger(log_file)
    if logger is not None:
        logger.warning(f"{context}: {message}")
