"""
Environment Plugin Implementation
================================

Main implementation of the Environment plugin for Sugar.
Provides environment variable management and .env file support.
"""

import os
from typing import Any, Dict, List, Optional, Union
from dotenv import dotenv_values

from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output

class EnvironmentPlugin(PluginBase):
    """
    Environment plugin for Sugar.
    
    Provides environment variable operations including:
    - Set/get environment variables
    - Load .env files
    - Check variable existence
    - Delete variables
    - Clear variables
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Environment variable management plugin for Sugar"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = ["python-dotenv"]
    REQUIREMENTS = ["python-dotenv>=0.19.0"]
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Environment plugin.
        
        Args:
            context: Sugar service context
            plugin_config: Plugin configuration
        """
        super().__init__(context, plugin_config)
        
        # Track loaded .env files
        self.loaded_files = {}
        self.meta_config = {}  # Store meta configuration
        self.preconfigured_vars = {}  # Store preconfigured variables
        
        Output.Console(self.plugin_name, "Environment plugin initialized")
    
    def meta_hook(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Meta hook for Environment plugin configuration.
        Called by the meta plugin to configure environment variables before execution.
        
        Args:
            config: Configuration from meta section
            
        Returns:
            Configuration result
        """
        try:
            Output.Console(self.plugin_name, f"Processing meta hook configuration: {config}")
            
            # Store meta configuration
            self.meta_config = config
            
            # Process variables
            variables = config.get("variables", {})
            
            # Process preconfigured variables
            for var_name, var_value in variables.items():
                if isinstance(var_value, (str, int, float, bool)):
                    self.preconfigured_vars[var_name] = var_value
                    Output.Console(self.plugin_name, f"Preconfigured variable: {var_name}")
                    
                    # Auto-set if specified
                    if config.get("auto_set", False):
                        try:
                            self._set_env({"name": var_name, "value": str(var_value)})
                        except Exception as e:
                            Output.Console(self.plugin_name, f"Auto-set failed for {var_name}: {str(e)}")
            
            # Process .env files
            env_files = config.get("env_files", [])
            for env_file in env_files:
                if isinstance(env_file, str):
                    try:
                        self._load_env({"file": env_file})
                        Output.Console(self.plugin_name, f"Loaded .env file: {env_file}")
                    except Exception as e:
                        Output.Console(self.plugin_name, f"Failed to load .env file {env_file}: {str(e)}")
            
            return {
                "success": True,
                "variables_configured": len(self.preconfigured_vars),
                "env_files_loaded": len(env_files),
                "auto_set_enabled": config.get("auto_set", False)
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error in meta hook: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_available_commands(self) -> List[str]:
        """
        Get list of available environment commands.
        
        Returns:
            List of available command names
        """
        return [
            # Variable operations
            "set",
            "get",
            "isset",
            "delete",
            
            # File operations
            "load",
            "clear",
            
            # Utility commands
            "list",
            "export",
            "import"
        ]
    
    def execute(self, operator: str, config: Dict[str, Any]) -> Any:
        """
        Execute an environment operator.
        
        Args:
            operator: Command to execute
            config: Configuration for the operator
            
        Returns:
            Command result
        """
        try:
            if operator == "set":
                return self._set_env(config)
            elif operator == "get":
                return self._get_env(config)
            elif operator == "isset":
                return self._isset_env(config)
            elif operator == "delete":
                return self._delete_env(config)
            elif operator == "load":
                return self._load_env(config)
            elif operator == "clear":
                return self._clear_env(config)
            elif operator == "list":
                return self._list_env(config)
            elif operator == "export":
                return self._export_env(config)
            elif operator == "import":
                return self._import_env(config)
            else:
                raise ValueError(f"Unknown operator: {operator}")
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing {operator}: {str(e)}")
            raise
    
    def _set_env(self, config: Dict[str, Any]) -> bool:
        """Set an environment variable."""
        name = config.get("name")
        value = config.get("value")
        
        if not name:
            raise ValueError("Variable name required")
        
        if value is None:
            raise ValueError("Variable value required")
        
        os.environ[name] = str(value)
        Output.Console(self.plugin_name, f"Set environment variable: {name}")
        return True
    
    def _get_env(self, config: Dict[str, Any]) -> str:
        """Get an environment variable."""
        name = config.get("name")
        result_var = config.get("id")
        default = config.get("default", "")
        
        if not name:
            raise ValueError("Variable name required")
        
        if not result_var:
            raise ValueError("Result variable required")
        
        value = os.environ.get(name, default)
        
        # Store in memory if context available
        if self.context and hasattr(self.context, 'memory_handler'):
            self.context.memory_handler._set_nested_variable(result_var, value)
        
        Output.Console(self.plugin_name, f"Got environment variable: {name} = {value}")
        return value
    
    def _isset_env(self, config: Dict[str, Any]) -> bool:
        """Check if an environment variable exists."""
        name = config.get("name")
        result_var = config.get("id")
        
        if not name:
            raise ValueError("Variable name required")
        
        if not result_var:
            raise ValueError("Result variable required")
        
        exists = name in os.environ
        
        # Store in memory if context available
        if self.context and hasattr(self.context, 'memory_handler'):
            self.context.memory_handler._set_nested_variable(result_var, exists)
        
        Output.Console(self.plugin_name, f"Checked environment variable: {name} exists = {exists}")
        return exists
    
    def _delete_env(self, config: Dict[str, Any]) -> bool:
        """Delete an environment variable."""
        name = config.get("name")
        
        if not name:
            raise ValueError("Variable name required")
        
        if name in os.environ:
            del os.environ[name]
            Output.Console(self.plugin_name, f"Deleted environment variable: {name}")
            return True
        else:
            Output.Console(self.plugin_name, f"Environment variable not found: {name}")
            return False
    
    def _load_env(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Load environment variables from a .env file."""
        path = config.get("path")
        
        if not path:
            raise ValueError("File path required")
        
        # Resolve path if it contains variables
        path = self._resolve_path(path)
        
        try:
            env_vars = dotenv_values(path)
            loaded_count = 0
            
            for key, value in env_vars.items():
                if value is not None:
                    os.environ[key] = value
                    loaded_count += 1
            
            # Track loaded file
            self.loaded_files[path] = list(env_vars.keys())
            
            Output.Console(self.plugin_name, f"Loaded {loaded_count} variables from: {path}")
            return env_vars
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error loading .env file {path}: {str(e)}")
            raise
    
    def _clear_env(self, config: Dict[str, Any]) -> bool:
        """Clear environment variables."""
        if "path" in config:
            # Clear variables loaded from specific file
            path = self._resolve_path(config["path"])
            if path in self.loaded_files:
                cleared_count = 0
                for var in self.loaded_files[path]:
                    if var in os.environ:
                        del os.environ[var]
                        cleared_count += 1
                del self.loaded_files[path]
                Output.Console(self.plugin_name, f"Cleared {cleared_count} variables from file: {path}")
                return True
        
        if "variables" in config:
            # Clear specific variables
            variables = config["variables"]
            if isinstance(variables, str):
                variables = [v.strip() for v in variables.split(',')]
            
            cleared_count = 0
            for var in variables:
                if var in os.environ:
                    del os.environ[var]
                    cleared_count += 1
            
            Output.Console(self.plugin_name, f"Cleared {cleared_count} variables")
            return True
        
        Output.Console(self.plugin_name, "No variables to clear")
        return False
    
    def _list_env(self, config: Dict[str, Any]) -> Dict[str, str]:
        """List environment variables."""
        pattern = config.get("pattern", "")
        result_var = config.get("id")
        
        env_vars = {}
        for key, value in os.environ.items():
            if not pattern or pattern.lower() in key.lower():
                env_vars[key] = value
        
        # Store in memory if context available
        if result_var and self.context and hasattr(self.context, 'memory_handler'):
            self.context.memory_handler._set_nested_variable(result_var, env_vars)
        
        Output.Console(self.plugin_name, f"Listed {len(env_vars)} environment variables")
        return env_vars
    
    def _export_env(self, config: Dict[str, Any]) -> str:
        """Export environment variables to a file."""
        path = config.get("path")
        variables = config.get("variables", [])
        
        if not path:
            raise ValueError("Export path required")
        
        if not variables:
            # Export all variables
            variables = list(os.environ.keys())
        
        try:
            with open(path, 'w') as f:
                for var in variables:
                    if var in os.environ:
                        f.write(f"{var}={os.environ[var]}\n")
            
            Output.Console(self.plugin_name, f"Exported {len(variables)} variables to: {path}")
            return path
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error exporting to {path}: {str(e)}")
            raise
    
    def _import_env(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Import environment variables from a file."""
        path = config.get("path")
        
        if not path:
            raise ValueError("Import path required")
        
        return self._load_env({"path": path})
    
    def _resolve_path(self, path: str) -> str:
        """Resolve path that may contain variables."""
        if path.startswith("${") and path.endswith("}"):
            var_name = path[2:-1].strip()
            if self.context and hasattr(self.context, 'memory_handler'):
                return self.context.memory_handler._get_nested_variable(var_name)
            else:
                return os.environ.get(var_name, path)
        return path
    
    def cleanup(self):
        """Cleanup resources."""
        Output.Console(self.plugin_name, "Environment plugin cleanup completed")