"""
Test suite for GnuPG Plugin
===========================

Basic tests for the GnuPG plugin functionality.
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Add the plugin path to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from GnuPGPlugin import GnuPGPlugin
from GnuPGKeyManager import GnuPGKeyManager
from GnuPGEncryption import GnuPGEncryption
from GnuPGSigning import GnuPGSigning
from GnuPGUtils import GnuPGUtils

class TestGnuPGPlugin(unittest.TestCase):
    """Test cases for GnuPGPlugin."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.plugin = GnuPGPlugin()
    
    def test_plugin_initialization(self):
        """Test plugin initialization."""
        self.assertIsNotNone(self.plugin)
        self.assertEqual(self.plugin.VERSION, "1.0.0")
        self.assertEqual(self.plugin.DESCRIPTION, "Comprehensive GnuPG cryptographic operations for Sugar")
        self.assertEqual(self.plugin.AUTHOR, "Sugar Team")
        self.assertEqual(self.plugin.LICENSE, "MIT")
    
    def test_available_commands(self):
        """Test available commands list."""
        commands = self.plugin.get_available_commands()
        self.assertIsInstance(commands, list)
        self.assertGreater(len(commands), 0)
        
        # Check for key management commands
        self.assertIn("generate_key", commands)
        self.assertIn("list_keys", commands)
        self.assertIn("import_key", commands)
        self.assertIn("export_key", commands)
        
        # Check for encryption commands
        self.assertIn("encrypt_file", commands)
        self.assertIn("decrypt_file", commands)
        self.assertIn("encrypt_text", commands)
        self.assertIn("decrypt_text", commands)
        
        # Check for signing commands
        self.assertIn("sign_file", commands)
        self.assertIn("verify_signature", commands)
        self.assertIn("detached_sign", commands)
        
        # Check for utility commands
        self.assertIn("check_dependencies", commands)
        self.assertIn("system_info", commands)
        self.assertIn("test_functionality", commands)
    
    @patch('subprocess.run')
    def test_check_system_dependencies(self, mock_run):
        """Test system dependency checking."""
        # Mock successful gpg --version
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "gpg (GnuPG) 2.4.4\n"
        
        status = self.plugin._check_system_dependencies()
        self.assertIsInstance(status, dict)
        self.assertIn('satisfied', status)
        self.assertIn('gpg', status)
    
    def test_find_gpg(self):
        """Test GnuPG executable finding."""
        gpg_path = self.plugin._find_gpg()
        # Should return a path or None
        self.assertTrue(gpg_path is None or isinstance(gpg_path, str))
    
    def test_unknown_command(self):
        """Test handling of unknown commands."""
        with self.assertRaises(ValueError):
            self.plugin.execute("unknown_command", {})
    
    def test_check_dependencies_command(self):
        """Test check_dependencies command."""
        result = self.plugin.execute("check_dependencies", {})
        self.assertIsInstance(result, dict)
        self.assertIn('system_dependencies', result)
        self.assertIn('python_dependencies', result)
        self.assertIn('hardware_requirements', result)
        self.assertIn('permission_requirements', result)
        self.assertIn('all_satisfied', result)

class TestGnuPGKeyManager(unittest.TestCase):
    """Test cases for GnuPGKeyManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.plugin = GnuPGPlugin()
        self.key_manager = GnuPGKeyManager(self.plugin)
    
    def test_key_manager_initialization(self):
        """Test key manager initialization."""
        self.assertIsNotNone(self.key_manager)
        self.assertEqual(self.key_manager.plugin, self.plugin)
    
    def test_unknown_key_command(self):
        """Test handling of unknown key management commands."""
        with self.assertRaises(ValueError):
            self.key_manager.execute("unknown_command", {})

class TestGnuPGEncryption(unittest.TestCase):
    """Test cases for GnuPGEncryption."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.plugin = GnuPGPlugin()
        self.encryption = GnuPGEncryption(self.plugin)
    
    def test_encryption_initialization(self):
        """Test encryption component initialization."""
        self.assertIsNotNone(self.encryption)
        self.assertEqual(self.encryption.plugin, self.plugin)
    
    def test_unknown_encryption_command(self):
        """Test handling of unknown encryption commands."""
        with self.assertRaises(ValueError):
            self.encryption.execute("unknown_command", {})

class TestGnuPGSigning(unittest.TestCase):
    """Test cases for GnuPGSigning."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.plugin = GnuPGPlugin()
        self.signing = GnuPGSigning(self.plugin)
    
    def test_signing_initialization(self):
        """Test signing component initialization."""
        self.assertIsNotNone(self.signing)
        self.assertEqual(self.signing.plugin, self.plugin)
    
    def test_unknown_signing_command(self):
        """Test handling of unknown signing commands."""
        with self.assertRaises(ValueError):
            self.signing.execute("unknown_command", {})

class TestGnuPGUtils(unittest.TestCase):
    """Test cases for GnuPGUtils."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.plugin = GnuPGPlugin()
        self.utils = GnuPGUtils(self.plugin)
    
    def test_utils_initialization(self):
        """Test utils component initialization."""
        self.assertIsNotNone(self.utils)
        self.assertEqual(self.utils.plugin, self.plugin)
    
    def test_unknown_utils_command(self):
        """Test handling of unknown utility commands."""
        with self.assertRaises(ValueError):
            self.utils.execute("unknown_command", {})
    
    def test_check_dependencies(self):
        """Test dependency checking."""
        result = self.utils._check_dependencies({})
        self.assertIsInstance(result, dict)
        self.assertIn('system_dependencies', result)
        self.assertIn('python_dependencies', result)
        self.assertIn('hardware_requirements', result)
        self.assertIn('permission_requirements', result)
        self.assertIn('all_satisfied', result)

if __name__ == '__main__':
    unittest.main()