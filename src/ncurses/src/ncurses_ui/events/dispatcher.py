"""Resolucion de eventos declarativos a acciones built-in."""

BUILTIN_ACTIONS = {"detail", "edit", "toggle", "select", "set", "emit", "close", "none", "navigate", "back"}


class EventDispatcher:
    """Mapea eventos (`on_item_click`, ...) a acciones built-in.

    Handlers soportados (Fase 1):
    - string: `{"on_item_click": "detail"}`
    - objeto con `action`: `{"on_item_click": {"action": "detail"}}`

    Una funcion/lambda inline (Fase 2) se devuelve como `action: "callback"`
    para que el bridge plugin->Sugar la resuelva (aun no implementado).
    """

    def __init__(self, events=None):
        self.events = events or {}

    def has(self, event_name):
        return event_name in self.events

    def dispatch(self, event_name, payload=None):
        handler = self.events.get(event_name)
        if handler is None:
            return None
        if isinstance(handler, str):
            action, extra = handler, {}
        elif isinstance(handler, dict) and "action" in handler:
            action = handler["action"]
            extra = {key: value for key, value in handler.items() if key != "action"}
        else:
            return {
                "event": event_name,
                "action": "callback",
                "handler": handler,
                "payload": payload or {},
            }
        result = {"event": event_name, "action": action, "payload": payload or {}}
        if action not in BUILTIN_ACTIONS:
            result["error"] = f"accion desconocida: {action}"
        result.update(extra)
        return result
