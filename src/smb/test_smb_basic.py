"""
Basic Tests for SMB Plugin Structure
===================================

Simple tests to verify the plugin structure and basic functionality.
"""

import unittest
import os
import sys
import json


class TestSMBPluginStructure(unittest.TestCase):
    """Test cases for SMB plugin structure."""
    
    def test_plugin_files_exist(self):
        """Test that all required plugin files exist."""
        plugin_dir = os.path.dirname(__file__)
        
        required_files = [
            '__init__.py',
            'requirements.txt',
            'src/SMBPlugin.py',
            'src/SMBConnection.py',
            'src/SMBFileTransfer.py'
        ]
        
        for file_path in required_files:
            full_path = os.path.join(plugin_dir, file_path)
            self.assertTrue(os.path.exists(full_path), f"File does not exist: {file_path}")
    
    def test_requirements_file_content(self):
        """Test that requirements.txt contains expected dependencies."""
        requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
        
        with open(requirements_file, 'r') as f:
            content = f.read()
        
        expected_dependencies = [
            'smbprotocol>=1.5.0',
            'pysmb>=1.2.9',
            'cryptography>=3.4.0'
        ]
        
        for dep in expected_dependencies:
            self.assertIn(dep, content, f"Dependency not found: {dep}")
    
    def test_init_file_content(self):
        """Test that __init__.py contains expected content."""
        init_file = os.path.join(os.path.dirname(__file__), '__init__.py')
        
        with open(init_file, 'r') as f:
            content = f.read()
        
        expected_content = [
            'SMB Plugin for Sugar',
            'Plugin = SMBPlugin',
            '__version__ = "1.0.0"'
        ]
        
        for item in expected_content:
            self.assertIn(item, content, f"Content not found: {item}")
    
    def test_smb_plugin_file_structure(self):
        """Test that SMBPlugin.py has expected structure."""
        plugin_file = os.path.join(os.path.dirname(__file__), 'src/SMBPlugin.py')
        
        with open(plugin_file, 'r') as f:
            content = f.read()
        
        expected_items = [
            'class SMBPlugin(PluginBase):',
            'VERSION = "1.0.0"',
            'DESCRIPTION = "Comprehensive SMB/CIFS operations for Sugar"',
            'def execute(self, command: str, config: Dict[str, Any]) -> Any:',
            'def get_available_commands(self) -> List[str]:',
            'def meta_hook(self, config: Dict[str, Any]) -> Dict[str, Any]:'
        ]
        
        for item in expected_items:
            self.assertIn(item, content, f"Content not found: {item}")
    
    def test_smb_connection_file_structure(self):
        """Test that SMBConnection.py has expected structure."""
        connection_file = os.path.join(os.path.dirname(__file__), 'src/SMBConnection.py')
        
        with open(connection_file, 'r') as f:
            content = f.read()
        
        expected_items = [
            'class SMBConnection:',
            'def connect(self,',
            'def test_connection(self,',
            'def disconnect(self,',
            'def get_connection(self,',
            'def get_session_info(self,'
        ]
        
        for item in expected_items:
            self.assertIn(item, content, f"Content not found: {item}")
    
    def test_smb_file_transfer_structure(self):
        """Test that SMBFileTransfer.py has expected structure."""
        transfer_file = os.path.join(os.path.dirname(__file__), 'src/SMBFileTransfer.py')
        
        with open(transfer_file, 'r') as f:
            content = f.read()
        
        expected_items = [
            'class SMBFileTransfer:',
            'def upload_file(self,',
            'def download_file(self,',
            'def upload_multiple(self,',
            'def download_multiple(self,',
            'def list_directory(self,',
            'def delete_file(self,',
            'def create_directory(self,',
            'def delete_directory(self,'
        ]
        
        for item in expected_items:
            self.assertIn(item, content, f"Content not found: {item}")
    
    def test_available_commands_list(self):
        """Test that the plugin defines the expected commands."""
        plugin_file = os.path.join(os.path.dirname(__file__), 'src/SMBPlugin.py')
        
        with open(plugin_file, 'r') as f:
            content = f.read()
        
        expected_commands = [
            '"connect"',
            '"test_connection"',
            '"disconnect"',
            '"upload"',
            '"upload_multiple"',
            '"download"',
            '"download_multiple"',
            '"list_directory"',
            '"create_directory"',
            '"delete_directory"',
            '"delete_file"',
            '"get_file_info"',
            '"get_session_info"',
            '"get_transfer_stats"'
        ]
        
        for cmd in expected_commands:
            self.assertIn(cmd, content, f"Command not found: {cmd}")
    
    def test_meta_hook_integration(self):
        """Test that the plugin has meta hook integration."""
        plugin_file = os.path.join(os.path.dirname(__file__), 'src/SMBPlugin.py')
        
        with open(plugin_file, 'r') as f:
            content = f.read()
        
        meta_hook_items = [
            'def meta_hook(self, config: Dict[str, Any]) -> Dict[str, Any]:',
            'preconfigured_connections',
            'auto_connect',
            'connections_configured'
        ]
        
        for item in meta_hook_items:
            self.assertIn(item, content, f"Meta hook item not found: {item}")


class TestSMBPluginSyntax(unittest.TestCase):
    """Test cases for SMB plugin syntax validation."""
    
    def test_python_syntax_validity(self):
        """Test that all Python files have valid syntax."""
        plugin_dir = os.path.dirname(__file__)
        
        python_files = [
            '__init__.py',
            'src/SMBPlugin.py',
            'src/SMBConnection.py',
            'src/SMBFileTransfer.py'
        ]
        
        for file_path in python_files:
            full_path = os.path.join(plugin_dir, file_path)
            
            try:
                with open(full_path, 'r') as f:
                    content = f.read()
                
                # Try to compile the content to check syntax
                compile(content, full_path, 'exec')
                
            except SyntaxError as e:
                self.fail(f"Syntax error in {file_path}: {e}")
            except Exception as e:
                self.fail(f"Error reading {file_path}: {e}")


if __name__ == '__main__':
    unittest.main()