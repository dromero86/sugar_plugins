"""
LDAP Plugin Implementation
=========================

Main plugin class for LDAP (Lightweight Directory Access Protocol) functionality.
Provides directory service operations, user authentication, and group management.
"""

import os
import ssl
import time
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output

class LDAPPlugin(PluginBase):
    """
    LDAP plugin for Sugar.
    
    Provides LDAP functionality including:
    - Directory service connections
    - User authentication and management
    - Group management
    - Search and query operations
    - Schema management
    - Security and access control
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "LDAP plugin for Sugar with comprehensive directory service management"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = ["python-ldap"]
    REQUIREMENTS = ["python-ldap>=3.4.0"]
    
    # System dependencies
    SYSTEM_DEPENDENCIES = ["ldapsearch", "ldapadd", "ldapmodify"]
    
    # Hardware requirements
    HARDWARE_REQUIREMENTS = {
        "min_ram_gb": 2,
        "min_disk_gb": 1,
        "min_cpu_cores": 1
    }
    
    # Permission requirements
    PERMISSION_REQUIREMENTS = {
        "network_access": True,
        "write_access": ["/tmp"],
        "read_access": ["./config"]
    }
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LDAP plugin.
        
        Args:
            context: Sugar service context
            plugin_config: Plugin configuration
        """
        super().__init__(context, plugin_config)
        
        # Initialize LDAP availability flags
        self.ldap_available = False
        self.ldap_module = None
        self.ldap_error = None
        self.ldap_invalid_credentials = None
        self.ldap_no_such_object = None
        
        # Initialize basic components without LDAP
        self.connections = {}
        self.meta_config = {}
        self.preconfigured_connections = {}
        
        # Try to import LDAP modules during initialization
        self._import_ldap_modules()
        
        Output.Console(self.plugin_name, "LDAP plugin initialized")
    
    def _import_ldap_modules(self):
        """Import LDAP modules safely during initialization."""
        try:
            # Import the python-ldap module specifically, avoiding conflicts with plugin directory
            import sys
            import importlib
            
            # Temporarily remove the current directory from sys.path to avoid conflicts
            original_path = sys.path.copy()
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            if current_dir in sys.path:
                sys.path.remove(current_dir)
            
            try:
                # Try to import the system ldap module
                ldap_module = importlib.import_module('ldap')
                Output.Console(self.plugin_name, f"LDAP module imported, version: {ldap_module.__version__}")
                
                # Try to import ldap.modlist
                try:
                    modlist_module = importlib.import_module('ldap.modlist')
                    Output.Console(self.plugin_name, "ldap.modlist imported successfully")
                except ImportError as e:
                    Output.Console(self.plugin_name, f"Warning: ldap.modlist not available: {e}")
                    modlist_module = None
                
                # Import LDAP constants
                try:
                    from ldap import LDAPError, INVALID_CREDENTIALS, NO_SUCH_OBJECT
                    self.ldap_error = LDAPError
                    self.ldap_invalid_credentials = INVALID_CREDENTIALS
                    self.ldap_no_such_object = NO_SUCH_OBJECT
                except ImportError as e:
                    Output.Console(self.plugin_name, f"Warning: LDAP constants not available: {e}")
                    self.ldap_error = Exception
                    self.ldap_invalid_credentials = Exception
                    self.ldap_no_such_object = Exception
                
                self.ldap_available = True
                self.ldap_module = ldap_module
                
                # Now import LDAP components
                try:
                    from .LDAPConnection import LDAPConnection
                    from .LDAPSearch import LDAPSearch
                    from .LDAPUserManagement import LDAPUserManagement
                    from .LDAPGroupManagement import LDAPGroupManagement
                except ImportError:
                    # Fallback to absolute imports if relative imports fail
                    from plugins.src.ldap_plugin.src.LDAPConnection import LDAPConnection
                    from plugins.src.ldap_plugin.src.LDAPSearch import LDAPSearch
                    from plugins.src.ldap_plugin.src.LDAPUserManagement import LDAPUserManagement
                    from plugins.src.ldap_plugin.src.LDAPGroupManagement import LDAPGroupManagement
                
                self.search = LDAPSearch(self)
                self.user_management = LDAPUserManagement(self)
                self.group_management = LDAPGroupManagement(self)
                
                Output.Console(self.plugin_name, "LDAP modules imported successfully")
                
            finally:
                # Restore original sys.path
                sys.path = original_path
                
        except ImportError as e:
            self.ldap_available = False
            self.ldap_error = Exception
            self.ldap_invalid_credentials = Exception
            self.ldap_no_such_object = Exception
            Output.Console(self.plugin_name, f"Warning: python-ldap not available. Install with: pip install python-ldap. Error: {e}")
        except Exception as e:
            self.ldap_available = False
            self.ldap_error = Exception
            self.ldap_invalid_credentials = Exception
            self.ldap_no_such_object = Exception
            Output.Console(self.plugin_name, f"Warning: LDAP import failed with unexpected error: {e}")
    
    def get_available_commands(self) -> List[str]:
        """
        Return available commands for this plugin.
        
        Returns:
            List of available command names
        """
        # Ensure ldap_available is initialized
        if not hasattr(self, 'ldap_available'):
            self.ldap_available = False
            
        if self.ldap_available:
            return [
                "connect", "disconnect", "search", "search_users", "search_groups",
                "search_computers", "authenticate", "bind", "unbind", "verify_credentials",
                "create_user", "modify_user", "delete_user", "enable_user", "disable_user",
                "reset_password", "unlock_user", "get_user_info", "list_users",
                "create_group", "modify_group", "delete_group", "add_user_to_group",
                "remove_user_from_group", "get_group_info", "list_groups",
                "get_schema", "get_dn_info", "list_attributes", "get_base_dn"
            ]
        else:
            return ["check_dependencies", "get_plugin_info"]
    
    def execute(self, operator: str, config: Dict[str, Any]) -> Any:
        """
        Execute a plugin operator.
        
        Args:
            operator: The operator to execute
            config: Configuration dictionary for the operator
            
        Returns:
            The result of the operator execution
        """
        try:
            # Check dependencies for critical commands
            if operator in ["connect", "authenticate", "search"] and not self.ldap_available:
                raise RuntimeError("LDAP library not available. Install python-ldap")
            
            if operator == "connect":
                return self._connect(config)
            elif operator == "disconnect":
                return self._disconnect(config)
            elif operator == "search":
                return self._search(config)
            elif operator == "search_users":
                return self._search_users(config)
            elif operator == "search_groups":
                return self._search_groups(config)
            elif operator == "search_computers":
                return self._search_computers(config)
            elif operator == "authenticate":
                return self._authenticate(config)
            elif operator == "bind":
                return self._bind(config)
            elif operator == "unbind":
                return self._unbind(config)
            elif operator == "verify_credentials":
                return self._verify_credentials(config)
            elif operator == "create_user":
                return self._create_user(config)
            elif operator == "modify_user":
                return self._modify_user(config)
            elif operator == "delete_user":
                return self._delete_user(config)
            elif operator == "enable_user":
                return self._enable_user(config)
            elif operator == "disable_user":
                return self._disable_user(config)
            elif operator == "reset_password":
                return self._reset_password(config)
            elif operator == "unlock_user":
                return self._unlock_user(config)
            elif operator == "get_user_info":
                return self._get_user_info(config)
            elif operator == "list_users":
                return self._list_users(config)
            elif operator == "create_group":
                return self._create_group(config)
            elif operator == "modify_group":
                return self._modify_group(config)
            elif operator == "delete_group":
                return self._delete_group(config)
            elif operator == "add_user_to_group":
                return self._add_user_to_group(config)
            elif operator == "remove_user_from_group":
                return self._remove_user_from_group(config)
            elif operator == "get_group_info":
                return self._get_group_info(config)
            elif operator == "list_groups":
                return self._list_groups(config)
            elif operator == "get_schema":
                return self._get_schema(config)
            elif operator == "get_dn_info":
                return self._get_dn_info(config)
            elif operator == "list_attributes":
                return self._list_attributes(config)
            elif operator == "get_base_dn":
                return self._get_base_dn(config)
            elif operator == "check_dependencies":
                return self.check_dependencies()
            elif operator == "get_plugin_info":
                return self.get_plugin_info()
            else:
                raise ValueError(f"Unknown operator: {operator}")
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing operator '{operator}': {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "operator": operator
            }
    
    def meta_hook(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Meta hook for LDAP plugin configuration.
        Called by the meta plugin to configure LDAP connections before execution.
        
        Args:
            config: Configuration from meta section
            
        Returns:
            Configuration result
        """
        try:
            Output.Console(self.plugin_name, f"Processing meta hook configuration: {config}")
            
            # Store meta configuration
            self.meta_config = config
            
            # Process options
            options = config.get("options", {})
            
            # Process preconfigured connections
            for connection_name, connection_config in options.items():
                if isinstance(connection_config, dict):
                    self.preconfigured_connections[connection_name] = connection_config
                    Output.Console(self.plugin_name, f"Preconfigured connection: {connection_name}")
                    
                    # Auto-connect if specified
                    if connection_config.get("auto_connect", False):
                        try:
                            self._auto_connect_connection(connection_name, connection_config)
                        except Exception as e:
                            Output.Console(self.plugin_name, f"Auto-connect failed for {connection_name}: {str(e)}")
            
            return {
                "status": "success",
                "message": "LDAP meta configuration processed",
                "connections": list(self.preconfigured_connections.keys())
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error in meta hook: {str(e)}")
            return {
                "status": "error",
                "message": f"Meta hook error: {str(e)}"
            }
    
    def _connect(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Connect to LDAP server."""
        server = config.get("server")
        if not server:
            raise ValueError("Server address is required")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPConnection import LDAPConnection
        connection = LDAPConnection(
            server=server,
            port=config.get("port", 389),
            username=config.get("username"),
            password=config.get("password"),
            use_ssl=config.get("use_ssl", False),
            use_tls=config.get("use_tls", False)
        )
        
        result = connection.connect()
        if result["status"] == "success":
            connection_name = config.get("name", f"ldap_{len(self.connections)}")
            self.connections[connection_name] = connection
            result["connection_name"] = connection_name
        
        return result
    
    def _disconnect(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Disconnect from LDAP server."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name in self.connections:
            result = self.connections[connection_name].disconnect()
            del self.connections[connection_name]
            Output.Console(self.plugin_name, f"LDAP connection '{connection_name}' disconnected")
        else:
            result = {"status": "error", "message": f"Connection '{connection_name}' not found"}
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _test_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test LDAP connection."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name in self.connections:
            result = self.connections[connection_name].test_connection()
        else:
            result = {"status": "error", "message": f"Connection '{connection_name}' not found"}
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _list_connections(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """List active LDAP connections."""
        connections = {}
        for name, conn in self.connections.items():
            connections[name] = {
                "server": conn.server,
                "port": conn.port,
                "connected": conn.is_connected()
            }
        
        result = {
            "status": "success",
            "connections": connections,
            "count": len(connections)
        }
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    # Search operations
    def _search(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform LDAP search."""
        connection_name = config.get("connection_name", "default")
        base_dn = config.get("base_dn")
        search_filter = config.get("search_filter")
        attributes = config.get("attributes", ["*"])
        scope = config.get("scope", "subtree")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPSearch import LDAPSearch
        result = self.search.search(
            connection=self.connections[connection_name],
            base_dn=base_dn,
            search_filter=search_filter,
            attributes=attributes,
            scope=scope
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _search_users(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Search for users."""
        connection_name = config.get("connection_name", "default")
        base_dn = config.get("base_dn")
        search_filter = config.get("search_filter", "(objectClass=person)")
        attributes = config.get("attributes", ["cn", "uid", "mail", "sn", "givenName"])
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPSearch import LDAPSearch
        result = self.search.search_users(
            connection=self.connections[connection_name],
            base_dn=base_dn,
            search_filter=search_filter,
            attributes=attributes
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _search_groups(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Search for groups."""
        connection_name = config.get("connection_name", "default")
        base_dn = config.get("base_dn")
        search_filter = config.get("search_filter", "(objectClass=group)")
        attributes = config.get("attributes", ["cn", "description", "member"])
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPSearch import LDAPSearch
        result = self.search.search_groups(
            connection=self.connections[connection_name],
            base_dn=base_dn,
            search_filter=search_filter,
            attributes=attributes
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _search_computers(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Search for computers."""
        connection_name = config.get("connection_name", "default")
        base_dn = config.get("base_dn")
        search_filter = config.get("search_filter", "(objectClass=computer)")
        attributes = config.get("attributes", ["cn", "dNSHostName", "operatingSystem"])
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPSearch import LDAPSearch
        result = self.search.search_computers(
            connection=self.connections[connection_name],
            base_dn=base_dn,
            search_filter=search_filter,
            attributes=attributes
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    # Authentication methods
    def _authenticate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate user against LDAP."""
        connection_name = config.get("connection_name", "default")
        username = config.get("username")
        password = config.get("password")
        base_dn = config.get("base_dn")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPConnection import LDAPConnection
        result = self.connections[connection_name].authenticate(
            username=username,
            password=password,
            base_dn=base_dn
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _bind(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Bind to LDAP with credentials."""
        connection_name = config.get("connection_name", "default")
        username = config.get("username")
        password = config.get("password")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPConnection import LDAPConnection
        result = self.connections[connection_name].bind(username, password)
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _unbind(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Unbind from LDAP."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPConnection import LDAPConnection
        result = self.connections[connection_name].unbind()
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _verify_credentials(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Verify user credentials."""
        connection_name = config.get("connection_name", "default")
        username = config.get("username")
        password = config.get("password")
        base_dn = config.get("base_dn")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPConnection import LDAPConnection
        result = self.connections[connection_name].verify_credentials(
            username=username,
            password=password,
            base_dn=base_dn
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    # User management methods
    def _create_user(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPUserManagement import LDAPUserManagement
        result = self.user_management.create_user(
            connection=self.connections[connection_name],
            config=config
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _modify_user(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Modify user attributes."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPUserManagement import LDAPUserManagement
        result = self.user_management.modify_user(
            connection=self.connections[connection_name],
            config=config
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _delete_user(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a user."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPUserManagement import LDAPUserManagement
        result = self.user_management.delete_user(
            connection=self.connections[connection_name],
            config=config
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _enable_user(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Enable a user account."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPUserManagement import LDAPUserManagement
        result = self.user_management.enable_user(
            connection=self.connections[connection_name],
            config=config
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _disable_user(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Disable a user account."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPUserManagement import LDAPUserManagement
        result = self.user_management.disable_user(
            connection=self.connections[connection_name],
            config=config
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _reset_password(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Reset user password."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPUserManagement import LDAPUserManagement
        result = self.user_management.reset_password(
            connection=self.connections[connection_name],
            config=config
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _unlock_user(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Unlock a user account."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPUserManagement import LDAPUserManagement
        result = self.user_management.unlock_user(
            connection=self.connections[connection_name],
            config=config
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _get_user_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get user information."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPUserManagement import LDAPUserManagement
        result = self.user_management.get_user_info(
            connection=self.connections[connection_name],
            config=config
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _list_users(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """List all users."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPUserManagement import LDAPUserManagement
        result = self.user_management.list_users(
            connection=self.connections[connection_name],
            config=config
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    # Group management methods
    def _create_group(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new group."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPGroupManagement import LDAPGroupManagement
        result = self.group_management.create_group(
            connection=self.connections[connection_name],
            config=config
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _modify_group(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Modify group attributes."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPGroupManagement import LDAPGroupManagement
        result = self.group_management.modify_group(
            connection=self.connections[connection_name],
            config=config
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _delete_group(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a group."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPGroupManagement import LDAPGroupManagement
        result = self.group_management.delete_group(
            connection=self.connections[connection_name],
            config=config
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _add_user_to_group(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Add user to group."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPGroupManagement import LDAPGroupManagement
        result = self.group_management.add_user_to_group(
            connection=self.connections[connection_name],
            config=config
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _remove_user_from_group(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Remove user from group."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPGroupManagement import LDAPGroupManagement
        result = self.group_management.remove_user_from_group(
            connection=self.connections[connection_name],
            config=config
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _get_group_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get group information."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPGroupManagement import LDAPGroupManagement
        result = self.group_management.get_group_info(
            connection=self.connections[connection_name],
            config=config
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _list_groups(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """List all groups."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPGroupManagement import LDAPGroupManagement
        result = self.group_management.list_groups(
            connection=self.connections[connection_name],
            config=config
        )
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    # Schema and structure methods
    def _get_schema(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get LDAP schema information."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPConnection import LDAPConnection
        result = self.connections[connection_name].get_schema()
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _get_dn_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about a DN."""
        connection_name = config.get("connection_name", "default")
        dn = config.get("dn")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not dn:
            raise ValueError("DN is required")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPConnection import LDAPConnection
        result = self.connections[connection_name].get_dn_info(dn)
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _list_attributes(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """List available attributes."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPConnection import LDAPConnection
        result = self.connections[connection_name].list_attributes()
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _get_base_dn(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get base DN information."""
        connection_name = config.get("connection_name", "default")
        
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        
        if not self.ldap_available:
            raise RuntimeError("LDAP library not available. Install python-ldap")

        from .LDAPConnection import LDAPConnection
        result = self.connections[connection_name].get_base_dn()
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    # Utility methods
    def check_dependencies(self) -> Dict[str, Any]:
        """Check plugin dependencies."""
        result = {
            "status": "success",
            "dependencies": {
                "python_ldap": self.ldap_available,
                "system_tools": self._check_system_dependencies()
            },
            "all_satisfied": self.ldap_available and self._check_system_dependencies()
        }
        
        return result
    
    def _system_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get system information."""
        import platform
        import sys
        
        result = {
            "status": "success",
            "system": {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "python_version": sys.version,
                "architecture": platform.architecture()[0]
            },
            "ldap_available": self.ldap_available
        }
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _test_functionality(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test plugin functionality."""
        result = {
            "status": "success",
            "tests": {
                "dependencies": self.check_dependencies(),
                "system_info": self._system_info({}),
                "plugin_info": self.get_plugin_info()
            }
        }
        
        if "result" in config:
            self.set_variable(config["id"], result)
        
        return result
    
    def _check_system_dependencies(self) -> bool:
        """Check if system dependencies are available."""
        import subprocess
        
        for tool in self.SYSTEM_DEPENDENCIES:
            try:
                subprocess.run([tool, "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False
        return True
    
    def _auto_connect_connection(self, connection_name: str, connection_config: Dict[str, Any]) -> None:
        """Auto-connect to a preconfigured connection."""
        try:
            self._connect({
                "connection_name": connection_name,
                **connection_config
            })
        except Exception as e:
            Output.Console(self.plugin_name, f"Auto-connect failed for {connection_name}: {str(e)}")
    
    def cleanup(self):
        """Cleanup plugin resources."""
        # Disconnect all connections
        for connection_name in list(self.connections.keys()):
            try:
                self._disconnect({"connection_name": connection_name})
            except Exception as e:
                Output.Console(self.plugin_name, f"Error disconnecting {connection_name}: {str(e)}")
        
        super().cleanup()