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
    'typing_delay_range': None,
    'typing_pause_chance': 0.0,
    'typing_pause_range': (0.15, 0.4),
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
    """Delay entre teclas. Si hay 'typing_delay_range', se muestrea al azar."""
    cfg = settings(humanize)
    rng = cfg.get('typing_delay_range')
    if rng:
        return random.uniform(float(rng[0]), float(rng[1]))
    return float(cfg['typing_delay'])


def typing_pause(humanize: Optional[Dict[str, Any]]) -> float:
    """Pausa ocasional entre teclas (duda/lectura), con probabilidad configurable."""
    cfg = settings(humanize)
    chance = float(cfg.get('typing_pause_chance') or 0.0)
    if chance <= 0.0 or random.random() >= chance:
        return 0.0
    rng = cfg.get('typing_pause_range') or (0.15, 0.4)
    return random.uniform(float(rng[0]), float(rng[1]))


def mouse_steps(humanize: Optional[Dict[str, Any]]) -> int:
    return max(1, int(settings(humanize)['mouse_steps']))


def scroll_step(humanize: Optional[Dict[str, Any]]) -> int:
    return max(1, int(settings(humanize)['scroll_step']))
