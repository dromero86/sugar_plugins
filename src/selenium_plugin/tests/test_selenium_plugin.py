"""
Test Suite para Selenium Plugin v2.0
===================================

Pruebas unitarias completas para el plugin Selenium v2.0.
Cubre todos los operadores, navegadores y funcionalidades.
"""

import unittest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Importar el plugin
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from SeleniumPlugin import SeleniumPlugin

class TestSeleniumPlugin(unittest.TestCase):
    """Suite de pruebas para SeleniumPlugin v2.0."""
    
    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.plugin = SeleniumPlugin()
        self.plugin.context = Mock()
        self.plugin.context.meta = {
            'browser': 'chrome',
            'headless': True,
            'timeout': 10,
            'implicit_wait': 5
        }
        
        # Mock del driver
        self.mock_driver = Mock()
        self.plugin.driver = self.mock_driver
        
    def tearDown(self):
        """Limpieza después de cada prueba."""
        if hasattr(self.plugin, 'driver') and self.plugin.driver:
            self.plugin.cleanup()
    
    def test_plugin_initialization(self):
        """Prueba la inicialización del plugin."""
        self.assertEqual(self.plugin.VERSION, "2.0.0")
        self.assertEqual(self.plugin.DESCRIPTION, "Plugin Selenium para Sugar con sintaxis @selenium/")
        self.assertEqual(self.plugin.AUTHOR, "Sugar Team")
        self.assertEqual(self.plugin.LICENSE, "MIT")
        self.assertIn("selenium>=4.0.0", self.plugin.DEPENDENCIES)
        self.assertIn("webdriver-manager>=3.8.0", self.plugin.DEPENDENCIES)
    
    def test_supported_browsers(self):
        """Prueba que todos los navegadores soportados estén definidos."""
        expected_browsers = ['chrome', 'firefox', 'edge', 'safari', 'opera', 'ie']
        
        for browser in expected_browsers:
            self.assertIn(browser, self.plugin.SUPPORTED_BROWSERS)
            browser_config = self.plugin.SUPPORTED_BROWSERS[browser]
            self.assertIn('name', browser_config)
            self.assertIn('service', browser_config)
            self.assertIn('options', browser_config)
            self.assertIn('driver_manager', browser_config)
    
    def test_execute_invalid_operator(self):
        """Prueba ejecución con operador inválido."""
        config = {'selenium': {'operator': 'invalid_operator'}}
        
        result = self.plugin.execute('selenium', config)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('Comando no soportado', result['error'])
    
    def test_execute_missing_operator(self):
        """Prueba ejecución sin operador."""
        config = {'selenium': {}}
        
        result = self.plugin.execute('selenium', config)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('Operador', result['error'])
    
    def test_execute_click(self):
        """Prueba el operador click."""
        # Mock del elemento
        mock_element = Mock()
        self.mock_driver.find_element.return_value = mock_element
        
        config = {
            'selenium': {
                'operator': 'click',
                'selector': '#btn',
                'result': 'is_clicked'
            }
        }
        
        result = self.plugin.execute('selenium', config)
        
        self.assertTrue(result['success'])
        self.assertTrue(result['is_clicked'])
        mock_element.click.assert_called_once()
    
    def test_execute_click_missing_selector(self):
        """Prueba click sin selector."""
        config = {
            'selenium': {
                'operator': 'click',
                'result': 'is_clicked'
            }
        }
        
        result = self.plugin.execute('selenium', config)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('Selector requerido', result['error'])
    
    def test_execute_open(self):
        """Prueba el operador open."""
        config = {
            'selenium': {
                'operator': 'open',
                'url': 'https://example.com',
                'result': 'is_open'
            }
        }
        
        result = self.plugin.execute('selenium', config)
        
        self.assertTrue(result['success'])
        self.assertTrue(result['is_open'])
        self.assertEqual(result['url'], 'https://example.com')
        self.mock_driver.get.assert_called_once_with('https://example.com')
    
    def test_execute_open_missing_url(self):
        """Prueba open sin URL."""
        config = {
            'selenium': {
                'operator': 'open',
                'result': 'is_open'
            }
        }
        
        result = self.plugin.execute('selenium', config)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('URL requerida', result['error'])
    
    def test_execute_javascript_from_string(self):
        """Prueba el operador javascript con string."""
        self.mock_driver.execute_script.return_value = "test result"
        
        config = {
            'selenium': {
                'operator': 'javascript',
                'from_string': 'return "test result";',
                'result': 'js_result'
            }
        }
        
        result = self.plugin.execute('selenium', config)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['js_result'], "test result")
        self.mock_driver.execute_script.assert_called_once_with('return "test result";')
    
    def test_execute_javascript_from_file(self):
        """Prueba el operador javascript con archivo."""
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write('return "test from file";')
            temp_file = f.name
        
        try:
            self.mock_driver.execute_script.return_value = "test from file"
            
            config = {
                'selenium': {
                    'operator': 'javascript',
                    'from_file': temp_file,
                    'result': 'js_result'
                }
            }
            
            result = self.plugin.execute('selenium', config)
            
            self.assertTrue(result['success'])
            self.assertEqual(result['js_result'], "test from file")
            self.mock_driver.execute_script.assert_called_once_with('return "test from file";')
            
        finally:
            os.unlink(temp_file)
    
    def test_execute_type(self):
        """Prueba el operador type."""
        mock_element = Mock()
        self.mock_driver.find_element.return_value = mock_element
        
        config = {
            'selenium': {
                'operator': 'type',
                'selector': 'input[name="q"]',
                'value': 'test text',
                'result': 'is_typed'
            }
        }
        
        result = self.plugin.execute('selenium', config)
        
        self.assertTrue(result['success'])
        self.assertTrue(result['is_typed'])
        self.assertEqual(result['value'], 'test text')
        mock_element.clear.assert_called_once()
        mock_element.send_keys.assert_called_once_with('test text')
    
    def test_execute_type_with_enter(self):
        """Prueba el operador type con enter."""
        mock_element = Mock()
        self.mock_driver.find_element.return_value = mock_element
        
        config = {
            'selenium': {
                'operator': 'type',
                'selector': 'input[name="q"]',
                'value': 'test text',
                'enter': True,
                'result': 'is_typed'
            }
        }
        
        result = self.plugin.execute('selenium', config)
        
        self.assertTrue(result['success'])
        mock_element.send_keys.assert_has_calls([
            unittest.mock.call('test text'),
            unittest.mock.call(unittest.mock.ANY)  # Keys.RETURN
        ])
    
    def test_execute_wait_time(self):
        """Prueba el operador wait con tiempo."""
        config = {
            'selenium': {
                'operator': 'wait',
                'type': 'time',
                'seconds': 2,
                'result': 'is_waited'
            }
        }
        
        result = self.plugin.execute('selenium', config)
        
        self.assertTrue(result['success'])
        self.assertTrue(result['is_waited'])
        self.assertEqual(result['seconds'], 2)
    
    def test_execute_wait_element(self):
        """Prueba el operador wait con elemento."""
        mock_element = Mock()
        mock_wait = Mock()
        mock_wait.until.return_value = mock_element
        
        with patch('selenium.webdriver.support.ui.WebDriverWait', return_value=mock_wait):
            config = {
                'selenium': {
                    'operator': 'wait',
                    'type': 'element',
                    'selector': '#content',
                    'result': 'element_found'
                }
            }
            
            result = self.plugin.execute('selenium', config)
            
            self.assertTrue(result['success'])
            self.assertTrue(result['element_found'])
    
    def test_execute_screenshot(self):
        """Prueba el operador screenshot."""
        config = {
            'selenium': {
                'operator': 'screenshot',
                'file': './test_screenshot.png',
                'result': 'screenshot'
            }
        }
        
        result = self.plugin.execute('selenium', config)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['screenshot'], './test_screenshot.png')
        self.mock_driver.save_screenshot.assert_called_once_with('./test_screenshot.png')
    
    def test_execute_navigate(self):
        """Prueba el operador navigate."""
        config = {
            'selenium': {
                'operator': 'navigate',
                'action': 'refresh',
                'result': 'navigated'
            }
        }
        
        result = self.plugin.execute('selenium', config)
        
        self.assertTrue(result['success'])
        self.assertTrue(result['navigated'])
        self.assertEqual(result['action'], 'refresh')
        self.mock_driver.refresh.assert_called_once()
    
    def test_execute_find_single(self):
        """Prueba el operador find para un elemento."""
        mock_element = Mock()
        mock_element.text = "Test Element"
        mock_element.tag_name = "div"
        self.mock_driver.find_element.return_value = mock_element
        
        config = {
            'selenium': {
                'operator': 'find',
                'selector': '.test-element',
                'result': 'found'
            }
        }
        
        result = self.plugin.execute('selenium', config)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['found']['text'], "Test Element")
        self.assertEqual(result['found']['tag'], "div")
    
    def test_execute_find_multiple(self):
        """Prueba el operador find para múltiples elementos."""
        mock_elements = [
            Mock(text="Element 1", tag_name="div"),
            Mock(text="Element 2", tag_name="span")
        ]
        self.mock_driver.find_elements.return_value = mock_elements
        
        config = {
            'selenium': {
                'operator': 'find',
                'selector': '.test-elements',
                'multiple': True,
                'result': 'found'
            }
        }
        
        result = self.plugin.execute('selenium', config)
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['found']), 2)
        self.assertEqual(result['found'][0]['text'], "Element 1")
        self.assertEqual(result['found'][1]['text'], "Element 2")
    
    def test_execute_cookies_get(self):
        """Prueba el operador cookies get."""
        mock_cookies = [
            {'name': 'session_id', 'value': 'abc123'},
            {'name': 'user_id', 'value': '456'}
        ]
        self.mock_driver.get_cookies.return_value = mock_cookies
        
        config = {
            'selenium': {
                'operator': 'cookies',
                'action': 'get',
                'result': 'cookies'
            }
        }
        
        result = self.plugin.execute('selenium', config)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['cookies'], mock_cookies)
        self.mock_driver.get_cookies.assert_called_once()
    
    def test_execute_cookies_add_single(self):
        """Prueba el operador cookies add con cookie individual."""
        config = {
            'selenium': {
                'operator': 'cookies',
                'action': 'add',
                'name': 'session_id',
                'value': 'abc123',
                'domain': '.example.com',
                'result': 'cookie_added'
            }
        }
        
        result = self.plugin.execute('selenium', config)
        
        self.assertTrue(result['success'])
        self.assertTrue(result['cookie_added'])
        self.mock_driver.add_cookie.assert_called_once()
    
    def test_execute_cookies_add_array(self):
        """Prueba el operador cookies con array de cookies."""
        config = {
            'selenium': {
                'operator': 'cookies',
                'action': 'add',
                'cookies': [
                    {'name': 'cookie1', 'value': 'value1'},
                    {'name': 'cookie2', 'value': 'value2'}
                ],
                'result': 'cookies_added'
            }
        }
        
        result = self.plugin.execute('selenium', config)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['cookies_added'], 2)
        self.assertEqual(self.mock_driver.add_cookie.call_count, 2)
    
    def test_execute_cookies_delete(self):
        """Prueba el operador cookies delete."""
        config = {
            'selenium': {
                'operator': 'cookies',
                'action': 'delete',
                'name': 'session_id',
                'result': 'cookie_deleted'
            }
        }
        
        result = self.plugin.execute('selenium', config)
        
        self.assertTrue(result['success'])
        self.assertTrue(result['cookie_deleted'])
        self.mock_driver.delete_cookie.assert_called_once_with('session_id')
    
    def test_execute_cookies_clear(self):
        """Prueba el operador cookies clear."""
        config = {
            'selenium': {
                'operator': 'cookies',
                'action': 'clear',
                'result': 'cookies_cleared'
            }
        }
        
        result = self.plugin.execute('selenium', config)
        
        self.assertTrue(result['success'])
        self.assertTrue(result['cookies_cleared'])
        self.mock_driver.delete_all_cookies.assert_called_once()
    
    def test_execute_cookies_get_by_name(self):
        """Prueba el operador cookies get_by_name."""
        mock_cookie = {'name': 'session_id', 'value': 'abc123'}
        self.mock_driver.get_cookie.return_value = mock_cookie
        
        config = {
            'selenium': {
                'operator': 'cookies',
                'action': 'get_by_name',
                'name': 'session_id',
                'result': 'cookie_by_name'
            }
        }
        
        result = self.plugin.execute('selenium', config)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['cookie_by_name'], mock_cookie)
        self.mock_driver.get_cookie.assert_called_once_with('session_id')
    
    def test_execute_cookies_get_by_domain(self):
        """Prueba el operador cookies get_by_domain."""
        all_cookies = [
            {'name': 'session_id', 'value': 'abc123', 'domain': '.example.com'},
            {'name': 'other_cookie', 'value': 'xyz', 'domain': '.other.com'}
        ]
        self.mock_driver.get_cookies.return_value = all_cookies
        
        config = {
            'selenium': {
                'operator': 'cookies',
                'action': 'get_by_domain',
                'domain': '.example.com',
                'result': 'cookies_by_domain'
            }
        }
        
        result = self.plugin.execute('selenium', config)
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['cookies_by_domain']), 1)
        self.assertEqual(result['cookies_by_domain'][0]['name'], 'session_id')
    
    def test_build_cookie_dict(self):
        """Prueba la construcción de diccionarios de cookies."""
        cookie_data = {
            'name': 'test_cookie',
            'value': 'test_value',
            'domain': '.example.com',
            'path': '/test',
            'secure': True,
            'httpOnly': False
        }
        
        result = self.plugin._build_cookie_dict(cookie_data)
        
        self.assertEqual(result['name'], 'test_cookie')
        self.assertEqual(result['value'], 'test_value')
        self.assertEqual(result['domain'], '.example.com')
        self.assertEqual(result['path'], '/test')
        self.assertTrue(result['secure'])
        self.assertFalse(result['httpOnly'])
    
    def test_build_cookie_dict_with_expiry_string(self):
        """Prueba la construcción de cookies con fecha de caducidad string."""
        cookie_data = {
            'name': 'test_cookie',
            'value': 'test_value',
            'expiry': '2024-12-31T23:59:59Z'
        }
        
        result = self.plugin._build_cookie_dict(cookie_data)
        
        self.assertEqual(result['name'], 'test_cookie')
        self.assertEqual(result['value'], 'test_value')
        self.assertIn('expiry', result)
    
    def test_build_cookie_dict_with_expiry_timestamp(self):
        """Prueba la construcción de cookies con fecha de caducidad timestamp."""
        cookie_data = {
            'name': 'test_cookie',
            'value': 'test_value',
            'expiry': 1735689599
        }
        
        result = self.plugin._build_cookie_dict(cookie_data)
        
        self.assertEqual(result['name'], 'test_cookie')
        self.assertEqual(result['value'], 'test_value')
        self.assertEqual(result['expiry'], 1735689599)
    
    def test_find_element_success(self):
        """Prueba la búsqueda exitosa de elementos."""
        mock_element = Mock()
        self.mock_driver.find_element.return_value = mock_element
        
        result = self.plugin._find_element('#test')
        
        self.assertEqual(result, mock_element)
        self.mock_driver.find_element.assert_called_once()
    
    def test_find_element_not_found(self):
        """Prueba la búsqueda de elementos no encontrados."""
        from selenium.common.exceptions import NoSuchElementException
        
        self.mock_driver.find_element.side_effect = NoSuchElementException("Element not found")
        
        with self.assertRaises(ValueError) as context:
            self.plugin._find_element('#test')
        
        self.assertIn('Elemento no encontrado', str(context.exception))
    
    def test_cleanup(self):
        """Prueba la limpieza del plugin."""
        self.plugin.cleanup()
        
        self.mock_driver.quit.assert_called_once()
        self.assertIsNone(self.plugin.driver)
    
    def test_cleanup_with_exception(self):
        """Prueba la limpieza del plugin con excepción."""
        self.mock_driver.quit.side_effect = Exception("Quit failed")
        
        # No debe lanzar excepción
        self.plugin.cleanup()
        
        self.assertIsNone(self.plugin.driver)

class TestSeleniumPluginBrowsers(unittest.TestCase):
    """Pruebas específicas para diferentes navegadores."""
    
    def setUp(self):
        """Configuración inicial."""
        self.plugin = SeleniumPlugin()
    
    def test_chrome_configuration(self):
        """Prueba la configuración de Chrome."""
        browser_config = self.plugin.SUPPORTED_BROWSERS['chrome']
        
        self.assertEqual(browser_config['name'], 'Chrome')
        self.assertTrue(browser_config['headless_support'])
        self.assertTrue(browser_config['detach_support'])
        self.assertIn('linux', browser_config['platforms'])
        self.assertIn('windows', browser_config['platforms'])
        self.assertIn('macos', browser_config['platforms'])
    
    def test_firefox_configuration(self):
        """Prueba la configuración de Firefox."""
        browser_config = self.plugin.SUPPORTED_BROWSERS['firefox']
        
        self.assertEqual(browser_config['name'], 'Firefox')
        self.assertTrue(browser_config['headless_support'])
        self.assertFalse(browser_config['detach_support'])
        self.assertIn('linux', browser_config['platforms'])
        self.assertIn('windows', browser_config['platforms'])
        self.assertIn('macos', browser_config['platforms'])
    
    def test_safari_configuration(self):
        """Prueba la configuración de Safari."""
        browser_config = self.plugin.SUPPORTED_BROWSERS['safari']
        
        self.assertEqual(browser_config['name'], 'Safari')
        self.assertFalse(browser_config['headless_support'])
        self.assertFalse(browser_config['detach_support'])
        self.assertEqual(browser_config['platforms'], ['macos'])
    
    def test_edge_configuration(self):
        """Prueba la configuración de Edge."""
        browser_config = self.plugin.SUPPORTED_BROWSERS['edge']
        
        self.assertEqual(browser_config['name'], 'Edge')
        self.assertTrue(browser_config['headless_support'])
        self.assertTrue(browser_config['detach_support'])
        self.assertIn('linux', browser_config['platforms'])
        self.assertIn('windows', browser_config['platforms'])
        self.assertIn('macos', browser_config['platforms'])
    
    def test_opera_configuration(self):
        """Prueba la configuración de Opera."""
        browser_config = self.plugin.SUPPORTED_BROWSERS['opera']
        
        self.assertEqual(browser_config['name'], 'Opera')
        self.assertTrue(browser_config['headless_support'])
        self.assertTrue(browser_config['detach_support'])
        self.assertIn('linux', browser_config['platforms'])
        self.assertIn('windows', browser_config['platforms'])
        self.assertIn('macos', browser_config['platforms'])
    
    def test_ie_configuration(self):
        """Prueba la configuración de Internet Explorer."""
        browser_config = self.plugin.SUPPORTED_BROWSERS['ie']
        
        self.assertEqual(browser_config['name'], 'Internet Explorer')
        self.assertFalse(browser_config['headless_support'])
        self.assertFalse(browser_config['detach_support'])
        self.assertEqual(browser_config['platforms'], ['windows'])

if __name__ == '__main__':
    # Ejecutar las pruebas
    unittest.main(verbosity=2)
