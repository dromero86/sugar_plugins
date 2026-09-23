"""
Tests de las capas kernel/session (Fase 1)
==========================================

Verifican el contrato y la sesion de navegador de forma aislada,
sin depender de Sugar.
"""

import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from kernel.contract import SessionSpec
from session.BrowserFactory import BrowserFactory
from session.BrowserSession import BrowserSession
from SeleniumPlugin import SeleniumPlugin


class TestSessionSpec(unittest.TestCase):
    def test_from_meta_parses_fields(self):
        spec = SessionSpec.from_meta({
            'browser': 'Firefox',
            'headless': True,
            'detach': True,
            'options': ['--width=1280'],
            'prefs': {'network.proxy.type': 0},
            'timeout': 30,
            'implicit_wait': 7,
            'driver': {'bin': '/tmp/geckodriver'},
            'binary': '/usr/bin/firefox',
        })
        self.assertEqual(spec.browser, 'firefox')
        self.assertTrue(spec.headless)
        self.assertTrue(spec.detach)
        self.assertEqual(spec.options, ['--width=1280'])
        self.assertEqual(spec.prefs, {'network.proxy.type': 0})
        self.assertEqual(spec.timeout, 30)
        self.assertEqual(spec.implicit_wait, 7)
        self.assertEqual(spec.driver_path, '/tmp/geckodriver')
        self.assertEqual(spec.binary, '/usr/bin/firefox')

    def test_from_meta_parses_profile(self):
        spec = SessionSpec.from_meta({'browser': 'firefox', 'profile': '/tmp/ffprof'})
        self.assertEqual(spec.profile, '/tmp/ffprof')

    def test_from_meta_defaults(self):
        spec = SessionSpec.from_meta({})
        self.assertEqual(spec.browser, 'chrome')
        self.assertFalse(spec.headless)
        self.assertFalse(spec.detach)
        self.assertEqual(spec.options, [])
        self.assertEqual(spec.prefs, {})
        self.assertIsNone(spec.driver_path)

    def test_cache_key_is_stable(self):
        a = SessionSpec.from_meta({'browser': 'firefox', 'prefs': {'b': 2, 'a': 1}})
        b = SessionSpec.from_meta({'browser': 'firefox', 'prefs': {'a': 1, 'b': 2}})
        self.assertEqual(a.cache_key(), b.cache_key())
        c = SessionSpec.from_meta({'browser': 'chrome', 'prefs': {'a': 1, 'b': 2}})
        self.assertNotEqual(a.cache_key(), c.cache_key())

    def test_cache_key_includes_profile(self):
        a = SessionSpec.from_meta({'browser': 'firefox', 'profile': '/tmp/a'})
        b = SessionSpec.from_meta({'browser': 'firefox', 'profile': '/tmp/b'})
        self.assertNotEqual(a.cache_key(), b.cache_key())


class TestBrowserFactoryProfile(unittest.TestCase):
    def setUp(self):
        self.profile_dir = tempfile.mkdtemp(prefix='ffprof_test_')

    def tearDown(self):
        shutil.rmtree(self.profile_dir, ignore_errors=True)

    def test_firefox_sets_profile_attribute(self):
        spec = SessionSpec.from_meta({'browser': 'firefox', 'profile': self.profile_dir})
        options = Mock()
        BrowserFactory._apply_profile(options, spec, 'firefox', 'T')
        self.assertEqual(options.profile, self.profile_dir)

    def test_chrome_uses_user_data_dir_flag(self):
        spec = SessionSpec.from_meta({'browser': 'chrome', 'profile': self.profile_dir})
        options = Mock()
        BrowserFactory._apply_profile(options, spec, 'chrome', 'T')
        options.add_argument.assert_called_once_with(f'--user-data-dir={self.profile_dir}')

    def test_missing_profile_raises(self):
        spec = SessionSpec.from_meta({'browser': 'firefox', 'profile': '/no/existe/profile'})
        with self.assertRaises(ValueError):
            BrowserFactory._apply_profile(Mock(), spec, 'firefox', 'T')

    def test_no_profile_is_noop(self):
        spec = SessionSpec.from_meta({'browser': 'firefox'})
        options = Mock()
        BrowserFactory._apply_profile(options, spec, 'firefox', 'T')
        self.assertEqual(options.profile.call_count, 0)
        self.assertEqual(options.add_argument.call_count, 0)


class TestBrowserSession(unittest.TestCase):
    def setUp(self):
        self.session = BrowserSession(plugin_name='TestSession')
        self.driver = Mock()
        self.session.driver = self.driver

    def test_initialize_uses_factory(self):
        spec = SessionSpec.from_meta({'browser': 'firefox', 'timeout': 20, 'implicit_wait': 3})
        with patch('session.BrowserSession.BrowserFactory.create', return_value=(self.driver, {'name': 'Firefox'})) as create:
            result = self.session.initialize(spec)
        create.assert_called_once()
        self.assertIs(result, self.driver)
        self.assertEqual(self.session.wait_timeout, 20)
        self.assertEqual(self.session.implicit_wait, 3)

    def test_ensure_driver_only_initializes_once(self):
        spec = SessionSpec.from_meta({'browser': 'firefox'})

        def fake_init(_spec):
            self.session.driver = self.driver

        with patch.object(self.session, 'initialize', side_effect=fake_init) as init:
            self.session.driver = None
            self.session.ensure_driver(spec)
            self.session.ensure_driver(spec)
        init.assert_called_once_with(spec)

    def test_execute_open_calls_get(self):
        result = self.session.execute_command('open', {'url': 'https://example.com', 'id': 'opened'})
        self.driver.get.assert_called_once_with('https://example.com')
        self.assertEqual(result, {'opened': True, 'success': True, 'url': 'https://example.com'})

    def test_execute_unknown_command_returns_error(self):
        result = self.session.execute_command('nope', {})
        self.assertFalse(result['success'])
        self.assertIn('no soportado', result['error'])

    def test_resolve_by(self):
        from selenium.webdriver.common.by import By
        self.assertEqual(self.session._resolve_by('xpath=//a'), (By.XPATH, '//a'))
        self.assertEqual(self.session._resolve_by('//a'), (By.XPATH, '//a'))
        self.assertEqual(self.session._resolve_by('#id'), (By.CSS_SELECTOR, '#id'))

    def test_quit_clears_driver(self):
        self.session.quit()
        self.driver.quit.assert_called_once()
        self.assertIsNone(self.session.driver)


class TestPluginLayering(unittest.TestCase):
    def test_plugin_is_a_browser_session(self):
        plugin = SeleniumPlugin()
        self.assertIsInstance(plugin, BrowserSession)

    def test_plugin_keeps_supported_browsers(self):
        plugin = SeleniumPlugin()
        self.assertIn('chrome', plugin.SUPPORTED_BROWSERS)
        self.assertIn('firefox', plugin.SUPPORTED_BROWSERS)
        self.assertIn('edge', plugin.SUPPORTED_BROWSERS)


class TestBrowserFactoryCompat(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='compat_test_')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_from_meta_parses_compat_fields(self):
        spec = SessionSpec.from_meta({
            'browser': 'firefox',
            'download_dir': '/tmp/dl',
            'proxy': 'http://proxy:8080',
            'user_agent': 'UA/1.0',
            'extensions': ['/tmp/ext.xpi'],
            'permissions': {'geolocation': 'allow'},
        })
        self.assertEqual(spec.download_dir, '/tmp/dl')
        self.assertEqual(spec.proxy, 'http://proxy:8080')
        self.assertEqual(spec.user_agent, 'UA/1.0')
        self.assertEqual(spec.extensions, ['/tmp/ext.xpi'])
        self.assertEqual(spec.permissions, {'geolocation': 'allow'})

    def test_binary_sets_binary_location(self):
        spec = SessionSpec.from_meta({'browser': 'firefox', 'binary': '/usr/bin/firefox'})
        options = Mock()
        BrowserFactory._apply_compat_options(options, spec, 'firefox', 'T')
        self.assertEqual(options.binary_location, '/usr/bin/firefox')

    def test_user_agent_chrome_flag(self):
        spec = SessionSpec.from_meta({'browser': 'chrome', 'user_agent': 'UA/1.0'})
        options = Mock()
        BrowserFactory._apply_user_agent(options, spec.user_agent, 'chrome', 'T')
        options.add_argument.assert_called_once_with('--user-agent=UA/1.0')

    def test_user_agent_firefox_pref(self):
        spec = SessionSpec.from_meta({'browser': 'firefox', 'user_agent': 'UA/1.0'})
        options = Mock()
        BrowserFactory._apply_user_agent(options, spec.user_agent, 'firefox', 'T')
        options.set_preference.assert_called_once_with('general.useragent.override', 'UA/1.0')

    def test_proxy_chrome_flag(self):
        spec = SessionSpec.from_meta({'browser': 'chrome', 'proxy': 'http://proxy:8080'})
        options = Mock()
        BrowserFactory._apply_proxy(options, spec.proxy, 'chrome', 'T')
        options.add_argument.assert_called_once_with('--proxy-server=http://proxy:8080')

    def test_proxy_firefox_prefs(self):
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        spec = SessionSpec.from_meta({'browser': 'firefox', 'proxy': 'http://proxy:8080'})
        options = FirefoxOptions()
        BrowserFactory._apply_proxy(options, spec.proxy, 'firefox', 'T')
        self.assertEqual(options.preferences['network.proxy.type'], 1)
        self.assertEqual(options.preferences['network.proxy.http'], 'proxy')
        self.assertEqual(options.preferences['network.proxy.http_port'], 8080)
        self.assertEqual(options.preferences['network.proxy.ssl'], 'proxy')

    def test_proxy_socks_firefox(self):
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        spec = SessionSpec.from_meta({'browser': 'firefox', 'proxy': 'socks5://proxy:1080'})
        options = FirefoxOptions()
        BrowserFactory._apply_proxy(options, spec.proxy, 'firefox', 'T')
        self.assertEqual(options.preferences['network.proxy.socks_version'], 5)
        self.assertEqual(options.preferences['network.proxy.socks_port'], 1080)

    def test_proxy_invalid_raises(self):
        spec = SessionSpec.from_meta({'browser': 'firefox', 'proxy': 'sin-puerto'})
        with self.assertRaises(ValueError):
            BrowserFactory._apply_proxy(Mock(), spec.proxy, 'firefox', 'T')

    def test_download_dir_prefs_firefox(self):
        prefs = BrowserFactory._download_dir_prefs(self.tmp, 'firefox')
        self.assertEqual(prefs['browser.download.folderList'], 2)
        self.assertEqual(prefs['browser.download.dir'], os.path.abspath(self.tmp))

    def test_download_dir_prefs_chrome(self):
        prefs = BrowserFactory._download_dir_prefs(self.tmp, 'chrome')
        self.assertEqual(prefs['download.default_directory'], os.path.abspath(self.tmp))
        self.assertFalse(prefs['download.prompt_for_download'])

    def test_permissions_prefs_firefox(self):
        prefs = BrowserFactory._permissions_prefs({'geolocation': 'allow', 'camera': 'block'}, 'firefox')
        self.assertEqual(prefs['permissions.default.geo'], 1)
        self.assertEqual(prefs['permissions.default.camera'], 2)

    def test_permissions_prefs_chrome(self):
        prefs = BrowserFactory._permissions_prefs({'geolocation': 'allow'}, 'chrome')
        self.assertEqual(prefs['profile.default_content_setting_values.geolocation'], 1)

    def test_permissions_unknown_ignored(self):
        prefs = BrowserFactory._permissions_prefs({'noexiste': 'allow'}, 'firefox')
        self.assertEqual(prefs, {})

    def test_extensions_missing_raises(self):
        spec = SessionSpec.from_meta({'browser': 'chrome', 'extensions': ['/no/existe.crx']})
        with self.assertRaises(ValueError):
            BrowserFactory._apply_extensions(Mock(), spec, 'chrome', 'T')

    def test_chrome_extension_added(self):
        ext = os.path.join(self.tmp, 'ext.crx')
        with open(ext, 'wb') as f:
            f.write(b'x')
        spec = SessionSpec.from_meta({'browser': 'chrome', 'extensions': [ext]})
        options = Mock()
        BrowserFactory._apply_extensions(options, spec, 'chrome', 'T')
        options.add_extension.assert_called_once_with(ext)

    def test_firefox_addons_installed_post_session(self):
        ext = os.path.join(self.tmp, 'ext.xpi')
        with open(ext, 'wb') as f:
            f.write(b'x')
        spec = SessionSpec.from_meta({'browser': 'firefox', 'extensions': [ext]})
        driver = Mock()
        BrowserFactory._install_firefox_addons(driver, spec, 'firefox', 'T')
        driver.install_addon.assert_called_once_with(ext, temporary=True)

    def test_pref_maps_merge_chrome_experimental(self):
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        spec = SessionSpec.from_meta({
            'browser': 'chrome',
            'download_dir': self.tmp,
            'permissions': {'geolocation': 'allow'},
        })
        options = ChromeOptions()
        options.add_experimental_option('detach', True)
        BrowserFactory._apply_pref_maps(options, spec, 'chrome', 'T')
        prefs = options.experimental_options['prefs']
        self.assertIn('download.default_directory', prefs)
        self.assertEqual(prefs['profile.default_content_setting_values.geolocation'], 1)
        self.assertTrue(options.experimental_options['detach'])


class TestBrowserFactoryStealth(unittest.TestCase):
    def test_from_meta_parses_stealth_fields(self):
        spec = SessionSpec.from_meta({
            'browser': 'chrome',
            'exclude_switches': ['enable-automation'],
            'experimental_options': {'useAutomationExtension': False},
            'anti_detection': True,
        })
        self.assertEqual(spec.exclude_switches, ['enable-automation'])
        self.assertEqual(spec.experimental_options, {'useAutomationExtension': False})
        self.assertTrue(spec.anti_detection)

    def test_chromium_options_sets_exclude_switches_and_experimental(self):
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        spec = SessionSpec.from_meta({
            'browser': 'chrome',
            'exclude_switches': ['enable-automation'],
            'experimental_options': {'useAutomationExtension': False},
        })
        options = ChromeOptions()
        BrowserFactory._apply_chromium_options(options, spec, 'chrome', 'T')
        self.assertEqual(options.experimental_options['excludeSwitches'], ['enable-automation'])
        self.assertFalse(options.experimental_options['useAutomationExtension'])

    def test_chromium_options_merges_existing(self):
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        spec = SessionSpec.from_meta({'browser': 'chrome', 'exclude_switches': ['enable-automation']})
        options = ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['load-extension'])
        BrowserFactory._apply_chromium_options(options, spec, 'chrome', 'T')
        self.assertEqual(options.experimental_options['excludeSwitches'], ['load-extension', 'enable-automation'])

    def test_chromium_options_ignored_on_firefox(self):
        spec = SessionSpec.from_meta({'browser': 'firefox', 'exclude_switches': ['x'], 'experimental_options': {'a': 1}})
        options = Mock()
        BrowserFactory._apply_chromium_options(options, spec, 'firefox', 'T')
        options.add_experimental_option.assert_not_called()

    def test_anti_detection_chromium(self):
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        spec = SessionSpec.from_meta({'browser': 'chrome', 'anti_detection': True})
        options = ChromeOptions()
        BrowserFactory._apply_anti_detection_options(options, spec, 'chrome', 'T')
        self.assertIn('--disable-blink-features=AutomationControlled', options.arguments)
        self.assertIn('enable-automation', options.experimental_options['excludeSwitches'])
        self.assertFalse(options.experimental_options['useAutomationExtension'])

    def test_anti_detection_firefox_pref(self):
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        spec = SessionSpec.from_meta({'browser': 'firefox', 'anti_detection': True})
        options = FirefoxOptions()
        BrowserFactory._apply_anti_detection_options(options, spec, 'firefox', 'T')
        self.assertFalse(options.preferences['dom.webdriver.enabled'])

    def test_anti_detection_noop_when_disabled(self):
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        spec = SessionSpec.from_meta({'browser': 'chrome'})
        options = ChromeOptions()
        BrowserFactory._apply_anti_detection_options(options, spec, 'chrome', 'T')
        self.assertEqual(options.arguments, [])
        self.assertEqual(options.experimental_options, {})

    def test_install_anti_detection_chromium(self):
        spec = SessionSpec.from_meta({'browser': 'chrome', 'anti_detection': True})
        driver = Mock()
        BrowserFactory._install_anti_detection(driver, spec, 'chrome', 'T')
        driver.execute_cdp_cmd.assert_called_once()
        self.assertEqual(driver.execute_cdp_cmd.call_args[0][0], 'Page.addScriptToEvaluateOnNewDocument')

    def test_install_anti_detection_firefox_noop(self):
        spec = SessionSpec.from_meta({'browser': 'firefox', 'anti_detection': True})
        driver = Mock()
        BrowserFactory._install_anti_detection(driver, spec, 'firefox', 'T')
        driver.execute_cdp_cmd.assert_not_called()


if __name__ == '__main__':
    unittest.main()
