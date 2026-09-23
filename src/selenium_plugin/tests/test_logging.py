"""
Tests de logging de fallos y comportamiento best-effort
=======================================================

Verifican que los fallos se registren (consola + archivo con traceback) y
que las features opcionales no tumben la sesion.
"""

import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from kernel.contract import SessionSpec
from session import Logging, Stealth
from session.BrowserFactory import BrowserFactory
from session.BrowserSession import BrowserSession
from SeleniumPlugin import SeleniumPlugin


class TestLoggingModule(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='log_test_')
        self.log_file = os.path.join(self.tmp, 'selenium.log')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_log_failure_writes_file_and_traceback(self):
        try:
            raise ValueError('boom')
        except ValueError as e:
            Logging.log_failure('T', 'contexto x', e, self.log_file)
        content = open(self.log_file, encoding='utf-8').read()
        self.assertIn('FALLO en contexto x', content)
        self.assertIn('ValueError: boom', content)
        self.assertIn('Traceback', content)

    def test_log_warning_writes_file(self):
        Logging.log_warning('T', 'ctx', 'algo', self.log_file)
        self.assertIn('algo', open(self.log_file, encoding='utf-8').read())

    def test_invalid_log_path_does_not_raise(self):
        Logging.log_failure('T', 'ctx', ValueError('x'), '/proc/imposible/log.txt')


class TestBestEffort(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='log_test_')
        self.log_file = os.path.join(self.tmp, 'selenium.log')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_stealth_cdp_failure_is_best_effort(self):
        driver = Mock()
        driver.name = 'chrome'

        def cdp(command, params):
            if command == 'Emulation.setTimezoneOverride':
                raise RuntimeError('cdp no soportado')
            return {}

        driver.execute_cdp_cmd.side_effect = cdp
        spec = SessionSpec.from_meta({'driver': 'chrome', 'timezone': 'UTC', 'log_file': self.log_file})
        Stealth._install_chromium(driver, spec, 'T')  # no debe lanzar
        self.assertIn('timezone override', open(self.log_file, encoding='utf-8').read())

    def test_firefox_addon_failure_is_best_effort(self):
        driver = Mock()
        driver.install_addon.side_effect = [RuntimeError('addon roto'), 'ok']
        spec = SessionSpec.from_meta({'driver': 'firefox', 'extensions': ['/a.xpi', '/b.xpi'], 'log_file': self.log_file})
        BrowserFactory._install_firefox_addons(driver, spec, 'firefox', 'T')  # no debe lanzar
        self.assertEqual(driver.install_addon.call_count, 2)
        self.assertIn('instalar extension Firefox', open(self.log_file, encoding='utf-8').read())

    def test_create_logs_and_reraises(self):
        spec = SessionSpec.from_meta({'driver': 'nope', 'log_file': self.log_file})
        with self.assertRaises(ValueError):
            BrowserFactory.create(spec, 'T')
        self.assertIn("crear driver 'nope'", open(self.log_file, encoding='utf-8').read())

    def test_browser_session_logs_operator_failure(self):
        session = BrowserSession(plugin_name='T')
        session.log_file = self.log_file
        session.driver = Mock()
        session.driver.get.side_effect = RuntimeError('nav fallo')
        result = session.execute_command('open', {'url': 'https://x'})
        self.assertFalse(result['success'])
        self.assertIn("operador 'open'", open(self.log_file, encoding='utf-8').read())

    def test_plugin_logs_failure(self):
        class FakeMemory:
            vars = {}
            current_loop = None
            def _interpolate_variables(self, value):
                return value
            def get(self):
                return []

        class FakeCtx:
            meta = {'driver': 'nope', 'log_file': self.log_file}
            memory_handler = FakeMemory()

        plugin = SeleniumPlugin(context=FakeCtx())
        result = plugin.execute('selenium', {'selenium': {'operator': 'open', 'url': 'https://x'}})
        self.assertFalse(result['success'])
        content = open(self.log_file, encoding='utf-8').read()
        self.assertIn("crear driver 'nope'", content)
        self.assertIn('plugin Selenium', content)


if __name__ == '__main__':
    unittest.main()
