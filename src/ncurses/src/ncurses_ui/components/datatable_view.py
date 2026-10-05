"""Render y loop del componente DataTable (curses).

Dibuja la tabla, maneja teclas y corre el loop de terminal. Se combina
con DataTableStateMixin en DataTableComponent.
"""
import curses
from typing import Any, Dict, List

from ncurses_ui.errors import NcursesError
from ncurses_ui.kernel.renderer import color_pair, safe_addstr
from ncurses_ui.themes import init_datatable_colors


class DataTableViewMixin:
    def _source_items(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        data = config.get("data")
        if isinstance(data, list):
            return data
        source = config.get("source") or (data if isinstance(data, str) else None)
        if not source:
            raise NcursesError("datatable: falta 'source' o 'data' (filas para mostrar)")
        handler = getattr(self.context, "memory_handler", None) if self.context else None
        if handler is None:
            raise NcursesError("datatable: no hay memory_handler para leer la variable de Sugar")
        value = handler.get_variable(source)
        if value is None:
            raise NcursesError(f"datatable: la variable '{source}' no existe o esta vacia")
        if isinstance(value, dict):
            return [value]
        if not isinstance(value, list):
            raise NcursesError(f"datatable: '{source}' no es una lista (es {type(value).__name__})")
        return value

    def _datatable_handle_key(self, key, state, page_size):
        if state["search_mode"]:
            return self._datatable_search_key(key, state)
        if state.get("header_focus"):
            return self._datatable_header_key(key, state)
        if state.get("edit_mode"):
            return self._datatable_edit_key(key, state)
        if key in (ord("q"), ord("Q")):
            return "quit"
        if key in (ord("h"), ord("H")):
            self._datatable_enter_header(state)
            return None
        if key in (curses.KEY_UP, ord("k")):
            if key == curses.KEY_UP and state["cursor"] == 0 and state["offset"] == 0 and state["show_header"]:
                self._datatable_enter_header(state)
            else:
                self._move_with_event(state, -1)
        elif key in (curses.KEY_DOWN, ord("j")):
            self._move_with_event(state, 1)
        elif key == curses.KEY_PPAGE:
            self._datatable_page(state, -page_size)
        elif key == curses.KEY_NPAGE:
            self._datatable_page(state, page_size)
        elif key == curses.KEY_HOME:
            state["cursor"] = 0
        elif key == curses.KEY_END:
            state["cursor"] = max(0, len(state["rows"]) - 1)
        elif key in (10, 13, curses.KEY_ENTER):
            action = self._dispatch_event(state, "on_item_click", self._current_row_payload(state))
            if action and action.get("action") in ("navigate", "back"):
                return action
            if action and action.get("action") == "callback":
                return "detail" if self._invoke_callback(action.get("handler"), action.get("payload")) else None
            if action and action.get("action") == "close":
                return "quit"
            if action and action.get("action") == "none":
                return None
            return "detail"
        elif key == ord("/"):
            state["search_mode"] = True
        elif key in (ord("f"), ord("F")):
            self._datatable_cycle_filter(state)
            return "reload"
        elif key in (ord("l"), ord("L")):
            state["only_flags"] = not state["only_flags"]
            state["offset"] = 0
            state["cursor"] = 0
            return "reload"
        elif key in (ord("s"), ord("S")):
            self._datatable_cycle_sort(state)
            return "reload"
        elif key in (ord("o"), ord("O")):
            self._datatable_toggle_sort(state)
            return "reload"
        elif key == ord(" "):
            action = self._dispatch_event(state, "on_check", self._current_row_payload(state))
            if action is None or action.get("action") == "toggle":
                self._datatable_toggle_mark(state)
        elif key in (ord("r"), ord("R")):
            return "reload"
        elif key in (ord("e"), ord("E")) and state.get("editable_cols"):
            self._start_edit(state)
        elif key == curses.KEY_LEFT and state.get("editable_cols"):
            self._cycle_edit_col(state, -1)
        elif key == curses.KEY_RIGHT and state.get("editable_cols"):
            self._cycle_edit_col(state, 1)
        action = self._dispatch_event(state, "on_key", {"key": key})
        if action and action.get("action") in ("navigate", "back"):
            return action
        if action and action.get("action") == "callback":
            self._invoke_callback(action.get("handler"), action.get("payload"))
        return None

    def _datatable_edit_key(self, key, state):
        if key == 27:
            state["edit_mode"] = False
            state["edit_buffer"] = ""
            return None
        if key in (10, 13, curses.KEY_ENTER):
            self._commit_edit(state)
            return "reload"
        if key in (curses.KEY_BACKSPACE, 127, 8):
            state["edit_buffer"] = state["edit_buffer"][:-1]
            return None
        if 32 <= key < 127:
            state["edit_buffer"] += chr(key)
        return None

    def _cycle_edit_col(self, state, delta):
        cols = state.get("editable_cols") or []
        if not cols:
            return
        current = state.get("edit_col")
        position = cols.index(current) if current in cols else 0
        state["edit_col"] = cols[(position + delta) % len(cols)]

    def _start_edit(self, state):
        rows = state.get("rows") or []
        if not rows or state.get("edit_col") is None:
            return
        row = rows[state["cursor"]]
        column = state["columns"][state["edit_col"]]
        value = row.get(column["id"])
        payload = {"row": row, "column": column["id"], "value": value}
        action = self._dispatch_event(state, "on_before_edit", payload)
        if action and action.get("action") == "callback":
            if not self._invoke_callback(action.get("handler"), action.get("payload")):
                return
        state["edit_mode"] = True
        state["edit_buffer"] = "" if value is None else str(value)

    def _commit_edit(self, state):
        rows = state.get("rows") or []
        if rows and state.get("edit_col") is not None:
            row = rows[state["cursor"]]
            column = state["columns"][state["edit_col"]]
            value = self._coerce_cell(state["edit_buffer"], column)
            row[column["id"]] = value
            payload = {"row": row, "column": column["id"], "value": value}
            after = self._dispatch_event(state, "on_after_edit", payload)
            if after and after.get("action") == "callback":
                self._invoke_callback(after.get("handler"), after.get("payload"))
        state["edit_mode"] = False
        state["edit_buffer"] = ""

    def _invoke_callback(self, handler, payload):
        manager = self.manager
        if manager is None or not hasattr(manager, "invoke_anonymous"):
            return None
        try:
            return manager.invoke_anonymous(handler, payload or {})
        except Exception:
            return None

    def _move_with_event(self, state, delta):
        rows = state.get("rows") or []
        target = state["cursor"] + delta
        if 0 <= target < len(rows):
            payload = {"row": rows[target]}
            action = self._dispatch_event(state, "on_before_select", payload)
            if action and action.get("action") == "callback":
                if not self._invoke_callback(action.get("handler"), payload):
                    return
        self._datatable_move(state, delta)
        after = self._dispatch_event(state, "on_after_select", self._current_row_payload(state))
        if after and after.get("action") == "callback":
            self._invoke_callback(after.get("handler"), after.get("payload"))

    def _datatable_search_key(self, key, state):
        if key in (10, 13, curses.KEY_ENTER):
            state["search_mode"] = False
        elif key == 27:
            state["query"] = ""
            state["search_mode"] = False
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            state["query"] = state["query"][:-1]
        elif 32 <= key < 127:
            state["query"] += chr(key)
        else:
            return None
        state["offset"] = 0
        state["cursor"] = 0
        return "reload"

    def _datatable_header_key(self, key, state):
        sortable = self._sortable_indices(state["columns"])
        if not sortable:
            state["header_focus"] = False
            return None
        if key in (27, curses.KEY_DOWN):
            state["header_focus"] = False
            return None
        if key in (ord("q"), ord("Q")):
            return "quit"
        position = sortable.index(state["header_cursor"]) if state["header_cursor"] in sortable else 0
        if key in (curses.KEY_LEFT, ord("h")):
            state["header_cursor"] = sortable[(position - 1) % len(sortable)]
        elif key in (curses.KEY_RIGHT, ord("l")):
            state["header_cursor"] = sortable[(position + 1) % len(sortable)]
        elif key in (10, 13, curses.KEY_ENTER, ord(" ")):
            self._datatable_sort_by(state, state["header_cursor"])
            action = self._dispatch_event(state, "on_header_click", {"index": state["header_cursor"]})
            if action and action.get("action") == "callback":
                self._invoke_callback(action.get("handler"), action.get("payload"))
        return None

    def _draw_datatable(self, window, state, title, page_size, region):
        y0, x0, height, width = region.y, region.x, region.height, region.width
        self._draw_box(window, region)
        self._safe_addstr(window, y0, x0 + 2, f" {title} ", color_pair(6), max(0, width - 4))
        self._draw_datatable_header(window, state, region)
        widths = self._column_widths(state, max(0, width - 2))
        first_row = y0 + (5 if state["show_header"] else 4)
        if state["show_header"]:
            self._draw_column_header(window, state, widths, y0 + 4, x0)
        self._draw_datatable_rows(window, state, page_size, widths, first_row, x0)
        self._draw_datatable_footer(window, state, region)

    def _draw_box(self, window, region):
        if region.width < 2 or region.height < 2:
            return
        line = "+" + "-" * (region.width - 2) + "+"
        self._safe_addstr(window, region.y, region.x, line, 0, region.width)
        for i in range(1, region.height - 1):
            self._safe_addstr(window, region.y + i, region.x, "|", 0, 1)
            self._safe_addstr(window, region.y + i, region.x + region.width - 1, "|", 0, 1)
        self._safe_addstr(window, region.y + region.height - 1, region.x, line, 0, region.width)

    def _draw_datatable_header(self, window, state, region):
        y0, x0, width = region.y, region.x, region.width
        cursor = "_" if state["search_mode"] else ""
        search_attr = color_pair(4) if state["search_mode"] else color_pair(1)
        self._safe_addstr(window, y0 + 1, x0 + 1, f"Buscar: {state['query']}{cursor}", search_attr, max(0, width - 2))
        parts = []
        spec = state.get("filter_spec")
        if spec:
            parts.append(f"{spec.get('header', spec['id'])} >= {state['filter_value']:g}")
        if any(col["type"] == "flag" for col in state["columns"]):
            parts.append(f"Flags: {'si' if state['only_flags'] else 'no'}")
        parts.append(f"Orden: {self._datatable_sort_label(state)}")
        if state.get("select_mode") == "multiselect":
            parts.append(f"Marcados: {len(state.get('marked', {}))}")
        parts.append(f"{state['total']} filas")
        self._safe_addstr(window, y0 + 2, x0 + 1, "   ".join(parts), color_pair(5), max(0, width - 2))
        self._safe_addstr(window, y0 + 3, x0 + 1, "-" * max(0, width - 2), color_pair(1), max(0, width - 2))

    def _column_widths(self, state, available):
        columns = state["columns"]
        if not columns:
            return []
        widths = []
        for column in columns:
            if column.get("width"):
                widths.append(int(column["width"]))
            elif column["type"] == "flag":
                widths.append(3)
            else:
                sample = max((len(self._cell_text(row, column)) for row in state["rows"][:50]), default=0)
                widths.append(max(len(column["header"]), min(sample, 40)))
        overhead = 2 + max(0, len(columns) - 1)
        budget = max(1, available - overhead)
        while sum(widths) > budget:
            index = max(
                range(len(columns)),
                key=lambda i: widths[i] if columns[i]["type"] != "flag" else -1,
            )
            if widths[index] <= 3:
                break
            widths[index] -= 1
        expandable = [i for i, column in enumerate(columns) if column.get("fillspace")]
        remaining = budget - sum(widths)
        if remaining > 0 and expandable:
            share = remaining // len(expandable)
            for index in expandable:
                widths[index] += share
            widths[expandable[0]] += remaining - share * len(expandable)
        return widths

    def _draw_column_header(self, window, state, widths, y, x0):
        x = x0 + 3
        sort_index = state["sort_index"]
        focus = state.get("header_focus")
        header_cursor = state.get("header_cursor")
        for index, (column, width) in enumerate(zip(state["columns"], widths)):
            text = column["header"]
            if index == sort_index:
                text = f"{text} {'v' if state['sort_desc'] else '^'}"
            text = text[:width]
            text = text.rjust(width) if self._align_right(column) else text.ljust(width)
            attr = color_pair(2) if (focus and index == header_cursor) else color_pair(5)
            self._safe_addstr(window, y, x, text, attr, width)
            x += width + 1

    def _draw_datatable_rows(self, window, state, page_size, widths, first_row, x0):
        for index, row in enumerate(state["rows"][:page_size]):
            self._draw_datatable_row(window, state, row, first_row + index, widths, index == state["cursor"], x0)

    def _draw_datatable_row(self, window, state, row, y, widths, selected, x0):
        row_attr = color_pair(2) if selected else color_pair(1)
        marked = state.get("select_mode") == "multiselect" and self._row_key(row) in state.get("marked", {})
        marker = ">" if selected else ("+" if marked else " ")
        self._safe_addstr(window, y, x0 + 1, marker, row_attr, 1)
        x = x0 + 3
        editing = state.get("edit_mode") and state.get("rows") and row is state["rows"][state["cursor"]]
        for index, (column, width) in enumerate(zip(state["columns"], widths)):
            if editing and index == state.get("edit_col"):
                text = (state["edit_buffer"] + "_")[:width]
            else:
                text = self._cell_text(row, column)[:width]
            text = text.rjust(width) if self._align_right(column) else text.ljust(width)
            if column["type"] == "flag":
                available = self._truthy(row.get(column["id"]))
                attr = row_attr if selected else (
                    color_pair(3) if available else color_pair(1)
                )
            else:
                attr = row_attr
            self._safe_addstr(window, y, x, text, attr, width)
            x += width + 1

    def _draw_datatable_footer(self, window, state, region):
        if state.get("header_focus"):
            keys = "Cabecera: flechas/h-l mover  Enter ordenar  Esc/abajo volver  q salir"
        else:
            keys = "Flechas/Enter detalle  /buscar  s orden  o dir"
            if state["show_header"] and self._sortable_indices(state["columns"]):
                keys += "  h cabecera"
            if state.get("filter_spec"):
                keys += "  f filtro"
            if any(column["type"] == "flag" for column in state["columns"]):
                keys += "  l flags"
            if state.get("select_mode") == "multiselect":
                keys += "  espacio marcar"
            keys += "  q salir"
        self._safe_addstr(window, region.y + region.height - 2, region.x + 1, keys, color_pair(1), max(0, region.width - 2))

    def _open_detail(self, state, title):
        if not state["rows"]:
            return
        row = state["rows"][state["cursor"]]
        first = state["detail_fields"][0] if state["detail_fields"] else None
        heading = str(row.get(first["id"])) if first else title
        self._show_overlay(f" {heading} ", self._detail_lines(row, state["detail_fields"]))

    def _show_overlay(self, title, lines):
        parent = self.manager.original_screen
        height, width = parent.getmaxyx()
        win_w = max(20, min(width - 2, 100))
        lines = self._wrap_lines(lines, win_w - 2)
        win_h = max(5, min(height - 2, len(lines) + 2))
        win_y = max(0, (height - win_h) // 2)
        win_x = max(0, (width - win_w) // 2)
        overlay = curses.newwin(win_h, win_w, win_y, win_x)
        overlay.keypad(True)
        top, body_h = 0, win_h - 2
        while True:
            self._draw_overlay(overlay, title, lines, top, win_h, win_w)
            key = overlay.getch()
            if key in (curses.KEY_UP, ord("k")):
                top = max(0, top - 1)
            elif key in (curses.KEY_DOWN, ord("j")):
                top = min(max(0, len(lines) - body_h), top + 1)
            elif key == curses.KEY_PPAGE:
                top = max(0, top - body_h)
            elif key == curses.KEY_NPAGE:
                top = min(max(0, len(lines) - body_h), top + body_h)
            else:
                break
        del overlay

    def _draw_overlay(self, overlay, title, lines, top, win_h, win_w):
        overlay.erase()
        overlay.box()
        self._safe_addstr(overlay, 0, 2, title, color_pair(5), win_w - 4)
        body_h = win_h - 2
        for i in range(body_h):
            index = top + i
            if index >= len(lines):
                break
            self._safe_addstr(overlay, i + 1, 1, lines[index], color_pair(1), win_w - 2)
        if len(lines) > body_h:
            pct = int(100 * (top + body_h) / len(lines))
            self._safe_addstr(overlay, win_h - 1, max(1, win_w - 6), f"{pct:3d}%", color_pair(5), 5)
        overlay.refresh()

    @staticmethod
    def _init_datatable_colors():
        init_datatable_colors()

    @staticmethod
    def _safe_addstr(window, y, x, text, attr=0, max_width=None):
        safe_addstr(window, y, x, text, attr, max_width)
