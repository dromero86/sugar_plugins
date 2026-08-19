"""
Test suite for ExtractTableSeleniumPlugin
=========================================

Tests the Selenium-based table extraction plugin functionality.
"""

import unittest
import unittest.mock
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import os

# Mock Selenium imports for testing
class MockWebDriver:
    def __init__(self):
        self.page_source = "<html><body><table><tr><th>Name</th><th>Age</th></tr><tr><td>John</td><td>30</td></tr></table></body></html>"
    
    def get(self, url):
        pass
    
    def find_element(self, by, selector):
        return MockTableElement()
    
    def quit(self):
        pass
    
    def implicitly_wait(self, time):
        pass
    
    def set_window_size(self, width, height):
        pass
    
    def execute_script(self, script, element):
        pass
    
    def save_screenshot(self, filename):
        pass

class MockTableElement:
    def find_elements(self, by, selector):
        if selector == "tbody tr":
            return [MockRowElement()]
        elif selector == "th, td":
            return [MockCellElement("Name"), MockCellElement("Age")]
        return []

class MockRowElement:
    def find_elements(self, by, selector):
        return [MockCellElement("John"), MockCellElement("30")]

class MockCellElement:
    def __init__(self, text):
        self.text = text
    
    def get_attribute(self, attr):
        return "1" if attr in ["colspan", "rowspan"] else None

class MockWebDriverWait:
    def __init__(self, driver, timeout):
        self.driver = driver
        self.timeout = timeout
    
    def until(self, condition):
        return True

# Import the plugin after mocking
import sys
sys.modules['selenium'] = Mock()
sys.modules['selenium.webdriver'] = Mock()
sys.modules['selenium.webdriver.common.by'] = Mock()
sys.modules['selenium.webdriver.support.ui'] = Mock()
sys.modules['selenium.webdriver.support'] = Mock()
sys.modules['selenium.webdriver.chrome.options'] = Mock()
sys.modules['selenium.webdriver.firefox.options'] = Mock()
sys.modules['selenium.webdriver.edge.options'] = Mock()
sys.modules['selenium.webdriver.common.action_chains'] = Mock()
sys.modules['selenium.common.exceptions'] = Mock()

from extract_table_selenium import ExtractTableSeleniumPlugin

class TestExtractTableSeleniumPlugin(unittest.TestCase):
    """Test cases for ExtractTableSeleniumPlugin."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.context = Mock()
        self.memory_handler = Mock()
        self.context.memory_handler = self.memory_handler
        
        # Mock plugin configuration
        self.plugin_config = {
            "browser": "chrome",
            "headless": True,
            "timeout": 30,
            "implicit_wait": 10
        }
        
        self.plugin = ExtractTableSeleniumPlugin(self.context, self.plugin_config)
    
    def test_plugin_initialization(self):
        """Test plugin initialization."""
        self.assertEqual(self.plugin.plugin_name, "ExtractTableSeleniumPlugin")
        self.assertEqual(self.plugin.VERSION, "1.0.0")
        self.assertEqual(self.plugin.DESCRIPTION, "Selenium-based HTML table extraction with advanced features")
        self.assertIn("selenium", self.plugin.DEPENDENCIES)
        self.assertIn("webdriver-manager", self.plugin.DEPENDENCIES)
    
    def test_get_available_commands(self):
        """Test available commands list."""
        commands = self.plugin.get_available_commands()
        expected_commands = [
            "extract_table", "navigate_to", "wait_for_element", 
            "scroll_to_element", "click_element", "get_page_source", 
            "take_screenshot", "close_browser"
        ]
        self.assertEqual(set(commands), set(expected_commands))
    
    @patch('extract_table_selenium.webdriver')
    def test_initialize_driver_chrome(self, mock_webdriver):
        """Test Chrome WebDriver initialization."""
        mock_webdriver.Chrome.return_value = MockWebDriver()
        
        result = self.plugin._initialize_driver()
        
        self.assertTrue(result)
        self.assertTrue(self.plugin.is_initialized)
        self.assertIsNotNone(self.plugin.driver)
        self.assertIsNotNone(self.plugin.wait)
    
    @patch('extract_table_selenium.webdriver')
    def test_initialize_driver_firefox(self, mock_webdriver):
        """Test Firefox WebDriver initialization."""
        self.plugin.browser_config["browser"] = "firefox"
        mock_webdriver.Firefox.return_value = MockWebDriver()
        
        result = self.plugin._initialize_driver()
        
        self.assertTrue(result)
        self.assertTrue(self.plugin.is_initialized)
    
    @patch('extract_table_selenium.webdriver')
    def test_initialize_driver_edge(self, mock_webdriver):
        """Test Edge WebDriver initialization."""
        self.plugin.browser_config["browser"] = "edge"
        mock_webdriver.Edge.return_value = MockWebDriver()
        
        result = self.plugin._initialize_driver()
        
        self.assertTrue(result)
        self.assertTrue(self.plugin.is_initialized)
    
    def test_initialize_driver_unsupported_browser(self):
        """Test initialization with unsupported browser."""
        self.plugin.browser_config["browser"] = "unsupported"
        
        with self.assertRaises(ValueError):
            self.plugin._initialize_driver()
    
    @patch.object(ExtractTableSeleniumPlugin, '_initialize_driver')
    @patch.object(ExtractTableSeleniumPlugin, '_extract_table_data')
    def test_extract_table_basic(self, mock_extract_data, mock_init_driver):
        """Test basic table extraction."""
        mock_init_driver.return_value = True
        mock_extract_data.return_value = [{"Name": "John", "Age": "30"}]
        
        config = {
            "selector": "table",
            "config": {
                "headers": "first_row",
                "format": "objects",
                "scope": "tbody"
            },
            "result": "table_data"
        }
        
        result = self.plugin._extract_table(config)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["rows_extracted"], 1)
        self.assertEqual(result["result_variable"], "table_data")
        self.memory_handler.set_variable.assert_called_with("table_data", [{"Name": "John", "Age": "30"}])
    
    @patch.object(ExtractTableSeleniumPlugin, '_initialize_driver')
    def test_extract_table_with_url(self, mock_init_driver):
        """Test table extraction with URL navigation."""
        mock_init_driver.return_value = True
        self.plugin.driver = MockWebDriver()
        self.plugin.wait = MockWebDriverWait(self.plugin.driver, 30)
        
        config = {
            "url": "https://example.com",
            "selector": "table",
            "config": {
                "headers": "first_row",
                "format": "objects",
                "scope": "tbody"
            },
            "result": "table_data"
        }
        
        with patch.object(self.plugin, '_extract_table_data', return_value=[]):
            result = self.plugin._extract_table(config)
        
        self.assertTrue(result["success"])
    
    @patch.object(ExtractTableSeleniumPlugin, '_initialize_driver')
    def test_extract_table_error_handling(self, mock_init_driver):
        """Test error handling in table extraction."""
        mock_init_driver.return_value = False
        
        config = {
            "selector": "table",
            "result": "table_data"
        }
        
        result = self.plugin._extract_table(config)
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_extract_headers_first_row(self):
        """Test header extraction from first row."""
        rows = [MockRowElement(), MockRowElement()]
        headers_config = "first_row"
        complex_config = {}
        
        headers = self.plugin._extract_headers(rows, headers_config, complex_config)
        
        self.assertEqual(len(headers), 2)
    
    def test_extract_headers_custom_array(self):
        """Test header extraction with custom array."""
        rows = [MockRowElement()]
        headers_config = ["Name", "Age", "City"]
        complex_config = {}
        
        headers = self.plugin._extract_headers(rows, headers_config, complex_config)
        
        self.assertEqual(headers, ["Name", "Age", "City"])
    
    def test_extract_headers_none(self):
        """Test header extraction with none configuration."""
        rows = [MockRowElement()]
        headers_config = "none"
        complex_config = {}
        
        headers = self.plugin._extract_headers(rows, headers_config, complex_config)
        
        self.assertEqual(headers, [])
    
    def test_extract_row_data(self):
        """Test row data extraction."""
        row_element = MockRowElement()
        headers = ["Name", "Age"]
        complex_config = {}
        
        row_data = self.plugin._extract_row_data(row_element, headers, complex_config)
        
        self.assertIn("Name", row_data)
        self.assertIn("Age", row_data)
    
    def test_apply_column_filters(self):
        """Test column filtering."""
        row_data = {"0": "John", "1": "30", "2": "New York"}
        filters = {
            "skip_columns": [0],
            "required_columns": [1],
            "min_columns": 2
        }
        
        result = self.plugin._apply_column_filters(row_data, filters)
        
        self.assertTrue(result)
        self.assertNotIn("0", row_data)  # Should be removed
    
    def test_apply_column_filters_required_columns_fail(self):
        """Test column filtering with missing required columns."""
        row_data = {"0": "John", "1": ""}  # Empty required column
        filters = {
            "required_columns": [1]
        }
        
        result = self.plugin._apply_column_filters(row_data, filters)
        
        self.assertFalse(result)
    
    def test_apply_transformations(self):
        """Test data transformations."""
        data = [{"Price": "$100", "Stock": "50"}]
        transform = {
            "columns": {
                "Price": "parse_currency(USD)",
                "Stock": "parse_int"
            },
            "custom": {
                "ID": "generate_uuid()"
            },
            "rename": {
                "Price": "ProductPrice"
            }
        }
        
        transformed_data = self.plugin._apply_transformations(data, transform)
        
        self.assertEqual(len(transformed_data), 1)
        self.assertIn("ProductPrice", transformed_data[0])
        self.assertIn("ID", transformed_data[0])
    
    def test_apply_column_transform_parse_int(self):
        """Test integer parsing transformation."""
        result = self.plugin._apply_column_transform("123", "parse_int")
        self.assertEqual(result, 123)
    
    def test_apply_column_transform_parse_float(self):
        """Test float parsing transformation."""
        result = self.plugin._apply_column_transform("123.45", "parse_float")
        self.assertEqual(result, 123.45)
    
    def test_apply_column_transform_parse_currency(self):
        """Test currency parsing transformation."""
        result = self.plugin._apply_column_transform("$1,234.56", "parse_currency(USD)")
        self.assertEqual(result, 1234.56)
    
    def test_apply_column_transform_trim(self):
        """Test trim transformation."""
        result = self.plugin._apply_column_transform("  hello world  ", "trim")
        self.assertEqual(result, "hello world")
    
    def test_apply_column_transform_lowercase(self):
        """Test lowercase transformation."""
        result = self.plugin._apply_column_transform("HELLO WORLD", "lowercase")
        self.assertEqual(result, "hello world")
    
    def test_apply_column_transform_uppercase(self):
        """Test uppercase transformation."""
        result = self.plugin._apply_column_transform("hello world", "uppercase")
        self.assertEqual(result, "HELLO WORLD")
    
    def test_evaluate_custom_expression(self):
        """Test custom expression evaluation."""
        row_data = {"Price": 100, "Quantity": 2}
        expression = "{{row.Price}} * {{row.Quantity}}"
        
        result = self.plugin._evaluate_custom_expression(expression, row_data)
        
        self.assertEqual(result, 200)
    
    def test_evaluate_custom_expression_with_uuid(self):
        """Test custom expression with UUID generation."""
        row_data = {"Name": "Product"}
        expression = "generate_uuid()"
        
        result = self.plugin._evaluate_custom_expression(expression, row_data)
        
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_apply_validation_success(self):
        """Test successful data validation."""
        data = [{"Name": "John", "Age": 30, "Email": "john@example.com"}]
        validation = {
            "required": ["Name", "Age"],
            "types": {
                "Age": "integer"
            },
            "on_error": "skip_row"
        }
        
        validated_data = self.plugin._apply_validation(data, validation)
        
        self.assertEqual(len(validated_data), 1)
    
    def test_apply_validation_missing_required(self):
        """Test validation with missing required fields."""
        data = [{"Name": "John"}]  # Missing Age
        validation = {
            "required": ["Name", "Age"],
            "on_error": "skip_row"
        }
        
        validated_data = self.plugin._apply_validation(data, validation)
        
        self.assertEqual(len(validated_data), 0)  # Row should be skipped
    
    def test_validate_type(self):
        """Test type validation."""
        self.assertTrue(self.plugin._validate_type("hello", "string"))
        self.assertTrue(self.plugin._validate_type(123, "integer"))
        self.assertTrue(self.plugin._validate_type(123.45, "number"))
        self.assertTrue(self.plugin._validate_type(True, "boolean"))
        self.assertFalse(self.plugin._validate_type("hello", "integer"))
    
    def test_format_output_objects(self):
        """Test object format output."""
        data = [{"Name": "John", "Age": 30}]
        format_type = "objects"
        headers = ["Name", "Age"]
        
        result = self.plugin._format_output(data, format_type, headers)
        
        self.assertEqual(result, data)
    
    def test_format_output_arrays(self):
        """Test array format output."""
        data = [{"Name": "John", "Age": 30}]
        format_type = "arrays"
        headers = ["Name", "Age"]
        
        result = self.plugin._format_output(data, format_type, headers)
        
        self.assertEqual(result[0], headers)  # First row should be headers
        self.assertEqual(result[1], ["John", 30])  # Second row should be data
    
    def test_format_output_key_value(self):
        """Test key-value format output."""
        data = [{"Name": "John", "Age": 30}]
        format_type = "key_value"
        headers = ["Name", "Age"]
        
        result = self.plugin._format_output(data, format_type, headers)
        
        self.assertIn("John", result)
        self.assertEqual(result["John"]["Age"], 30)
    
    @patch.object(ExtractTableSeleniumPlugin, '_initialize_driver')
    def test_navigate_to(self, mock_init_driver):
        """Test navigation to URL."""
        mock_init_driver.return_value = True
        self.plugin.driver = MockWebDriver()
        
        config = {
            "url": "https://example.com",
            "wait": 5
        }
        
        result = self.plugin._navigate_to(config)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["url"], "https://example.com")
    
    @patch.object(ExtractTableSeleniumPlugin, '_initialize_driver')
    def test_wait_for_element(self, mock_init_driver):
        """Test waiting for element."""
        mock_init_driver.return_value = True
        self.plugin.driver = MockWebDriver()
        self.plugin.wait = MockWebDriverWait(self.plugin.driver, 30)
        
        config = {
            "selector": ".table",
            "timeout": 30
        }
        
        result = self.plugin._wait_for_element(config)
        
        self.assertTrue(result["success"])
        self.assertTrue(result["element_found"])
    
    @patch.object(ExtractTableSeleniumPlugin, '_initialize_driver')
    def test_scroll_to_element(self, mock_init_driver):
        """Test scrolling to element."""
        mock_init_driver.return_value = True
        self.plugin.driver = MockWebDriver()
        
        config = {
            "selector": ".table"
        }
        
        result = self.plugin._scroll_to_element(config)
        
        self.assertTrue(result["success"])
    
    @patch.object(ExtractTableSeleniumPlugin, '_initialize_driver')
    def test_click_element(self, mock_init_driver):
        """Test clicking element."""
        mock_init_driver.return_value = True
        self.plugin.driver = MockWebDriver()
        
        config = {
            "selector": ".button",
            "wait_after": 1
        }
        
        result = self.plugin._click_element(config)
        
        self.assertTrue(result["success"])
    
    @patch.object(ExtractTableSeleniumPlugin, '_initialize_driver')
    def test_get_page_source(self, mock_init_driver):
        """Test getting page source."""
        mock_init_driver.return_value = True
        self.plugin.driver = MockWebDriver()
        
        config = {
            "result": "page_source"
        }
        
        result = self.plugin._get_page_source(config)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["result_variable"], "page_source")
        self.memory_handler.set_variable.assert_called_with("page_source", self.plugin.driver.page_source)
    
    @patch.object(ExtractTableSeleniumPlugin, '_initialize_driver')
    def test_take_screenshot(self, mock_init_driver):
        """Test taking screenshot."""
        mock_init_driver.return_value = True
        self.plugin.driver = MockWebDriver()
        
        config = {
            "filename": "test_screenshot.png"
        }
        
        result = self.plugin._take_screenshot(config)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["filename"], "test_screenshot.png")
    
    def test_close_browser(self):
        """Test closing browser."""
        self.plugin.driver = MockWebDriver()
        self.plugin.wait = MockWebDriverWait(self.plugin.driver, 30)
        self.plugin.is_initialized = True
        
        config = {}
        
        result = self.plugin._close_browser(config)
        
        self.assertTrue(result["success"])
        self.assertFalse(self.plugin.is_initialized)
        self.assertIsNone(self.plugin.driver)
        self.assertIsNone(self.plugin.wait)
    
    def test_cleanup(self):
        """Test plugin cleanup."""
        self.plugin.driver = MockWebDriver()
        self.plugin.wait = MockWebDriverWait(self.plugin.driver, 30)
        self.plugin.is_initialized = True
        
        self.plugin.cleanup()
        
        self.assertFalse(self.plugin.is_initialized)
        self.assertIsNone(self.plugin.driver)
        self.assertIsNone(self.plugin.wait)
    
    def test_interpolate_variables(self):
        """Test variable interpolation."""
        self.plugin.context = self.context
        self.context.memory_handler._interpolate_variables.return_value = "interpolated_value"
        
        result = self.plugin.interpolate_variables("{{variable}}")
        
        self.assertEqual(result, "interpolated_value")
    
    def test_set_variable(self):
        """Test setting variable in memory."""
        self.plugin.context = self.context
        
        result = self.plugin.set_variable("test_var", "test_value")
        
        self.assertTrue(result)
        self.context.memory_handler.set_variable.assert_called_with("test_var", "test_value")
    
    def test_get_variable(self):
        """Test getting variable from memory."""
        self.plugin.context = self.context
        self.context.memory_handler.get_variable.return_value = "test_value"
        
        result = self.plugin.get_variable("test_var", "default_value")
        
        self.assertEqual(result, "test_value")
        self.context.memory_handler.get_variable.assert_called_with("test_var", "default_value")
    
    def test_validate_config(self):
        """Test configuration validation."""
        config = {"required_key": "value", "optional_key": "value"}
        required_keys = ["required_key"]
        
        result = self.plugin.validate_config(config, required_keys)
        
        self.assertTrue(result)
    
    def test_validate_config_missing_required(self):
        """Test configuration validation with missing required keys."""
        config = {"optional_key": "value"}
        required_keys = ["required_key"]
        
        result = self.plugin.validate_config(config, required_keys)
        
        self.assertFalse(result)
    
    def test_get_plugin_info(self):
        """Test getting plugin information."""
        info = self.plugin.get_plugin_info()
        
        self.assertEqual(info["name"], "ExtractTableSeleniumPlugin")
        self.assertEqual(info["version"], "1.0.0")
        self.assertEqual(info["description"], "Selenium-based HTML table extraction with advanced features")
        self.assertIn("commands", info)
        self.assertIn("dependencies", info)

if __name__ == "__main__":
    unittest.main()