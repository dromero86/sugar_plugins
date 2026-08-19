"""
Test cases for LDAP Plugin
==========================

Basic test cases for the LDAP plugin functionality.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the plugin path to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from LDAPPlugin import LDAPPlugin

class TestLDAPPlugin(unittest.TestCase):
    """Test cases for LDAPPlugin class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.plugin = LDAPPlugin()
    
    def test_plugin_initialization(self):
        """Test plugin initialization."""
        self.assertIsNotNone(self.plugin)
        self.assertEqual(self.plugin.VERSION, "1.0.0")
        self.assertEqual(self.plugin.DESCRIPTION, "LDAP plugin for Sugar with comprehensive directory service management")
        self.assertEqual(self.plugin.AUTHOR, "Sugar Team")
        self.assertEqual(self.plugin.LICENSE, "MIT")
    
    def test_available_commands(self):
        """Test that plugin has available commands."""
        commands = self.plugin.get_available_commands()
        self.assertIsInstance(commands, list)
        self.assertGreater(len(commands), 0)
        
        # Check for essential commands
        essential_commands = ["connect", "disconnect", "search", "authenticate"]
        for cmd in essential_commands:
            self.assertIn(cmd, commands)
    
    def test_check_dependencies(self):
        """Test dependency checking."""
        result = self.plugin.execute("check_dependencies", {})
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)
        self.assertIn("dependencies", result)
    
    def test_system_info(self):
        """Test system info retrieval."""
        result = self.plugin.execute("system_info", {})
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)
        self.assertIn("system", result)
    
    def test_test_functionality(self):
        """Test functionality testing."""
        result = self.plugin.execute("test_functionality", {})
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)
        self.assertIn("tests", result)
    
    def test_unknown_command(self):
        """Test handling of unknown commands."""
        with self.assertRaises(ValueError):
            self.plugin.execute("unknown_command", {})
    
    def test_plugin_metadata(self):
        """Test plugin metadata."""
        info = self.plugin.get_plugin_info()
        self.assertIsInstance(info, dict)
        self.assertIn("name", info)
        self.assertIn("version", info)
        self.assertIn("description", info)
        self.assertIn("commands", info)

if __name__ == '__main__':
    unittest.main()