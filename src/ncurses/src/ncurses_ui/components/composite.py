"""Vista compuesta generica (`composite`) y presets."""
import curses

from ncurses_ui.components.base import Component, StaticComponent, draw_child
from ncurses_ui.components.layout import Layout
from ncurses_ui.kernel.layout import split
from ncurses_ui.kernel.renderer import safe_addstr


class Composite(StaticComponent):
    """Compone `parts` en filas (o columnas) sobre el kernel."""

    def parts(self):
        return self.config.get("parts", {})

    def render(self, window, region):
        parts = self.parts()
        if not parts:
            return
        keys = list(parts.keys())
        horizontal = bool(self.config.get("horizontal", False))
        regions = split(region, [{"weight": 1}] * len(keys), horizontal=horizontal, gap=self.config.get("gap", 0))
        for key, child_region in zip(keys, regions):
            child = self._create_child(parts[key])
            if child is not None:
                draw_child(child, window, child_region)


class ListView(Layout):
    """Preset: titulo + datatable/list."""

    def __init__(self, config=None, context=None, manager=None):
        config = config or {}
        columns = config.get("columns")
        rows = []
        if config.get("title"):
            rows.append({"operator": "label", "label": config["title"], "height": 1})
        rows.append({
            "operator": "datatable" if columns else "list",
            "data": config.get("data"),
            "columns": columns,
            "template": config.get("template"),
            "select": config.get("select", "row"),
            "id": config.get("id"),
        })
        super().__init__({"operator": "layout", "rows": rows}, context, manager)


class FormView(Layout):
    """Preset: titulo + form."""

    def __init__(self, config=None, context=None, manager=None):
        config = config or {}
        rows = []
        title = config.get("title_set") or config.get("title_add") or config.get("title")
        if title:
            rows.append({"operator": "label", "label": title, "height": 1})
        rows.append({
            "operator": "form",
            "fields": config.get("elements", config.get("fields", [])),
            "rules": config.get("rules", {}),
            "id": config.get("id"),
        })
        super().__init__({"operator": "layout", "rows": rows}, context, manager)


class DataFull(Layout):
    """Preset: busqueda + list/dataview."""

    def __init__(self, config=None, context=None, manager=None):
        config = config or {}
        columns = config.get("columns")
        rows = [{"operator": "search", "placeholder": config.get("search", "Buscar"), "height": 1}]
        rows.append({
            "operator": "datatable" if columns else config.get("body", "list"),
            "data": config.get("data"),
            "columns": columns,
            "template": config.get("template"),
            "search_fields": config.get("search_fields"),
            "id": config.get("id"),
        })
        super().__init__({"operator": "layout", "rows": rows}, context, manager)


class CardView(Layout):
    """Preset: grilla de cards (dataview)."""

    def __init__(self, config=None, context=None, manager=None):
        config = config or {}
        super().__init__(
            {"operator": "layout", "rows": [{
                "operator": "dataview",
                "data": config.get("data"),
                "template": config.get("template"),
                "id": config.get("id"),
            }]},
            context,
            manager,
        )


class MasterDetail(Component):
    """Preset: lista maestra + detalle que sigue la seleccion.

    El panel de detalle se sincroniza con la fila seleccionada de la lista en
    cada `draw` (reactivo). `Tab` cambia el foco entre maestro y detalle.
    """

    focusable = True

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.master_config = self.config.get("master") or {
            "operator": "list",
            "data": self.config.get("data"),
            "template": self.config.get("template", "#nombre#"),
            "events": self.config.get("events", {}),
        }
        self.detail_config = self.config.get("detail") or {
            "operator": "property",
            "data": self.config.get("detail_data", {}),
        }
        self.master_width = int(self.config.get("master_width", 30))
        self.master = None
        self.detail = None
        self.focus = 0

    def _ensure_children(self):
        if self.master is None:
            self.master = self._create_child(self.master_config)
        if self.detail is None:
            self.detail = self._create_child(self.detail_config)

    def _selected_item(self):
        if self.master is not None and getattr(self.master, "items", None):
            return self.master.items[self.master.cursor]
        return None

    def _sync_detail(self):
        if self.detail is not None and hasattr(self.detail, "set_data"):
            self.detail.set_data(self._selected_item())

    def _regions(self, region):
        return split(region, [{"size": self.master_width}, {"weight": 1}], horizontal=True, gap=self.config.get("gap", 0))

    def draw(self, window, region):
        self._ensure_children()
        self._sync_detail()
        regions = self._regions(region)
        draw_child(self.master, window, regions[0])
        draw_child(self.detail, window, regions[1])

    def handle_key(self, key):
        self._ensure_children()
        if key in (9, curses.KEY_BTAB):
            self.focus = 1 - self.focus
            return None
        child = self.master if self.focus == 0 else self.detail
        if child is None:
            return "quit" if key in (ord("q"), ord("Q"), 27) else None
        return child.handle_key(key)

    def handle_mouse(self, x, y, region):
        self._ensure_children()
        regions = self._regions(region)
        for index, (child, child_region) in enumerate(((self.master, regions[0]), (self.detail, regions[1]))):
            if child is None or not hasattr(child, "handle_mouse"):
                continue
            inside = (child_region.x <= x < child_region.x + child_region.width
                      and child_region.y <= y < child_region.y + child_region.height)
            if inside:
                self.focus = index
                action = child.handle_mouse(x, y, child_region)
                self._sync_detail()
                return action
        return None

    def result(self):
        return {"status": "ok", "master": self.master.result() if self.master else None}


class Dashboard(Component):
    """Panel de administracion: mainbar + sidebar + grilla de cards.

    El `mainbar` (arriba) tiene el nombre de la app y el toggle del sidebar a
    la izquierda, y el menu de usuario (popup) a la derecha. Config:
    `name`/`title`, `user_menu`, `menu`, `cards` (`{label, value, icon}`),
    `cols`, `sidebar_width`, `toolbar_height`.
    """

    focusable = True

    def __init__(self, config=None, context=None, manager=None):
        super().__init__(config, context, manager)
        self.toolbar_height = int(self.config.get("toolbar_height", 1))
        self.sidebar_width = int(self.config.get("sidebar_width", 24))
        self.collapsed = False
        self.user_open = False
        self.mainbar = None
        self.sidebar = None
        self.content = None

    def _ensure_children(self):
        if self.mainbar is None:
            self.mainbar = self._create_child({
                "operator": "mainbar",
                "name": self.config.get("name", self.config.get("title", "")),
                "user_menu": self.config.get("user_menu", []),
                "height": self.toolbar_height,
            })
        if self.sidebar is None:
            self.sidebar = self._create_child({
                "operator": "sidebar",
                "items": self.config.get("menu", []),
                "id": "sidebar",
                "events": self.config.get("menu_events", {}),
            })
        if self.content is None:
            cards = [
                {"operator": "card", "label": card.get("label", ""), "value": card.get("value", 0), "icon": card.get("icon", "")}
                for card in self.config.get("cards", [])
            ]
            self.content = self._create_child(
                {"operator": "gridlayout", "cols": int(self.config.get("cols", 2)), "cells": cards}
            )

    def _regions(self, region):
        top = split(region, [{"size": self.toolbar_height}, {"weight": 1}], horizontal=False)
        width = 0 if self.collapsed else self.sidebar_width
        body = split(top[1], [{"size": width}, {"weight": 1}], horizontal=True)
        return top[0], body[0], body[1]

    def draw(self, window, region):
        self._ensure_children()
        top, side, content = self._regions(region)
        draw_child(self.mainbar, window, top)
        if not self.collapsed:
            draw_child(self.sidebar, window, side)
        draw_child(self.content, window, content)
        if self.user_open:
            self._draw_user_menu(window, region)

    def _draw_user_menu(self, window, region):
        items = [
            str(item.get("value", item.get("label", item))) if isinstance(item, dict) else str(item)
            for item in self.config.get("user_menu", [])
        ]
        if not items:
            return
        width = max(len(item) for item in items) + 4
        x = max(region.x, region.x + region.width - width)
        y = region.y + self.toolbar_height
        line = "+" + "-" * (width - 2) + "+"
        safe_addstr(window, y, x, line, 0, width)
        for i, item in enumerate(items):
            safe_addstr(window, y + 1 + i, x, "| " + item.ljust(width - 4) + " |", 0, width)
        safe_addstr(window, y + len(items) + 1, x, line, 0, width)

    def _handle_action(self, action):
        kind = action.get("action")
        if kind == "toggle_sidebar":
            self.collapsed = not self.collapsed
        elif kind == "user_menu":
            self.user_open = not self.user_open
        return None

    def handle_key(self, key):
        self._ensure_children()
        if key in (ord("q"), 27):
            return "quit"
        if key in (ord("="), 9, ord("u"), ord("U")):
            action = self.mainbar.handle_key(key) if self.mainbar else None
            return self._handle_action(action) if isinstance(action, dict) else None
        if self.sidebar is not None and hasattr(self.sidebar, "handle_key"):
            return self.sidebar.handle_key(key)
        return None

    def handle_mouse(self, x, y, region):
        self._ensure_children()
        top, side, content = self._regions(region)
        action = self.mainbar.handle_mouse(x, y, top) if self.mainbar else None
        if isinstance(action, dict):
            return self._handle_action(action)
        if not self.collapsed and self.sidebar is not None and hasattr(self.sidebar, "handle_mouse"):
            if side.x <= x < side.x + side.width and side.y <= y < side.y + side.height:
                return self.sidebar.handle_mouse(x, y, side)
        return None

    def result(self):
        return {"status": "ok", "sidebar": self.sidebar.result() if self.sidebar else None}
