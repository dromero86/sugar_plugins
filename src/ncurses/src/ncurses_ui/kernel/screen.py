"""Ciclo de vida del terminal (curses) para los componentes."""
import curses
import locale

from ncurses_ui.themes import init_datatable_colors


class TerminalScreen:
    """Context manager que inicializa y restaura el terminal."""

    def __init__(self, manager=None, enable_mouse=False):
        self.manager = manager
        self.enable_mouse = enable_mouse
        self.screen = None

    def __enter__(self):
        locale.setlocale(locale.LC_ALL, "")
        screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        screen.keypad(True)
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        curses.start_color()
        try:
            curses.use_default_colors()
        except curses.error:
            pass
        if self.enable_mouse:
            try:
                curses.mousemask(curses.ALL_MOUSE_EVENTS)
            except curses.error:
                pass
        init_datatable_colors()
        self.screen = screen
        if self.manager is not None:
            self.manager.initialized = True
            self.manager.original_screen = screen
        return screen

    def __exit__(self, *exc):
        curses.nocbreak()
        if self.screen is not None:
            self.screen.keypad(False)
        curses.echo()
        curses.endwin()
        if self.manager is not None:
            self.manager.initialized = False
        return False
