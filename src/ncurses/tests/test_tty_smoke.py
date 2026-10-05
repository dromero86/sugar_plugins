"""Smoke en TTY real (pty): corre un componente ncurses en un pseudo-terminal.

Se saltea si el entorno no soporta `pty`/`fork`. No requiere un terminal
interactivo: asigna un pty y le envia teclas.
"""
import os
import pty
import select
import sys
import time

import pytest

PLUGIN = os.path.join(os.path.dirname(__file__), "..", "src", "ncurses_plugin.py")

CHILD = r'''
import json, sys, types, importlib.util
sys.path.insert(0, "__SRC__")

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
    def call_function(self, *a, **k):
        return None
    def register_function(self, *a, **k):
        return None
    def invoke_anonymous(self, *a, **k):
        return None

sugar = types.ModuleType("Sugar")
lang = types.ModuleType("Sugar.Lang")
plugins = types.ModuleType("Sugar.Lang.Plugins")
pbm = types.ModuleType("Sugar.Lang.Plugins.PluginBase")
utils = types.ModuleType("Sugar.Lang.Utils")
outm = types.ModuleType("Sugar.Lang.Utils.Output")
pbm.PluginBase = PluginBase
outm.Output = Output
plugins.PluginBase = PluginBase
sys.modules.update({
    "Sugar": sugar, "Sugar.Lang": lang, "Sugar.Lang.Plugins": plugins,
    "Sugar.Lang.Plugins.PluginBase": pbm, "Sugar.Lang.Utils": utils,
    "Sugar.Lang.Utils.Output": outm,
})

spec = importlib.util.spec_from_file_location("ncurses_plugin", "__PLUGIN__")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
plugin = module.NcursesPlugin()
result = plugin.execute("ncurses", json.loads(sys.argv[1]))
sys.stdout.write("\nRESULT:%s\n" % result)
'''.replace("__SRC__", os.path.join(os.path.dirname(PLUGIN), "")).replace("__PLUGIN__", PLUGIN)


def _run_in_pty(config, keys):
    os.environ["TERM"] = "xterm"
    os.environ["LANG"] = "C.UTF-8"
    pid, fd = pty.fork()
    if pid == 0:
        os.execv(sys.executable, [sys.executable, "-c", CHILD, config])
    time.sleep(0.8)
    for char in keys:
        os.write(fd, bytes([char]))
        time.sleep(0.2)
    out = b""
    while True:
        ready, _, _ = select.select([fd], [], [], 3.0)
        if not ready:
            break
        try:
            data = os.read(fd, 4096)
        except OSError:
            break
        if not data:
            break
        out += data
    os.waitpid(pid, 0)
    return out.decode("utf-8", "replace")


def _maybe_skip():
    if not hasattr(os, "fork"):
        pytest.skip("sin fork/pty")


def test_list_renders_and_selects_in_tty():
    _maybe_skip()
    config = '{"operator": "list", "data": ["uno", "dos", "tres"], "id": "r"}'
    text = _run_in_pty(config, [ord("j"), ord("q")])
    assert "uno" in text
    assert "'selected': 'dos'" in text


def test_datatable_renders_and_selects_in_tty():
    _maybe_skip()
    config = ('{"operator": "datatable", "data": [{"n": "alfa", "v": 1}, {"n": "beta", "v": 2}], '
              '"columns": [{"id": "n", "header": "N"}, {"id": "v", "header": "V", "sort": "int"}], "id": "r"}')
    text = _run_in_pty(config, [ord("j"), ord("q")])
    assert "alfa" in text
    assert "'n': 'beta'" in text


def test_screen_navigates_in_tty():
    _maybe_skip()
    config = ('{"operator": "screen", "view": {"operator": "list", "data": ["uno", "dos"], '
              '"events": {"on_item_click": {"action": "navigate", '
              '"view": {"operator": "property", "data": {"detalle": "ok"}}}}}}')
    text = _run_in_pty(config, [13, ord("q")])
    assert "'detalle': 'ok'" in text
