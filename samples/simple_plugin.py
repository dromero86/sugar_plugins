"""
Simple Plugin Example
====================

A simple example plugin demonstrating basic plugin functionality
with optional SDK integration for enhanced capabilities.
"""

from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Plugins.SDK import (
    ExtensionManager, ExtensionType,
    HookSystem, HookPoint,
    CommandCustomizer, CommandEvent
)
from Sugar.Lang.Utils.Output import Output

class SimplePlugin(PluginBase):
    """
    Simple example plugin for Sugar.
    
    Demonstrates basic plugin functionality including:
    - Command execution
    - Variable interpolation
    - Result assignment
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Simple example plugin for Sugar"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    
    def __init__(self, context=None, plugin_config=None):
        """Initialize the simple plugin with optional SDK support."""
        super().__init__(context, plugin_config)
        
        # Initialize SDK components (optional)
        self.sdk_enabled = plugin_config.get('enable_sdk', False) if plugin_config else False
        
        if self.sdk_enabled:
            self._initialize_sdk()
        
        Output.Console(self.plugin_name, "Simple plugin initialized")
    
    def _initialize_sdk(self):
        """Initialize SDK components for enhanced functionality."""
        try:
            self.extension_manager = ExtensionManager()
            self.hook_system = HookSystem()
            self.command_customizer = CommandCustomizer()
            
            # Register basic SDK extensions
            self._register_sdk_extensions()
            
            Output.Console(self.plugin_name, "SDK components initialized")
        except Exception as e:
            Output.Console(self.plugin_name, f"SDK initialization failed: {e}")
            self.sdk_enabled = False
    
    def _register_sdk_extensions(self):
        """Register SDK extensions for enhanced functionality."""
        # Register command customization
        self.command_customizer.register_customizer(
            event=CommandEvent.BEFORE_COMMAND_EXECUTION,
            callback=self._before_command_callback,
            priority=5
        )
        
        # Register hook for task execution
        self.hook_system.register_hook(
            hook_point=HookPoint.BEFORE_TASK_EXECUTION,
            callback=self._before_task_hook,
            priority=3
        )
    
    def _before_command_callback(self, context):
        """Callback for command customization."""
        command_name = context.command_name
        Output.Console(self.plugin_name, f"Executing command: {command_name}")
        return context
    
    def _before_task_hook(self, hook_context):
        """Hook for task execution."""
        Output.Console(self.plugin_name, "Simple plugin hook executed")
        return hook_context
    
    def get_available_commands(self) -> list:
        """
        Get list of available commands.
        
        Returns:
            List of available command names
        """
        commands = ["hello", "add", "multiply", "subtract", "divide"]
        
        # Add SDK-related commands if SDK is enabled
        if hasattr(self, 'sdk_enabled') and self.sdk_enabled:
            commands.extend(["sdk_info", "sdk_test"])
        
        return commands
    
    def execute(self, command: str, config: dict) -> any:
        """
        Execute a plugin command.
        
        Args:
            command: Command to execute
            config: Command configuration
            
        Returns:
            Command execution result
        """
        if command == "hello":
            return self._hello(config)
        elif command == "add":
            return self._add(config)
        elif command == "multiply":
            return self._multiply(config)
        elif command == "subtract":
            return self._subtract(config)
        elif command == "divide":
            return self._divide(config)
        elif command == "sdk_info":
            return self._sdk_info(config)
        elif command == "sdk_test":
            return self._sdk_test(config)
        else:
            raise ValueError(f"Unknown command: {command}")
    
    def _hello(self, config: dict) -> str:
        """Generate a greeting message."""
        name = config.get("name", "World")
        return f"Hello, {name}!"
    
    def _add(self, config: dict) -> float:
        """Add two numbers."""
        a = float(config.get("a", 0))
        b = float(config.get("b", 0))
        return a + b
    
    def _multiply(self, config: dict) -> float:
        """Multiply two numbers."""
        a = float(config.get("a", 1))
        b = float(config.get("b", 1))
        return a * b
    
    def _subtract(self, config: dict) -> float:
        """ Subtract two numbers."""
        a = float(config.get("a", 0))
        b = float(config.get("b", 0))
        return a - b
    
    def _divide(self, config: dict) -> float:
        """Divide two numbers."""
        a = float(config.get("a", 0))
        b = float(config.get("b", 1))
        
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        
        return a / b
    
    def _sdk_info(self, config: dict) -> dict:
        """Get SDK information."""
        return {
            "sdk_enabled": getattr(self, 'sdk_enabled', False),
            "plugin_name": self.plugin_name,
            "version": self.VERSION,
            "available_commands": self.get_available_commands()
        }
    
    def _sdk_test(self, config: dict) -> dict:
        """Test SDK functionality."""
        if not getattr(self, 'sdk_enabled', False):
            return {
                "status": "error",
                "message": "SDK is not enabled for this plugin"
            }
        
        return {
            "status": "success",
            "message": "SDK functionality is working",
            "sdk_components": {
                "extension_manager": hasattr(self, 'extension_manager'),
                "hook_system": hasattr(self, 'hook_system'),
                "command_customizer": hasattr(self, 'command_customizer')
            }
        } 