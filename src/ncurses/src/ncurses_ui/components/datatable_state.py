"""Logica pura del componente DataTable (estado, filtros, orden, formato).

Sin curses: normalizacion de columnas, filtrado, orden, paginacion y
formateo de celdas. Se combina con DataTableViewMixin en DataTableComponent.
"""
import unicodedata
from typing import Any, Dict, List

from ncurses_ui.events.dispatcher import EventDispatcher
from ncurses_ui.kernel.renderer import render_template, wrap_lines


class DataTableStateMixin:
    def _datatable_state(self, config: Dict[str, Any], items: List[Dict[str, Any]]) -> Dict[str, Any]:
        columns = self._normalize_columns(config.get("columns"), items)
        search_fields = config.get("search_fields") or self._default_search_fields(columns, items)
        detail_fields = self._normalize_detail_fields(
            config.get("detail") or config.get("detail_fields"), items
        )
        sort_id = config.get("sort") if isinstance(config.get("sort"), str) else None
        sort_index = 0
        if sort_id:
            sort_index = next((i for i, col in enumerate(columns) if col["id"] == sort_id), 0)
        filter_spec = self._normalize_filter(config.get("filter"))
        filter_value = 0.0
        if filter_spec:
            filter_value = float(config.get("filter_default", filter_spec.get("default", 0)) or 0)
        return {
            "items": items,
            "columns": columns,
            "search_fields": search_fields,
            "detail_fields": detail_fields,
            "filter_spec": filter_spec,
            "filter_value": filter_value,
            "query": config.get("initial_query", ""),
            "only_flags": False,
            "offset": 0,
            "cursor": 0,
            "total": 0,
            "rows": [],
            "search_mode": False,
            "show_header": bool(config.get("header", True)),
            "select_mode": config.get("select", "row"),
            "marked": {},
            "sort_index": sort_index % len(columns) if columns else 0,
            "sort_desc": bool(config.get("sort_desc", False)),
            "header_focus": False,
            "header_cursor": sort_index % len(columns) if columns else 0,
            "dirty": True,
            "dispatcher": EventDispatcher(config.get("events")),
            "editable_cols": self._editable_columns(config, columns),
            "edit_mode": False,
            "edit_col": (self._editable_columns(config, columns) or [None])[0],
            "edit_buffer": "",
        }

    @staticmethod
    def _editable_columns(config, columns):
        editable = config.get("editable")
        if isinstance(editable, list):
            return [i for i, col in enumerate(columns) if col["id"] in editable]
        if editable:
            return [i for i, col in enumerate(columns) if col["type"] != "flag" and col.get("editable", True)]
        return []

    @staticmethod
    def _coerce_cell(buffer, column):
        if column["type"] == "number":
            try:
                number = float(buffer)
                return int(number) if number.is_integer() else number
            except (TypeError, ValueError):
                return buffer
        return buffer

    def _dispatch_event(self, state, event_name, payload=None):
        dispatcher = state.get("dispatcher")
        if dispatcher is None:
            return None
        return dispatcher.dispatch(event_name, payload)

    @staticmethod
    def _current_row_payload(state):
        rows = state.get("rows") or []
        cursor = state.get("cursor", 0)
        row = rows[cursor] if 0 <= cursor < len(rows) else None
        return {"row": row}

    @staticmethod
    def _normalize_columns(columns, items):
        if not columns:
            keys = list(items[0].keys()) if items else []
            return [
                {
                    "id": key, "header": key, "type": DataTableStateMixin._guess_type(items, key),
                    "width": None, "fillspace": False, "template": None, "align": None,
                    "format": None, "sortable": True, "editable": True,
                }
                for key in keys
            ]
        normalized = []
        for column in columns:
            if isinstance(column, str):
                column = {"id": column}
            header = column.get("header", column["id"])
            if isinstance(header, list):
                header = header[0] if header else column["id"]
            normalized.append({
                "id": column["id"],
                "header": str(header),
                "type": DataTableStateMixin._column_type(column),
                "width": column.get("width"),
                "fillspace": bool(column.get("fillspace", False)),
                "template": column.get("template"),
                "align": column.get("align"),
                "format": column.get("format"),
                "sortable": "sort" in column,
                "editable": bool(column.get("editable", True)),
            })
        return normalized

    @staticmethod
    def _column_type(column):
        template = column.get("template")
        if isinstance(template, str) and "common.checkbox" in template:
            return "flag"
        sort = str(column.get("sort", "")).lower()
        if sort in ("int", "integer", "number", "float", "double", "decimal"):
            return "number"
        if sort in ("flag", "bool", "boolean", "checkbox"):
            return "flag"
        return "text"

    @staticmethod
    def _guess_type(items, field):
        for row in items[:20]:
            value = row.get(field)
            if value is None or value == "":
                continue
            return "number" if isinstance(value, (int, float)) and not isinstance(value, bool) else "text"
        return "text"

    @staticmethod
    def _default_search_fields(columns, items):
        fields = [col["id"] for col in columns if col["type"] == "text"]
        if fields:
            return fields
        if not items:
            return []
        return [key for key, value in items[0].items() if isinstance(value, str)]

    @staticmethod
    def _normalize_filter(filter_spec):
        if not filter_spec:
            return None
        field = filter_spec.get("id") or filter_spec.get("field")
        if not field:
            return None
        return {
            "id": field,
            "header": filter_spec.get("header") or filter_spec.get("label") or field,
            "steps": filter_spec.get("steps") or [0],
            "default": filter_spec.get("default", 0),
        }

    @staticmethod
    def _normalize_detail_fields(detail_fields, items):
        if not detail_fields:
            keys = list(items[0].keys()) if items else []
            return [{"id": key, "header": key} for key in keys]
        normalized = []
        for field in detail_fields:
            if isinstance(field, str):
                normalized.append({"id": field, "header": field})
            else:
                field_id = field.get("id") or field.get("field")
                normalized.append({
                    "id": field_id,
                    "header": field.get("header") or field.get("label") or field_id,
                })
        return normalized

    def _datatable_reload(self, state: Dict[str, Any], page_size: int):
        view = self._apply_view(state)
        state["view"] = view
        state["total"] = len(view)
        state["offset"] = min(state["offset"], max(0, state["total"] - 1))
        state["rows"] = view[state["offset"]:state["offset"] + page_size]
        state["cursor"] = min(state["cursor"], max(0, len(state["rows"]) - 1))
        state["dirty"] = False

    def _apply_view(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        query = self._normalize(state["query"])
        search_fields = state["search_fields"]
        filter_spec = state["filter_spec"]
        flag_fields = [col["id"] for col in state["columns"] if col["type"] == "flag"]
        view = []
        for row in state["items"]:
            if query and not self._row_matches(row, query, search_fields):
                continue
            if filter_spec and not self._passes_filter(row, filter_spec, state["filter_value"]):
                continue
            if state["only_flags"] and flag_fields and not any(self._truthy(row.get(f)) for f in flag_fields):
                continue
            view.append(row)
        return self._sort_rows(view, state)

    def _sort_rows(self, view, state):
        if not state["columns"]:
            return view
        column = state["columns"][state["sort_index"] % len(state["columns"])]
        field = column["id"]
        is_number = column["type"] == "number"

        def has_value(row):
            return self._truthy(row.get(field))

        present = [row for row in view if has_value(row)]
        missing = [row for row in view if not has_value(row)]

        def key(row):
            value = row.get(field)
            if is_number:
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return 0.0
            return self._normalize(value)

        present.sort(key=key, reverse=state["sort_desc"])
        return present + missing

    def _row_matches(self, row, query, search_fields):
        for field in search_fields:
            if query in self._normalize(row.get(field)):
                return True
        return False

    @staticmethod
    def _passes_filter(row, filter_spec, minimum):
        if not minimum:
            return True
        try:
            return float(row.get(filter_spec["id"])) >= float(minimum)
        except (TypeError, ValueError):
            return False

    @staticmethod
    def _truthy(value):
        return value is not None and value != "" and value != 0 and value is not False

    @staticmethod
    def _normalize(value):
        text = "" if value is None else str(value)
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        return text.lower()

    def _selected_rows(self, state):
        if state.get("select_mode") == "multiselect":
            marked = state.get("marked", {})
            selected = [row for row in state.get("view", []) if self._row_key(row) in marked]
            if not selected and state["rows"]:
                selected = [state["rows"][state["cursor"]]]
            return selected
        return state["rows"][state["cursor"]] if state["rows"] else None

    def _datatable_toggle_mark(self, state):
        if state.get("select_mode") != "multiselect" or not state["rows"]:
            return
        key = self._row_key(state["rows"][state["cursor"]])
        marked = state["marked"]
        if key in marked:
            del marked[key]
        else:
            marked[key] = True

    @staticmethod
    def _datatable_move(state, delta):
        page = len(state["rows"])
        if page == 0:
            return
        target = state["cursor"] + delta
        if target < 0:
            if state["offset"] > 0:
                state["offset"] -= 1
                state["dirty"] = True
            state["cursor"] = 0
        elif target >= page:
            if state["offset"] + page < state["total"]:
                state["offset"] += 1
                state["dirty"] = True
            state["cursor"] = page - 1
        else:
            state["cursor"] = target

    @staticmethod
    def _datatable_page(state, delta):
        max_offset = max(0, state["total"] - 1)
        state["offset"] = max(0, min(state["offset"] + delta, max_offset))
        state["cursor"] = 0
        state["dirty"] = True

    @staticmethod
    def _datatable_cycle_filter(state):
        spec = state.get("filter_spec")
        if not spec:
            return
        steps = spec.get("steps") or [0]
        try:
            index = steps.index(state["filter_value"])
        except ValueError:
            index = 0
        state["filter_value"] = float(steps[(index + 1) % len(steps)])
        state["offset"] = 0
        state["cursor"] = 0

    @staticmethod
    def _sortable_indices(columns):
        return [i for i, col in enumerate(columns) if col.get("sortable") and col["type"] != "flag"]

    @staticmethod
    def _datatable_cycle_sort(state):
        columns = state["columns"]
        sortable = DataTableStateMixin._sortable_indices(columns)
        if not sortable:
            return
        try:
            position = sortable.index(state["sort_index"])
        except ValueError:
            position = -1
        state["sort_index"] = sortable[(position + 1) % len(sortable)]
        state["sort_desc"] = columns[state["sort_index"]]["type"] == "number"
        state["offset"] = 0
        state["cursor"] = 0

    @staticmethod
    def _datatable_sort_by(state, index):
        if index == state["sort_index"]:
            state["sort_desc"] = not state["sort_desc"]
        else:
            state["sort_index"] = index
            state["sort_desc"] = state["columns"][index]["type"] == "number"
        state["offset"] = 0
        state["cursor"] = 0
        state["dirty"] = True

    def _datatable_enter_header(self, state):
        sortable = self._sortable_indices(state["columns"])
        if not state["show_header"] or not sortable:
            return
        state["header_focus"] = True
        if state["header_cursor"] not in sortable:
            state["header_cursor"] = sortable[0]

    @staticmethod
    def _datatable_toggle_sort(state):
        state["sort_desc"] = not state["sort_desc"]
        state["offset"] = 0
        state["cursor"] = 0

    @staticmethod
    def _datatable_sort_label(state):
        if not state["columns"]:
            return "-"
        column = state["columns"][state["sort_index"] % len(state["columns"])]
        return f"{column['header']} {'v' if state['sort_desc'] else '^'}"

    def _cell_text(self, row, column):
        value = row.get(column["id"])
        if column["type"] == "flag":
            return "[X]" if self._truthy(value) else "[ ]"
        template = column.get("template")
        if template:
            return self._apply_template(template, row)
        if value is None:
            return ""
        if column.get("format"):
            return self._format_cell(value, column["format"])
        return str(value)

    @staticmethod
    def _format_cell(value, fmt):
        date_directives = ("%Y", "%m", "%d", "%H", "%M", "%S", "%b", "%B", "%j", "%a", "%A", "%p")
        if any(directive in fmt for directive in date_directives):
            import datetime
            text = str(value)
            for parse in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
                try:
                    return datetime.datetime.strptime(text, parse).strftime(fmt)
                except ValueError:
                    continue
            return text
        try:
            return fmt % float(value)
        except (TypeError, ValueError):
            return str(value)

    @staticmethod
    def _apply_template(template, row):
        values = {key: ("" if value is None else value) for key, value in row.items()}
        return render_template(template, values)

    @staticmethod
    def _row_key(row):
        if isinstance(row, dict) and row.get("id") is not None:
            return row["id"]
        return id(row)

    @staticmethod
    def _align_right(column):
        if column.get("align"):
            return column["align"] == "right"
        return column["type"] == "number"

    @staticmethod
    def _detail_lines(row, detail_fields):
        lines = []
        for field in detail_fields:
            value = row.get(field["id"])
            if value is None or value == "":
                continue
            chunks = str(value).splitlines() or [""]
            for i, chunk in enumerate(chunks):
                prefix = f"{field['header']}: " if i == 0 else " " * (len(field["header"]) + 2)
                lines.append(prefix + chunk)
        return lines
    @staticmethod
    def _wrap_lines(lines, width):
        return wrap_lines(lines, width)

