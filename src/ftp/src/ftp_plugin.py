"""
FTP Plugin for Sugar
===================

A comprehensive FTP plugin that provides file transfer operations
including upload, download, directory listing, and more with support
for both standard FTP and FTPS (FTP over SSL/TLS).
"""

import os
import ftplib
import ssl
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output

class FtpPlugin(PluginBase):
    """
    FTP plugin for Sugar.
    
    Provides comprehensive FTP operations including:
    - File upload and download
    - Directory listing and creation
    - File deletion
    - Support for both FTP and FTPS
    - Permission management
    - Logging and error handling
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Comprehensive FTP operations for Sugar"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = []  # Uses only built-in modules
    REQUIREMENTS = []  # No external dependencies
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """Initialize the FTP plugin."""
        super().__init__(context, plugin_config)
        self.connection = None
        self.config = None
        self.meta_config = {}  # Store meta configuration
        self.preconfigured_connections = {}  # Store preconfigured connections
        
        Output.Console(self.plugin_name, "FTP plugin initialized")
    
    def meta_hook(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Meta hook for FTP plugin configuration.
        Called by the meta plugin to configure FTP connections before execution.
        
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
                    Output.Console(self.plugin_name, f"Preconfigured FTP connection: {connection_name}")
                    
                    # Auto-connect if specified
                    if connection_config.get("auto_connect", False):
                        try:
                            self._auto_connect_ftp(connection_name, connection_config)
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
    
    def _auto_connect_ftp(self, connection_name: str, connection_config: Dict[str, Any]) -> bool:
        """Auto-connect to a preconfigured FTP server."""
        try:
            # Create connection config
            ftp_config = {
                "host": connection_config.get("host"),
                "port": connection_config.get("port", 21),
                "username": connection_config.get("username"),
                "password": connection_config.get("password"),
                "use_ssl": connection_config.get("use_ssl", False),
                "timeout": connection_config.get("timeout", 30)
            }
            
            # Connect
            result = self._connect(ftp_config)
            if result.get("success", False):
                Output.Console(self.plugin_name, f"Auto-connected to FTP: {connection_name}")
                return True
            else:
                Output.Console(self.plugin_name, f"Auto-connect failed for FTP {connection_name}: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error in auto-connect for {connection_name}: {str(e)}")
            return False
    
    def get_available_commands(self) -> List[str]:
        """
        Get list of available FTP commands.
        
        Returns:
            List of available command names
        """
        return [
            "connect",
            "disconnect", 
            "upload",
            "download",
            "list",
            "delete",
            "mkdir",
            "exists",
            "setup",
            "execute"
        ]
    
    def execute(self, operator: str, config: Dict[str, Any]) -> Any:
        """
        Execute FTP operator.
        
        Args:
            operator: Command to execute
            config: Configuration for the operator
            
        Returns:
            Result of the operator execution
        """
        if operator == "setup":
            return self._setup_ftp(config)
        elif operator == "connect":
            return self._connect(config)
        elif operator == "disconnect":
            return self._disconnect()
        elif operator == "upload":
            return self._upload_file(config)
        elif operator == "download":
            return self._download_file(config)
        elif operator == "list":
            return self._list_directory(config)
        elif operator == "delete":
            return self._delete_file(config)
        elif operator == "mkdir":
            return self._make_directory(config)
        elif operator == "exists":
            return self._file_exists(config.get("remote_path", ""))
        elif operator == "execute":
            return self._execute_command(config)
        else:
            raise ValueError(f"Unknown FTP operator: {operator}")
    
    def _setup_ftp(self, ftp_config: dict) -> Dict[str, Any]:
        """Setup and execute complete FTP operation"""
        try:
            self.config = ftp_config
            
            # Configure logging if enabled
            if ftp_config.get("logging", {}).get("enabled", False):
                self._setup_logging(ftp_config["logging"])
            
            # Connect to server
            self._connect(ftp_config)
            
            results = []
            # Execute commands if defined
            if "commands" in ftp_config:
                for command in ftp_config["commands"]:
                    result = self._execute_command(command)
                    results.append(result)
            
            # Disconnect
            self._disconnect()
            
            return {
                "success": True,
                "results": results,
                "message": "FTP operation completed successfully"
            }
            
        except Exception as e:
            self._disconnect()
            return {
                "success": False,
                "error": str(e),
                "message": f"FTP operation failed: {e}"
            }
    
    def _setup_logging(self, logging_config: dict) -> None:
        """Setup logging system"""
        level = getattr(logging, logging_config.get("level", "INFO").upper())
        log_file = logging_config.get("log_file", "/var/log/ftp_client.log")
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(self.plugin_name)
    
    def _connect(self, ftp_config: dict) -> Dict[str, Any]:
        """Establish FTP connection"""
        host = ftp_config["host"]
        port = ftp_config.get("port", 21)
        auth = ftp_config.get("auth", {})
        security = ftp_config.get("security", {})
        timeout = ftp_config.get("timeout", 30)
        retries = ftp_config.get("retries", 2)
        
        username = auth.get("username", "anonymous")
        password = auth.get("password", "")
        
        for attempt in range(retries + 1):
            try:
                if security.get("use_tls", False):
                    # FTPS connection
                    self.connection = ftplib.FTP_TLS()
                    self.connection.connect(host, port, timeout=timeout)
                    self.connection.login(username, password)
                    
                    if security.get("verify_certificate", True):
                        self.connection.prot_p()  # Enable secure passive mode
                    else:
                        # Disable certificate verification (not recommended in production)
                        self.connection.ssl_version = ssl.PROTOCOL_TLSv1_2
                else:
                    # Standard FTP connection
                    self.connection = ftplib.FTP()
                    self.connection.connect(host, port, timeout=timeout)
                    self.connection.login(username, password)
                
                # Configure mode
                if ftp_config.get("mode", "passive") == "passive":
                    self.connection.set_pasv(True)
                else:
                    self.connection.set_pasv(False)
                
                # Configure encoding
                encoding = ftp_config.get("encoding", "utf-8")
                if hasattr(self.connection, 'encoding'):
                    self.connection.encoding = encoding
                
                self._log(f"Successfully connected to {host}:{port}")
                return {
                    "success": True,
                    "message": f"Connected to {host}:{port}",
                    "host": host,
                    "port": port
                }
                
            except Exception as e:
                if attempt < retries:
                    self._log(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    continue
                else:
                    error_msg = f"Failed to connect to {host}:{port} after {retries + 1} attempts: {e}"
                    self._log(error_msg)
                    return {
                        "success": False,
                        "error": str(e),
                        "message": error_msg
                    }
    
    def _disconnect(self) -> Dict[str, Any]:
        """Close FTP connection"""
        if self.connection:
            try:
                self.connection.quit()
                self._log("FTP connection closed")
                self.connection = None
                return {
                    "success": True,
                    "message": "Connection closed successfully"
                }
            except:
                try:
                    self.connection.close()
                except:
                    pass
                finally:
                    self.connection = None
                return {
                    "success": True,
                    "message": "Connection closed (with errors)"
                }
        return {
            "success": True,
            "message": "No connection to close"
        }
    
    def _execute_command(self, command: dict) -> Dict[str, Any]:
        """Execute individual FTP command"""
        action = command["action"]
        
        # Check permissions before executing
        if not self._check_permissions(action, command.get("remote_path", "")):
            error_msg = f"Action '{action}' not allowed for specified path"
            self._log(error_msg)
            return {
                "success": False,
                "error": "Permission denied",
                "message": error_msg
            }
        
        try:
            if action == "upload":
                return self._upload_file(command)
            elif action == "download":
                return self._download_file(command)
            elif action == "list":
                return self._list_directory(command)
            elif action == "delete":
                return self._delete_file(command)
            elif action == "mkdir":
                return self._make_directory(command)
            else:
                return {
                    "success": False,
                    "error": "Unsupported action",
                    "message": f"FTP action not supported: {action}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Command execution failed: {e}"
            }
    
    def _check_permissions(self, action: str, remote_path: str) -> bool:
        """Check if action is allowed for specified path"""
        if not self.config or "permissions" not in self.config:
            return True  # No restrictions if no permission configuration
        
        permissions = self.config["permissions"]
        default_permission = permissions.get("default", "read-write")
        
        # Check default permissions
        if not self._is_action_allowed(action, default_permission):
            return False
        
        # Check specific rules
        rules = permissions.get("rules", [])
        for rule in rules:
            rule_path = rule["path"]
            if remote_path.startswith(rule_path):
                allowed_actions = rule.get("allowed_actions", [])
                if not allowed_actions:  # Empty list = no actions allowed
                    return False
                return action in allowed_actions
        
        return True
    
    def _is_action_allowed(self, action: str, permission: str) -> bool:
        """Check if action is allowed according to permission type"""
        action_mapping = {
            "upload": ["write-only", "read-write"],
            "download": ["read-only", "read-write"],
            "list": ["read-only", "read-write"],
            "delete": ["write-only", "read-write"],
            "mkdir": ["write-only", "read-write"]
        }
        
        return permission in action_mapping.get(action, [])
    
    def _upload_file(self, command: dict) -> Dict[str, Any]:
        """Upload file to FTP server"""
        local_path = self._interpolate(command["local_path"])
        remote_path = command["remote_path"]
        overwrite = command.get("overwrite", False)
        
        if not os.path.exists(local_path):
            return {
                "success": False,
                "error": "File not found",
                "message": f"Local file not found: {local_path}"
            }
        
        # Check if remote file exists
        if not overwrite and self._file_exists(remote_path):
            return {
                "success": False,
                "error": "File exists",
                "message": f"Remote file already exists: {remote_path}"
            }
        
        try:
            with open(local_path, 'rb') as local_file:
                self.connection.storbinary(f'STOR {remote_path}', local_file)
            
            self._log(f"File uploaded successfully: {local_path} -> {remote_path}")
            return {
                "success": True,
                "message": f"File uploaded: {local_path} -> {remote_path}",
                "local_path": local_path,
                "remote_path": remote_path
            }
            
        except Exception as e:
            self._log(f"Error uploading file {local_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Upload failed: {e}"
            }
    
    def _download_file(self, command: dict) -> Dict[str, Any]:
        """Download file from FTP server"""
        remote_path = command["remote_path"]
        local_path = self._interpolate(command["local_path"])
        
        # Create local directory if it doesn't exist
        local_dir = os.path.dirname(local_path)
        if local_dir and not os.path.exists(local_dir):
            os.makedirs(local_dir, exist_ok=True)
        
        try:
            with open(local_path, 'wb') as local_file:
                self.connection.retrbinary(f'RETR {remote_path}', local_file.write)
            
            self._log(f"File downloaded successfully: {remote_path} -> {local_path}")
            return {
                "success": True,
                "message": f"File downloaded: {remote_path} -> {local_path}",
                "remote_path": remote_path,
                "local_path": local_path
            }
            
        except Exception as e:
            self._log(f"Error downloading file {remote_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Download failed: {e}"
            }
    
    def _list_directory(self, command: dict) -> Dict[str, Any]:
        """List directory contents"""
        remote_path = command["remote_path"]
        
        try:
            files = []
            self.connection.retrlines(f'LIST {remote_path}', files.append)
            
            self._log(f"Directory listed: {remote_path}")
            for file_info in files:
                self._log(f"  {file_info}")
            
            return {
                "success": True,
                "message": f"Directory listed: {remote_path}",
                "remote_path": remote_path,
                "files": files,
                "count": len(files)
            }
                
        except Exception as e:
            self._log(f"Error listing directory {remote_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"List failed: {e}"
            }
    
    def _delete_file(self, command: dict) -> Dict[str, Any]:
        """Delete file from FTP server"""
        remote_path = command["remote_path"]
        
        try:
            self.connection.delete(remote_path)
            self._log(f"File deleted: {remote_path}")
            return {
                "success": True,
                "message": f"File deleted: {remote_path}",
                "remote_path": remote_path
            }
            
        except Exception as e:
            self._log(f"Error deleting file {remote_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Delete failed: {e}"
            }
    
    def _make_directory(self, command: dict) -> Dict[str, Any]:
        """Create directory on FTP server"""
        remote_path = command["remote_path"]
        
        try:
            self.connection.mkd(remote_path)
            self._log(f"Directory created: {remote_path}")
            return {
                "success": True,
                "message": f"Directory created: {remote_path}",
                "remote_path": remote_path
            }
            
        except Exception as e:
            self._log(f"Error creating directory {remote_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Create directory failed: {e}"
            }
    
    def _file_exists(self, remote_path: str) -> bool:
        """Check if file exists on FTP server"""
        try:
            self.connection.size(remote_path)
            return True
        except:
            return False
    
    def _interpolate(self, value: str) -> str:
        """Use the task_handler's interpolation system"""
        if self.context and hasattr(self.context, 'memory_handler'):
            return self.context.memory_handler._interpolate_variables(value)
        return value
    
    def _log(self, message: str) -> None:
        """Safely log a message using Output.Console or print."""
        try:
            Output.Console(self.plugin_name, message)
        except AttributeError:
            # Handle case where Output or plugin_name is not available (e.g., in tests)
            print(f"[FtpPlugin] {message}")
    
    def get_dependency_info(self) -> Dict[str, Any]:
        """
        Get dependency information.
        
        Returns:
            Dictionary with dependency status
        """
        return {
            'built_in_modules': {
                'ftplib': True,
                'ssl': True,
                'os': True,
                'logging': True
            },
            'external_dependencies': [],
            'message': 'FTP plugin uses only built-in Python modules'
        }