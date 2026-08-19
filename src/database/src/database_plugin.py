"""
Database Plugin Implementation
============================

Main implementation of the Database plugin for Sugar.
Provides database operations including connection management, query execution,
and transaction handling through SQLAlchemy.
"""

import os
import re
import time
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output

class DatabasePlugin(PluginBase):
    """
    Database plugin for Sugar.
    
    Provides database operations including:
    - Connection management
    - SQL query execution
    - Transaction handling
    - Result processing
    - Error handling
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Database operations plugin for Sugar with SQLAlchemy support"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = ["sqlalchemy", "mysql-connector-python"]
    REQUIREMENTS = ["sqlalchemy>=1.4.0", "mysql-connector-python>=8.0.0"]
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Database plugin.
        
        Args:
            context: Sugar service context
            plugin_config: Plugin configuration
        """
        super().__init__(context, plugin_config)
        
        # Database connection state
        self.engine = None
        self.connection = None
        self.dns = None
        self.meta_config = {}  # Store meta configuration
        self.preconfigured_connections = {}  # Store preconfigured connections
        
        Output.Console(self.plugin_name, "Database plugin initialized")
    
    def meta_hook(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Meta hook for Database plugin configuration.
        Called by the meta plugin to configure database connections before execution.
        
        Args:
            config: Configuration from meta section
            
        Returns:
            Configuration result
        """
        try:
            Output.Console(self.plugin_name, f"Processing meta hook configuration: {config}")
            
            # Store meta configuration
            self.meta_config = config
            
            # Process connections
            connections = config.get("connections", {})
            
            # Process preconfigured connections
            for connection_name, connection_config in connections.items():
                if isinstance(connection_config, dict):
                    self.preconfigured_connections[connection_name] = connection_config
                    Output.Console(self.plugin_name, f"Preconfigured connection: {connection_name}")
                    
                    # Auto-connect if specified
                    if connection_config.get("auto_connect", False):
                        try:
                            self._auto_connect_database(connection_name, connection_config)
                        except Exception as e:
                            Output.Console(self.plugin_name, f"Auto-connect failed for {connection_name}: {str(e)}")
            
            return {
                "success": True,
                "connections_configured": len(self.preconfigured_connections),
                "auto_connected": len([c for c in self.preconfigured_connections.values() if c.get("auto_connect", False)])
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error in meta hook: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _auto_connect_database(self, connection_name: str, connection_config: Dict[str, Any]) -> bool:
        """Auto-connect to a preconfigured database."""
        try:
            # Create connection config
            db_config = {
                "dns": connection_config.get("dns"),
                "host": connection_config.get("host"),
                "port": connection_config.get("port"),
                "database": connection_config.get("database"),
                "username": connection_config.get("username"),
                "password": connection_config.get("password"),
                "engine_options": connection_config.get("engine_options", {})
            }
            
            # Connect
            result = self._connect(db_config)
            if result:
                Output.Console(self.plugin_name, f"Auto-connected to database: {connection_name}")
                return True
            else:
                Output.Console(self.plugin_name, f"Auto-connect failed for database: {connection_name}")
                return False
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error in auto-connect for {connection_name}: {str(e)}")
            return False
    
    def get_available_commands(self) -> List[str]:
        """
        Get list of available database commands.
        
        Returns:
            List of available command names
        """
        return [
            # Connection management
            "connect",
            "disconnect",
            "test_connection",
            
            # Query execution
            "execute",
            "execute_many",
            "query",
            
            # Transaction management
            "begin_transaction",
            "commit",
            "rollback",
            
            # Connection info
            "get_connection_info",
            "list_tables",
            "describe_table"
        ]
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """
        Execute a database command.
        
        Args:
            command: Command to execute
            config: Configuration for the command
            
        Returns:
            Command result
        """
        try:
            if command == "connect":
                return self._connect(config)
            elif command == "disconnect":
                return self._disconnect(config)
            elif command == "execute":
                return self._execute_sql(config)
            elif command == "query":
                return self._query_data(config)
            elif command == "begin_transaction":
                return self._begin_transaction(config)
            elif command == "commit":
                return self._commit_transaction(config)
            elif command == "rollback":
                return self._rollback_transaction(config)
            elif command == "test_connection":
                return self._test_connection(config)
            elif command == "get_connection_info":
                return self._get_connection_info(config)
            elif command == "list_tables":
                return self._list_tables(config)
            elif command == "describe_table":
                return self._describe_table(config)
            else:
                raise ValueError(f"Unknown command: {command}")
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing {command}: {str(e)}")
            raise
    
    def _connect(self, config: Dict[str, Any]) -> bool:
        """Establish database connection."""
        dns = config.get("dns")
        if not dns:
            raise ValueError("DNS configuration required")
        
        # Handle environment variable substitution
        if dns.startswith("env(") and dns.endswith(")"):
            env_var = dns[4:-1].strip()
            dns = os.environ.get(env_var)
            if not dns:
                raise ValueError(f"Environment variable '{env_var}' not set")
        
        self.dns = dns
        self._disconnect()  # Close existing connection
        
        try:
            self.engine = create_engine(self.dns)
            self.connection = self.engine.connect()
            Output.Console(self.plugin_name, f"Connected to database: {self.dns}")
            return True
        except Exception as e:
            Output.Console(self.plugin_name, f"Connection failed: {str(e)}")
            raise
    
    def _disconnect(self, config: Dict[str, Any] = None) -> bool:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
        if self.engine:
            self.engine.dispose()
            self.engine = None
        Output.Console(self.plugin_name, "Database connection closed")
        return True
    
    def _execute_sql(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SQL statement."""
        if not self.connection:
            self._connect({"dns": self.dns})
        
        sql = config.get("sql")
        if not sql:
            raise ValueError("SQL statement required")
        
        start_time = time.time()
        result = None
        
        try:
            # Process dynamic values (${variable})
            sql, params = self._process_dynamic_values(sql)
            
            # Execute query
            result = self.connection.execute(sql, params)
            
            # Handle results
            result_data = self._handle_query_result(config, result)
            
            # Handle engine options
            engine_info = self._handle_engine_options(config, result, start_time)
            
            return {
                "success": True,
                "result": result_data,
                "engine": engine_info
            }
            
        except SQLAlchemyError as e:
            return self._handle_engine_errors(config, e)
        finally:
            if result:
                result.close()
    
    def _query_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SELECT query and return data."""
        return self._execute_sql(config)
    
    def _process_dynamic_values(self, sql: str) -> tuple:
        """Replace ${variable} with placeholders and create parameters."""
        pattern = r"\$\{\s*(\w+)\s*\}"
        params = {}
        param_names = set()
        
        # Find all variable names
        for match in re.finditer(pattern, sql):
            var_name = match.group(1)
            param_names.add(var_name)
        
        # Get variable values from context
        for name in param_names:
            if self.context and hasattr(self.context, 'memory_handler'):
                value = self.context.memory_handler._get_nested_variable(name)
            else:
                value = None
            if value is None:
                raise ValueError(f"Variable '{name}' not found")
            params[name] = value
        
        # Replace in SQL
        processed_sql = re.sub(pattern, lambda m: f":{m.group(1)}", sql)
        return processed_sql, params
    
    def _handle_query_result(self, config: Dict[str, Any], result) -> Any:
        """Process and store query results."""
        # Only for queries that return data
        if not result.returns_rows:
            return None
            
        rows = result.fetchall()
        keys = result.keys()
        
        # Convert to list of dictionaries
        dict_rows = [dict(zip(keys, row)) for row in rows]
        row_count = len(dict_rows)
        
        # Handle assignment to main variable
        if "value" in config:
            var_path = config["value"]
            
            # Automatically determine appropriate format
            if row_count == 0:
                value_to_assign = None
            elif row_count == 1:
                value_to_assign = dict_rows[0]  # Single object
            else:
                value_to_assign = dict_rows     # List of objects
            
            if self.context and hasattr(self.context, 'memory_handler'):
                self.context.memory_handler._set_nested_variable(var_path, value_to_assign)
        
        # Handle extraction of specific values
        if "store" in config:
            first_row = dict_rows[0] if dict_rows else {}
            for assignment in config["store"]:
                col_name = assignment["column"]
                var_path = assignment["value"]
                value = first_row.get(col_name)
                if self.context and hasattr(self.context, 'memory_handler'):
                    self.context.memory_handler._set_nested_variable(var_path, value)
        
        return dict_rows
    
    def _handle_engine_options(self, config: Dict[str, Any], result, start_time: float) -> Dict[str, Any]:
        """Handle additional engine options."""
        engine_cfg = config.get("engine")
        if not engine_cfg:
            return {}
            
        name = engine_cfg["name"]
        var_path = engine_cfg["value"]
        value = None
        
        if name == "affected_rows":
            value = result.rowcount
        elif name == "execution_time":
            value = int((time.time() - start_time) * 1000)
        
        if value is not None and self.context and hasattr(self.context, 'memory_handler'):
            self.context.memory_handler._set_nested_variable(var_path, value)
        
        return {name: value}
    
    def _handle_engine_errors(self, config: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """Handle errors according to configuration."""
        engine_cfg = config.get("engine")
        if engine_cfg and engine_cfg["name"] == "errors":
            var_path = engine_cfg["value"]
            if self.context and hasattr(self.context, 'memory_handler'):
                self.context.memory_handler._set_nested_variable(var_path, str(error))
        
        return {
            "success": False,
            "error": str(error)
        }
    
    def _begin_transaction(self, config: Dict[str, Any]) -> bool:
        """Begin a database transaction."""
        if not self.connection:
            raise RuntimeError("No database connection")
        
        self.connection.begin()
        Output.Console(self.plugin_name, "Transaction begun")
        return True
    
    def _commit_transaction(self, config: Dict[str, Any]) -> bool:
        """Commit the current transaction."""
        if not self.connection:
            raise RuntimeError("No database connection")
        
        self.connection.commit()
        Output.Console(self.plugin_name, "Transaction committed")
        return True
    
    def _rollback_transaction(self, config: Dict[str, Any]) -> bool:
        """Rollback the current transaction."""
        if not self.connection:
            raise RuntimeError("No database connection")
        
        self.connection.rollback()
        Output.Console(self.plugin_name, "Transaction rolled back")
        return True
    
    def _test_connection(self, config: Dict[str, Any]) -> bool:
        """Test database connection."""
        try:
            if not self.connection:
                self._connect({"dns": self.dns})
            
            # Simple test query
            result = self.connection.execute("SELECT 1")
            result.close()
            return True
        except Exception as e:
            Output.Console(self.plugin_name, f"Connection test failed: {str(e)}")
            return False
    
    def _get_connection_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get database connection information."""
        return {
            "connected": self.connection is not None,
            "dns": self.dns,
            "engine": str(self.engine) if self.engine else None
        }
    
    def _list_tables(self, config: Dict[str, Any]) -> List[str]:
        """List all tables in the database."""
        if not self.connection:
            raise RuntimeError("No database connection")
        
        # This is a simplified version - actual implementation depends on database type
        result = self.connection.execute("SHOW TABLES")
        tables = [row[0] for row in result.fetchall()]
        result.close()
        return tables
    
    def _describe_table(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Describe table structure."""
        if not self.connection:
            raise RuntimeError("No database connection")
        
        table_name = config.get("table")
        if not table_name:
            raise ValueError("Table name required")
        
        result = self.connection.execute(f"DESCRIBE {table_name}")
        columns = [dict(zip(result.keys(), row)) for row in result.fetchall()]
        result.close()
        return {"table": table_name, "columns": columns}
    
    def cleanup(self):
        """Cleanup resources."""
        self._disconnect()
        Output.Console(self.plugin_name, "Database plugin cleanup completed")