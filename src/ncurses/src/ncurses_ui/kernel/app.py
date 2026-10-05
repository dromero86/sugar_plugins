"""Driver de pantalla unico para componentes."""
import curses

from ncurses_ui.kernel.renderer import Region
from ncurses_ui.kernel.screen import TerminalScreen


class App:
    """Corre el loop de terminal y despacha teclas al componente raiz."""

    def __init__(self, root, manager=None):
        self.root = root
        self.manager = manager if manager is not None else getattr(root, "manager", None)

    def run(self):
        enable_mouse = bool(getattr(self.root, "config", {}).get("enable_mouse", False))
        with TerminalScreen(self.manager, enable_mouse=enable_mouse) as screen:
            while True:
                height, width = screen.getmaxyx()
                region = Region(0, 0, height, width)
                try:
                    screen.erase()
                except curses.error:
                    pass
                self.root.draw(screen, region)
                screen.refresh()
                if getattr(self.root, "wait", False):
                    screen.getch()
                    break
                key = screen.getch()
                if key == curses.KEY_RESIZE:
                    self._notify("on_resize", {"height": height, "width": width})
                    continue
                if key == curses.KEY_MOUSE:
                    action = self._handle_mouse(region)
                else:
                    action = self.root.handle_key(key)
                if action in ("quit", "done", "cancel"):
                    break
        self._notify("on_close", {})
        return self.root.result()

    def _notify(self, event_name, payload):
        notify = getattr(self.root, "notify", None)
        if notify is not None:
            notify(event_name, payload)

    def _handle_mouse(self, region):
        try:
            _, mx, my, _, bstate = curses.getmouse()
        except curses.error:
            return None
        if not (bstate & (curses.BUTTON1_CLICKED | curses.BUTTON1_PRESSED)):
            return None
        return self.root.handle_mouse(mx, my, region)
