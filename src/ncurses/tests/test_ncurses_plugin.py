"""Tests del plugin ncurses.

Cubren el arreglo de carga/dispatch y el operador generico `datatable`
(frontend sin acceso a datos, config estilo Webix). No requieren terminal.
"""

import curses
import importlib.util
import os
import sys
import types

import pytest

PLUGIN_PATH = os.path.join(
    os.path.dirname(__file__), "..", "src", "ncurses_plugin.py"
)

_MODULE = None


def _install_sugar_stubs():
    class Output:
        debug = False

        @staticmethod
        def Console(tag, message):
            pass

    class PluginBase:
        def __init__(self, context=None, plugin_config=None):
            self.context = context
            self.plugin_config = plugin_config or {}
            self.plugin_name = self.__class__.__name__
            self.metadata = {"commands": self.get_available_commands()}

        def get_available_commands(self):
            return []

        def interpolate_variables(self, value):
            return value

        def set_variable(self, name, value):
            return True

    sugar = types.ModuleType("Sugar")
    lang = types.ModuleType("Sugar.Lang")
    plugins = types.ModuleType("Sugar.Lang.Plugins")
    plugin_base_mod = types.ModuleType("Sugar.Lang.Plugins.PluginBase")
    utils = types.ModuleType("Sugar.Lang.Utils")
    output_mod = types.ModuleType("Sugar.Lang.Utils.Output")

    plugin_base_mod.PluginBase = PluginBase
    output_mod.Output = Output
    plugins.PluginBase = PluginBase

    sys.modules.update(
        {
            "Sugar": sugar,
            "Sugar.Lang": lang,
            "Sugar.Lang.Plugins": plugins,
            "Sugar.Lang.Plugins.PluginBase": plugin_base_mod,
            "Sugar.Lang.Utils": utils,
            "Sugar.Lang.Utils.Output": output_mod,
        }
    )


def _plugin_module():
    global _MODULE
    if _MODULE is None:
        _install_sugar_stubs()
        spec = importlib.util.spec_from_file_location("ncurses_plugin_under_test", PLUGIN_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _MODULE = module
    return _MODULE


class _FakeMemory:
    def __init__(self, variables):
        self.variables = variables

    def get_variable(self, name, default=None):
        return self.variables.get(name, default)


class _FakeContext:
    def __init__(self, variables):
        self.memory_handler = _FakeMemory(variables)


def _new_plugin(context=None):
    return _plugin_module().NcursesPlugin(context=context)


def test_plugin_loads_and_exposes_plugin_name():
    assert _new_plugin().get_available_commands() == ["ncurses"]


def test_datatable_operator_is_registered():
    plugin = _new_plugin()
    assert "datatable" in plugin.commands
    assert "browse" not in plugin.commands


def test_execute_resolves_operator_from_config():
    result = _new_plugin().execute("ncurses", {"operator": "on_key_press", "key": "q", "action": {}})
    assert result == {"status": "registered", "key": "q"}


def test_execute_rejects_unknown_operator():
    with pytest.raises(Exception):
        _new_plugin().execute("ncurses", {"operator": "no_existe"})


def test_source_items_prefers_inline_data():
    plugin = _new_plugin()
    items = [{"a": 1}]
    assert plugin._source_items({"data": items}) is items


def test_source_items_reads_sugar_variable():
    plugin = _new_plugin(context=_FakeContext({"rows": [{"a": 1}, {"a": 2}]}))
    assert plugin._source_items({"source": "rows"}) == [{"a": 1}, {"a": 2}]


def test_source_items_accepts_variable_name_in_data():
    plugin = _new_plugin(context=_FakeContext({"rows": [{"a": 1}]}))
    assert plugin._source_items({"data": "rows"}) == [{"a": 1}]


def test_source_items_wraps_single_dict():
    plugin = _new_plugin(context=_FakeContext({"rows": {"a": 1}}))
    assert plugin._source_items({"source": "rows"}) == [{"a": 1}]


def test_source_items_errors_on_missing_variable():
    plugin = _new_plugin(context=_FakeContext({}))
    with pytest.raises(Exception):
        plugin._source_items({"source": "nope"})


def test_normalize_columns_derives_from_items():
    plugin = _new_plugin()
    columns = plugin._normalize_columns(None, [{"nombre": "x", "imdb": 8.0}])
    assert [c["id"] for c in columns] == ["nombre", "imdb"]
    assert columns[1]["type"] == "number"


def test_normalize_columns_webix_keys():
    plugin = _new_plugin()
    columns = plugin._normalize_columns(
        ["nombre", {"id": "imdb", "header": "R", "sort": "int", "width": 6, "fillspace": True}], []
    )
    assert columns[0] == {
        "id": "nombre", "header": "nombre", "type": "text",
        "width": None, "fillspace": False, "template": None, "align": None,
        "format": None, "sortable": False,
    }
    assert columns[1]["header"] == "R"
    assert columns[1]["type"] == "number"
    assert columns[1]["width"] == 6
    assert columns[1]["fillspace"] is True


def test_normalize_columns_header_as_array():
    plugin = _new_plugin()
    columns = plugin._normalize_columns([{"id": "n", "header": ["Nombre", {"content": "textFilter"}]}], [])
    assert columns[0]["header"] == "Nombre"


def test_column_type_mapping():
    plugin = _new_plugin()
    assert plugin._column_type({"sort": "int"}) == "number"
    assert plugin._column_type({"sort": "number"}) == "number"
    assert plugin._column_type({"sort": "string"}) == "text"
    assert plugin._column_type({"sort": "flag"}) == "flag"
    assert plugin._column_type({"template": "{common.checkbox()}"}) == "flag"


def test_default_search_fields_uses_text_columns():
    plugin = _new_plugin()
    columns = plugin._normalize_columns([{"id": "n"}, {"id": "v", "sort": "int"}], [])
    assert plugin._default_search_fields(columns, []) == ["n"]


def test_apply_view_search_is_accent_insensitive():
    plugin = _new_plugin()
    items = [{"nombre": "Película"}, {"nombre": "Otra"}]
    state = plugin._datatable_state({"search_fields": ["nombre"]}, items)
    state["query"] = "pelicula"
    assert [r["nombre"] for r in plugin._apply_view(state)] == ["Película"]


def test_apply_view_numeric_filter():
    plugin = _new_plugin()
    items = [{"n": "a", "imdb": 6.0}, {"n": "b", "imdb": 8.0}]
    config = {"columns": [{"id": "n"}, {"id": "imdb", "sort": "int"}],
              "filter": {"id": "imdb", "header": "Rating", "steps": [0, 7]}}
    state = plugin._datatable_state(config, items)
    state["filter_value"] = 7
    assert [r["n"] for r in plugin._apply_view(state)] == ["b"]


def test_apply_view_only_flags():
    plugin = _new_plugin()
    items = [{"n": "a", "link": "u"}, {"n": "b", "link": None}]
    state = plugin._datatable_state({"columns": [{"id": "n"}, {"id": "link", "sort": "flag"}]}, items)
    state["only_flags"] = True
    assert [r["n"] for r in plugin._apply_view(state)] == ["a"]


def test_sort_rows_numbers_desc_nulls_last():
    plugin = _new_plugin()
    items = [{"n": "b", "imdb": 7.0}, {"n": "a", "imdb": 9.0}, {"n": "c", "imdb": None}]
    config = {"columns": [{"id": "n"}, {"id": "imdb", "sort": "int"}],
              "sort": "imdb", "sort_desc": True}
    state = plugin._datatable_state(config, items)
    assert [r["n"] for r in plugin._apply_view(state)] == ["a", "b", "c"]


def test_sort_rows_text_asc():
    plugin = _new_plugin()
    items = [{"n": "Zorro"}, {"n": "Alma"}, {"n": "marta"}]
    state = plugin._datatable_state({"columns": [{"id": "n"}]}, items)
    assert [r["n"] for r in plugin._apply_view(state)] == ["Alma", "marta", "Zorro"]


def test_datatable_state_cycles_sort_and_filter():
    plugin = _new_plugin()
    items = [{"n": "a", "imdb": 8.0}]
    config = {"columns": [{"id": "n"}, {"id": "imdb", "sort": "int"}],
              "filter": {"id": "imdb", "steps": [0, 6.5, 7]}}
    state = plugin._datatable_state(config, items)
    plugin._datatable_cycle_sort(state)
    assert state["sort_index"] == 1
    assert state["sort_desc"] is True
    plugin._datatable_toggle_sort(state)
    assert state["sort_desc"] is False
    plugin._datatable_cycle_filter(state)
    assert state["filter_value"] == 6.5
    assert plugin._datatable_sort_label(state) == "imdb ^"


def test_cycle_sort_skips_flag_columns():
    plugin = _new_plugin()
    config = {"columns": [{"id": "n", "sort": "string"}, {"id": "link", "sort": "flag"}, {"id": "imdb", "sort": "int"}]}
    state = plugin._datatable_state(config, [{"n": "a", "link": "x", "imdb": 8.0}])
    plugin._datatable_cycle_sort(state)
    assert state["sort_index"] == 2
    assert state["sort_desc"] is True
    plugin._datatable_cycle_sort(state)
    assert state["sort_index"] == 0
    assert state["sort_desc"] is False


def test_sortable_indices_excludes_flags_and_unsortable():
    plugin = _new_plugin()
    columns = plugin._normalize_columns(
        [{"id": "a", "sort": "string"}, {"id": "b"}, {"id": "c", "sort": "flag"}, {"id": "d", "sort": "int"}],
        [],
    )
    assert plugin._sortable_indices(columns) == [0, 3]


def test_header_click_sorts_and_toggles_direction():
    plugin = _new_plugin()
    items = [{"n": "a", "imdb": 8.0}, {"n": "b", "imdb": 9.0}]
    state = plugin._datatable_state(
        {"columns": [{"id": "n", "sort": "string"}, {"id": "imdb", "sort": "int"}]}, items
    )
    plugin._datatable_enter_header(state)
    assert state["header_focus"] is True
    state["header_cursor"] = 1
    plugin._datatable_header_key(10, state)
    assert state["sort_index"] == 1
    assert state["sort_desc"] is True
    assert state["dirty"] is True
    plugin._datatable_header_key(10, state)
    assert state["sort_desc"] is False


def test_header_key_moves_between_sortable_columns():
    plugin = _new_plugin()
    state = plugin._datatable_state(
        {"columns": [{"id": "n", "sort": "string"}, {"id": "imdb", "sort": "int"}]}, []
    )
    plugin._datatable_enter_header(state)
    state["header_cursor"] = 0
    plugin._datatable_header_key(curses.KEY_RIGHT, state)
    assert state["header_cursor"] == 1
    plugin._datatable_header_key(curses.KEY_LEFT, state)
    assert state["header_cursor"] == 0
    plugin._datatable_header_key(curses.KEY_DOWN, state)
    assert state["header_focus"] is False


def test_enter_header_without_sortable_does_nothing():
    plugin = _new_plugin()
    state = plugin._datatable_state({"columns": [{"id": "n"}, {"id": "l", "sort": "flag"}]}, [{"n": "a"}])
    plugin._datatable_enter_header(state)
    assert state["header_focus"] is False


def test_cell_text_flag_number_and_template():
    plugin = _new_plugin()
    assert plugin._cell_text({"l": "x"}, {"id": "l", "type": "flag"}) == "[X]"
    assert plugin._cell_text({"l": None}, {"id": "l", "type": "flag"}) == "[ ]"
    assert plugin._cell_text({"r": 8.25}, {"id": "r", "type": "number", "format": "%.1f"}) == "8.2"
    assert plugin._cell_text({"n": "Matrix", "y": 1999},
                             {"id": "n", "type": "text", "template": "{n} ({y})"}) == "Matrix (1999)"


def test_detail_lines_generic():
    plugin = _new_plugin()
    fields = [{"id": "nombre", "header": "Nombre"}, {"id": "link", "header": "Link"}]
    lines = plugin._detail_lines({"nombre": "Matrix", "link": "http://x"}, fields)
    assert lines == ["Nombre: Matrix", "Link: http://x"]


def test_multiselect_toggle_marks_rows():
    plugin = _new_plugin()
    items = [{"id": 1, "n": "a"}, {"id": 2, "n": "b"}]
    state = plugin._datatable_state({"select": "multiselect", "columns": [{"id": "n"}]}, items)
    plugin._datatable_reload(state, 10)
    state["cursor"] = 1
    plugin._datatable_toggle_mark(state)
    assert plugin._selected_rows(state) == [items[1]]
    state["cursor"] = 0
    plugin._datatable_toggle_mark(state)
    assert plugin._selected_rows(state) == [items[0], items[1]]
    plugin._datatable_toggle_mark(state)
    assert plugin._selected_rows(state) == [items[1]]


def test_single_select_returns_current_row():
    plugin = _new_plugin()
    items = [{"id": 1, "n": "a"}, {"id": 2, "n": "b"}]
    state = plugin._datatable_state({"columns": [{"id": "n"}]}, items)
    plugin._datatable_reload(state, 10)
    state["cursor"] = 1
    assert plugin._selected_rows(state) == items[1]


def test_wrap_lines():
    module = _plugin_module()
    assert module.NcursesPlugin._wrap_lines(["abcdef"], 3) == ["abc", "def"]
    assert module.NcursesPlugin._wrap_lines(["ab"], 3) == ["ab"]


def test_datatable_move_within_page_keeps_dirty_false():
    plugin = _new_plugin()
    state = plugin._datatable_state({}, [{"id": i} for i in range(3)])
    state.update({"rows": [{"id": i} for i in range(3)], "total": 10, "dirty": False})
    plugin._datatable_move(state, 1)
    assert state["cursor"] == 1
    assert state["dirty"] is False


def test_datatable_move_at_bottom_scrolls_and_marks_dirty():
    plugin = _new_plugin()
    state = plugin._datatable_state({}, [{"id": i} for i in range(3)])
    state.update({"rows": [{"id": i} for i in range(3)], "total": 10, "cursor": 2, "dirty": False})
    plugin._datatable_move(state, 1)
    assert state["offset"] == 1
    assert state["cursor"] == 2
    assert state["dirty"] is True
