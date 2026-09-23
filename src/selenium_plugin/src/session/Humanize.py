"""
Capa de sesion: humanizacion
============================

Helpers para introducir variabilidad (delays, typing, scroll) y que la
automatizacion no sea perfectamente regular.
"""

import os
import random
import sys
import time
from typing import Any, Dict, Optional

# Bootstrap: ver BrowserFactory.
_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)


DEFAULTS = {
    'min_delay': 0.1,
    'max_delay': 0.5,
    'typing_delay': 0.05,
    'mouse_steps': 3,
    'scroll_step': 250,
}


def settings(humanize: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    merged = dict(DEFAULTS)
    if isinstance(humanize, dict):
        merged.update({k: v for k, v in humanize.items() if v is not None})
    return merged


def between_operators_delay(humanize: Optional[Dict[str, Any]]) -> float:
    cfg = settings(humanize)
    return random.uniform(float(cfg['min_delay']), float(cfg['max_delay']))


def sleep_between_operators(humanize: Optional[Dict[str, Any]]) -> None:
    time.sleep(between_operators_delay(humanize))


def typing_delay(humanize: Optional[Dict[str, Any]]) -> float:
    return float(settings(humanize)['typing_delay'])


def mouse_steps(humanize: Optional[Dict[str, Any]]) -> int:
    return max(1, int(settings(humanize)['mouse_steps']))


def scroll_step(humanize: Optional[Dict[str, Any]]) -> int:
    return max(1, int(settings(humanize)['scroll_step']))
