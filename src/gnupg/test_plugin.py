#!/usr/bin/env python3
"""
Test script for GnuPG Plugin
============================

Simple test script to verify the plugin structure and basic functionality.
"""

import sys
import os
import subprocess

# Mock the Sugar framework classes for testing
class MockPluginBase:
    def __init__(self, context=None, plugin_config=None):
        self.context = context
        self.plugin_config = plugin_config
        self.plugin_name = "GnuPGPlugin"

class MockOutput:
    @staticmethod
    def Console(plugin_name, message):
        print(f"[{plugin_name}] {message}")

# Add mock classes to sys.modules
sys.modules['Sugar.Lang.Plugins'] = type('MockSugarPlugins', (), {'PluginBase': MockPluginBase})()
sys.modules['Sugar.Lang.Utils.Output'] = type('MockSugarOutput', (), {'Output': MockOutput})()

def test_plugin_structure():
    """Test the plugin structure and basic functionality."""
    print("=== Testing GnuPG Plugin Structure ===")
    
    try:
        # Test imports
        from src.GnuPGPlugin import GnuPGPlugin
        from src.GnuPGKeyManager import GnuPGKeyManager
        from src.GnuPGEncryption import GnuPGEncryption
        from src.GnuPGSigning import GnuPGSigning
        from src.GnuPGUtils import GnuPGUtils
        
        print("All components imported successfully")
        
        # Test plugin initialization
        plugin = GnuPGPlugin()
        print(f"Plugin initialized: {plugin.VERSION}")
        
        # Test available commands
        commands = plugin.get_available_commands()
        print(f"Available commands: {len(commands)} commands")
        
        # Test dependency checking
        deps = plugin.execute("check_dependencies", {})
        print(f"Dependencies checked: {deps.get('all_satisfied', False)}")
        
        # Test system info
        info = plugin.execute("system_info", {})
        print(f"System info retrieved: {info.get('gpg_path', 'Not found')}")
        
        print("All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

def test_gpg_availability():
    """Test if GnuPG is available on the system."""
    print("\n=== Testing GnuPG Availability ===")
    
    try:
        result = subprocess.run(['gpg', '--version'], 
                              capture_output=True, text=True, check=True)
        version = result.stdout.split('\n')[0]
        print(f"GnuPG available: {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("GnuPG not found in PATH")
        print("   Install with: sudo apt-get install gnupg")
        return False

def main():
    """Main test function."""
    print("GnuPG Plugin Test Suite")
    print("=" * 50)
    
    # Test plugin structure
    structure_ok = test_plugin_structure()
    
    # Test GnuPG availability
    gpg_ok = test_gpg_availability()
    
    print("\n" + "=" * 50)
    if structure_ok and gpg_ok:
        print("All tests passed! Plugin is ready to use.")
        return 0
    elif structure_ok:
        print(" Plugin structure is correct, but GnuPG is not available.")
        print("   Install GnuPG to use the plugin.")
        return 1
    else:
        print("Plugin structure has issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())