"""Decodificacion de teclas de curses a nombres legibles."""
import curses


_KEY_NAMES = {
    curses.KEY_UP: "UP",
    curses.KEY_DOWN: "DOWN",
    curses.KEY_LEFT: "LEFT",
    curses.KEY_RIGHT: "RIGHT",
    curses.KEY_ENTER: "ENTER",
    curses.KEY_BACKSPACE: "BACKSPACE",
    curses.KEY_DC: "DELETE",
    curses.KEY_HOME: "HOME",
    curses.KEY_END: "END",
    curses.KEY_PPAGE: "PAGE_UP",
    curses.KEY_NPAGE: "PAGE_DOWN",
    curses.KEY_F1: "F1",
    curses.KEY_F2: "F2",
    curses.KEY_F3: "F3",
    curses.KEY_F4: "F4",
    curses.KEY_F5: "F5",
    curses.KEY_F6: "F6",
    curses.KEY_F7: "F7",
    curses.KEY_F8: "F8",
    curses.KEY_F9: "F9",
    curses.KEY_F10: "F10",
    curses.KEY_F11: "F11",
    curses.KEY_F12: "F12",
    27: "ESC",
    9: "TAB",
    10: "ENTER",
}


def key_to_name(key):
    return _KEY_NAMES.get(key, f"KEY_{key}")


def is_enter(key):
    return key in (10, 13, curses.KEY_ENTER)


def is_escape(key):
    return key == 27


def is_backspace(key):
    return key in (curses.KEY_BACKSPACE, 127, 8)


def is_printable(key):
    return 32 <= key < 127
