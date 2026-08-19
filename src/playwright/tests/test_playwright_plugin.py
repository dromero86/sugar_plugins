"""
Test cases for Playwright Plugin
===============================

Tests for the main Playwright plugin functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the plugin path to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PlaywrightPlugin import PlaywrightPlugin

class TestPlaywrightPlugin(unittest.TestCase):
    """Test cases for PlaywrightPlugin class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.plugin = PlaywrightPlugin()
    
    def test_plugin_initialization(self):
        """Test plugin initialization."""
        self.assertIsNotNone(self.plugin)
        self.assertEqual(self.plugin.VERSION, "1.0.0")
        self.assertEqual(self.plugin.DESCRIPTION, "Playwright web automation plugin for Sugar")
        self.assertEqual(self.plugin.AUTHOR, "Sugar Team")
        self.assertEqual(self.plugin.LICENSE, "MIT")
    
    def test_dependencies(self):
        """Test plugin dependencies."""
        self.assertIn("playwright", self.plugin.DEPENDENCIES)
        self.assertIn("playwright>=1.40.0", self.plugin.REQUIREMENTS)
    
    def test_hardware_requirements(self):
        """Test hardware requirements."""
        requirements = self.plugin.HARDWARE_REQUIREMENTS
        self.assertIn("min_ram_gb", requirements)
        self.assertIn("min_disk_gb", requirements)
        self.assertIn("min_cpu_cores", requirements)
        self.assertGreaterEqual(requirements["min_ram_gb"], 1)
        self.assertGreaterEqual(requirements["min_disk_gb"], 1)
        self.assertGreaterEqual(requirements["min_cpu_cores"], 1)
    
    def test_permission_requirements(self):
        """Test permission requirements."""
        permissions = self.plugin.PERMISSION_REQUIREMENTS
        self.assertIn("network_access", permissions)
        self.assertIn("write_access", permissions)
        self.assertIn("read_access", permissions)
        self.assertTrue(permissions["network_access"])
    
    def test_available_commands(self):
        """Test available commands list."""
        commands = self.plugin.get_available_commands()
        self.assertIsInstance(commands, list)
        self.assertGreater(len(commands), 0)
        
        # Check for essential commands
        essential_commands = [
            "launch_browser", "close_browser", "new_context", "new_page",
            "goto", "click", "type", "fill", "screenshot", "get_title"
        ]
        
        for command in essential_commands:
            self.assertIn(command, commands)
    
    def test_meta_hook(self):
        """Test meta hook functionality."""
        config = {
            "browser_type": "chromium",
            "headless": False,
            "slow_mo": 1000
        }
        
        result = self.plugin.meta_hook(config)
        
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertTrue(result["success"])
        self.assertIn("browser_configured", result)
        self.assertIn("headless_enabled", result)
        self.assertIn("slow_mo", result)
    
    def test_meta_hook_with_error(self):
        """Test meta hook with error handling."""
        # Mock the Output.Console to avoid actual logging during tests
        with patch('Sugar.Lang.Utils.Output.Output.Console'):
            # Test with invalid config
            config = None
            result = self.plugin.meta_hook(config)
            
            self.assertIsInstance(result, dict)
            self.assertIn("success", result)
            self.assertFalse(result["success"])
            self.assertIn("error", result)
    
    def test_execute_unknown_command(self):
        """Test execution of unknown command."""
        with patch('Sugar.Lang.Utils.Output.Output.Console'):
            result = self.plugin.execute("unknown_command", {})
            self.assertIsNone(result)
    
    def test_execute_with_error(self):
        """Test command execution with error."""
        with patch('Sugar.Lang.Utils.Output.Output.Console'):
            # Mock browser component to raise an exception
            self.plugin.browser.execute = Mock(side_effect=Exception("Test error"))
            
            with self.assertRaises(Exception):
                self.plugin.execute("launch_browser", {})
    
    def test_cleanup(self):
        """Test cleanup functionality."""
        # Mock browser and playwright objects
        self.plugin.browser.browser = Mock()
        self.plugin.playwright.playwright = Mock()
        
        with patch('Sugar.Lang.Utils.Output.Output.Console'):
            self.plugin.cleanup()
            
            # Verify cleanup was called
            self.plugin.browser.browser.close.assert_called_once()
            self.plugin.playwright.playwright.stop.assert_called_once()

class TestBrowserComponent(unittest.TestCase):
    """Test cases for Browser component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.plugin = PlaywrightPlugin()
        self.browser = self.plugin.browser
    
    def test_browser_initialization(self):
        """Test browser component initialization."""
        self.assertIsNotNone(self.browser)
        self.assertEqual(self.browser.browser_type, "chromium")
        self.assertIsNone(self.browser.browser)
        self.assertIsNone(self.browser.context)
    
    def test_configure(self):
        """Test browser configuration."""
        config = {
            "browser_type": "firefox",
            "headless": True
        }
        
        with patch('Sugar.Lang.Utils.Output.Output.Console'):
            self.browser.configure(config)
            
            self.assertEqual(self.browser.browser_type, "firefox")
            self.assertEqual(self.browser.config, config)
    
    def test_execute_unknown_browser_command(self):
        """Test execution of unknown browser command."""
        with patch('Sugar.Lang.Utils.Output.Output.Console'):
            result = self.browser.execute("unknown_command", {})
            self.assertIsNone(result)

class TestPageComponent(unittest.TestCase):
    """Test cases for Page component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.plugin = PlaywrightPlugin()
        self.page = self.plugin.page
    
    def test_page_initialization(self):
        """Test page component initialization."""
        self.assertIsNotNone(self.page)
        self.assertIsNone(self.page.page)
    
    def test_execute_unknown_page_command(self):
        """Test execution of unknown page command."""
        with patch('Sugar.Lang.Utils.Output.Output.Console'):
            result = self.page.execute("unknown_command", {})
            self.assertIsNone(result)

class TestPlaywrightComponent(unittest.TestCase):
    """Test cases for Playwright component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.plugin = PlaywrightPlugin()
        self.playwright = self.plugin.playwright
    
    def test_playwright_initialization(self):
        """Test playwright component initialization."""
        self.assertIsNotNone(self.playwright)
        self.assertIsNone(self.playwright.playwright)
    
    @patch('subprocess.run')
    def test_install_browsers(self, mock_run):
        """Test browser installation."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        with patch('Sugar.Lang.Utils.Output.Output.Console'):
            result = self.playwright.install_browsers()
            
            self.assertIsInstance(result, dict)
            self.assertIn("success", result)
            self.assertTrue(result["success"])
            mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_install_browsers_error(self, mock_run):
        """Test browser installation with error."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Installation failed"
        
        with patch('Sugar.Lang.Utils.Output.Output.Console'):
            result = self.playwright.install_browsers()
            
            self.assertIsInstance(result, dict)
            self.assertIn("success", result)
            self.assertFalse(result["success"])
            self.assertIn("error", result)

if __name__ == '__main__':
    unittest.main()
