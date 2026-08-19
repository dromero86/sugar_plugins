"""
SSH Plugin Implementation
========================

Main plugin class for SSH functionality.
Provides remote server management, file transfer, and command execution capabilities.
"""

import os
import time
import threading
import tempfile
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

# Suprimir warnings de deprecación de cryptography/paramiko (no afectan funcionalidad)
warnings.filterwarnings('ignore', message='.*TripleDES.*')
warnings.filterwarnings('ignore', category=DeprecationWarning, module='paramiko')
warnings.filterwarnings('ignore', category=DeprecationWarning, module='cryptography')

import paramiko
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.ssh_exception import SSHException, AuthenticationException, NoValidConnectionsError

from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output

from .SSHConnection import SSHConnection
from .SSHFileTransfer import SSHFileTransfer
from .SSHTunnel import SSHTunnel

class SSHPlugin(PluginBase):
    """
    SSH plugin for Sugar.
    
    Provides SSH functionality including:
    - Remote server connections
    - Command execution
    - File transfer (SCP/SFTP)
    - SSH tunneling
    - System monitoring
    - Service management
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "SSH plugin for Sugar with comprehensive remote server management"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = ["paramiko", "cryptography"]
    REQUIREMENTS = ["paramiko>=3.0.0", "cryptography>=3.4.0"]
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the SSH plugin.
        
        Args:
            context: Sugar service context
            plugin_config: Plugin configuration
        """
        super().__init__(context, plugin_config)
        
        # Initialize components
        self.connections: Dict[str, SSHConnection] = {}
        self.file_transfer = SSHFileTransfer(self)
        self.tunnels: Dict[str, SSHTunnel] = {}
        self.meta_config = {}  # Store meta configuration
        self.preconfigured_sessions = {}  # Store preconfigured sessions
        
        # Output.Console(self.plugin_name, "SSH plugin components initialized")
    
    def meta_hook(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Meta hook for SSH plugin configuration.
        Called by the meta plugin to configure SSH sessions before execution.
        
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
            
            # Process preconfigured sessions
            for session_name, session_config in options.items():
                if isinstance(session_config, dict):
                    self.preconfigured_sessions[session_name] = session_config
                    Output.Console(self.plugin_name, f"Preconfigured session: {session_name}")
                    
                    # Auto-connect if specified
                    if session_config.get("auto_connect", False):
                        try:
                            self._auto_connect_session(session_name, session_config)
                        except Exception as e:
                            Output.Console(self.plugin_name, f"Auto-connect failed for {session_name}: {str(e)}")
            
            return {
                "success": True,
                "sessions_configured": len(self.preconfigured_sessions),
                "auto_connected": len([s for s in self.preconfigured_sessions.values() if s.get("auto_connect", False)])
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error in meta hook: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _auto_connect_session(self, session_name: str, session_config: Dict[str, Any]) -> bool:
        """Auto-connect to a preconfigured session."""
        try:
            # Create connection config
            connection_config = {
                "session_name": session_name,
                "host": session_config.get("host"),
                "username": session_config.get("username"),
                "password": session_config.get("password"),
                "port": session_config.get("port", 22),
                "timeout": session_config.get("timeout", 30)
            }
            
            # Connect
            result = self._connect(connection_config)
            if result:
                Output.Console(self.plugin_name, f"Auto-connected to session: {session_name}")
                return True
            else:
                Output.Console(self.plugin_name, f"Auto-connect failed for session: {session_name}")
                return False
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error in auto-connect for {session_name}: {str(e)}")
            return False
    
    def get_available_commands(self) -> List[str]:
        """
        Get list of available SSH commands.
        
        Returns:
            List of available command names
        """
        return [
            # Connection management
            "connect",
            "disconnect",
            "list_sessions",
            "close_session",
            "close_all_sessions",
            
            # Command execution
            "execute",
            "execute_interactive",
            
            # File transfer
            "upload",
            "download",
            "upload_dir",
            "download_dir",
            
            # File management
            "mkdir",
            "rm",
            "ls",
            "chmod",
            "chown",
            
            # Tunneling
            "create_tunnel",
            "create_reverse_tunnel",
            "close_tunnel",
            "list_tunnels",
            
            # System information
            "system_info",
            "list_processes",
            "kill_process",
            
            # Service management
            "service_control",
            
            # Utility
            "test_connection"
        ]
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """
        Execute an SSH command.
        
        Args:
            command: Command to execute
            config: Command configuration
            
        Returns:
            Command execution result
        """
        Output.Console(self.plugin_name, f"Executing SSH command: {command}")
        
        # Interpolate variables in config
        interpolated_config = self.interpolate_variables(config)
        
        try:
            if command == "connect":
                return self._connect(interpolated_config)
            elif command == "disconnect":
                return self._disconnect(interpolated_config)
            elif command == "list_sessions":
                return self._list_sessions(interpolated_config)
            elif command == "close_session":
                return self._close_session(interpolated_config)
            elif command == "close_all_sessions":
                return self._close_all_sessions(interpolated_config)
            elif command == "execute":
                return self._execute_command(interpolated_config)
            elif command == "execute_interactive":
                return self._execute_interactive(interpolated_config)
            elif command in ["upload", "download"]:
                return self.file_transfer.transfer_file(command, interpolated_config)
            elif command in ["upload_dir", "download_dir"]:
                return self.file_transfer.transfer_directory(command, interpolated_config)
            elif command in ["mkdir", "rm", "ls", "chmod", "chown"]:
                return self._file_operations(command, interpolated_config)
            elif command in ["create_tunnel", "create_reverse_tunnel"]:
                return self._create_tunnel(command, interpolated_config)
            elif command == "close_tunnel":
                return self._close_tunnel(interpolated_config)
            elif command == "list_tunnels":
                return self._list_tunnels(interpolated_config)
            elif command == "system_info":
                return self._get_system_info(interpolated_config)
            elif command == "list_processes":
                return self._list_processes(interpolated_config)
            elif command == "kill_process":
                return self._kill_process(interpolated_config)
            elif command == "service_control":
                return self._service_control(interpolated_config)
            elif command == "test_connection":
                return self._test_connection(interpolated_config)
            else:
                Output.Console(self.plugin_name, f"Unknown SSH command: {command}")
                return None
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing SSH command '{command}': {str(e)}")
            raise
    
    def _connect(self, config: Dict[str, Any]) -> bool:
        """Establish SSH connection."""
        required_keys = ["host", "username"]
        if not self.validate_config(config, required_keys):
            raise ValueError(f"Missing required keys: {required_keys}")
        
        host = config["host"]
        port = config.get("port", 22)
        username = config["username"]
        password = config.get("password")
        private_key = config.get("private_key")
        passphrase = config.get("passphrase")
        timeout = config.get("timeout", 30)
        session_name = config.get("session_name", "default")
        
        try:
            connection = SSHConnection(
                host=host,
                port=port,
                username=username,
                password=password,
                private_key=private_key,
                passphrase=passphrase,
                timeout=timeout
            )
            
            if connection.connect():
                self.connections[session_name] = connection
                Output.Console(self.plugin_name, f"SSH connection established to {host}:{port}")
                return True
            else:
                Output.Console(self.plugin_name, f"Failed to establish SSH connection to {host}:{port}")
                return False
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error establishing SSH connection: {str(e)}")
            return False
    
    def _disconnect(self, config: Dict[str, Any]) -> bool:
        """Disconnect SSH session."""
        session_name = config.get("session_name", "default")
        
        if session_name in self.connections:
            try:
                self.connections[session_name].disconnect()
                del self.connections[session_name]
                Output.Console(self.plugin_name, f"SSH session '{session_name}' disconnected")
                return True
            except Exception as e:
                Output.Console(self.plugin_name, f"Error disconnecting session '{session_name}': {str(e)}")
                return False
        else:
            Output.Console(self.plugin_name, f"SSH session '{session_name}' not found")
            return False
    
    def _list_sessions(self, config: Dict[str, Any]) -> List[str]:
        """List active SSH sessions."""
        return list(self.connections.keys())
    
    def _close_session(self, config: Dict[str, Any]) -> bool:
        """Close specific SSH session."""
        return self._disconnect(config)
    
    def _close_all_sessions(self, config: Dict[str, Any]) -> bool:
        """Close all SSH sessions."""
        try:
            for session_name in list(self.connections.keys()):
                self._disconnect({"session_name": session_name})
            Output.Console(self.plugin_name, "All SSH sessions closed")
            return True
        except Exception as e:
            Output.Console(self.plugin_name, f"Error closing all sessions: {str(e)}")
            return False
    
    def _execute_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command on remote server."""
        required_keys = ["session", "command"]
        if not self.validate_config(config, required_keys):
            raise ValueError(f"Missing required keys: {required_keys}")
        
        session_name = config["session"]
        command = config["command"]
        timeout = config.get("timeout", 60)
        
        if session_name not in self.connections:
            raise ValueError(f"SSH session '{session_name}' not found")
        
        try:
            result = self.connections[session_name].execute_command(command, timeout)
            return result
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing command: {str(e)}")
            raise
    
    def _execute_interactive(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute interactive commands on remote server."""
        required_keys = ["session", "commands"]
        if not self.validate_config(config, required_keys):
            raise ValueError(f"Missing required keys: {required_keys}")
        
        session_name = config["session"]
        commands = config["commands"]
        timeout = config.get("timeout", 120)
        
        if session_name not in self.connections:
            raise ValueError(f"SSH session '{session_name}' not found")
        
        try:
            result = self.connections[session_name].execute_interactive(commands, timeout)
            return result
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing interactive commands: {str(e)}")
            raise
    
    def _file_operations(self, operation: str, config: Dict[str, Any]) -> Any:
        """Perform file operations on remote server."""
        required_keys = ["session"]
        if not self.validate_config(config, required_keys):
            raise ValueError(f"Missing required keys: {required_keys}")
        
        session_name = config["session"]
        
        if session_name not in self.connections:
            raise ValueError(f"SSH session '{session_name}' not found")
        
        try:
            if operation == "mkdir":
                return self.connections[session_name].mkdir(
                    config["path"],
                    config.get("permissions", "755")
                )
            elif operation == "rm":
                return self.connections[session_name].rm(
                    config["path"],
                    config.get("recursive", False),
                    config.get("force", False)
                )
            elif operation == "ls":
                return self.connections[session_name].ls(
                    config.get("path", "."),
                    config.get("detailed", False)
                )
            elif operation == "chmod":
                return self.connections[session_name].chmod(
                    config["path"],
                    config["permissions"],
                    config.get("recursive", False)
                )
            elif operation == "chown":
                return self.connections[session_name].chown(
                    config["path"],
                    config["user"],
                    config.get("group"),
                    config.get("recursive", False)
                )
        except Exception as e:
            Output.Console(self.plugin_name, f"Error in file operation '{operation}': {str(e)}")
            raise
    
    def _create_tunnel(self, tunnel_type: str, config: Dict[str, Any]) -> bool:
        """Create SSH tunnel."""
        required_keys = ["session", "tunnel_name"]
        if not self.validate_config(config, required_keys):
            raise ValueError(f"Missing required keys: {required_keys}")
        
        session_name = config["session"]
        tunnel_name = config["tunnel_name"]
        
        if session_name not in self.connections:
            raise ValueError(f"SSH session '{session_name}' not found")
        
        try:
            if tunnel_type == "create_tunnel":
                tunnel = SSHTunnel(
                    self.connections[session_name],
                    local_port=config["local_port"],
                    remote_host=config["remote_host"],
                    remote_port=config["remote_port"]
                )
            else:  # create_reverse_tunnel
                tunnel = SSHTunnel(
                    self.connections[session_name],
                    remote_port=config["remote_port"],
                    local_host=config["local_host"],
                    local_port=config["local_port"],
                    reverse=True
                )
            
            if tunnel.start():
                self.tunnels[tunnel_name] = tunnel
                Output.Console(self.plugin_name, f"SSH tunnel '{tunnel_name}' created successfully")
                return True
            else:
                Output.Console(self.plugin_name, f"Failed to create SSH tunnel '{tunnel_name}'")
                return False
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error creating tunnel: {str(e)}")
            return False
    
    def _close_tunnel(self, config: Dict[str, Any]) -> bool:
        """Close SSH tunnel."""
        tunnel_name = config["tunnel_name"]
        
        if tunnel_name in self.tunnels:
            try:
                self.tunnels[tunnel_name].stop()
                del self.tunnels[tunnel_name]
                Output.Console(self.plugin_name, f"SSH tunnel '{tunnel_name}' closed")
                return True
            except Exception as e:
                Output.Console(self.plugin_name, f"Error closing tunnel '{tunnel_name}': {str(e)}")
                return False
        else:
            Output.Console(self.plugin_name, f"SSH tunnel '{tunnel_name}' not found")
            return False
    
    def _list_tunnels(self, config: Dict[str, Any]) -> List[str]:
        """List active SSH tunnels."""
        return list(self.tunnels.keys())
    
    def _get_system_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get system information from remote server."""
        required_keys = ["session"]
        if not self.validate_config(config, required_keys):
            raise ValueError(f"Missing required keys: {required_keys}")
        
        session_name = config["session"]
        
        if session_name not in self.connections:
            raise ValueError(f"SSH session '{session_name}' not found")
        
        try:
            return self.connections[session_name].get_system_info()
        except Exception as e:
            Output.Console(self.plugin_name, f"Error getting system info: {str(e)}")
            raise
    
    def _list_processes(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """List processes on remote server."""
        required_keys = ["session"]
        if not self.validate_config(config, required_keys):
            raise ValueError(f"Missing required keys: {required_keys}")
        
        session_name = config["session"]
        user = config.get("user")
        
        if session_name not in self.connections:
            raise ValueError(f"SSH session '{session_name}' not found")
        
        try:
            return self.connections[session_name].list_processes(user)
        except Exception as e:
            Output.Console(self.plugin_name, f"Error listing processes: {str(e)}")
            raise
    
    def _kill_process(self, config: Dict[str, Any]) -> bool:
        """Kill process on remote server."""
        required_keys = ["session", "pid"]
        if not self.validate_config(config, required_keys):
            raise ValueError(f"Missing required keys: {required_keys}")
        
        session_name = config["session"]
        pid = config["pid"]
        signal = config.get("signal", "SIGTERM")
        
        if session_name not in self.connections:
            raise ValueError(f"SSH session '{session_name}' not found")
        
        try:
            return self.connections[session_name].kill_process(pid, signal)
        except Exception as e:
            Output.Console(self.plugin_name, f"Error killing process: {str(e)}")
            raise
    
    def _service_control(self, config: Dict[str, Any]) -> bool:
        """Control system services."""
        required_keys = ["session", "service", "action"]
        if not self.validate_config(config, required_keys):
            raise ValueError(f"Missing required keys: {required_keys}")
        
        session_name = config["session"]
        service = config["service"]
        action = config["action"]
        
        if session_name not in self.connections:
            raise ValueError(f"SSH session '{session_name}' not found")
        
        try:
            return self.connections[session_name].service_control(service, action)
        except Exception as e:
            Output.Console(self.plugin_name, f"Error controlling service: {str(e)}")
            raise
    
    def _test_connection(self, config: Dict[str, Any]) -> bool:
        """Test SSH connection without establishing session."""
        required_keys = ["host", "username"]
        if not self.validate_config(config, required_keys):
            raise ValueError(f"Missing required keys: {required_keys}")
        
        host = config["host"]
        port = config.get("port", 22)
        username = config["username"]
        password = config.get("password")
        private_key = config.get("private_key")
        passphrase = config.get("passphrase")
        timeout = config.get("timeout", 10)
        
        try:
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            
            if private_key:
                key = RSAKey.from_private_key_file(private_key, password=passphrase)
                client.connect(host, port, username, pkey=key, timeout=timeout)
            else:
                client.connect(host, port, username, password=password, timeout=timeout)
            
            client.close()
            Output.Console(self.plugin_name, f"SSH connection test to {host}:{port} successful")
            return True
            
        except Exception as e:
            Output.Console(self.plugin_name, f"SSH connection test to {host}:{port} failed: {str(e)}")
            return False
    
    def cleanup(self):
        """
        Cleanup SSH resources.
        """
        try:
            # Close all tunnels
            for tunnel_name in list(self.tunnels.keys()):
                self._close_tunnel({"tunnel_name": tunnel_name})
            
            # Close all connections
            self._close_all_sessions({})
            
            Output.Console(self.plugin_name, "SSH resources cleaned up")
        except Exception as e:
            Output.Console(self.plugin_name, f"Error during cleanup: {str(e)}")
        finally:
            super().cleanup()