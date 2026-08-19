"""
SQLite Plugin Implementation
==========================

Main implementation of the SQLite plugin for Sugar.
Provides SQLite database operations including connection management, 
query execution, transaction handling, and database administration.
"""

import os
import sqlite3
import json
import csv
import time
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from contextlib import contextmanager

from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output

class SQLitePlugin(PluginBase):
    """
    SQLite plugin for Sugar.
    
    Provides SQLite database operations including:
    - Connection management
    - SQL query execution
    - Transaction handling
    - Database administration
    - Data import/export
    - Backup and restore
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "SQLite database operations plugin for Sugar"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    
    # No external dependencies required - SQLite3 is built into Python
    DEPENDENCIES = []
    REQUIREMENTS = []
    
    # System dependencies (SQLite should be available)
    SYSTEM_DEPENDENCIES = []
    
    # Hardware requirements
    HARDWARE_REQUIREMENTS = {
        "min_ram_gb": 1,
        "min_disk_gb": 0.1,
        "min_cpu_cores": 1
    }
    
    # Permission requirements
    PERMISSION_REQUIREMENTS = {
        "network_access": False,
        "write_access": ["./data", "./backups"],
        "read_access": ["./data", "./backups"]
    }
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the SQLite plugin.
        
        Args:
            context: Sugar service context
            plugin_config: Plugin configuration
        """
        super().__init__(context, plugin_config)
        
        # Database connection state
        self.connection = None
        self.database_path = None
        self.in_transaction = False
        self.savepoints = []
        
        # Plugin configuration
        self.config = plugin_config or {}
        self.timeout = self.config.get("timeout", 30.0)
        self.check_same_thread = self.config.get("check_same_thread", True)
        self.isolation_level = self.config.get("isolation_level", None)
        
        Output.Console(self.plugin_name, "SQLite plugin initialized")
    
    def get_available_commands(self) -> List[str]:
        """
        Get list of available SQLite commands.
        
        Returns:
            List of available command names
        """
        return [
            # Connection management
            "connect",
            "disconnect",
            "test_connection",
            
            # Basic operations
            "execute",
            "query",
            "select",
            
            # Table operations
            "create_table",
            "insert",
            "update", 
            "delete",
            "list_tables",
            "describe_table",
            "get_table_info",
            
            # Database administration
            "backup",
            "restore",
            "vacuum",
            "analyze",
            "check_integrity",
            "get_indexes",
            "get_triggers",
            "get_views",
            
            # Data import/export
            "export_data",
            "import_data",
            
            # Transaction management
            "begin_transaction",
            "commit",
            "rollback",
            "savepoint",
            "rollback_to_savepoint",
            "release_savepoint"
        ]
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """
        Execute a SQLite command.
        
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
            elif command == "select":
                return self._select_data(config)
            elif command == "create_table":
                return self._create_table(config)
            elif command == "insert":
                return self._insert_data(config)
            elif command == "update":
                return self._update_data(config)
            elif command == "delete":
                return self._delete_data(config)
            elif command == "list_tables":
                return self._list_tables(config)
            elif command == "describe_table":
                return self._describe_table(config)
            elif command == "backup":
                return self._backup_database(config)
            elif command == "restore":
                return self._restore_database(config)
            elif command == "vacuum":
                return self._vacuum_database(config)
            elif command == "analyze":
                return self._analyze_database(config)
            elif command == "check_integrity":
                return self._check_integrity(config)
            elif command == "get_table_info":
                return self._get_table_info(config)
            elif command == "get_indexes":
                return self._get_indexes(config)
            elif command == "get_triggers":
                return self._get_triggers(config)
            elif command == "get_views":
                return self._get_views(config)
            elif command == "export_data":
                return self._export_data(config)
            elif command == "import_data":
                return self._import_data(config)
            elif command == "begin_transaction":
                return self._begin_transaction(config)
            elif command == "commit":
                return self._commit_transaction(config)
            elif command == "rollback":
                return self._rollback_transaction(config)
            elif command == "savepoint":
                return self._create_savepoint(config)
            elif command == "rollback_to_savepoint":
                return self._rollback_to_savepoint(config)
            elif command == "release_savepoint":
                return self._release_savepoint(config)
            elif command == "test_connection":
                return self._test_connection(config)
            else:
                raise ValueError(f"Unknown command: {command}")
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing {command}: {str(e)}")
            raise
    
    def _connect(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Establish SQLite database connection.
        
        Args:
            config: Connection configuration
            
        Returns:
            Connection result
        """
        database_path = config.get("database_path")
        if not database_path:
            raise ValueError("database_path is required")
        
        # Handle environment variable substitution
        if database_path.startswith("env(") and database_path.endswith(")"):
            env_var = database_path[4:-1].strip()
            database_path = os.environ.get(env_var)
            if not database_path:
                raise ValueError(f"Environment variable '{env_var}' not set")
        
        # Ensure directory exists
        db_dir = os.path.dirname(database_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        try:
            # Close existing connection
            if self.connection:
                self._disconnect({})
            
            # Create connection
            self.connection = sqlite3.connect(
                database_path,
                timeout=self.timeout,
                check_same_thread=self.check_same_thread,
                isolation_level=self.isolation_level
            )
            
            # Enable foreign keys
            self.connection.execute("PRAGMA foreign_keys = ON")
            
            # Set other pragmas
            self.connection.execute("PRAGMA journal_mode = WAL")
            self.connection.execute("PRAGMA synchronous = NORMAL")
            
            self.database_path = database_path
            
            Output.Console(self.plugin_name, f"Connected to SQLite database: {database_path}")
            
            return {
                "success": True,
                "database_path": database_path,
                "message": "Connected successfully"
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Connection failed: {str(e)}")
            raise
    
    def _disconnect(self, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Close SQLite database connection.
        
        Args:
            config: Disconnect configuration
            
        Returns:
            Disconnect result
        """
        if self.connection:
            # Rollback any pending transaction
            if self.in_transaction:
                self.connection.rollback()
                self.in_transaction = False
                self.savepoints = []
            
            self.connection.close()
            self.connection = None
            self.database_path = None
            
            Output.Console(self.plugin_name, "SQLite connection closed")
        
        return {
            "success": True,
            "message": "Disconnected successfully"
        }
    
    def _execute_sql(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute SQL statement.
        
        Args:
            config: SQL execution configuration
            
        Returns:
            Execution result
        """
        if not self.connection:
            raise RuntimeError("No database connection. Use 'connect' first.")
        
        sql = config.get("sql")
        if not sql:
            raise ValueError("SQL statement is required")
        
        params = config.get("params", [])
        result_variable = config.get("result")
        
        start_time = time.time()
        
        try:
            # Process dynamic values (${variable})
            sql, params = self._process_dynamic_values(sql, params)
            
            # Execute query
            cursor = self.connection.cursor()
            cursor.execute(sql, params)
            
            # Get results
            if sql.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                # Convert to list of dictionaries
                result_data = []
                for row in rows:
                    result_data.append(dict(zip(columns, row)))
                
                result = {
                    "success": True,
                    "rows_affected": len(result_data),
                    "data": result_data,
                    "columns": columns,
                    "execution_time": time.time() - start_time
                }
            else:
                # For non-SELECT statements
                self.connection.commit()
                result = {
                    "success": True,
                    "rows_affected": cursor.rowcount,
                    "lastrowid": cursor.lastrowid,
                    "execution_time": time.time() - start_time
                }
            
            cursor.close()
            
            # Store result in variable if specified
            if result_variable:
                self.set_variable(result_variable, result)
            
            return result
            
        except sqlite3.Error as e:
            Output.Console(self.plugin_name, f"SQLite error: {str(e)}")
            raise
    
    def _query_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute SELECT query and return data.
        
        Args:
            config: Query configuration
            
        Returns:
            Query result
        """
        return self._execute_sql(config)
    
    def _select_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute SELECT query with simplified syntax.
        
        Args:
            config: Select configuration
            
        Returns:
            Select result
        """
        table = config.get("table")
        columns = config.get("columns", "*")
        where = config.get("where")
        order_by = config.get("order_by")
        limit = config.get("limit")
        offset = config.get("offset")
        
        if not table:
            raise ValueError("Table name is required")
        
        # Build SQL query
        sql = f"SELECT {columns} FROM {table}"
        params = []
        
        if where:
            sql += f" WHERE {where}"
        
        if order_by:
            sql += f" ORDER BY {order_by}"
        
        if limit:
            sql += f" LIMIT {limit}"
        
        if offset:
            sql += f" OFFSET {offset}"
        
        return self._execute_sql({
            "sql": sql,
            "params": params,
            "result": config.get("result")
        })
    
    def _create_table(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new table.
        
        Args:
            config: Table creation configuration
            
        Returns:
            Creation result
        """
        table_name = config.get("table_name")
        columns = config.get("columns")
        
        if not table_name:
            raise ValueError("table_name is required")
        if not columns:
            raise ValueError("columns definition is required")
        
        # Build CREATE TABLE SQL
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("
        column_definitions = []
        
        for column in columns:
            name = column.get("name")
            data_type = column.get("type")
            constraints = column.get("constraints", "")
            
            if not name or not data_type:
                raise ValueError("Column name and type are required")
            
            column_def = f"{name} {data_type}"
            if constraints:
                column_def += f" {constraints}"
            
            column_definitions.append(column_def)
        
        sql += ", ".join(column_definitions) + ")"
        
        return self._execute_sql({
            "sql": sql,
            "result": config.get("result")
        })
    
    def _insert_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert data into table.
        
        Args:
            config: Insert configuration
            
        Returns:
            Insert result
        """
        table = config.get("table")
        data = config.get("data")
        
        if not table:
            raise ValueError("Table name is required")
        if not data:
            raise ValueError("Data is required")
        
        if isinstance(data, dict):
            # Single row insert
            columns = list(data.keys())
            values = list(data.values())
            placeholders = ", ".join(["?" for _ in values])
            
            sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            
            return self._execute_sql({
                "sql": sql,
                "params": values,
                "result": config.get("result")
            })
        elif isinstance(data, list):
            # Multiple rows insert
            if not data:
                raise ValueError("Data list cannot be empty")
            
            columns = list(data[0].keys())
            placeholders = ", ".join(["?" for _ in columns])
            sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            
            cursor = self.connection.cursor()
            cursor.executemany(sql, [list(row.values()) for row in data])
            self.connection.commit()
            
            result = {
                "success": True,
                "rows_affected": cursor.rowcount,
                "lastrowid": cursor.lastrowid
            }
            
            cursor.close()
            
            if config.get("result"):
                self.set_variable(config["result"], result)
            
            return result
        else:
            raise ValueError("Data must be a dictionary or list of dictionaries")
    
    def _update_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update data in table.
        
        Args:
            config: Update configuration
            
        Returns:
            Update result
        """
        table = config.get("table")
        data = config.get("data")
        where = config.get("where")
        
        if not table:
            raise ValueError("Table name is required")
        if not data:
            raise ValueError("Data is required")
        
        # Build UPDATE SQL
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        sql = f"UPDATE {table} SET {set_clause}"
        params = list(data.values())
        
        if where:
            sql += f" WHERE {where}"
        
        return self._execute_sql({
            "sql": sql,
            "params": params,
            "result": config.get("result")
        })
    
    def _delete_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete data from table.
        
        Args:
            config: Delete configuration
            
        Returns:
            Delete result
        """
        table = config.get("table")
        where = config.get("where")
        
        if not table:
            raise ValueError("Table name is required")
        
        # Build DELETE SQL
        sql = f"DELETE FROM {table}"
        params = []
        
        if where:
            sql += f" WHERE {where}"
        
        return self._execute_sql({
            "sql": sql,
            "params": params,
            "result": config.get("result")
        })
    
    def _list_tables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        List all tables in the database.
        
        Args:
            config: List tables configuration
            
        Returns:
            Tables list
        """
        sql = """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
        
        return self._execute_sql({
            "sql": sql,
            "result": config.get("result")
        })
    
    def _describe_table(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Describe table structure.
        
        Args:
            config: Describe table configuration
            
        Returns:
            Table description
        """
        table = config.get("table")
        if not table:
            raise ValueError("Table name is required")
        
        sql = f"PRAGMA table_info({table})"
        
        return self._execute_sql({
            "sql": sql,
            "result": config.get("result")
        })
    
    def _backup_database(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create database backup.
        
        Args:
            config: Backup configuration
            
        Returns:
            Backup result
        """
        backup_path = config.get("backup_path")
        if not backup_path:
            raise ValueError("backup_path is required")
        
        if not self.connection:
            raise RuntimeError("No database connection")
        
        try:
            # Ensure backup directory exists
            backup_dir = os.path.dirname(backup_path)
            if backup_dir and not os.path.exists(backup_dir):
                os.makedirs(backup_dir, exist_ok=True)
            
            # Create backup connection
            backup_conn = sqlite3.connect(backup_path)
            
            # Backup database
            self.connection.backup(backup_conn)
            
            backup_conn.close()
            
            Output.Console(self.plugin_name, f"Database backed up to: {backup_path}")
            
            return {
                "success": True,
                "backup_path": backup_path,
                "message": "Backup completed successfully"
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Backup failed: {str(e)}")
            raise
    
    def _restore_database(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Restore database from backup.
        
        Args:
            config: Restore configuration
            
        Returns:
            Restore result
        """
        backup_path = config.get("backup_path")
        if not backup_path:
            raise ValueError("backup_path is required")
        
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        try:
            # Close current connection
            self._disconnect({})
            
            # Copy backup to current database
            shutil.copy2(backup_path, self.database_path)
            
            # Reconnect
            self._connect({"database_path": self.database_path})
            
            Output.Console(self.plugin_name, f"Database restored from: {backup_path}")
            
            return {
                "success": True,
                "backup_path": backup_path,
                "message": "Restore completed successfully"
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Restore failed: {str(e)}")
            raise
    
    def _vacuum_database(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vacuum database to reclaim space.
        
        Args:
            config: Vacuum configuration
            
        Returns:
            Vacuum result
        """
        return self._execute_sql({
            "sql": "VACUUM",
            "result": config.get("result")
        })
    
    def _analyze_database(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze database for query optimization.
        
        Args:
            config: Analyze configuration
            
        Returns:
            Analyze result
        """
        return self._execute_sql({
            "sql": "ANALYZE",
            "result": config.get("result")
        })
    
    def _check_integrity(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check database integrity.
        
        Args:
            config: Integrity check configuration
            
        Returns:
            Integrity check result
        """
        return self._execute_sql({
            "sql": "PRAGMA integrity_check",
            "result": config.get("result")
        })
    
    def _get_table_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed table information.
        
        Args:
            config: Table info configuration
            
        Returns:
            Table information
        """
        table = config.get("table")
        if not table:
            raise ValueError("Table name is required")
        
        return self._execute_sql({
            "sql": f"PRAGMA table_info({table})",
            "result": config.get("result")
        })
    
    def _get_indexes(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get indexes for a table.
        
        Args:
            config: Indexes configuration
            
        Returns:
            Indexes information
        """
        table = config.get("table")
        if not table:
            raise ValueError("Table name is required")
        
        sql = f"PRAGMA index_list({table})"
        
        return self._execute_sql({
            "sql": sql,
            "result": config.get("result")
        })
    
    def _get_triggers(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get triggers for a table.
        
        Args:
            config: Triggers configuration
            
        Returns:
            Triggers information
        """
        table = config.get("table")
        if not table:
            raise ValueError("Table name is required")
        
        sql = f"PRAGMA trigger_list({table})"
        
        return self._execute_sql({
            "sql": sql,
            "result": config.get("result")
        })
    
    def _get_views(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get all views in the database.
        
        Args:
            config: Views configuration
            
        Returns:
            Views information
        """
        sql = """
        SELECT name FROM sqlite_master 
        WHERE type='view'
        ORDER BY name
        """
        
        return self._execute_sql({
            "sql": sql,
            "result": config.get("result")
        })
    
    def _export_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export table data to file.
        
        Args:
            config: Export configuration
            
        Returns:
            Export result
        """
        table = config.get("table")
        file_path = config.get("file_path")
        format_type = config.get("format", "csv")
        
        if not table:
            raise ValueError("Table name is required")
        if not file_path:
            raise ValueError("file_path is required")
        
        # Get table data
        result = self._select_data({"table": table})
        data = result.get("data", [])
        
        if not data:
            return {
                "success": True,
                "message": "No data to export",
                "rows_exported": 0
            }
        
        try:
            # Ensure directory exists
            file_dir = os.path.dirname(file_path)
            if file_dir and not os.path.exists(file_dir):
                os.makedirs(file_dir, exist_ok=True)
            
            if format_type.lower() == "csv":
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
            
            elif format_type.lower() == "json":
                with open(file_path, 'w', encoding='utf-8') as jsonfile:
                    json.dump(data, jsonfile, indent=2, ensure_ascii=False)
            
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            Output.Console(self.plugin_name, f"Data exported to: {file_path}")
            
            return {
                "success": True,
                "file_path": file_path,
                "format": format_type,
                "rows_exported": len(data),
                "message": "Export completed successfully"
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Export failed: {str(e)}")
            raise
    
    def _import_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Import data from file to table.
        
        Args:
            config: Import configuration
            
        Returns:
            Import result
        """
        table = config.get("table")
        file_path = config.get("file_path")
        format_type = config.get("format", "csv")
        
        if not table:
            raise ValueError("Table name is required")
        if not file_path:
            raise ValueError("file_path is required")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Import file not found: {file_path}")
        
        try:
            data = []
            
            if format_type.lower() == "csv":
                with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    data = [row for row in reader]
            
            elif format_type.lower() == "json":
                with open(file_path, 'r', encoding='utf-8') as jsonfile:
                    data = json.load(jsonfile)
            
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            if not data:
                return {
                    "success": True,
                    "message": "No data to import",
                    "rows_imported": 0
                }
            
            # Insert data
            result = self._insert_data({
                "table": table,
                "data": data
            })
            
            Output.Console(self.plugin_name, f"Data imported from: {file_path}")
            
            return {
                "success": True,
                "file_path": file_path,
                "format": format_type,
                "rows_imported": result.get("rows_affected", 0),
                "message": "Import completed successfully"
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Import failed: {str(e)}")
            raise
    
    def _begin_transaction(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Begin a transaction.
        
        Args:
            config: Transaction configuration
            
        Returns:
            Transaction result
        """
        if self.in_transaction:
            raise RuntimeError("Transaction already in progress")
        
        self.connection.execute("BEGIN TRANSACTION")
        self.in_transaction = True
        
        Output.Console(self.plugin_name, "Transaction started")
        
        return {
            "success": True,
            "message": "Transaction started"
        }
    
    def _commit_transaction(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Commit current transaction.
        
        Args:
            config: Commit configuration
            
        Returns:
            Commit result
        """
        if not self.in_transaction:
            raise RuntimeError("No transaction in progress")
        
        self.connection.commit()
        self.in_transaction = False
        self.savepoints = []
        
        Output.Console(self.plugin_name, "Transaction committed")
        
        return {
            "success": True,
            "message": "Transaction committed"
        }
    
    def _rollback_transaction(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rollback current transaction.
        
        Args:
            config: Rollback configuration
            
        Returns:
            Rollback result
        """
        if not self.in_transaction:
            raise RuntimeError("No transaction in progress")
        
        self.connection.rollback()
        self.in_transaction = False
        self.savepoints = []
        
        Output.Console(self.plugin_name, "Transaction rolled back")
        
        return {
            "success": True,
            "message": "Transaction rolled back"
        }
    
    def _create_savepoint(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a savepoint.
        
        Args:
            config: Savepoint configuration
            
        Returns:
            Savepoint result
        """
        savepoint_name = config.get("name", f"sp_{len(self.savepoints)}")
        
        if savepoint_name in self.savepoints:
            raise ValueError(f"Savepoint '{savepoint_name}' already exists")
        
        self.connection.execute(f"SAVEPOINT {savepoint_name}")
        self.savepoints.append(savepoint_name)
        
        Output.Console(self.plugin_name, f"Savepoint created: {savepoint_name}")
        
        return {
            "success": True,
            "savepoint_name": savepoint_name,
            "message": "Savepoint created"
        }
    
    def _rollback_to_savepoint(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rollback to a savepoint.
        
        Args:
            config: Rollback configuration
            
        Returns:
            Rollback result
        """
        savepoint_name = config.get("name")
        
        if not savepoint_name:
            raise ValueError("Savepoint name is required")
        
        if savepoint_name not in self.savepoints:
            raise ValueError(f"Savepoint '{savepoint_name}' not found")
        
        self.connection.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
        
        # Remove savepoints after this one
        index = self.savepoints.index(savepoint_name)
        self.savepoints = self.savepoints[:index + 1]
        
        Output.Console(self.plugin_name, f"Rolled back to savepoint: {savepoint_name}")
        
        return {
            "success": True,
            "savepoint_name": savepoint_name,
            "message": "Rolled back to savepoint"
        }
    
    def _release_savepoint(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Release a savepoint.
        
        Args:
            config: Release configuration
            
        Returns:
            Release result
        """
        savepoint_name = config.get("name")
        
        if not savepoint_name:
            raise ValueError("Savepoint name is required")
        
        if savepoint_name not in self.savepoints:
            raise ValueError(f"Savepoint '{savepoint_name}' not found")
        
        self.connection.execute(f"RELEASE SAVEPOINT {savepoint_name}")
        self.savepoints.remove(savepoint_name)
        
        Output.Console(self.plugin_name, f"Savepoint released: {savepoint_name}")
        
        return {
            "success": True,
            "savepoint_name": savepoint_name,
            "message": "Savepoint released"
        }
    
    def _test_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test database connection.
        
        Args:
            config: Test configuration
            
        Returns:
            Test result
        """
        if not self.connection:
            return {
                "success": False,
                "message": "No database connection"
            }
        
        try:
            # Test with a simple query
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            
            if result and result[0] == 1:
                return {
                    "success": True,
                    "message": "Connection test successful",
                    "database_path": self.database_path
                }
            else:
                return {
                    "success": False,
                    "message": "Connection test failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection test failed: {str(e)}"
            }
    
    def _process_dynamic_values(self, sql: str, params: List[Any]) -> Tuple[str, List[Any]]:
        """
        Replace ${variable} with placeholders and create parameters.
        
        Args:
            sql: SQL statement
            params: Current parameters
            
        Returns:
            Processed SQL and parameters
        """
        import re
        
        pattern = r"\$\{\s*(\w+)\s*\}"
        processed_params = params.copy()
        
        def replace_var(match):
            var_name = match.group(1)
            
            # Get variable value from context
            if self.context and hasattr(self.context, 'memory_handler'):
                value = self.context.memory_handler._get_nested_variable(var_name)
            else:
                value = None
            
            if value is None:
                raise ValueError(f"Variable '{var_name}' not found")
            
            processed_params.append(value)
            return "?"
        
        processed_sql = re.sub(pattern, replace_var, sql)
        return processed_sql, processed_params
    
    def __del__(self):
        """Cleanup on plugin destruction."""
        if self.connection:
            self._disconnect({})