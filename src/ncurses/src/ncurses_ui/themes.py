"""Pares de color del plugin ncurses."""
import curses


def init_datatable_colors():
    """Inicializa los pares de color usados por los componentes.

    En terminales sin color (monocromo) no hace nada: los componentes caen a
    atributos (bold/reverse) o a texto plano.
    """
    if not curses.has_colors():
        return
    curses.init_pair(1, curses.COLOR_WHITE, -1)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(3, curses.COLOR_GREEN, -1)
    curses.init_pair(4, curses.COLOR_YELLOW, -1)
    curses.init_pair(5, curses.COLOR_CYAN, -1)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)
