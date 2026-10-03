"""
Tests de stealth, humanizacion y config avanzada
================================================

Verifican build_script, instalacion CDP/BiDi, humanizacion, y el parseo
de las nuevas claves de meta en SessionSpec.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from kernel.contract import SessionSpec
from session import Stealth, Humanize
from session.BrowserFactory import BrowserFactory


class TestStealthScript(unittest.TestCase):
    def test_build_script_defaults(self):
        script = Stealth.build_script({})
        self.assertIn("navigator,'webdriver'", script)
        self.assertIn('window.chrome', script)
        self.assertIn("navigator,'plugins'", script)
        self.assertIn("navigator,'languages'", script)
        self.assertIn('WebGLRenderingContext', script)
        self.assertIn('navigator.permissions', script)

    def test_build_script_fingerprint_values(self):
        script = Stealth.build_script({
            'platform': 'Win32',
            'hardware_concurrency': 8,
            'device_memory': 8,
            'webgl_vendor': 'Acme',
            'webgl_renderer': 'Acme GPU',
        })
        self.assertIn('Win32', script)
        self.assertIn('hardwareConcurrency', script)
        self.assertIn('Acme GPU', script)

    def test_build_script_noise(self):
        script = Stealth.build_script({'canvas_noise': True, 'audio_noise': True})
        self.assertIn('toDataURL', script)
        self.assertIn('getFloatFrequencyData', script)

    def test_build_script_firefox_is_not_chrome(self):
        script = Stealth.build_script({}, browser='firefox')
        self.assertIn('webdriver', script)
        self.assertIn('Navigator.prototype', script)
        self.assertNotIn('window.chrome', script)
        self.assertNotIn('Chrome PDF Plugin', script)
        self.assertNotIn('deviceMemory', script)
        self.assertNotIn('WebGLRenderingContext', script)

    def test_build_script_firefox_optional_fingerprint(self):
        script = Stealth.build_script(
            {'languages': ['es-AR', 'es'], 'webgl': True, 'webgl_vendor': 'Acme'},
            browser='firefox',
        )
        self.assertIn('es-AR', script)
        self.assertIn('WebGLRenderingContext', script)
        self.assertIn('Acme', script)

    def test_build_preload_function_wraps_in_function(self):
        fn = Stealth.build_preload_function({}, browser='firefox')
        self.assertTrue(fn.startswith('() => {'))
        self.assertTrue(fn.rstrip().endswith('}'))

    def test_url_pattern_conversion(self):
        self.assertEqual(Stealth.url_pattern({'type': 'string', 'pattern': 'x'}), {'type': 'string', 'pattern': 'x'})
        self.assertEqual(Stealth.url_pattern('/api'), {'type': 'string', 'pattern': '/api'})
        self.assertEqual(
            Stealth.url_pattern('https://example.com/a'),
            {'type': 'pattern', 'protocol': 'https', 'hostname': 'example.com', 'pathname': '/a'},
        )
        self.assertEqual(Stealth.url_pattern('*.png'), {'type': 'pattern', 'pathname': '\\*.png'})


class TestStealthInstall(unittest.TestCase):
    def _driver(self, name='chrome'):
        driver = Mock()
        driver.name = name
        return driver

    def test_install_chromium_cdp(self):
        spec = SessionSpec.from_meta({
            'browser': 'chrome',
            'stealth': True,
            'timezone': 'America/Argentina/Buenos_Aires',
            'locale': 'es-AR',
            'geolocation': {'latitude': -34.6, 'longitude': -58.4, 'accuracy': 20},
            'accept_language': 'es-AR,es',
        })
        driver = self._driver('chrome')
        Stealth.install(driver, spec, 'chrome', 'T')
        calls = [c[0][0] for c in driver.execute_cdp_cmd.call_args_list]
        self.assertIn('Page.addScriptToEvaluateOnNewDocument', calls)
        self.assertIn('Emulation.setTimezoneOverride', calls)
        self.assertIn('Emulation.setLocaleOverride', calls)
        self.assertIn('Emulation.setGeolocationOverride', calls)
        self.assertIn('Network.setExtraHTTPHeaders', calls)

    def test_install_bidi_auth_and_block(self):
        spec = SessionSpec.from_meta({
            'browser': 'firefox',
            'bidi': True,
            'proxy_user': 'user',
            'proxy_pass': 'pass',
            'network_block': ['*.png'],
        })
        driver = self._driver('firefox')
        Stealth.install(driver, spec, 'firefox', 'T')
        driver.network.add_auth_handler.assert_called_once_with('user', 'pass')
        driver.network.add_request_handler.assert_called_once()

    def test_install_firefox_pins_preload_script(self):
        spec = SessionSpec.from_meta({'browser': 'firefox', 'stealth': True})
        driver = self._driver('firefox')
        Stealth.install(driver, spec, 'firefox', 'T')
        driver.script.pin.assert_called_once()
        script = driver.script.pin.call_args[0][0]
        self.assertTrue(script.startswith('() => {'))

    def test_install_firefox_stealth_does_not_warn_unsupported(self):
        spec = SessionSpec.from_meta({
            'browser': 'firefox', 'stealth': True, 'on_unsupported': 'error',
        })
        driver = self._driver('firefox')
        Stealth.install(driver, spec, 'firefox', 'T')

    def test_install_firefox_noop_without_stealth(self):
        spec = SessionSpec.from_meta({'browser': 'firefox'})
        driver = self._driver('firefox')
        Stealth.install(driver, spec, 'firefox', 'T')
        driver.script.pin.assert_not_called()


class TestHumanize(unittest.TestCase):
    def test_settings_defaults(self):
        cfg = Humanize.settings(None)
        self.assertEqual(cfg['min_delay'], 0.1)
        self.assertEqual(cfg['typing_delay'], 0.05)

    def test_settings_override(self):
        cfg = Humanize.settings({'min_delay': 1, 'typing_delay': 0.2})
        self.assertEqual(cfg['min_delay'], 1)
        self.assertEqual(cfg['typing_delay'], 0.2)

    def test_delays_and_steps(self):
        cfg = {'min_delay': 0.2, 'max_delay': 0.3, 'mouse_steps': 5, 'scroll_step': 100}
        self.assertGreaterEqual(Humanize.between_operators_delay(cfg), 0.2)
        self.assertLessEqual(Humanize.between_operators_delay(cfg), 0.3)
        self.assertEqual(Humanize.mouse_steps(cfg), 5)
        self.assertEqual(Humanize.scroll_step(cfg), 100)

    def test_typing_delay_fixed(self):
        self.assertEqual(Humanize.typing_delay({'typing_delay': 0.02}), 0.02)

    def test_typing_delay_range(self):
        cfg = {'typing_delay_range': [0.01, 0.03]}
        for _ in range(20):
            delay = Humanize.typing_delay(cfg)
            self.assertGreaterEqual(delay, 0.01)
            self.assertLessEqual(delay, 0.03)

    def test_typing_pause_disabled_by_default(self):
        self.assertEqual(Humanize.typing_pause(None), 0.0)
        self.assertEqual(Humanize.typing_pause({'typing_pause_chance': 0}), 0.0)

    def test_typing_pause_when_certain(self):
        cfg = {'typing_pause_chance': 1.0, 'typing_pause_range': [0.1, 0.2]}
        for _ in range(20):
            pause = Humanize.typing_pause(cfg)
            self.assertGreaterEqual(pause, 0.1)
            self.assertLessEqual(pause, 0.2)


class TestAdvancedSpec(unittest.TestCase):
    def test_from_meta_parses_advanced_fields(self):
        spec = SessionSpec.from_meta({
            'browser': 'chrome',
            'stealth': True,
            'fingerprint': {'platform': 'Win32'},
            'timezone': 'UTC',
            'locale': 'en-US',
            'geolocation': {'latitude': 1.0, 'longitude': 2.0},
            'accept_language': 'en-US,en',
            'humanize': {'min_delay': 0.5},
            'profiles': ['/p/a', '/p/b'],
            'profile_strategy': 'random',
            'proxy_user': 'u',
            'proxy_pass': 'p',
            'network_block': ['*.gif'],
        })
        self.assertTrue(spec.stealth)
        self.assertEqual(spec.fingerprint, {'platform': 'Win32'})
        self.assertEqual(spec.timezone, 'UTC')
        self.assertEqual(spec.geolocation['latitude'], 1.0)
        self.assertEqual(spec.humanize, {'min_delay': 0.5})
        self.assertEqual(spec.profiles, ['/p/a', '/p/b'])
        self.assertTrue(spec.bidi)  # se auto-habilita con proxy_user

    def test_humanize_bool_true_becomes_empty_dict(self):
        spec = SessionSpec.from_meta({'browser': 'chrome', 'humanize': True})
        self.assertEqual(spec.humanize, {})

    def test_humanize_absent_is_none(self):
        spec = SessionSpec.from_meta({'browser': 'chrome'})
        self.assertIsNone(spec.humanize)

    def test_apply_bidi_capability(self):
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        spec = SessionSpec.from_meta({'browser': 'firefox', 'bidi': True})
        options = FirefoxOptions()
        BrowserFactory._apply_bidi(options, spec, 'T')
        self.assertTrue(options.capabilities['webSocketUrl'])

    def test_apply_bidi_auto_enabled_for_firefox_stealth(self):
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        spec = SessionSpec.from_meta({'browser': 'firefox', 'stealth': True})
        self.assertFalse(spec.bidi)
        options = FirefoxOptions()
        BrowserFactory._apply_bidi(options, spec, 'T', 'firefox')
        self.assertTrue(options.capabilities['webSocketUrl'])

    def test_apply_bidi_not_forced_for_chrome_stealth(self):
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        spec = SessionSpec.from_meta({'browser': 'chrome', 'stealth': True})
        options = ChromeOptions()
        BrowserFactory._apply_bidi(options, spec, 'T', 'chrome')
        self.assertNotIn('webSocketUrl', options.capabilities)

    def test_normalize_accept_languages_strips_qvalues(self):
        self.assertEqual(
            BrowserFactory._normalize_accept_languages('es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7'),
            'es-AR,es,en-US,en',
        )
        self.assertEqual(BrowserFactory._normalize_accept_languages('es-AR'), 'es-AR')
        self.assertEqual(BrowserFactory._normalize_accept_languages(' es , en '), 'es,en')

    def test_humanized_window(self):
        spec = SessionSpec.from_meta({
            'browser': 'firefox',
            'humanize': {'window_width_range': [800, 900], 'window_height_range': [600, 700]},
        })
        driver = Mock()
        BrowserFactory._apply_humanized_window(driver, spec, 'T')
        width, height = driver.set_window_size.call_args[0]
        self.assertTrue(800 <= width <= 900)
        self.assertTrue(600 <= height <= 700)

    def test_humanized_window_noop(self):
        spec = SessionSpec.from_meta({'browser': 'firefox'})
        driver = Mock()
        BrowserFactory._apply_humanized_window(driver, spec, 'T')
        driver.set_window_size.assert_not_called()

    def test_effective_profile_strategies(self):
        self.assertEqual(BrowserFactory._effective_profile(SessionSpec.from_meta({'profiles': ['a', 'b']})), 'a')
        random_spec = SessionSpec.from_meta({'profiles': ['a', 'b'], 'profile_strategy': 'random'})
        self.assertIn(BrowserFactory._effective_profile(random_spec), ['a', 'b'])
        rr_spec = SessionSpec.from_meta({'profiles': ['a', 'b'], 'profile_strategy': 'round_robin'})
        picks = {BrowserFactory._effective_profile(rr_spec) for _ in range(4)}
        self.assertEqual(picks, {'a', 'b'})
        self.assertEqual(BrowserFactory._effective_profile(SessionSpec.from_meta({'profile': 'x', 'profiles': ['a']})), 'x')


class TestUnifiedSyntax(unittest.TestCase):
    def test_driver_alias_string(self):
        spec = SessionSpec.from_meta({'driver': 'Firefox'})
        self.assertEqual(spec.browser, 'firefox')

    def test_identity_nesting(self):
        spec = SessionSpec.from_meta({'driver': 'firefox', 'identity': {
            'profile': '/p', 'user_agent': 'UA', 'accept_language': 'es',
            'timezone': 'UTC', 'locale': 'es-AR',
            'geolocation': {'latitude': 1, 'longitude': 2}, 'binary': '/bin/ff',
        }})
        self.assertEqual(spec.profile, '/p')
        self.assertEqual(spec.user_agent, 'UA')
        self.assertEqual(spec.accept_language, 'es')
        self.assertEqual(spec.timezone, 'UTC')
        self.assertEqual(spec.locale, 'es-AR')
        self.assertEqual(spec.geolocation, {'latitude': 1, 'longitude': 2})
        self.assertEqual(spec.binary, '/bin/ff')

    def test_downloads_nesting(self):
        spec = SessionSpec.from_meta({'driver': 'chrome', 'downloads': {'enabled': True, 'dir': '/tmp/dl'}})
        self.assertTrue(spec.downloads)
        self.assertEqual(spec.download_dir, '/tmp/dl')
        self.assertTrue(SessionSpec.from_meta({'driver': 'chrome', 'downloads': {'dir': '/tmp/dl'}}).downloads)
        self.assertTrue(SessionSpec.from_meta({'driver': 'chrome', 'downloads': True}).downloads)

    def test_network_nesting(self):
        spec = SessionSpec.from_meta({'driver': 'firefox', 'network': {'block': ['*.png'], 'headers': {'X-A': '1'}}})
        self.assertEqual(spec.network_block, ['*.png'])
        self.assertEqual(spec.network_headers, {'X-A': '1'})
        self.assertTrue(spec.bidi)

    def test_proxy_dict(self):
        spec = SessionSpec.from_meta({'driver': 'chrome', 'identity': {
            'proxy': {'server': 'http://p:8080', 'username': 'u', 'password': 'pw'},
        }})
        self.assertEqual(spec.proxy, 'http://p:8080')
        self.assertEqual(spec.proxy_user, 'u')
        self.assertEqual(spec.proxy_pass, 'pw')
        self.assertTrue(spec.bidi)

    def test_proxy_dict_host_port(self):
        spec = SessionSpec.from_meta({'driver': 'chrome', 'proxy': {'host': 'p', 'port': 8080, 'scheme': 'socks5'}})
        self.assertEqual(spec.proxy, 'socks5://p:8080')

    def test_overrides_merge(self):
        spec = SessionSpec.from_meta({
            'driver': 'chrome',
            'options': ['--a'],
            'prefs': {'x': 1},
            'overrides': {
                'chrome': {'options': ['--b'], 'prefs': {'y': 2}, 'exclude_switches': ['enable-automation']},
                'firefox': {'options': ['--ignored']},
            },
        })
        self.assertEqual(spec.options, ['--a', '--b'])
        self.assertEqual(spec.prefs, {'x': 1, 'y': 2})
        self.assertEqual(spec.exclude_switches, ['enable-automation'])

    def test_overrides_not_applied_for_other_driver(self):
        spec = SessionSpec.from_meta({'driver': 'firefox', 'overrides': {'chrome': {'options': ['--b']}}})
        self.assertEqual(spec.options, [])

    def test_on_unsupported(self):
        self.assertEqual(SessionSpec.from_meta({'driver': 'firefox', 'on_unsupported': 'error'}).on_unsupported, 'error')

    def test_legacy_driver_dict(self):
        spec = SessionSpec.from_meta({'browser': 'firefox', 'driver': {'bin': '/x/gecko'}})
        self.assertEqual(spec.browser, 'firefox')
        self.assertEqual(spec.driver_path, '/x/gecko')


class TestSupport(unittest.TestCase):
    def test_warn_does_not_raise(self):
        from session.Support import unsupported
        unsupported(SessionSpec.from_meta({'on_unsupported': 'warn'}), 'T', 'msg')

    def test_ignore_does_not_raise(self):
        from session.Support import unsupported
        unsupported(SessionSpec.from_meta({'on_unsupported': 'ignore'}), 'T', 'msg')

    def test_error_raises(self):
        from session.Support import unsupported
        with self.assertRaises(ValueError):
            unsupported(SessionSpec.from_meta({'on_unsupported': 'error'}), 'T', 'msg')

    def test_none_spec_defaults_to_warn(self):
        from session.Support import unsupported
        unsupported(None, 'T', 'msg')

    def test_on_unsupported_error_raises_in_factory(self):
        spec = SessionSpec.from_meta({'driver': 'firefox', 'exclude_switches': ['x'], 'on_unsupported': 'error'})
        with self.assertRaises(ValueError):
            BrowserFactory._apply_chromium_options(Mock(), spec, 'firefox', 'T')


if __name__ == '__main__':
    unittest.main()
