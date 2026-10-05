"""Componente Form: agrupa campos editables, valida y devuelve sus valores."""
import curses

from ncurses_ui.components.base import Component, draw_child
from ncurses_ui.kernel.input import is_enter, is_escape
from ncurses_ui.kernel.renderer import Region, safe_addstr


class Form(Component):
    """Formulario: dibuja campos, rutea teclas al campo enfocado y devuelve `values`."""

    focusable = True

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.fields = self._build_fields()
        self.field_components = []
        self.cursor = 0
        self.action = None

    def _build_fields(self):
        out = []
        for field in self.config.get("fields", self.config.get("elements", [])):
            if isinstance(field, str):
                out.append({"name": field, "label": field, "type": "text"})
            else:
                out.append(field)
        return out

    def _child_config(self, field):
        config = dict(field)
        config.setdefault("operator", config.get("type", "text"))
        return config

    def _ensure_fields(self):
        if len(self.field_components) != len(self.fields):
            self.field_components = [self._create_child(self._child_config(field)) for field in self.fields]

    def render(self, window, region):
        self._ensure_fields()
        y = region.y
        for i, field in enumerate(self.fields):
            if y >= region.y + region.height:
                break
            marker = ">" if i == self.cursor else " "
            safe_addstr(window, y, region.x, marker, 0, 1)
            child = self.field_components[i]
            if child is not None:
                draw_child(child, window, Region(y, region.x + 2, 1, max(0, region.width - 2)))
            else:
                label = field.get("label", field.get("name", ""))
                safe_addstr(window, y, region.x + 2, label, 0, max(0, region.width - 2))
            y += 1

    def handle_key(self, key):
        self._ensure_fields()
        if is_escape(key):
            action = self.dispatch_event("on_cancel", {"values": self.values()})
            if action and action.get("action") in ("navigate", "back"):
                return action
            if action and action.get("action") == "callback":
                self.invoke_callback(action.get("handler"), action.get("payload"))
            self.action = "cancel"
            return "cancel"
        if is_enter(key):
            action = self.dispatch_event("on_submit", {"values": self.values()})
            if action and action.get("action") in ("navigate", "back"):
                return action
            if action and action.get("action") == "callback":
                if not self.invoke_callback(action.get("handler"), action.get("payload")):
                    return None
            self.action = "done"
            return "done"
        if key in (9, curses.KEY_BTAB, curses.KEY_DOWN):
            self.cursor = (self.cursor + 1) % max(1, len(self.fields))
            return None
        if key == curses.KEY_UP:
            self.cursor = (self.cursor - 1) % max(1, len(self.fields))
            return None
        child = self.field_components[self.cursor] if self.field_components else None
        if child is not None and hasattr(child, "handle_key"):
            child.handle_key(key)
        return None

    def values(self):
        self._ensure_fields()
        values = {}
        for field, child in zip(self.fields, self.field_components):
            name = field.get("name")
            if not name:
                continue
            if child is not None and hasattr(child, "result"):
                values[name] = child.result().get("value")
            else:
                values[name] = field.get("value")
        return values

    def validate(self):
        errors = []
        rules = self.config.get("rules") or {}
        values = self.values()
        for field in self.fields:
            name = field.get("name")
            if not name:
                continue
            field_rules = rules.get(name) or {}
            value = values.get(name)
            if field_rules.get("required") and (value is None or value == ""):
                errors.append({"field": name, "error": "required"})
        return errors

    def result(self):
        return {
            "status": "ok",
            "values": self.values(),
            "errors": self.validate(),
            "action": "submit" if self.action == "done" else "cancel",
        }
