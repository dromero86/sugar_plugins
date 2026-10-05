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

        def call_function(self, name, args=None, kwargs=None):
            return None

        def register_function(self, node):
            return None

        def invoke_anonymous(self, node, args=None, kwargs=None):
            return None

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


def _new_datatable(context=None):
    _plugin_module()
    from ncurses_ui.components.datatable import DataTable
    return DataTable(context=context)


def test_plugin_loads_and_exposes_plugin_name():
    assert _new_plugin().get_available_commands() == ["ncurses"]


def test_datatable_operator_is_registered():
    plugin = _new_plugin()
    assert plugin.registry.has("datatable")


def test_execute_rejects_unknown_operator():
    with pytest.raises(Exception):
        _new_plugin().execute("ncurses", {"operator": "no_existe"})


def test_source_items_prefers_inline_data():
    plugin = _new_datatable()
    items = [{"a": 1}]
    assert plugin._source_items({"data": items}) is items


def test_source_items_reads_sugar_variable():
    plugin = _new_datatable(context=_FakeContext({"rows": [{"a": 1}, {"a": 2}]}))
    assert plugin._source_items({"source": "rows"}) == [{"a": 1}, {"a": 2}]


def test_source_items_accepts_variable_name_in_data():
    plugin = _new_datatable(context=_FakeContext({"rows": [{"a": 1}]}))
    assert plugin._source_items({"data": "rows"}) == [{"a": 1}]


def test_source_items_wraps_single_dict():
    plugin = _new_datatable(context=_FakeContext({"rows": {"a": 1}}))
    assert plugin._source_items({"source": "rows"}) == [{"a": 1}]


def test_source_items_errors_on_missing_variable():
    plugin = _new_datatable(context=_FakeContext({}))
    with pytest.raises(Exception):
        plugin._source_items({"source": "nope"})


def test_normalize_columns_derives_from_items():
    plugin = _new_datatable()
    columns = plugin._normalize_columns(None, [{"nombre": "x", "imdb": 8.0}])
    assert [c["id"] for c in columns] == ["nombre", "imdb"]
    assert columns[1]["type"] == "number"


def test_normalize_columns_webix_keys():
    plugin = _new_datatable()
    columns = plugin._normalize_columns(
        ["nombre", {"id": "imdb", "header": "R", "sort": "int", "width": 6, "fillspace": True}], []
    )
    assert columns[0] == {
        "id": "nombre", "header": "nombre", "type": "text",
        "width": None, "fillspace": False, "template": None, "align": None,
        "format": None, "sortable": False, "editable": True,
    }
    assert columns[1]["header"] == "R"
    assert columns[1]["type"] == "number"
    assert columns[1]["width"] == 6
    assert columns[1]["fillspace"] is True


def test_normalize_columns_header_as_array():
    plugin = _new_datatable()
    columns = plugin._normalize_columns([{"id": "n", "header": ["Nombre", {"content": "textFilter"}]}], [])
    assert columns[0]["header"] == "Nombre"


def test_column_type_mapping():
    plugin = _new_datatable()
    assert plugin._column_type({"sort": "int"}) == "number"
    assert plugin._column_type({"sort": "number"}) == "number"
    assert plugin._column_type({"sort": "string"}) == "text"
    assert plugin._column_type({"sort": "flag"}) == "flag"
    assert plugin._column_type({"template": "{common.checkbox()}"}) == "flag"


def test_default_search_fields_uses_text_columns():
    plugin = _new_datatable()
    columns = plugin._normalize_columns([{"id": "n"}, {"id": "v", "sort": "int"}], [])
    assert plugin._default_search_fields(columns, []) == ["n"]


def test_apply_view_search_is_accent_insensitive():
    plugin = _new_datatable()
    items = [{"nombre": "Película"}, {"nombre": "Otra"}]
    state = plugin._datatable_state({"search_fields": ["nombre"]}, items)
    state["query"] = "pelicula"
    assert [r["nombre"] for r in plugin._apply_view(state)] == ["Película"]


def test_apply_view_numeric_filter():
    plugin = _new_datatable()
    items = [{"n": "a", "imdb": 6.0}, {"n": "b", "imdb": 8.0}]
    config = {"columns": [{"id": "n"}, {"id": "imdb", "sort": "int"}],
              "filter": {"id": "imdb", "header": "Rating", "steps": [0, 7]}}
    state = plugin._datatable_state(config, items)
    state["filter_value"] = 7
    assert [r["n"] for r in plugin._apply_view(state)] == ["b"]


def test_apply_view_only_flags():
    plugin = _new_datatable()
    items = [{"n": "a", "link": "u"}, {"n": "b", "link": None}]
    state = plugin._datatable_state({"columns": [{"id": "n"}, {"id": "link", "sort": "flag"}]}, items)
    state["only_flags"] = True
    assert [r["n"] for r in plugin._apply_view(state)] == ["a"]


def test_sort_rows_numbers_desc_nulls_last():
    plugin = _new_datatable()
    items = [{"n": "b", "imdb": 7.0}, {"n": "a", "imdb": 9.0}, {"n": "c", "imdb": None}]
    config = {"columns": [{"id": "n"}, {"id": "imdb", "sort": "int"}],
              "sort": "imdb", "sort_desc": True}
    state = plugin._datatable_state(config, items)
    assert [r["n"] for r in plugin._apply_view(state)] == ["a", "b", "c"]


def test_sort_rows_text_asc():
    plugin = _new_datatable()
    items = [{"n": "Zorro"}, {"n": "Alma"}, {"n": "marta"}]
    state = plugin._datatable_state({"columns": [{"id": "n"}]}, items)
    assert [r["n"] for r in plugin._apply_view(state)] == ["Alma", "marta", "Zorro"]


def test_datatable_state_cycles_sort_and_filter():
    plugin = _new_datatable()
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
    plugin = _new_datatable()
    config = {"columns": [{"id": "n", "sort": "string"}, {"id": "link", "sort": "flag"}, {"id": "imdb", "sort": "int"}]}
    state = plugin._datatable_state(config, [{"n": "a", "link": "x", "imdb": 8.0}])
    plugin._datatable_cycle_sort(state)
    assert state["sort_index"] == 2
    assert state["sort_desc"] is True
    plugin._datatable_cycle_sort(state)
    assert state["sort_index"] == 0
    assert state["sort_desc"] is False


def test_sortable_indices_excludes_flags_and_unsortable():
    plugin = _new_datatable()
    columns = plugin._normalize_columns(
        [{"id": "a", "sort": "string"}, {"id": "b"}, {"id": "c", "sort": "flag"}, {"id": "d", "sort": "int"}],
        [],
    )
    assert plugin._sortable_indices(columns) == [0, 3]


def test_header_click_sorts_and_toggles_direction():
    plugin = _new_datatable()
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
    plugin = _new_datatable()
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
    plugin = _new_datatable()
    state = plugin._datatable_state({"columns": [{"id": "n"}, {"id": "l", "sort": "flag"}]}, [{"n": "a"}])
    plugin._datatable_enter_header(state)
    assert state["header_focus"] is False


def test_cell_text_flag_number_and_template():
    plugin = _new_datatable()
    assert plugin._cell_text({"l": "x"}, {"id": "l", "type": "flag"}) == "[X]"
    assert plugin._cell_text({"l": None}, {"id": "l", "type": "flag"}) == "[ ]"
    assert plugin._cell_text({"r": 8.25}, {"id": "r", "type": "number", "format": "%.1f"}) == "8.2"
    assert plugin._cell_text({"n": "Matrix", "y": 1999},
                             {"id": "n", "type": "text", "template": "{n} ({y})"}) == "Matrix (1999)"


def test_cell_format_strftime():
    _plugin_module()
    from ncurses_ui.components.datatable import DataTable

    datatable = DataTable({})
    assert datatable._format_cell(8.25, "%.1f") == "8.2"
    assert datatable._format_cell("2020-01-02", "%d/%m/%Y") == "02/01/2020"


def test_detail_lines_generic():
    plugin = _new_datatable()
    fields = [{"id": "nombre", "header": "Nombre"}, {"id": "link", "header": "Link"}]
    lines = plugin._detail_lines({"nombre": "Matrix", "link": "http://x"}, fields)
    assert lines == ["Nombre: Matrix", "Link: http://x"]


def test_multiselect_toggle_marks_rows():
    plugin = _new_datatable()
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
    plugin = _new_datatable()
    items = [{"id": 1, "n": "a"}, {"id": 2, "n": "b"}]
    state = plugin._datatable_state({"columns": [{"id": "n"}]}, items)
    plugin._datatable_reload(state, 10)
    state["cursor"] = 1
    assert plugin._selected_rows(state) == items[1]


def test_wrap_lines():
    datatable = _new_datatable()
    assert datatable._wrap_lines(["abcdef"], 3) == ["abc", "def"]
    assert datatable._wrap_lines(["ab"], 3) == ["ab"]


def test_datatable_move_within_page_keeps_dirty_false():
    plugin = _new_datatable()
    state = plugin._datatable_state({}, [{"id": i} for i in range(3)])
    state.update({"rows": [{"id": i} for i in range(3)], "total": 10, "dirty": False})
    plugin._datatable_move(state, 1)
    assert state["cursor"] == 1
    assert state["dirty"] is False


def test_datatable_move_at_bottom_scrolls_and_marks_dirty():
    plugin = _new_datatable()
    state = plugin._datatable_state({}, [{"id": i} for i in range(3)])
    state.update({"rows": [{"id": i} for i in range(3)], "total": 10, "cursor": 2, "dirty": False})
    plugin._datatable_move(state, 1)
    assert state["offset"] == 1
    assert state["cursor"] == 2
    assert state["dirty"] is True


def test_view_registry_register_and_create():
    _plugin_module()
    from ncurses_ui.components.base import Component
    from ncurses_ui.kernel.registry import ViewRegistry

    class Dummy(Component):
        def run(self):
            return {"status": "ok", "got": self.config}

    registry = ViewRegistry()
    assert registry.operators() == []
    registry.register("dummy", Dummy)
    assert registry.has("dummy")
    assert registry.operators() == ["dummy"]
    assert registry.create("dummy", {"a": 1}, None, None).run() == {"status": "ok", "got": {"a": 1}}


def test_view_registry_create_unknown_raises():
    _plugin_module()
    from ncurses_ui.kernel.registry import ViewRegistry

    with pytest.raises(Exception):
        ViewRegistry().create("nope", {}, None, None)


def test_contract_normalize_config_and_results():
    _plugin_module()
    from ncurses_ui.kernel.contract import error, normalize_config, ok

    assert normalize_config({"a": 1}) == {"a": 1}
    with pytest.raises(ValueError):
        normalize_config(["no", "dict"])
    with pytest.raises(ValueError):
        normalize_config({}, required=["a"])
    assert ok(x=1) == {"status": "ok", "x": 1}
    assert error("boom") == {"status": "error", "error": "boom"}


class _FakeWindow:
    def __init__(self):
        self.calls = []

    def addstr(self, y, x, text, attr=0):
        self.calls.append((y, x, text, attr))

    def getmaxyx(self):
        return (24, 80)


def _child_manager():
    class Child:
        def __init__(self, tag):
            self.tag = tag

        def draw(self, window, region):
            window.addstr(region.y, region.x, self.tag, 0)

    class FakeRegistry:
        def has(self, op):
            return True

        def create(self, op, config, context, manager):
            return Child(op)

    class FakeManager:
        pass

    manager = FakeManager()
    manager.registry = FakeRegistry()
    return manager


def test_registry_has_builtin_components():
    plugin = _new_plugin()
    operators = [
        "datatable", "template", "label", "spacer", "icon", "button",
        "text", "textarea", "search", "checkbox", "radio", "toggle",
        "switch", "counter", "slider", "rangeslider", "list", "property",
        "grouplist", "dataview", "unitlist", "timeline", "tree", "pager",
        "layout", "window", "popup", "tooltip", "context", "multiview",
        "carousel", "tabbar", "tabview", "proxy", "scrollview", "align",
        "abslayout", "gridlayout", "headerlayout", "portlet", "dashboard",
        "accordion", "select", "richselect", "combo", "suggest", "menu",
        "contextmenu", "sidebar", "toolbar", "hint", "form", "composite",
        "listview", "formview", "datafull", "cardview", "gage", "bullet", "chart",
    ]
    for operator in operators:
        assert plugin.registry.has(operator)


def test_render_template_hash_and_brace():
    _plugin_module()
    from ncurses_ui.kernel.renderer import render_template

    assert render_template("Hola #nombre#", {"nombre": "Ana"}) == "Hola Ana"
    assert render_template("Hola {nombre}", {"nombre": "Ana"}) == "Hola Ana"
    assert render_template("", {}) == ""
    assert render_template("x", None) == "x"


def test_template_render_and_result():
    _plugin_module()
    from ncurses_ui.components.template import Template
    from ncurses_ui.kernel.renderer import Region

    template = Template({"content": "Hola #nombre#", "data": {"nombre": "Ana"}})
    window = _FakeWindow()
    template.render(window, Region(2, 3, 10, 40))
    assert window.calls == [(2, 3, "Hola Ana", 0)]
    assert template.result() == {"status": "ok", "content": "Hola Ana"}


def test_label_uses_label_or_value():
    _plugin_module()
    from ncurses_ui.components.label import Label

    assert Label({"label": "Nombre"}).content() == "Nombre"
    assert Label({"value": 42}).content() == "42"


def test_spacer_renders_nothing():
    _plugin_module()
    from ncurses_ui.components.spacer import Spacer
    from ncurses_ui.kernel.renderer import Region

    window = _FakeWindow()
    Spacer({}).render(window, Region(0, 0, 5, 5))
    assert window.calls == []


def test_icon_content_and_render():
    _plugin_module()
    from ncurses_ui.components.icon import Icon
    from ncurses_ui.kernel.renderer import Region

    assert Icon({"glyph": "*", "label": "Fav"}).content() == "* Fav"
    assert Icon({"icon": "*"}).content() == "*"
    window = _FakeWindow()
    Icon({"glyph": "*"}).render(window, Region(1, 1, 1, 10))
    assert window.calls == [(1, 1, "*", 0)]


def test_button_label_and_action():
    _plugin_module()
    from ncurses_ui.components.button import Button
    from ncurses_ui.kernel.renderer import Region

    button = Button({"text": "Salir", "action": "exit"})
    window = _FakeWindow()
    button.render(window, Region(0, 0, 1, 20))
    assert window.calls == [(0, 0, "[Salir]", 0)]
    assert button.result() == {"status": "ok", "action": "exit"}


def test_text_editing_and_result():
    _plugin_module()
    from ncurses_ui.components.text import Text

    text = Text({"label": "Nombre", "value": ""})
    assert text.handle_key(ord("A")) is None
    assert text.handle_key(ord("n")) is None
    assert text.value == "An"
    text.handle_key(8)
    assert text.value == "A"
    assert text.handle_key(10) == "done"
    assert text.result() == {"status": "ok", "value": "A"}


def test_text_max_length():
    _plugin_module()
    from ncurses_ui.components.text import Text

    text = Text({"max_length": 2})
    text.handle_key(ord("a"))
    text.handle_key(ord("b"))
    text.handle_key(ord("c"))
    assert text.value == "ab"


def test_text_escape_cancels():
    _plugin_module()
    from ncurses_ui.components.text import Text

    assert Text({}).handle_key(27) == "cancel"


def test_textarea_enter_inserts_newline():
    _plugin_module()
    from ncurses_ui.components.textarea import Textarea

    area = Textarea({"value": "a"})
    area.handle_key(ord("b"))
    area.handle_key(10)
    area.handle_key(ord("c"))
    assert area.value == "ab\nc"
    assert area.handle_key(27) == "done"


def test_search_result_has_query():
    _plugin_module()
    from ncurses_ui.components.search import Search

    search = Search({})
    search.handle_key(ord("h"))
    assert search.result() == {"status": "ok", "query": "h", "value": "h"}


def test_checkbox_toggles_and_result():
    _plugin_module()
    from ncurses_ui.components.checkbox import Checkbox
    from ncurses_ui.kernel.renderer import Region

    checkbox = Checkbox({"label": "Activo", "value": False})
    window = _FakeWindow()
    checkbox.render(window, Region(0, 0, 1, 20))
    assert window.calls == [(0, 0, "[ ] Activo", 0)]
    checkbox.handle_key(ord(" "))
    assert checkbox.value is True
    assert checkbox.result() == {"status": "ok", "value": True}


def test_toggle_renders_on_off():
    _plugin_module()
    from ncurses_ui.components.toggle import Toggle

    assert Toggle({"value": True}).box() == "[ON ]"
    assert Toggle({"value": False}).box() == "[OFF]"


def test_radio_navigates_and_returns_id():
    _plugin_module()
    from ncurses_ui.components.radio import Radio

    radio = Radio({"options": [{"id": "a", "value": "A"}, {"id": "b", "value": "B"}], "value": "b"})
    assert radio.index == 1
    radio.handle_key(ord("k"))
    assert radio.index == 0
    assert radio.result() == {"status": "ok", "value": "a"}
    assert radio.handle_key(10) == "done"


def test_counter_increments_and_clamps():
    _plugin_module()
    from ncurses_ui.components.counter import Counter

    counter = Counter({"value": 5, "min": 0, "max": 6, "step": 2})
    counter.handle_key(ord("+"))
    assert counter.value == 6
    counter.handle_key(ord("+"))
    assert counter.value == 6
    counter.handle_key(ord("-"))
    assert counter.value == 4


def test_slider_bar_and_adjust():
    _plugin_module()
    from ncurses_ui.components.slider import Slider

    slider = Slider({"value": 0, "min": 0, "max": 10, "bar_width": 10})
    assert slider.bar() == "[----------]"
    slider.handle_key(ord("+"))
    assert slider.value == 1
    assert slider.bar() == "[#---------]"


def test_rangeslider_adjusts_active_handle():
    _plugin_module()
    from ncurses_ui.components.rangeslider import RangeSlider

    slider = RangeSlider({"value": [2, 8], "min": 0, "max": 10, "bar_width": 10})
    assert slider.active == 0
    slider.handle_key(ord("+"))
    assert slider.value == [3, 8]
    slider.handle_key(9)
    assert slider.active == 1
    slider.handle_key(ord("-"))
    assert slider.value == [3, 7]


def test_event_dispatcher_builtin_and_string():
    _plugin_module()
    from ncurses_ui.events.dispatcher import EventDispatcher

    dispatcher = EventDispatcher({"on_item_click": {"action": "detail"}, "on_key": "emit"})
    assert dispatcher.has("on_item_click")
    result = dispatcher.dispatch("on_item_click", {"row": {"id": 1}})
    assert result == {"event": "on_item_click", "action": "detail", "payload": {"row": {"id": 1}}}
    assert dispatcher.dispatch("on_key") == {"event": "on_key", "action": "emit", "payload": {}}
    assert dispatcher.dispatch("nope") is None


def test_event_dispatcher_unknown_and_callback():
    _plugin_module()
    from ncurses_ui.events.dispatcher import EventDispatcher

    unknown = EventDispatcher({"on_x": {"action": "wat"}}).dispatch("on_x")
    assert unknown["action"] == "wat"
    assert "error" in unknown

    inline = {"function": {"args": ["row"], "task": []}}
    callback = EventDispatcher({"on_before_select": inline}).dispatch("on_before_select")
    assert callback["action"] == "callback"
    assert callback["handler"] == inline


def test_datatable_state_has_dispatcher_and_dispatch():
    _plugin_module()
    from ncurses_ui.events.dispatcher import EventDispatcher

    datatable = _new_datatable()
    state = datatable._datatable_state({"events": {"on_item_click": {"action": "close"}}}, [{"id": 1}])
    assert isinstance(state["dispatcher"], EventDispatcher)
    datatable._datatable_reload(state, 10)
    state["cursor"] = 0
    payload = datatable._current_row_payload(state)
    assert payload == {"row": {"id": 1}}
    assert datatable._dispatch_event(state, "on_item_click", payload)["action"] == "close"


def test_datatable_enter_respects_events():
    _plugin_module()

    datatable = _new_datatable()
    close_state = datatable._datatable_state({"events": {"on_item_click": {"action": "close"}}}, [{"id": 1}])
    datatable._datatable_reload(close_state, 10)
    assert datatable._datatable_handle_key(10, close_state, 10) == "quit"

    none_state = datatable._datatable_state({"events": {"on_item_click": {"action": "none"}}}, [{"id": 1}])
    datatable._datatable_reload(none_state, 10)
    assert datatable._datatable_handle_key(10, none_state, 10) is None

    default_state = datatable._datatable_state({}, [{"id": 1}])
    datatable._datatable_reload(default_state, 10)
    assert datatable._datatable_handle_key(10, default_state, 10) == "detail"


def test_list_items_template_and_render():
    _plugin_module()
    from ncurses_ui.components.list import List
    from ncurses_ui.kernel.renderer import Region

    items = [{"nombre": "Ana"}, {"nombre": "Beto"}]
    listing = List({"data": items, "template": "#nombre#"})
    assert listing.text(items[0]) == "Ana"
    window = _FakeWindow()
    listing.cursor = 1
    listing.render(window, Region(0, 0, 5, 20))
    assert window.calls == [(0, 0, "  Ana", 0), (1, 0, "> Beto", 0)]


def test_list_reads_context_variable_and_navigates():
    _plugin_module()
    from ncurses_ui.components.list import List

    context = _FakeContext({"rows": ["a", "b", "c"]})
    listing = List({"data": "rows"}, context=context)
    assert listing.items == ["a", "b", "c"]
    listing.handle_key(ord("j"))
    assert listing.cursor == 1
    assert listing.result() == {"status": "ok", "selected": "b"}
    assert listing.handle_key(ord("q")) == "quit"


def test_list_multiselect_result():
    _plugin_module()
    from ncurses_ui.components.list import List

    listing = List({"data": ["a", "b"], "select": "multiselect"})
    listing.handle_key(ord(" "))
    listing.cursor = 1
    listing.handle_key(ord(" "))
    assert listing.result() == {"status": "ok", "selected": ["a", "b"]}


def test_property_fields_and_lines():
    _plugin_module()
    from ncurses_ui.components.property import Property
    from ncurses_ui.kernel.renderer import Region

    prop = Property({"data": {"nombre": "Ana", "edad": 30}, "fields": ["nombre", {"id": "edad", "header": "Edad"}]})
    assert prop.lines() == ["nombre: Ana", "Edad: 30"]
    window = _FakeWindow()
    prop.render(window, Region(0, 0, 5, 40))
    assert window.calls == [(0, 0, "nombre: Ana", 0), (1, 0, "Edad: 30", 0)]
    assert prop.result() == {"status": "ok", "values": {"nombre": "Ana", "edad": 30}}


def test_grouplist_builds_group_rows_and_navigation():
    _plugin_module()
    from ncurses_ui.components.grouplist import GroupList
    from ncurses_ui.kernel.renderer import Region

    items = [{"g": "A", "n": "1"}, {"g": "A", "n": "2"}, {"g": "B", "n": "3"}]
    listing = GroupList({"data": items, "group_by": "g", "template": "#n#"})
    assert [row["kind"] for row in listing.rows] == ["group", "item", "item", "group", "item"]
    window = _FakeWindow()
    listing.render(window, Region(0, 0, 10, 20))
    assert window.calls[0] == (0, 0, "[A]", 0)
    assert window.calls[1] == (1, 0, "> 1", 0)
    listing.handle_key(ord("j"))
    assert listing.cursor == 1
    listing.handle_key(ord("j"))
    assert listing.cursor == 2
    assert listing.result() == {"status": "ok", "selected": items[2]}


def test_dataview_renders_multiline_blocks():
    _plugin_module()
    from ncurses_ui.components.dataview import DataView
    from ncurses_ui.kernel.renderer import Region

    listing = DataView({"data": [{"n": "a", "d": "x"}], "template": "#n#\n#d#"})
    window = _FakeWindow()
    listing.render(window, Region(0, 0, 10, 20))
    assert window.calls == [(0, 0, "> a", 0), (1, 0, "  x", 0)]


def test_timeline_sorts_items():
    _plugin_module()
    from ncurses_ui.components.timeline import TimeLine

    listing = TimeLine({"data": [{"t": "2020", "n": "b"}, {"t": "2019", "n": "a"}], "sort_by": "t"})
    assert [item["n"] for item in listing.items] == ["a", "b"]


def test_unitlist_is_grouplist():
    _plugin_module()
    from ncurses_ui.components.grouplist import GroupList
    from ncurses_ui.components.unitlist import UnitList

    assert issubclass(UnitList, GroupList)


def test_tree_builds_hierarchy_and_expands():
    _plugin_module()
    from ncurses_ui.components.tree import Tree
    from ncurses_ui.kernel.renderer import Region

    items = [
        {"id": 1, "parent": None, "value": "root"},
        {"id": 2, "parent": 1, "value": "child"},
    ]
    tree = Tree({"data": items, "text": "value"})
    assert len(tree.visible()) == 1
    window = _FakeWindow()
    tree.render(window, Region(0, 0, 10, 20))
    assert window.calls[0][2] == ">> root"
    tree.handle_key(ord("l"))
    assert len(tree.visible()) == 2
    assert tree.result() == {"status": "ok", "selected": items[0]}


def test_pager_pages_and_result():
    _plugin_module()
    from ncurses_ui.components.pager import Pager
    from ncurses_ui.kernel.renderer import Region

    pager = Pager({"total": 45, "per_page": 20})
    assert pager.pages == 3
    window = _FakeWindow()
    pager.render(window, Region(0, 0, 1, 40))
    assert window.calls == [(0, 0, "[<] Pagina 1/3 [>]", 0)]
    pager.handle_key(ord(">"))
    assert pager.result() == {"status": "ok", "page": 2, "pages": 3}
    pager.handle_key(ord(">"))
    pager.handle_key(ord(">"))
    assert pager.page == 3


def test_layout_split_fixed_and_fill():
    _plugin_module()
    from ncurses_ui.kernel.layout import split
    from ncurses_ui.kernel.renderer import Region

    regions = split(Region(0, 0, 10, 80), [{"size": 30}, {"weight": 1}], horizontal=True)
    assert regions == [Region(0, 0, 10, 30), Region(0, 30, 10, 50)]


def test_layout_split_vertical_with_gap():
    _plugin_module()
    from ncurses_ui.kernel.layout import split
    from ncurses_ui.kernel.renderer import Region

    regions = split(Region(0, 0, 20, 10), [{"size": 5}, "fill"], horizontal=False, gap=1)
    assert regions == [Region(0, 0, 5, 10), Region(6, 0, 14, 10)]


def test_layout_child_spec():
    _plugin_module()
    from ncurses_ui.components.layout import Layout

    assert Layout.child_spec({"width": 30}, True) == {"size": 30}
    assert Layout.child_spec({}, True) == {"weight": 1}
    assert Layout.child_spec({"height": 5}, False) == {"size": 5}


def test_layout_render_composes_children():
    _plugin_module()
    from ncurses_ui.components.layout import Layout
    from ncurses_ui.kernel.renderer import Region

    class Child:
        def __init__(self, tag):
            self.tag = tag

        def render(self, window, region):
            window.addstr(region.y, region.x, self.tag, 0)

    class FakeRegistry:
        def has(self, op):
            return True

        def create(self, op, config, context, manager):
            return Child(op)

    class FakeManager:
        registry = FakeRegistry()

    layout = Layout({"cols": [{"operator": "a", "width": 3}, {"operator": "b"}]})
    layout.manager = FakeManager()
    window = _FakeWindow()
    layout.draw(window, Region(0, 0, 5, 10))
    assert window.calls == [(0, 0, "a", 0), (0, 3, "b", 0)]


def test_window_box_and_border():
    _plugin_module()
    from ncurses_ui.components.overlays import Window
    from ncurses_ui.kernel.renderer import Region

    win = Window({"width": 10, "height": 4, "title": "Hola"})
    assert win.box_region(Region(0, 0, 10, 20)) == Region(3, 5, 4, 10)
    fake = _FakeWindow()
    win.render(fake, Region(0, 0, 10, 20))
    assert fake.calls[0] == (3, 5, "+--------+", 0)
    assert (3, 7, " Hola ", 0) in fake.calls


def test_popup_tooltip_context_regions():
    _plugin_module()
    from ncurses_ui.components.overlays import Context, Popup, Tooltip
    from ncurses_ui.kernel.renderer import Region

    assert Popup({"width": 4, "height": 2}).config["border"] is False
    assert Tooltip({"width": 5, "height": 2}).box_region(Region(0, 0, 10, 20)) == Region(0, 0, 2, 5)
    context = Context({"width": 5, "height": 2, "position": {"x": 3, "y": 4}})
    assert context.box_region(Region(0, 0, 10, 20)) == Region(4, 3, 2, 5)


def test_tabbar_navigation_and_result():
    _plugin_module()
    from ncurses_ui.components.tabs import TabBar
    from ncurses_ui.kernel.renderer import Region

    bar = TabBar({"cells": [{"header": "A"}, {"header": "B"}]})
    window = _FakeWindow()
    bar.render(window, Region(0, 0, 1, 20))
    assert window.calls[0] == (0, 0, "[A]", 0)
    bar.handle_key(ord("l"))
    assert bar.result() == {"status": "ok", "index": 1}


def test_form_values_and_validation():
    _plugin_module()
    from ncurses_ui.components.form import Form

    form = Form({
        "fields": [{"name": "nombre", "label": "Nombre", "value": ""}, {"name": "edad", "value": 3}],
        "rules": {"nombre": {"required": True}},
    })
    assert form.values() == {"nombre": "", "edad": 3}
    assert form.validate() == [{"field": "nombre", "error": "required"}]


def test_select_and_combo():
    _plugin_module()
    from ncurses_ui.components.selects import Combo, Select

    select = Select({"options": [{"id": "a", "value": "A"}, {"id": "b", "value": "B"}], "value": "b"})
    assert select.label() == "B"
    select.handle_key(ord("h"))
    assert select.result() == {"status": "ok", "value": "a"}

    combo = Combo({})
    combo.handle_key(ord("x"))
    assert combo.result() == {"status": "ok", "value": "x"}


def test_composite_composes_parts():
    _plugin_module()
    from ncurses_ui.components.composite import Composite
    from ncurses_ui.kernel.renderer import Region

    class Child:
        def __init__(self, tag):
            self.tag = tag

        def render(self, window, region):
            window.addstr(region.y, region.x, self.tag, 0)

    class FakeRegistry:
        def has(self, op):
            return True

        def create(self, op, config, context, manager):
            return Child(op)

    class FakeManager:
        registry = FakeRegistry()

    composite = Composite({"parts": {"a": {"operator": "x"}, "b": {"operator": "y"}}})
    composite.manager = FakeManager()
    window = _FakeWindow()
    composite.render(window, Region(0, 0, 4, 10))
    assert window.calls == [(0, 0, "x", 0), (2, 0, "y", 0)]


def test_viz_gage_bullet_chart():
    _plugin_module()
    from ncurses_ui.components.viz import Bullet, Chart, Gage
    from ncurses_ui.kernel.renderer import Region

    assert Gage({"value": 0, "min": 0, "max": 10, "bar_width": 10}).bar() == "[----------]"
    assert Bullet({"value": 5, "min": 0, "max": 10, "bar_width": 10, "target": 8}).bar() == "[=====---|-]"
    chart = Chart({"data": [{"label": "a", "value": 10}, {"label": "b", "value": 5}], "bar_width": 10})
    window = _FakeWindow()
    chart.render(window, Region(0, 0, 5, 40))
    assert window.calls[0] == (0, 0, "########## a", 0)
    assert window.calls[1] == (1, 0, "#####      b", 0)


def test_menu_navigation_and_result():
    _plugin_module()
    from ncurses_ui.components.navigation import Menu
    from ncurses_ui.kernel.renderer import Region

    menu = Menu({"items": [{"id": "n", "value": "Nuevo"}, {"id": "s", "value": "Salir"}]})
    window = _FakeWindow()
    menu.render(window, Region(0, 0, 5, 20))
    assert window.calls[0] == (0, 0, "> Nuevo", 0)
    menu.handle_key(ord("j"))
    assert menu.result() == {"status": "ok", "selected": {"id": "s", "value": "Salir"}}


def test_view_stack_push_back():
    _plugin_module()
    from ncurses_ui.kernel.navigation import ViewStack

    stack = ViewStack()
    assert stack.current() is None
    stack.push("a")
    stack.push("b")
    assert stack.current() == "b"
    assert stack.pop() == "b"
    assert len(stack) == 1


def test_event_dispatcher_navigate_back():
    _plugin_module()
    from ncurses_ui.events.dispatcher import EventDispatcher

    dispatcher = EventDispatcher({"on_item_click": {"action": "navigate", "target": "home"}})
    result = dispatcher.dispatch("on_item_click")
    assert result["action"] == "navigate"
    assert result["target"] == "home"
    assert "error" not in result


def test_datatable_invokes_inline_callback():
    _plugin_module()
    from ncurses_ui.components.datatable import DataTable

    class FakeManager:
        def __init__(self, result):
            self.result = result
            self.calls = []

        def invoke_anonymous(self, handler, args):
            self.calls.append((handler, args))
            return self.result

    events = {"on_item_click": {"function": {"args": ["row"], "task": []}}}
    for result, expected in [(True, "detail"), (False, None)]:
        datatable = DataTable({"events": events}, manager=FakeManager(result))
        state = datatable._datatable_state(datatable.config, [{"id": 1}])
        datatable._datatable_reload(state, 10)
        assert datatable._datatable_handle_key(10, state, 10) == expected
        assert datatable.manager.calls


def test_datatable_before_select_callback_vetoes():
    _plugin_module()
    from ncurses_ui.components.datatable import DataTable

    class FakeManager:
        def __init__(self, result):
            self.result = result

        def invoke_anonymous(self, handler, args):
            return self.result

    events = {"on_before_select": {"function": {"args": ["row"], "task": []}}}
    datatable = DataTable({"events": events}, manager=FakeManager(False))
    state = datatable._datatable_state(datatable.config, [{"id": 1}, {"id": 2}])
    datatable._datatable_reload(state, 10)
    assert datatable._datatable_handle_key(ord("j"), state, 10) is None
    assert state["cursor"] == 0


def test_datatable_after_select_callback():
    _plugin_module()
    from ncurses_ui.components.datatable import DataTable

    class FakeManager:
        def __init__(self):
            self.calls = []

        def invoke_anonymous(self, handler, args):
            self.calls.append((handler, args))
            return True

    events = {"on_after_select": {"function": {"args": ["row"], "task": []}}}
    datatable = DataTable({"events": events, "columns": [{"id": "n", "sort": "string"}]}, manager=FakeManager())
    state = datatable._datatable_state(datatable.config, [{"id": 1, "n": "a"}, {"id": 2, "n": "b"}])
    datatable._datatable_reload(state, 10)
    datatable._move_with_event(state, 1)
    assert datatable.manager.calls
    assert datatable.manager.calls[0][1]["row"]["id"] == 2


def test_datatable_edit_mode():
    _plugin_module()
    from ncurses_ui.components.datatable import DataTable

    items = [{"n": "a", "v": 1}]
    datatable = DataTable({
        "columns": [{"id": "n", "sort": "string"}, {"id": "v", "sort": "int"}],
        "editable": True,
        "data": items,
    })
    state = datatable._datatable_state(datatable.config, items)
    datatable._datatable_reload(state, 10)
    assert state["editable_cols"] == [0, 1]

    datatable._start_edit(state)
    assert state["edit_mode"] is True
    assert state["edit_buffer"] == "a"
    state["edit_buffer"] = "abc"
    datatable._commit_edit(state)
    assert state["items"][0]["n"] == "abc"
    assert state["edit_mode"] is False

    datatable._cycle_edit_col(state, 1)
    datatable._start_edit(state)
    state["edit_buffer"] = "42"
    datatable._commit_edit(state)
    assert state["items"][0]["v"] == 42
    assert datatable.result()["rows"] == items


def test_execute_blocks_ui_reentrancy():
    plugin = _new_plugin()
    plugin._ui_active = True
    with pytest.raises(Exception):
        plugin.execute("ncurses", {"operator": "datatable", "data": []})


def test_layout_routes_keys_to_focused_child():
    _plugin_module()
    from ncurses_ui.components.layout import Layout
    from ncurses_ui.components.list import List
    from ncurses_ui.kernel.registry import ViewRegistry
    from ncurses_ui.kernel.renderer import Region

    registry = ViewRegistry()
    registry.register("list", List)

    class FakeManager:
        pass

    manager = FakeManager()
    manager.registry = registry

    layout = Layout(
        {"rows": [
            {"operator": "list", "data": ["a", "b"], "height": 2},
            {"operator": "list", "data": ["c", "d"]},
        ]},
        manager=manager,
    )
    window = _FakeWindow()
    layout.draw(window, Region(0, 0, 6, 10))
    assert len(layout.children) == 2

    layout.handle_key(ord("j"))
    assert layout.children[0].cursor == 1

    layout.handle_key(9)  # Tab: foco al segundo hijo
    layout.handle_key(ord("j"))
    assert layout.children[0].cursor == 1
    assert layout.children[1].cursor == 1


def test_form_submit_callback():
    _plugin_module()
    from ncurses_ui.components.form import Form

    class FakeManager:
        def __init__(self):
            self.calls = []

        def invoke_anonymous(self, handler, args):
            self.calls.append((handler, args))
            return True

    manager = FakeManager()
    form = Form(
        {"fields": [{"name": "n", "value": 1}],
         "events": {"on_submit": {"function": {"args": ["values"], "task": []}}}},
        manager=manager,
    )
    assert form.handle_key(10) == "done"
    assert manager.calls
    assert manager.calls[0][1]["values"] == {"n": 1}


def test_display_width_and_truncate_visual():
    _plugin_module()
    from ncurses_ui.kernel.renderer import display_width, truncate_visual

    assert display_width("abc") == 3
    assert display_width("日本") == 4
    assert truncate_visual("abcdef", 3) == "abc"
    assert truncate_visual("日本語", 4) == "日本"
    assert truncate_visual("abc", None) == "abc"


def test_form_edits_focused_field():
    _plugin_module()
    from ncurses_ui.components.form import Form
    from ncurses_ui.components.text import Text
    from ncurses_ui.kernel.registry import ViewRegistry

    registry = ViewRegistry()
    registry.register("text", Text)

    class FakeManager:
        pass

    manager = FakeManager()
    manager.registry = registry

    form = Form({"fields": [{"name": "n", "type": "text", "value": ""}]}, manager=manager)
    form.handle_key(ord("a"))
    form.handle_key(ord("b"))
    assert form.values()["n"] == "ab"


def test_screen_navigates_inline_and_back():
    _plugin_module()
    from ncurses_ui.components.list import List
    from ncurses_ui.components.screen import Screen
    from ncurses_ui.kernel.registry import ViewRegistry
    from ncurses_ui.kernel.renderer import Region

    registry = ViewRegistry()
    registry.register("list", List)

    class FakeManager:
        pass

    manager = FakeManager()
    manager.registry = registry

    detail = {"operator": "list", "data": ["x"], "events": {"on_item_click": {"action": "back"}}}
    view = {"operator": "list", "data": ["a"], "events": {"on_item_click": {"action": "navigate", "view": detail}}}
    screen = Screen({"view": view}, manager=manager)
    window = _FakeWindow()
    screen.draw(window, Region(0, 0, 5, 20))
    assert screen.view == view
    screen.handle_key(10)
    assert screen.view == detail
    screen.handle_key(10)
    assert screen.view == view


def test_list_handle_mouse_selects_row():
    _plugin_module()
    from ncurses_ui.components.list import List
    from ncurses_ui.kernel.renderer import Region

    listing = List({"data": ["a", "b", "c"]})
    assert listing.handle_mouse(0, 2, Region(0, 0, 5, 10)) == "done"
    assert listing.cursor == 2
    assert listing.handle_mouse(0, 9, Region(0, 0, 5, 10)) is None


def test_layout_routes_mouse_to_child():
    _plugin_module()
    from ncurses_ui.components.layout import Layout
    from ncurses_ui.components.list import List
    from ncurses_ui.kernel.registry import ViewRegistry
    from ncurses_ui.kernel.renderer import Region

    registry = ViewRegistry()
    registry.register("list", List)

    class FakeManager:
        pass

    manager = FakeManager()
    manager.registry = registry

    layout = Layout(
        {"cols": [{"operator": "list", "data": ["a"], "width": 5}, {"operator": "list", "data": ["b"]}]},
        manager=manager,
    )
    layout.draw(_FakeWindow(), Region(0, 0, 4, 10))
    assert layout.handle_mouse(6, 0, Region(0, 0, 4, 10)) == "done"
    assert layout.children[1].cursor == 0


def test_select_opens_popup_and_selects():
    _plugin_module()
    from ncurses_ui.components.selects import Select

    select = Select({"options": ["a", "b", "c"]})
    assert select.handle_key(10) is None
    assert select.open is True
    select.handle_key(ord("j"))
    assert select.index == 1
    assert select.handle_key(10) == "done"
    assert select.open is False
    assert select.result() == {"status": "ok", "value": "b"}


def test_combo_filters_and_selects_option():
    _plugin_module()
    from ncurses_ui.components.selects import Combo, Suggest

    combo = Combo({"options": [{"id": 1, "value": "Ana"}, {"id": 2, "value": "Beto"}]})
    combo.handle_key(ord("a"))
    combo.handle_key(10)
    assert combo.open is True
    assert [value for _, value in combo.filtered()] == ["Ana"]
    combo.handle_key(10)
    assert combo.result() == {"status": "ok", "value": "Ana"}
    assert issubclass(Suggest, Combo)


def test_masterdetail_syncs_detail():
    _plugin_module()
    from ncurses_ui.components.composite import MasterDetail
    from ncurses_ui.components.list import List
    from ncurses_ui.components.property import Property
    from ncurses_ui.kernel.registry import ViewRegistry
    from ncurses_ui.kernel.renderer import Region

    registry = ViewRegistry()
    registry.register("list", List)
    registry.register("property", Property)

    class FakeManager:
        pass

    manager = FakeManager()
    manager.registry = registry

    items = [{"nombre": "Ana", "edad": 30}, {"nombre": "Beto", "edad": 40}]
    master_detail = MasterDetail({"data": items, "template": "#nombre#"}, manager=manager)
    window = _FakeWindow()
    master_detail.draw(window, Region(0, 0, 5, 40))
    assert master_detail.detail.data == items[0]
    master_detail.handle_key(ord("j"))
    master_detail.draw(window, Region(0, 0, 5, 40))
    assert master_detail.detail.data == items[1]


def test_form_renders_fields():
    _plugin_module()
    from ncurses_ui.components.form import Form
    from ncurses_ui.kernel.renderer import Region

    form = Form({"fields": [{"name": "n", "label": "Nombre", "value": "Ana"}]})
    window = _FakeWindow()
    form.draw(window, Region(0, 0, 3, 20))
    assert (0, 0, ">", 0) in window.calls
    assert (0, 2, "Nombre", 0) in window.calls


def test_notify_invokes_callback():
    _plugin_module()
    from ncurses_ui.components.form import Form

    class FakeManager:
        def __init__(self):
            self.calls = []

        def invoke_anonymous(self, handler, args):
            self.calls.append((handler, args))
            return True

    manager = FakeManager()
    form = Form({"events": {"on_resize": {"function": {"args": [], "task": []}}}}, manager=manager)
    form.notify("on_resize", {"width": 80})
    assert manager.calls


def test_button_and_toolbar_mouse():
    _plugin_module()
    from ncurses_ui.components.button import Button
    from ncurses_ui.components.navigation import Toolbar
    from ncurses_ui.kernel.renderer import Region

    button = Button({"text": "OK", "action": "ok"})
    assert button.handle_mouse(1, 0, Region(0, 0, 1, 10)) == "done"
    assert button.handle_mouse(1, 5, Region(0, 0, 1, 10)) is None

    toolbar = Toolbar({"items": ["A", "B"]})
    assert toolbar.handle_mouse(1, 0, Region(0, 0, 1, 20)) == "done"
    assert toolbar.handle_mouse(5, 0, Region(0, 0, 1, 20)) == "done"
    assert toolbar.handle_mouse(19, 0, Region(0, 0, 1, 20)) is None


def test_tabview_and_accordion_render():
    _plugin_module()
    from ncurses_ui.components.containers import Accordion
    from ncurses_ui.components.tabs import TabView
    from ncurses_ui.kernel.renderer import Region

    tabview = TabView({"cells": [{"header": "A"}, {"header": "B"}], "index": 1})
    window = _FakeWindow()
    tabview.draw(window, Region(0, 0, 3, 20))
    assert window.calls[0] == (0, 0, " A ", 0)
    assert window.calls[1] == (0, 4, "[B]", 0)

    accordion = Accordion({"sections": [{"header": "S1"}, {"header": "S2"}], "expanded": [1]})
    window = _FakeWindow()
    accordion.draw(window, Region(0, 0, 4, 20))
    assert window.calls[0] == (0, 0, "> S1", 0)
    assert window.calls[1] == (1, 0, "v S2", 0)


def test_containers_golden():
    _plugin_module()
    from ncurses_ui.components.containers import (
        AbsLayout,
        Align,
        HeaderLayout,
        Portlet,
        Proxy,
        ScrollView,
    )
    from ncurses_ui.components.tabs import MultiView
    from ncurses_ui.kernel.renderer import Region

    manager = _child_manager()
    region = Region(0, 0, 4, 20)

    for component_class, config, expected in [
        (Proxy, {"body": {"operator": "x"}}, (0, 0, "x", 0)),
        (ScrollView, {"body": {"operator": "y"}}, (0, 0, "y", 0)),
        (Align, {"body": {"operator": "z"}}, (0, 0, "z", 0)),
        (MultiView, {"cells": [{"body": {"operator": "m"}}]}, (0, 0, "m", 0)),
    ]:
        component = component_class(config)
        component.manager = manager
        window = _FakeWindow()
        component.draw(window, region)
        assert window.calls == [expected]

    header = HeaderLayout({"header": {"operator": "h"}, "body": {"operator": "b"}})
    header.manager = manager
    window = _FakeWindow()
    header.draw(window, region)
    assert (0, 0, "h", 0) in window.calls and (1, 0, "b", 0) in window.calls

    portlet = Portlet({"title": "P", "body": {"operator": "c"}})
    portlet.manager = manager
    window = _FakeWindow()
    portlet.draw(window, region)
    assert (0, 0, "[P]", 0) in window.calls and (1, 0, "c", 0) in window.calls

    abslayout = AbsLayout({"cells": [{"operator": "a", "x": 3, "y": 1}]})
    abslayout.manager = manager
    window = _FakeWindow()
    abslayout.draw(window, region)
    assert window.calls == [(1, 3, "a", 0)]


def test_navigation_selects_and_presets_golden():
    _plugin_module()
    from ncurses_ui.components.composite import CardView, DataFull, FormView, ListView
    from ncurses_ui.components.navigation import ContextMenu, Hint, Sidebar
    from ncurses_ui.components.selects import RichSelect
    from ncurses_ui.components.tabs import Carousel
    from ncurses_ui.kernel.renderer import Region

    manager = _child_manager()
    region = Region(0, 0, 4, 20)

    for menu_class in (Sidebar, ContextMenu):
        menu = menu_class({"items": ["A", "B"]})
        window = _FakeWindow()
        menu.draw(window, region)
        assert window.calls[0] == (0, 0, "> A", 0)

    hint = Hint({"text": "ayuda"})
    window = _FakeWindow()
    hint.draw(window, region)
    assert window.calls == [(0, 0, "ayuda", 0)]

    assert RichSelect({"options": [{"id": 1, "value": "Ana"}]}).label() == "Ana"

    carousel = Carousel({"cells": [{"body": {"operator": "m"}}]})
    carousel.manager = manager
    window = _FakeWindow()
    carousel.draw(window, region)
    assert window.calls == [(0, 0, "m", 0)]

    for preset_class, config in [
        (ListView, {"data": "x", "columns": [{"id": "n"}], "title": "T"}),
        (FormView, {"elements": [{"name": "n", "type": "text"}], "title": "F"}),
        (DataFull, {"data": "x"}),
        (CardView, {"data": "x"}),
    ]:
        preset = preset_class(config)
        preset.manager = manager
        window = _FakeWindow()
        preset.draw(window, region)
        assert window.calls


def test_controls_render_golden():
    _plugin_module()
    from ncurses_ui.components.checkbox import Checkbox
    from ncurses_ui.components.counter import Counter
    from ncurses_ui.components.icon import Icon
    from ncurses_ui.components.label import Label
    from ncurses_ui.components.rangeslider import RangeSlider
    from ncurses_ui.components.slider import Slider
    from ncurses_ui.components.spacer import Spacer
    from ncurses_ui.components.textarea import Textarea
    from ncurses_ui.components.toggle import Toggle
    from ncurses_ui.kernel.renderer import Region

    region = Region(0, 0, 4, 20)
    for component, first in [
        (Checkbox({"label": "A", "value": True}), (0, 0, "[X] A", 0)),
        (Toggle({"label": "B", "value": False}), (0, 0, "[OFF] B", 0)),
        (Icon({"glyph": "*", "label": "F"}), (0, 0, "* F", 0)),
        (Label({"label": "L"}), (0, 0, "L", 0)),
        (Counter({"label": "N", "value": 5}), None),
        (Slider({"value": 0, "min": 0, "max": 10, "bar_width": 5}), None),
        (RangeSlider({"value": [2, 8], "min": 0, "max": 10, "bar_width": 10}), None),
        (Textarea({"value": "a\nb"}), None),
    ]:
        window = _FakeWindow()
        component.draw(window, region)
        assert window.calls
        if first is not None:
            assert window.calls[0] == first

    window = _FakeWindow()
    Spacer({}).draw(window, region)
    assert window.calls == []


def test_dashboard_composes_mainbar_sidebar_cards():
    _plugin_module()
    from ncurses_ui.components.composite import Dashboard
    from ncurses_ui.components.containers import GridLayout
    from ncurses_ui.components.navigation import MainBar, Sidebar
    from ncurses_ui.components.viz import Card
    from ncurses_ui.kernel.registry import ViewRegistry
    from ncurses_ui.kernel.renderer import Region

    registry = ViewRegistry()
    registry.register("mainbar", MainBar)
    registry.register("sidebar", Sidebar)
    registry.register("gridlayout", GridLayout)
    registry.register("card", Card)

    class FakeManager:
        pass

    manager = FakeManager()
    manager.registry = registry

    dashboard = Dashboard(
        {"name": "App", "menu": ["M"], "cards": [{"label": "L", "value": 1}], "user_menu": ["Cuenta"]},
        manager=manager,
    )
    window = _FakeWindow()
    dashboard.draw(window, Region(0, 0, 8, 40))
    assert dashboard.mainbar is not None
    assert dashboard.sidebar is not None
    assert dashboard.content is not None
    assert window.calls

    dashboard.handle_key(ord("="))
    assert dashboard.collapsed is True
    dashboard.handle_key(ord("="))
    assert dashboard.collapsed is False
    dashboard.handle_key(ord("u"))
    assert dashboard.user_open is True
    window = _FakeWindow()
    dashboard.draw(window, Region(0, 0, 8, 40))
    assert any("Cuenta" in call[2] for call in window.calls)


def test_mainbar_render_and_actions():
    _plugin_module()
    from ncurses_ui.components.navigation import MainBar
    from ncurses_ui.kernel.renderer import Region

    bar = MainBar({"name": "Mediapp"})
    window = _FakeWindow()
    bar.draw(window, Region(0, 0, 1, 30))
    assert window.calls[0] == (0, 0, "Mediapp", 0)
    assert any(call[2] == "[=]" for call in window.calls)
    assert any(call[2] == "[...]" for call in window.calls)
    assert bar.handle_mouse(8, 0, Region(0, 0, 1, 30)) == {"action": "toggle_sidebar"}
    assert bar.handle_mouse(27, 0, Region(0, 0, 1, 30)) == {"action": "user_menu"}


def test_card_render():
    _plugin_module()
    from ncurses_ui.components.viz import Card
    from ncurses_ui.kernel.renderer import Region

    window = _FakeWindow()
    Card({"icon": "*", "value": 7, "label": "Usuarios"}).draw(window, Region(0, 0, 1, 30))
    assert window.calls == [(0, 0, "[ * 7 - Usuarios ]", 0)]


def test_gridlayout_and_toolbar():
    _plugin_module()
    from ncurses_ui.components.containers import GridLayout
    from ncurses_ui.components.navigation import Toolbar
    from ncurses_ui.kernel.renderer import Region

    class Child:
        def __init__(self, tag):
            self.tag = tag

        def draw(self, window, region):
            window.addstr(region.y, region.x, self.tag, 0)

    class FakeRegistry:
        def has(self, op):
            return True

        def create(self, op, config, context, manager):
            return Child(op)

    class FakeManager:
        registry = FakeRegistry()

    grid = GridLayout({"cols": 2, "cells": [{"operator": "a"}, {"operator": "b"}]})
    grid.manager = FakeManager()
    window = _FakeWindow()
    grid.draw(window, Region(0, 0, 4, 10))
    assert window.calls == [(0, 0, "a", 0), (0, 5, "b", 0)]

    toolbar = Toolbar({"items": [{"value": "Nuevo"}, "Abrir"]})
    window = _FakeWindow()
    toolbar.draw(window, Region(0, 0, 1, 40))
    assert window.calls == [(0, 0, "[Nuevo]", 0), (0, 8, "[Abrir]", 0)]


def test_datatable_draws_within_region():
    _plugin_module()
    from ncurses_ui.components.datatable import DataTable
    from ncurses_ui.kernel.renderer import Region

    datatable = DataTable({"columns": [{"id": "n", "header": "N", "sort": "string"}], "data": [{"n": "a"}]})
    datatable._ensure_state()
    window = _FakeWindow()
    region = Region(2, 5, 8, 30)
    datatable._draw_datatable(window, datatable.state, datatable.title, 3, region)
    assert (2, 5, "+" + "-" * 28 + "+", 0) in window.calls
    assert any(call[0] == 2 and call[1] == 7 and "Tabla" in call[2] for call in window.calls)
    assert all(call[0] >= 2 for call in window.calls)
    assert all(call[1] >= 5 for call in window.calls)
