"""
Tests for SMB Plugin
===================

Basic tests for SMB plugin functionality.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

# Import the plugin classes
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../Sugar'))

# Mock Sugar modules for testing
class MockOutput:
    @staticmethod
    def Console(plugin_name, message):
        print(f"[{plugin_name}] {message}")

class MockPluginBase:
    def __init__(self, context=None, plugin_config=None):
        self.context = context
        self.plugin_config = plugin_config or {}
        self.plugin_name = "SMBPlugin"
    
    def interpolate_variables(self, value):
        return value

# Mock the imports
import sys
sys.modules['Sugar.Lang.Plugins'] = type('MockModule', (), {'PluginBase': MockPluginBase})()
sys.modules['Sugar.Lang.Utils.Output'] = type('MockModule', (), {'Output': MockOutput})()

# Mock SMB dependencies
class MockPySMBConnection:
    def __init__(self, *args, **kwargs):
        pass
    
    def connect(self, *args, **kwargs):
        return True
    
    def listPath(self, *args, **kwargs):
        return []
    
    def close(self):
        pass

class MockOperationFailure(Exception):
    pass

sys.modules['smb.SMBConnection'] = type('MockModule', (), {'SMBConnection': MockPySMBConnection})()
sys.modules['smb.smb_structs'] = type('MockModule', (), {'OperationFailure': MockOperationFailure})()

# Now import the plugin classes
from src.SMBPlugin import SMBPlugin
from src.SMBConnection import SMBConnection
from src.SMBFileTransfer import SMBFileTransfer


class TestSMBPlugin(unittest.TestCase):
    """Test cases for SMBPlugin class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.plugin = SMBPlugin()
    
    def test_plugin_initialization(self):
        """Test plugin initialization."""
        self.assertIsNotNone(self.plugin)
        self.assertEqual(self.plugin.VERSION, "1.0.0")
        self.assertEqual(self.plugin.DESCRIPTION, "Comprehensive SMB/CIFS operations for Sugar")
        self.assertEqual(self.plugin.AUTHOR, "Sugar Team")
        self.assertEqual(self.plugin.LICENSE, "MIT")
    
    def test_available_commands(self):
        """Test available commands list."""
        commands = self.plugin.get_available_commands()
        expected_commands = [
            "connect", "test_connection", "disconnect",
            "upload", "upload_multiple", "download", "download_multiple",
            "list_directory", "create_directory", "delete_directory",
            "delete_file", "get_file_info", "get_session_info",
            "get_transfer_stats", "search_files", "sync_directory", "create_backup"
        ]
        
        self.assertEqual(len(commands), len(expected_commands))
        for cmd in expected_commands:
            self.assertIn(cmd, commands)
    
    def test_connect_missing_fields(self):
        """Test connect command with missing required fields."""
        config = {"host": "test.com", "username": "user"}
        result = self.plugin.execute("connect", config)
        
        self.assertEqual(result["status"], "error")
        self.assertIn("Missing required field", result["error"])
    
    def test_test_connection_missing_fields(self):
        """Test test_connection command with missing required fields."""
        config = {"host": "test.com"}
        result = self.plugin.execute("test_connection", config)
        
        self.assertEqual(result["status"], "error")
        self.assertIn("Missing required field", result["error"])
    
    def test_upload_missing_fields(self):
        """Test upload command with missing required fields."""
        config = {"session": "test_session"}
        result = self.plugin.execute("upload", config)
        
        self.assertEqual(result["status"], "error")
        self.assertIn("Missing required field", result["error"])
    
    def test_download_missing_fields(self):
        """Test download command with missing required fields."""
        config = {"session": "test_session"}
        result = self.plugin.execute("download", config)
        
        self.assertEqual(result["status"], "error")
        self.assertIn("Missing required field", result["error"])
    
    def test_list_directory_missing_session(self):
        """Test list_directory command with missing session."""
        config = {"path": "/test"}
        result = self.plugin.execute("list_directory", config)
        
        self.assertEqual(result["status"], "error")
        self.assertIn("Missing required field", result["error"])
    
    def test_unknown_command(self):
        """Test unknown command handling."""
        config = {}
        result = self.plugin.execute("unknown_command", config)
        
        self.assertEqual(result["status"], "error")
        self.assertIn("Unknown command", result["error"])
    
    def test_meta_hook(self):
        """Test meta hook functionality."""
        config = {
            "connections": {
                "test_connection": {
                    "host": "test.com",
                    "share": "test_share",
                    "username": "user",
                    "password": "pass",
                    "auto_connect": False
                }
            }
        }
        
        result = self.plugin.meta_hook(config)
        
        self.assertEqual(result["success"], True)
        self.assertEqual(result["connections_configured"], 1)
        self.assertEqual(result["auto_connected"], 0)


class TestSMBConnection(unittest.TestCase):
    """Test cases for SMBConnection class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.connection_manager = SMBConnection()
    
    def test_connection_manager_initialization(self):
        """Test connection manager initialization."""
        self.assertIsNotNone(self.connection_manager)
        self.assertEqual(len(self.connection_manager.connections), 0)
        self.assertEqual(len(self.connection_manager.connection_info), 0)
    
    def test_disconnect_nonexistent_session(self):
        """Test disconnecting from non-existent session."""
        result = self.connection_manager.disconnect("nonexistent")
        
        self.assertEqual(result["status"], "error")
        self.assertIn("Session not found", result["error"])
    
    def test_get_session_info_nonexistent(self):
        """Test getting info for non-existent session."""
        result = self.connection_manager.get_session_info("nonexistent")
        
        self.assertEqual(result["status"], "error")
        self.assertIn("Session not found", result["error"])
    
    def test_list_active_sessions_empty(self):
        """Test listing active sessions when none exist."""
        result = self.connection_manager.list_active_sessions()
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["total_sessions"], 0)
        self.assertEqual(len(result["active_sessions"]), 0)
    
    def test_close_all_connections_empty(self):
        """Test closing all connections when none exist."""
        result = self.connection_manager.close_all_connections()
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["closed_count"], 0)


class TestSMBFileTransfer(unittest.TestCase):
    """Test cases for SMBFileTransfer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.file_transfer = SMBFileTransfer()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_file_transfer_initialization(self):
        """Test file transfer manager initialization."""
        self.assertIsNotNone(self.file_transfer)
        self.assertEqual(self.file_transfer.transfer_stats["total_transfers"], 0)
        self.assertEqual(self.file_transfer.transfer_stats["successful_transfers"], 0)
        self.assertEqual(self.file_transfer.transfer_stats["failed_transfers"], 0)
    
    def test_upload_multiple_empty_files(self):
        """Test upload_multiple with empty files list."""
        mock_conn = Mock()
        result = self.file_transfer.upload_multiple(mock_conn, "test_share", [])
        
        self.assertEqual(result["status"], "error")
        self.assertIn("No files specified", result["error"])
    
    def test_download_multiple_empty_files(self):
        """Test download_multiple with empty files list."""
        mock_conn = Mock()
        result = self.file_transfer.download_multiple(mock_conn, "test_share", [])
        
        self.assertEqual(result["status"], "error")
        self.assertIn("No files specified", result["error"])
    
    def test_get_transfer_stats(self):
        """Test getting transfer statistics."""
        result = self.file_transfer.get_transfer_stats()
        
        self.assertEqual(result["status"], "success")
        self.assertIn("transfer_statistics", result)
        stats = result["transfer_statistics"]
        self.assertIn("total_transfers", stats)
        self.assertIn("successful_transfers", stats)
        self.assertIn("failed_transfers", stats)
        self.assertIn("total_bytes", stats)


if __name__ == '__main__':
    unittest.main()