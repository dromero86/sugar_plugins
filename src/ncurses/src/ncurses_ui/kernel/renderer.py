"""Primitivas de dibujo seguras sobre curses."""
import curses
import re
import unicodedata
from collections import defaultdict
from collections import namedtuple

Region = namedtuple("Region", "y x height width")

_PLACEHOLDER = re.compile(r"#(\w+)#")


def char_width(char):
    """Ancho visual de un caracter (0 combinante, 2 ancho, 1 resto)."""
    if unicodedata.combining(char):
        return 0
    return 2 if unicodedata.east_asian_width(char) in ("W", "F") else 1


def display_width(text):
    """Ancho visual de un string (tiene en cuenta wide chars y combinantes)."""
    return sum(char_width(char) for char in str(text))


def truncate_visual(text, max_width):
    """Recorta `text` a `max_width` columnas visuales."""
    if max_width is None:
        return text
    text = str(text)
    if display_width(text) <= max_width:
        return text
    out = []
    width = 0
    for char in text:
        size = char_width(char)
        if width + size > max_width:
            break
        out.append(char)
        width += size
    return "".join(out)


def color_pair(pair):
    """`curses.color_pair` seguro: 0 si curses no esta inicializado."""
    try:
        return curses.color_pair(pair)
    except curses.error:
        return 0


def safe_addstr(window, y, x, text, attr=0, max_width=None):
    try:
        if max_width is not None:
            text = truncate_visual(text, max_width)
        window.addstr(y, x, str(text), attr)
    except curses.error:
        pass


def wrap_lines(lines, width):
    if width <= 1:
        return lines
    wrapped = []
    for line in lines:
        if len(line) <= width:
            wrapped.append(line)
        else:
            wrapped.extend(line[i:i + width] for i in range(0, len(line), width))
    return wrapped


def render_template(text, data):
    """Renderiza `#campo#` (y `{campo}` por compatibilidad) con `data`."""
    if text is None or text == "":
        return ""
    text = str(text)
    data = data or {}
    text = _PLACEHOLDER.sub(lambda m: str(data.get(m.group(1), "")), text)
    try:
        return text.format_map(defaultdict(str, data))
    except (KeyError, ValueError, IndexError):
        return text
