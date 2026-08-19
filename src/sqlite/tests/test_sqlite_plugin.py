"""
Tests for SQLite Plugin
======================

Basic tests for the SQLite plugin functionality.
"""

import unittest
import tempfile
import os
import json
from unittest.mock import Mock, patch

# Import the plugin
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from plugins.src.sqlite.src.sqlite_plugin import SQLitePlugin

class TestSQLitePlugin(unittest.TestCase):
    """Test cases for SQLitePlugin."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.plugin = SQLitePlugin()
        
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self.plugin, 'connection') and self.plugin.connection:
            self.plugin._disconnect({})
        
        # Clean up temp files
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_plugin_initialization(self):
        """Test plugin initialization."""
        self.assertIsNotNone(self.plugin)
        self.assertEqual(self.plugin.VERSION, "1.0.0")
        self.assertEqual(self.plugin.DESCRIPTION, "SQLite database operations plugin for Sugar")
        self.assertEqual(self.plugin.AUTHOR, "Sugar Team")
        self.assertEqual(self.plugin.LICENSE, "MIT")
    
    def test_get_available_commands(self):
        """Test available commands list."""
        commands = self.plugin.get_available_commands()
        self.assertIsInstance(commands, list)
        self.assertIn("connect", commands)
        self.assertIn("disconnect", commands)
        self.assertIn("execute", commands)
        self.assertIn("query", commands)
        self.assertIn("create_table", commands)
        self.assertIn("insert", commands)
        self.assertIn("select", commands)
        self.assertIn("update", commands)
        self.assertIn("delete", commands)
        self.assertIn("backup", commands)
        self.assertIn("restore", commands)
        self.assertIn("begin_transaction", commands)
        self.assertIn("commit", commands)
        self.assertIn("rollback", commands)
    
    def test_connect_success(self):
        """Test successful database connection."""
        result = self.plugin._connect({"database_path": self.db_path})
        
        self.assertTrue(result["success"])
        self.assertEqual(result["database_path"], self.db_path)
        self.assertIsNotNone(self.plugin.connection)
        self.assertEqual(self.plugin.database_path, self.db_path)
    
    def test_connect_missing_path(self):
        """Test connection with missing database path."""
        with self.assertRaises(ValueError):
            self.plugin._connect({})
    
    def test_disconnect(self):
        """Test database disconnection."""
        # First connect
        self.plugin._connect({"database_path": self.db_path})
        self.assertIsNotNone(self.plugin.connection)
        
        # Then disconnect
        result = self.plugin._disconnect({})
        
        self.assertTrue(result["success"])
        self.assertIsNone(self.plugin.connection)
        self.assertIsNone(self.plugin.database_path)
    
    def test_create_table(self):
        """Test table creation."""
        # Connect first
        self.plugin._connect({"database_path": self.db_path})
        
        # Create table
        columns = [
            {
                "name": "id",
                "type": "INTEGER",
                "constraints": "PRIMARY KEY AUTOINCREMENT"
            },
            {
                "name": "name",
                "type": "TEXT",
                "constraints": "NOT NULL"
            },
            {
                "name": "email",
                "type": "TEXT",
                "constraints": "UNIQUE"
            }
        ]
        
        result = self.plugin._create_table({
            "table_name": "users",
            "columns": columns
        })
        
        self.assertTrue(result["success"])
        
        # Verify table exists
        cursor = self.plugin.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone() is not None
        cursor.close()
        
        self.assertTrue(table_exists)
    
    def test_insert_single_row(self):
        """Test single row insertion."""
        # Connect and create table
        self.plugin._connect({"database_path": self.db_path})
        self.plugin._create_table({
            "table_name": "users",
            "columns": [
                {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                {"name": "name", "type": "TEXT", "constraints": "NOT NULL"},
                {"name": "email", "type": "TEXT"}
            ]
        })
        
        # Insert data
        data = {
            "name": "John Doe",
            "email": "john@example.com"
        }
        
        result = self.plugin._insert_data({
            "table": "users",
            "data": data
        })
        
        self.assertTrue(result["success"])
        self.assertEqual(result["rows_affected"], 1)
    
    def test_insert_multiple_rows(self):
        """Test multiple rows insertion."""
        # Connect and create table
        self.plugin._connect({"database_path": self.db_path})
        self.plugin._create_table({
            "table_name": "users",
            "columns": [
                {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                {"name": "name", "type": "TEXT", "constraints": "NOT NULL"},
                {"name": "email", "type": "TEXT"}
            ]
        })
        
        # Insert multiple rows
        data = [
            {"name": "John Doe", "email": "john@example.com"},
            {"name": "Jane Smith", "email": "jane@example.com"},
            {"name": "Bob Johnson", "email": "bob@example.com"}
        ]
        
        result = self.plugin._insert_data({
            "table": "users",
            "data": data
        })
        
        self.assertTrue(result["success"])
        self.assertEqual(result["rows_affected"], 3)
    
    def test_select_data(self):
        """Test data selection."""
        # Connect and create table
        self.plugin._connect({"database_path": self.db_path})
        self.plugin._create_table({
            "table_name": "users",
            "columns": [
                {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                {"name": "name", "type": "TEXT", "constraints": "NOT NULL"},
                {"name": "email", "type": "TEXT"}
            ]
        })
        
        # Insert test data
        self.plugin._insert_data({
            "table": "users",
            "data": [
                {"name": "John Doe", "email": "john@example.com"},
                {"name": "Jane Smith", "email": "jane@example.com"}
            ]
        })
        
        # Select data
        result = self.plugin._select_data({
            "table": "users",
            "columns": "id, name, email",
            "result": "users_data"
        })
        
        self.assertTrue(result["success"])
        self.assertEqual(result["rows_affected"], 2)
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(result["data"][0]["name"], "John Doe")
        self.assertEqual(result["data"][1]["name"], "Jane Smith")
    
    def test_update_data(self):
        """Test data update."""
        # Connect and create table
        self.plugin._connect({"database_path": self.db_path})
        self.plugin._create_table({
            "table_name": "users",
            "columns": [
                {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                {"name": "name", "type": "TEXT", "constraints": "NOT NULL"},
                {"name": "email", "type": "TEXT"}
            ]
        })
        
        # Insert test data
        self.plugin._insert_data({
            "table": "users",
            "data": {"name": "John Doe", "email": "john@example.com"}
        })
        
        # Update data
        result = self.plugin._update_data({
            "table": "users",
            "data": {"email": "john.updated@example.com"},
            "where": "name = 'John Doe'"
        })
        
        self.assertTrue(result["success"])
        self.assertEqual(result["rows_affected"], 1)
    
    def test_delete_data(self):
        """Test data deletion."""
        # Connect and create table
        self.plugin._connect({"database_path": self.db_path})
        self.plugin._create_table({
            "table_name": "users",
            "columns": [
                {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                {"name": "name", "type": "TEXT", "constraints": "NOT NULL"},
                {"name": "email", "type": "TEXT"}
            ]
        })
        
        # Insert test data
        self.plugin._insert_data({
            "table": "users",
            "data": [
                {"name": "John Doe", "email": "john@example.com"},
                {"name": "Jane Smith", "email": "jane@example.com"}
            ]
        })
        
        # Delete data
        result = self.plugin._delete_data({
            "table": "users",
            "where": "name = 'John Doe'"
        })
        
        self.assertTrue(result["success"])
        self.assertEqual(result["rows_affected"], 1)
    
    def test_list_tables(self):
        """Test listing tables."""
        # Connect and create table
        self.plugin._connect({"database_path": self.db_path})
        self.plugin._create_table({
            "table_name": "users",
            "columns": [
                {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                {"name": "name", "type": "TEXT", "constraints": "NOT NULL"}
            ]
        })
        
        # List tables
        result = self.plugin._list_tables({})
        
        self.assertTrue(result["success"])
        self.assertEqual(result["rows_affected"], 1)
        self.assertEqual(result["data"][0]["name"], "users")
    
    def test_transaction_management(self):
        """Test transaction management."""
        # Connect and create table
        self.plugin._connect({"database_path": self.db_path})
        self.plugin._create_table({
            "table_name": "accounts",
            "columns": [
                {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                {"name": "balance", "type": "REAL", "constraints": "DEFAULT 0.0"}
            ]
        })
        
        # Begin transaction
        result = self.plugin._begin_transaction({})
        self.assertTrue(result["success"])
        self.assertTrue(self.plugin.in_transaction)
        
        # Insert data
        self.plugin._insert_data({
            "table": "accounts",
            "data": {"balance": 100.0}
        })
        
        # Commit transaction
        result = self.plugin._commit_transaction({})
        self.assertTrue(result["success"])
        self.assertFalse(self.plugin.in_transaction)
        
        # Verify data was committed
        select_result = self.plugin._select_data({"table": "accounts"})
        self.assertEqual(select_result["rows_affected"], 1)
    
    def test_backup_and_restore(self):
        """Test backup and restore functionality."""
        # Connect and create table with data
        self.plugin._connect({"database_path": self.db_path})
        self.plugin._create_table({
            "table_name": "users",
            "columns": [
                {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                {"name": "name", "type": "TEXT", "constraints": "NOT NULL"}
            ]
        })
        
        self.plugin._insert_data({
            "table": "users",
            "data": {"name": "John Doe"}
        })
        
        # Create backup
        backup_path = os.path.join(self.temp_dir, 'backup.db')
        result = self.plugin._backup_database({"backup_path": backup_path})
        
        self.assertTrue(result["success"])
        self.assertTrue(os.path.exists(backup_path))
        
        # Disconnect and restore
        self.plugin._disconnect({})
        restore_path = os.path.join(self.temp_dir, 'restored.db')
        
        # Copy backup to restore location
        import shutil
        shutil.copy2(backup_path, restore_path)
        
        # Connect to restored database
        self.plugin._connect({"database_path": restore_path})
        
        # Verify data exists
        select_result = self.plugin._select_data({"table": "users"})
        self.assertEqual(select_result["rows_affected"], 1)
        self.assertEqual(select_result["data"][0]["name"], "John Doe")
        
        # Clean up
        os.remove(backup_path)
        os.remove(restore_path)
    
    def test_export_and_import_csv(self):
        """Test CSV export and import."""
        # Connect and create table with data
        self.plugin._connect({"database_path": self.db_path})
        self.plugin._create_table({
            "table_name": "users",
            "columns": [
                {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                {"name": "name", "type": "TEXT", "constraints": "NOT NULL"},
                {"name": "email", "type": "TEXT"}
            ]
        })
        
        self.plugin._insert_data({
            "table": "users",
            "data": [
                {"name": "John Doe", "email": "john@example.com"},
                {"name": "Jane Smith", "email": "jane@example.com"}
            ]
        })
        
        # Export to CSV
        csv_path = os.path.join(self.temp_dir, 'users.csv')
        result = self.plugin._export_data({
            "table": "users",
            "file_path": csv_path,
            "format": "csv"
        })
        
        self.assertTrue(result["success"])
        self.assertTrue(os.path.exists(csv_path))
        self.assertEqual(result["rows_exported"], 2)
        
        # Import from CSV to new table
        self.plugin._import_data({
            "table": "users_imported",
            "file_path": csv_path,
            "format": "csv"
        })
        
        # Verify imported data
        select_result = self.plugin._select_data({"table": "users_imported"})
        self.assertEqual(select_result["rows_affected"], 2)
        
        # Clean up
        os.remove(csv_path)
    
    def test_error_handling(self):
        """Test error handling."""
        # Test connection without database path
        with self.assertRaises(ValueError):
            self.plugin._connect({})
        
        # Test execute without connection
        with self.assertRaises(RuntimeError):
            self.plugin._execute_sql({"sql": "SELECT 1"})
        
        # Test execute without SQL
        self.plugin._connect({"database_path": self.db_path})
        with self.assertRaises(ValueError):
            self.plugin._execute_sql({})

if __name__ == '__main__':
    unittest.main()