"""
Plugin Ncurses para Sugar Language
==================================

Proporciona capacidades completas de interfaz de terminal (TUI) utilizando ncurses.
"""

__version__ = "1.0.0"
__author__ = "Sugar Team"
__description__ = "Plugin Ncurses para Sugar - Interfaces de terminal interactivas (TUI)"

from .src.ncurses_plugin import NcursesPlugin

__all__ = ['NcursesPlugin']