"""Contrato base de los componentes de UI ncurses.

Contrato unico:
- `draw(window, region)`: dibuja una vez en la region.
- `handle_key(key)`: procesa una tecla; devuelve 'quit'/'done'/'cancel'/None.
- `result()`: resultado del componente (contrato comun de retorno).
- `run()`: driver de pantalla completa (kernel/app.App).

Un componente componible NO corre su propio loop: el driver o el layout padre
lo dibuja y le rutea las teclas. `StaticComponent`/`FieldComponent` son atajos.
"""
from abc import ABC, abstractmethod

from ncurses_ui.kernel.renderer import Region
from ncurses_ui.kernel.screen import TerminalScreen


def draw_child(child, window, region):
    """Dibuja un hijo usando `draw` o, por compatibilidad, `render`."""
    if child is None:
        return
    if hasattr(child, "draw"):
        child.draw(window, region)
    elif hasattr(child, "render"):
        child.render(window, region)


class Component(ABC):
    """Componente de UI: dibuja, maneja teclas y devuelve un resultado."""

    wait = False
    focusable = False

    def __init__(self, config=None, context=None, manager=None):
        self.config = config or {}
        self.context = context
        self.manager = manager

    def draw(self, window, region):
        render = getattr(self, "render", None)
        if render is not None:
            render(window, region)

    def handle_key(self, key):
        return None

    def handle_mouse(self, x, y, region):
        """Click en (x, y) dentro de `region`. Devuelve accion o None."""
        return None

    def result(self):
        return {"status": "ok"}

    def run(self):
        from ncurses_ui.kernel.app import App
        return App(self).run()

    def _create_child(self, config):
        registry = getattr(self.manager, "registry", None) if self.manager is not None else None
        if registry is None or not isinstance(config, dict):
            return None
        operator = config.get("operator") or config.get("view")
        if not operator or not registry.has(operator):
            return None
        return registry.create(operator, config, self.context, self.manager)

    def dispatch_event(self, event_name, payload=None):
        from ncurses_ui.events.dispatcher import EventDispatcher
        if not hasattr(self, "_event_dispatcher"):
            self._event_dispatcher = EventDispatcher(self.config.get("events"))
        return self._event_dispatcher.dispatch(event_name, payload)

    def invoke_callback(self, handler, payload):
        manager = self.manager
        if manager is None or not hasattr(manager, "invoke_anonymous"):
            return None
        try:
            return manager.invoke_anonymous(handler, payload or {})
        except Exception:
            return None

    def notify(self, event_name, payload=None):
        """Despacha un evento y, si el handler es callback, lo invoca (notifica)."""
        action = self.dispatch_event(event_name, payload)
        if action and action.get("action") == "callback":
            self.invoke_callback(action.get("handler"), action.get("payload"))
        return action


class StaticComponent(Component):
    """Dibuja una vez y (por defecto) espera una tecla para cerrar."""

    wait = True


class FieldComponent(Component):
    """Componente de un campo interactivo de una linea."""

    focusable = True

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.value = self.config.get("value")

    def handle_key(self, key):
        return "done"

    def result(self):
        return {"status": "ok", "value": self.value}
