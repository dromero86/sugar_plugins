"""
Meta Plugin Implementation
=========================

Main implementation of the Meta plugin for Sugar.
Handles plugin configuration hooks and system-wide settings.
This plugin acts as a hook system where plugins can define their initial behavior.
"""

from typing import Any, Dict, List, Optional, Union

from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output

class MetaPlugin(PluginBase):
    """
    Meta plugin for Sugar.
    
    Provides a hook system for plugin configuration including:
    - Plugin configuration hooks
    - System-wide configuration management
    - Plugin dependency management
    - Pre-execution configuration loading
    """
    
    VERSION = "2.0.0"
    DESCRIPTION = "Hook system for plugin configuration in Sugar"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = []  # No external dependencies
    REQUIREMENTS = []
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Meta plugin.
        
        Args:
            context: Sugar service context
            plugin_config: Plugin configuration
        """
        super().__init__(context, plugin_config)
        
        # Configuration state
        self.meta_config = {}
        self.plugin_hooks = {}
        self.initialized_plugins = set()
        
        Output.Console(self.plugin_name, "Meta plugin initialized as hook system")
    
    def get_available_commands(self) -> List[str]:
        """
        Get list of available meta commands.
        
        Returns:
            List of available command names
        """
        return [
            # Configuration management
            "configure",
            "get_config",
            "set_config",
            "get_plugin_config",
            
            # Hook management
            "register_hook",
            "unregister_hook",
            "list_hooks",
            "execute_hooks",
            
            # Plugin management
            "initialize_plugin",
            "get_initialized_plugins",
            
            # Jinja2 integration
            "jinja2",
            
            # System status
            "get_status",
            "get_hook_status"
        ]
    
    def execute(self, operator: str, config: Dict[str, Any]) -> Any:
        """
        Execute a meta operator.
        
        Args:
            operator: Command to execute
            config: Configuration for the operator
            
        Returns:
            Command result
        """
        try:
            if operator == "configure":
                return self._configure_system(config)
            elif operator == "get_config":
                return self._get_config(config)
            elif operator == "set_config":
                return self._set_config(config)
            elif operator == "get_plugin_config":
                return self._get_plugin_config(config)
            elif operator == "register_hook":
                return self._register_hook(config)
            elif operator == "unregister_hook":
                return self._unregister_hook(config)
            elif operator == "list_hooks":
                return self._list_hooks(config)
            elif operator == "execute_hooks":
                return self._execute_hooks(config)
            elif operator == "initialize_plugin":
                return self._initialize_plugin(config)
            elif operator == "get_initialized_plugins":
                return self._get_initialized_plugins(config)
            elif operator == "get_status":
                return self._get_status(config)
            elif operator == "get_hook_status":
                return self._get_hook_status(config)
            elif operator == "jinja2":
                return self._handle_jinja2(config)
            else:
                raise ValueError(f"Unknown operator: {operator}")
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing {operator}: {str(e)}")
            raise
    
    def _configure_system(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure the system based on meta configuration."""
        # Get meta configuration from protocol or use defaults
        if hasattr(self.context, 'protocol') and 'meta' in self.context.protocol:
            meta_config = self.context.memory_handler._interpolate_variables(
                self.context.protocol['meta']
            )
        else:
            # Default configuration
            meta_config = {}
            Output.Console(self.plugin_name, "Meta not specified, using empty configuration")
        
        # Store configuration
        self.meta_config = meta_config
        
        # Process plugin hooks
        self._process_plugin_hooks(meta_config)
        
        Output.Console(self.plugin_name, f"System configured with {len(meta_config)} plugin configurations")
        return {"success": True, "config": meta_config, "hooks_processed": len(self.plugin_hooks)}
    
    def _process_plugin_hooks(self, meta_config: Dict[str, Any]) -> None:
        """Process plugin configurations from meta."""
        self.plugin_hooks = {}
        
        for plugin_name, plugin_config in meta_config.items():
            if isinstance(plugin_config, dict):
                self.plugin_hooks[plugin_name] = plugin_config
                Output.Console(self.plugin_name, f"Registered hook for plugin: {plugin_name}")
            else:
                Output.Console(self.plugin_name, f"Invalid configuration for plugin {plugin_name}: must be a dictionary")
    
    def _get_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get current meta configuration."""
        return self.meta_config
    
    def _set_config(self, config: Dict[str, Any]) -> bool:
        """Set meta configuration."""
        key = config.get("key")
        value = config.get("value")
        
        if key is None:
            raise ValueError("Configuration key required")
        
        self.meta_config[key] = value
        Output.Console(self.plugin_name, f"Set config: {key} = {value}")
        return True
    
    def _get_plugin_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get configuration for a specific plugin."""
        plugin_name = config.get("plugin")
        if plugin_name is None:
            raise ValueError("Plugin name required")
        
        return self.plugin_hooks.get(plugin_name, {})
    
    def _register_hook(self, config: Dict[str, Any]) -> bool:
        """Register a hook for a plugin."""
        plugin_name = config.get("plugin")
        hook_config = config.get("config", {})
        
        if plugin_name is None:
            raise ValueError("Plugin name required")
        
        self.plugin_hooks[plugin_name] = hook_config
        Output.Console(self.plugin_name, f"Registered hook for plugin: {plugin_name}")
        return True
    
    def _unregister_hook(self, config: Dict[str, Any]) -> bool:
        """Unregister a hook for a plugin."""
        plugin_name = config.get("plugin")
        
        if plugin_name is None:
            raise ValueError("Plugin name required")
        
        if plugin_name in self.plugin_hooks:
            del self.plugin_hooks[plugin_name]
            Output.Console(self.plugin_name, f"Unregistered hook for plugin: {plugin_name}")
            return True
        else:
            Output.Console(self.plugin_name, f"No hook found for plugin: {plugin_name}")
            return False
    
    def _list_hooks(self, config: Dict[str, Any]) -> List[str]:
        """List all registered plugin hooks."""
        return list(self.plugin_hooks.keys())
    
    def _execute_hooks(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all registered plugin hooks."""
        results = {}
        
        for plugin_name, hook_config in self.plugin_hooks.items():
            try:
                result = self._execute_plugin_hook(plugin_name, hook_config)
                results[plugin_name] = {"success": True, "result": result}
                self.initialized_plugins.add(plugin_name)
            except Exception as e:
                results[plugin_name] = {"success": False, "error": str(e)}
                Output.Console(self.plugin_name, f"Failed to execute hook for {plugin_name}: {str(e)}")
        
        return results
    
    def _execute_plugin_hook(self, plugin_name: str, hook_config: Dict[str, Any]) -> Any:
        """Execute a specific plugin hook."""
        if not hasattr(self.context, 'plugin_manager'):
            raise RuntimeError("Plugin manager not available")
        
        plugin = self.context.plugin_manager.get_plugin(plugin_name)
        if not plugin:
            raise RuntimeError(f"Plugin {plugin_name} not found")
        
        # Check if plugin has a meta_hook method
        if hasattr(plugin, 'meta_hook'):
            return plugin.meta_hook(hook_config)
        else:
            # Default behavior: store configuration in plugin
            if hasattr(plugin, 'meta_config'):
                plugin.meta_config = hook_config
            Output.Console(self.plugin_name, f"Applied configuration to plugin: {plugin_name}")
            return {"config_applied": True}
    
    def _initialize_plugin(self, config: Dict[str, Any]) -> bool:
        """Initialize a specific plugin with its meta configuration."""
        plugin_name = config.get("plugin")
        
        if plugin_name is None:
            raise ValueError("Plugin name required")
        
        if plugin_name not in self.plugin_hooks:
            Output.Console(self.plugin_name, f"No hook configuration found for plugin: {plugin_name}")
            return False
        
        try:
            hook_config = self.plugin_hooks[plugin_name]
            result = self._execute_plugin_hook(plugin_name, hook_config)
            self.initialized_plugins.add(plugin_name)
            Output.Console(self.plugin_name, f"Initialized plugin: {plugin_name}")
            return True
        except Exception as e:
            Output.Console(self.plugin_name, f"Failed to initialize plugin {plugin_name}: {str(e)}")
            return False
    
    def _get_initialized_plugins(self, config: Dict[str, Any]) -> List[str]:
        """Get list of initialized plugins."""
        return list(self.initialized_plugins)
    
    def _get_status(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get system status."""
        return {
            "meta_config": self.meta_config,
            "plugin_hooks": self.plugin_hooks,
            "initialized_plugins": list(self.initialized_plugins),
            "plugin_manager_available": hasattr(self.context, 'plugin_manager'),
            "total_hooks": len(self.plugin_hooks),
            "total_initialized": len(self.initialized_plugins)
        }
    
    def _get_hook_status(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed hook status."""
        plugin_name = config.get("plugin")
        
        if plugin_name:
            hook_config = self.plugin_hooks.get(plugin_name, {})
            is_initialized = plugin_name in self.initialized_plugins
            return {
                "plugin": plugin_name,
                "has_hook": plugin_name in self.plugin_hooks,
                "hook_config": hook_config,
                "initialized": is_initialized
            }
        else:
            return {
                "hooks": self.plugin_hooks,
                "initialized": list(self.initialized_plugins)
            }
    
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """Get configuration for a specific plugin (for other plugins)."""
        return self.plugin_hooks.get(plugin_name, {})
    
    def is_plugin_initialized(self, plugin_name: str) -> bool:
        """Check if a plugin is initialized (for other plugins)."""
        return plugin_name in self.initialized_plugins
    
    def get_all_hooks(self) -> Dict[str, Any]:
        """Get all plugin hooks (for other plugins)."""
        return self.plugin_hooks.copy()
    
    def cleanup(self):
        """Cleanup resources."""
        Output.Console(self.plugin_name, "Meta plugin cleanup completed")
    
    def _handle_jinja2(self, config: Dict[str, Any]) -> Any:
        """
        Handle Jinja2 template processing through meta plugin.
        
        Supports:
        - "interpolate": true/false - Enable/disable Jinja2 interpolation
        - "operator": "parser" - Parse and render template
        - "template": "template string" - Template to process
        - "result": "variable_name" - Variable to store result
        
        Args:
            config: Jinja2 configuration
            
        Returns:
            Processing result
        """
        try:
            # Check if Jinja2 interpolation is enabled
            if config.get("interpolate") is False:
                Output.Console(self.plugin_name, "Jinja2 interpolation disabled")
                return {"success": False, "message": "Jinja2 interpolation disabled"}
            
            # Handle parser operator
            if config.get("operator") == "parser":
                return self._parse_jinja2_template(config)
            
            # Handle other operators
            operator = config.get("operator")
            if operator:
                Output.Console(self.plugin_name, f"Unknown Jinja2 operator: {operator}")
                return {"success": False, "error": f"Unknown operator: {operator}"}
            
            # Default: enable Jinja2 interpolation
            Output.Console(self.plugin_name, "Jinja2 interpolation enabled")
            return {"success": True, "message": "Jinja2 interpolation enabled"}
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error handling Jinja2: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _parse_jinja2_template(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and render a Jinja2 template.
        
        Args:
            config: Configuration with template and result variable
            
        Returns:
            Processing result
        """
        try:
            template = config.get("template")
            result_var = config.get("id")
            
            if not template:
                return {"success": False, "error": "Template not provided"}
            
            if not result_var:
                return {"success": False, "error": "Result variable not provided"}
            
            # Try to import and use Jinja2 plugin
            try:
                from plugins.jinja2.interpolation_adapter import interpolate_with_jinja2
                
                # Get memory handler from context
                memory_handler = getattr(self.context, 'memory_handler', None)
                if not memory_handler:
                    return {"success": False, "error": "Memory handler not available"}
                
                # Process template
                result = interpolate_with_jinja2(template, memory_handler, mode='smart')
                
                # Store result in memory
                memory_handler.set_variable(result_var, result)
                
                Output.Console(self.plugin_name, f"Jinja2 template processed and stored in '{result_var}'")
                return {
                    "success": True,
                    "template": template,
                    "result": result,
                    "result_variable": result_var
                }
                
            except ImportError:
                return {"success": False, "error": "Jinja2 plugin not available"}
            except Exception as e:
                return {"success": False, "error": f"Template processing error: {str(e)}"}
                
        except Exception as e:
            return {"success": False, "error": f"Parse error: {str(e)}"}