"""
Tests de operadores extendidos (cobertura Selenium)
===================================================

Verifican dispatch y comportamiento de los operadores agregados:
timeouts, actions, element, shadow, cdp, network, capabilities y las
extensiones de wait/screenshot/javascript/alert/select/window/frame.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from session.BrowserSession import BrowserSession


class PlainDriver:
    """Driver sin APIs Chromium, para probar los errores de CDP/network."""


class TestExtendedOperators(unittest.TestCase):
    def setUp(self):
        self.session = BrowserSession(plugin_name='T')
        self.driver = Mock()
        self.session.driver = self.driver

    def test_timeouts(self):
        result = self.session.execute_command('timeouts', {'page_load': 30, 'script': 20, 'implicit': 3})
        self.assertTrue(result['success'])
        self.driver.set_page_load_timeout.assert_called_once_with(30)
        self.driver.set_script_timeout.assert_called_once_with(20)
        self.driver.implicitly_wait.assert_called_once_with(3)
        self.assertEqual(self.session.implicit_wait, 3)

    def test_actions_sequence(self):
        element = Mock()
        self.driver.find_element.return_value = element
        with patch('session.BrowserSession.ActionChains') as chains_cls:
            chains = chains_cls.return_value
            result = self.session.execute_command('actions', {
                'sequence': [
                    {'type': 'move_to_element', 'selector': '#a'},
                    {'type': 'click_and_hold'},
                    {'type': 'move_by_offset', 'x': 10, 'y': 0},
                    {'type': 'release'},
                ],
                'id': 'act',
            })
        chains_cls.assert_called_once_with(self.driver)
        chains.move_to_element.assert_called_once_with(element)
        chains.click_and_hold.assert_called_once_with(None)
        chains.move_by_offset.assert_called_once_with(10, 0)
        chains.release.assert_called_once_with(None)
        chains.perform.assert_called_once()
        self.assertTrue(result['act'])

    def test_actions_unknown_step(self):
        result = self.session.execute_command('actions', {'sequence': [{'type': 'nope'}]})
        self.assertFalse(result['success'])

    def test_actions_send_keys_to_element(self):
        element = Mock()
        self.driver.find_element.return_value = element
        with patch('session.BrowserSession.ActionChains') as chains_cls:
            chains = chains_cls.return_value
            self.session.execute_command('actions', {'sequence': [{'type': 'send_keys', 'keys': 'hola', 'selector': '#i'}]})
        chains.send_keys_to_element.assert_called_once_with(element, 'hola')

    def test_actions_scroll_from_origin(self):
        with patch('session.BrowserSession.ActionChains') as chains_cls, \
             patch('session.BrowserSession.ScrollOrigin') as scroll_origin:
            chains = chains_cls.return_value
            self.session.execute_command('actions', {'sequence': [{'type': 'scroll_from_origin', 'x': 0, 'y': 100}]})
        scroll_origin.from_viewport.assert_called_once()
        chains.scroll_from_origin.assert_called_once()

    def test_element_property(self):
        element = Mock()
        element.get_property.return_value = 'val'
        self.driver.find_element.return_value = element
        result = self.session.execute_command('element', {'action': 'property', 'selector': '#a', 'name': 'x', 'id': 'p'})
        self.assertEqual(result['p'], 'val')

    def test_element_css(self):
        element = Mock()
        element.value_of_css_property.return_value = 'red'
        self.driver.find_element.return_value = element
        result = self.session.execute_command('element', {'action': 'css', 'selector': '#a', 'name': 'color'})
        self.assertEqual(result['css'], 'red')

    def test_element_active(self):
        element = Mock()
        element.tag_name = 'body'
        element.text = 'contenido'
        self.driver.switch_to.active_element = element
        result = self.session.execute_command('element', {'action': 'active', 'id': 't'})
        self.assertEqual(result['t']['tag'], 'body')

    def test_shadow(self):
        inner = Mock()
        inner.text = 'hola'
        inner.tag_name = 'span'
        root = Mock()
        root.find_element.return_value = inner
        host = Mock()
        host.shadow_root = root
        self.driver.find_element.return_value = host
        result = self.session.execute_command('shadow', {'host': '#h', 'selector': '.i', 'id': 's'})
        self.assertEqual(result['s']['text'], 'hola')

    def test_cdp(self):
        self.driver.name = 'chrome'
        self.driver.execute_cdp_cmd.return_value = {'ok': 1}
        result = self.session.execute_command('cdp', {'command': 'Page.enable', 'id': 'c'})
        self.assertEqual(result['c'], {'ok': 1})

    def test_cdp_unsupported(self):
        self.session.driver = PlainDriver()
        result = self.session.execute_command('cdp', {'command': 'Page.enable'})
        self.assertFalse(result['success'])
        self.assertIn('Chromium', result['error'])

    def test_network_set(self):
        self.driver.name = 'chrome'
        result = self.session.execute_command('network', {'action': 'set', 'offline': True, 'latency': 100, 'id': 'n'})
        self.assertTrue(result['n'])
        self.driver.set_network_conditions.assert_called_once_with(offline=True, latency=100)

    def test_network_unsupported(self):
        self.session.driver = PlainDriver()
        result = self.session.execute_command('network', {'action': 'get'})
        self.assertFalse(result['success'])

    def test_capabilities(self):
        self.driver.name = 'firefox'
        self.driver.capabilities = {'browserName': 'firefox'}
        result = self.session.execute_command('capabilities', {'id': 'cap'})
        self.assertEqual(result['cap']['browserName'], 'firefox')

    def test_wait_text_present(self):
        with patch('session.BrowserSession.EC') as ec, patch('session.BrowserSession.WebDriverWait') as wait_cls:
            wait_cls.return_value.until.return_value = True
            result = self.session.execute_command('wait', {'type': 'text_present', 'selector': '#a', 'text': 'x'})
        ec.text_to_be_present_in_element.assert_called_once()
        self.assertTrue(result['success'])

    def test_wait_alert_present(self):
        with patch('session.BrowserSession.EC') as ec, patch('session.BrowserSession.WebDriverWait') as wait_cls:
            wait_cls.return_value.until.return_value = True
            result = self.session.execute_command('wait', {'type': 'alert_present'})
        ec.alert_is_present.assert_called_once()
        self.assertTrue(result['success'])

    def test_window_handles(self):
        self.driver.window_handles = ['h1', 'h2']
        result = self.session.execute_command('window', {'action': 'handles', 'id': 'w'})
        self.assertEqual(result['w'], ['h1', 'h2'])

    def test_window_set_rect(self):
        self.session.execute_command('window', {'action': 'set_rect', 'x': 0, 'y': 0, 'width': 800, 'height': 600})
        self.driver.set_window_rect.assert_called_once_with(x=0, y=0, width=800, height=600)

    def test_window_new_tab(self):
        self.session.execute_command('window', {'action': 'new', 'type': 'tab'})
        self.driver.switch_to.new_window.assert_called_once_with('tab')

    def test_frame_parent(self):
        self.session.execute_command('frame', {'action': 'parent'})
        self.driver.switch_to.parent_frame.assert_called_once()

    def test_select_options(self):
        element = Mock()
        self.driver.find_element.return_value = element
        select = Mock()
        select.options = [Mock(text='A'), Mock(text='B')]
        with patch('session.BrowserSession.Select', return_value=select):
            result = self.session.execute_command('select', {'selector': '#s', 'action': 'options'})
        self.assertEqual(result['selected'], ['A', 'B'])

    def test_select_deselect_all(self):
        element = Mock()
        self.driver.find_element.return_value = element
        select = Mock()
        with patch('session.BrowserSession.Select', return_value=select):
            result = self.session.execute_command('select', {'selector': '#s', 'action': 'deselect_all'})
        select.deselect_all.assert_called_once()
        self.assertTrue(result['success'])

    def test_alert_text(self):
        alert = Mock()
        alert.text = 'hola'
        self.driver.switch_to.alert = alert
        result = self.session.execute_command('alert', {'action': 'text', 'id': 'a'})
        self.assertEqual(result['a'], 'hola')

    def test_javascript_async(self):
        self.driver.execute_async_script.return_value = 42
        result = self.session.execute_command('javascript', {'from_string': 'done()', 'async': True, 'id': 'js'})
        self.assertEqual(result['js'], 42)
        self.driver.execute_async_script.assert_called_once_with('done()')

    def test_screenshot_base64(self):
        self.driver.get_screenshot_as_base64.return_value = 'AAAA'
        result = self.session.execute_command('screenshot', {'encoding': 'base64', 'id': 's'})
        self.assertEqual(result['s'], 'AAAA')

    def test_storage_state_export(self):
        self.driver.get_cookies.return_value = [{'name': 'a', 'value': 'b'}]
        self.driver.execute_script.return_value = {'k': 'v'}
        result = self.session.execute_command('storage_state', {'action': 'export', 'id': 'st'})
        self.assertEqual(result['st']['cookies'], [{'name': 'a', 'value': 'b'}])
        self.assertEqual(result['st']['localStorage'], {'k': 'v'})

    def test_storage_state_import(self):
        self.session.execute_command('storage_state', {
            'action': 'import',
            'state': {'cookies': [{'name': 'a', 'value': 'b'}], 'localStorage': {'k': 'v'}},
            'id': 'st',
        })
        self.driver.add_cookie.assert_called_once_with({'name': 'a', 'value': 'b'})
        self.driver.execute_script.assert_called()

    def test_challenge_detect_cloudflare(self):
        self.driver.title = 'Just a moment...'
        self.driver.page_source = '<html>cf-challenge</html>'
        result = self.session.execute_command('challenge', {'action': 'detect', 'id': 'c'})
        self.assertTrue(result['c']['detected'])
        self.assertEqual(result['c']['provider'], 'cloudflare')

    def test_challenge_not_detected(self):
        self.driver.title = 'Example'
        self.driver.page_source = '<html>ok</html>'
        result = self.session.execute_command('challenge', {'action': 'detect', 'id': 'c'})
        self.assertFalse(result['c']['detected'])

    def test_bidi_execute(self):
        self.driver.caps = {'webSocketUrl': 'ws://x'}
        self.driver.current_window_handle = 'ctx'
        self.driver.script.execute.return_value = 4
        result = self.session.execute_command('bidi', {'action': 'execute', 'function': '(a)=>a+2', 'args': [2], 'id': 'b'})
        self.assertEqual(result['b'], 4)
        self.driver.script.execute.assert_called_once_with('(a)=>a+2', 2)

    def test_bidi_not_enabled(self):
        self.driver.caps = {}
        result = self.session.execute_command('bidi', {'action': 'execute', 'function': '()=>1'})
        self.assertFalse(result['success'])
        self.assertIn('BiDi', result['error'])

    def test_bidi_block(self):
        self.driver.caps = {'webSocketUrl': 'ws://x'}
        result = self.session.execute_command('bidi', {'action': 'block', 'patterns': ['*.png'], 'id': 'b'})
        self.driver.network.add_request_handler.assert_called_once()
        self.assertTrue(result['b'])

    def test_bidi_add_auth(self):
        self.driver.caps = {'webSocketUrl': 'ws://x'}
        self.session.execute_command('bidi', {'action': 'add_auth', 'username': 'u', 'password': 'p', 'id': 'b'})
        self.driver.network.add_auth_handler.assert_called_once_with('u', 'p')

    def test_wait_url_to_be(self):
        with patch('session.BrowserSession.EC') as ec, patch('session.BrowserSession.WebDriverWait') as wait_cls:
            wait_cls.return_value.until.return_value = True
            result = self.session.execute_command('wait', {'type': 'url_to_be', 'url': 'https://x', 'id': 'w'})
        ec.url_to_be.assert_called_once_with('https://x')
        self.assertTrue(result['w'])

    def test_wait_all_of_combinator(self):
        with patch('session.BrowserSession.EC') as ec, patch('session.BrowserSession.WebDriverWait') as wait_cls:
            wait_cls.return_value.until.return_value = True
            result = self.session.execute_command('wait', {
                'type': 'all_of',
                'conditions': [
                    {'type': 'title_is', 'title': 'x'},
                    {'type': 'url_contains', 'url': 'y'},
                ],
                'id': 'w',
            })
        self.assertTrue(result['w'])
        ec.all_of.assert_called_once()

    def test_wait_visibility_all(self):
        with patch('session.BrowserSession.EC') as ec, patch('session.BrowserSession.WebDriverWait') as wait_cls:
            wait_cls.return_value.until.return_value = True
            self.session.execute_command('wait', {'type': 'visibility_of_all_elements_located', 'selector': '.x'})
        ec.visibility_of_all_elements_located.assert_called_once()

    def test_downloads_list(self):
        self.driver.capabilities = {'se:downloadsEnabled': True}
        self.driver.get_downloadable_files.return_value = ['a.zip']
        result = self.session.execute_command('downloads', {'action': 'list', 'id': 'd'})
        self.assertEqual(result['d'], ['a.zip'])

    def test_downloads_not_enabled(self):
        self.driver.capabilities = {}
        result = self.session.execute_command('downloads', {'action': 'list'})
        self.assertFalse(result['success'])
        self.assertIn('downloads', result['error'])

    def test_bidi_context_tree_serialized(self):
        self.driver.caps = {'webSocketUrl': 'ws://x'}
        info = type('Info', (), {})()
        info.context = 'c1'
        info.url = 'u'
        info.children = []
        self.driver.browsing_context.get_tree.return_value = [info]
        result = self.session.execute_command('bidi', {'action': 'context_tree', 'id': 'b'})
        self.assertEqual(result['b'][0]['context'], 'c1')

    def test_bidi_emulate_geolocation(self):
        self.driver.caps = {'webSocketUrl': 'ws://x'}
        self.driver.current_window_handle = 'ctx'
        self.session.execute_command('bidi', {'action': 'emulate_geolocation', 'latitude': 1.0, 'longitude': 2.0, 'id': 'b'})
        self.driver.emulation.set_geolocation_override.assert_called_once()

    def test_bidi_user_context_create(self):
        self.driver.caps = {'webSocketUrl': 'ws://x'}
        self.driver.browser.create_user_context.return_value = 'uc1'
        result = self.session.execute_command('bidi', {'action': 'user_context_create', 'id': 'b'})
        self.assertEqual(result['b'], 'uc1')

    def test_bidi_extension_install(self):
        self.driver.caps = {'webSocketUrl': 'ws://x'}
        self.driver.webextension.install.return_value = {'extension': 'id1'}
        result = self.session.execute_command('bidi', {'action': 'extension_install', 'path': '/x', 'id': 'b'})
        self.assertEqual(result['b'], {'extension': 'id1'})

    def test_bidi_pin(self):
        self.driver.caps = {'webSocketUrl': 'ws://x'}
        self.driver.script.pin.return_value = 'sid'
        result = self.session.execute_command('bidi', {'action': 'pin', 'script': 'x', 'id': 'b'})
        self.assertEqual(result['b'], 'sid')

    def test_bidi_input_keys(self):
        self.driver.caps = {'webSocketUrl': 'ws://x'}
        self.driver.current_window_handle = 'ctx'
        self.session.execute_command('bidi', {'action': 'input_keys', 'keys': 'ab', 'id': 'b'})
        self.driver.input.perform_actions.assert_called_once()

    def test_bidi_handle_prompt(self):
        self.driver.caps = {'webSocketUrl': 'ws://x'}
        self.driver.current_window_handle = 'ctx'
        self.session.execute_command('bidi', {'action': 'handle_prompt', 'accept': True, 'id': 'b'})
        self.driver.browsing_context.handle_user_prompt.assert_called_once_with('ctx', True, None)

    def test_find_within(self):
        container = Mock()
        child = Mock()
        child.text = 'x'
        child.tag_name = 'span'
        container.find_element.return_value = child
        self.driver.find_element.return_value = container
        result = self.session.execute_command('find', {'selector': '.c', 'within': '#box', 'id': 'f'})
        self.assertEqual(result['f']['tag'], 'span')
        container.find_element.assert_called_once()

    def test_element_parent(self):
        parent = Mock()
        parent.tag_name = 'div'
        parent.text = 'p'
        element = Mock()
        element.find_element.return_value = parent
        self.driver.find_element.return_value = element
        result = self.session.execute_command('element', {'action': 'parent', 'selector': '#a', 'id': 'p'})
        self.assertEqual(result['p']['tag'], 'div')

    def test_element_id(self):
        element = Mock()
        element.id = 'abc'
        self.driver.find_element.return_value = element
        result = self.session.execute_command('element', {'action': 'id', 'selector': '#a', 'id': 'e'})
        self.assertEqual(result['e'], 'abc')

    def test_element_scrolled_location(self):
        element = Mock()
        element.location_once_scrolled_into_view = {'x': 1, 'y': 2}
        self.driver.find_element.return_value = element
        result = self.session.execute_command('element', {'action': 'scrolled_location', 'selector': '#a', 'id': 'e'})
        self.assertEqual(result['e'], {'x': 1, 'y': 2})


if __name__ == '__main__':
    unittest.main()
