"""
SSH Connection Handler
=====================

Handles individual SSH connections and provides methods for command execution,
file operations, and system information retrieval.
"""

import os
import re
import time
import platform
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

import paramiko
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.ssh_exception import SSHException, AuthenticationException, NoValidConnectionsError

from Sugar.Lang.Utils.Output import Output

class SSHConnection:
    """
    SSH connection handler for managing individual SSH sessions.
    
    Provides methods for:
    - Command execution
    - Interactive command execution
    - File operations
    - System information retrieval
    - Process management
    - Service control
    """
    
    def __init__(self, host: str, port: int = 22, username: str = None, 
                 password: str = None, private_key: str = None, 
                 passphrase: str = None, timeout: int = 30):
        """
        Initialize SSH connection.
        
        Args:
            host: Remote host address
            port: SSH port (default: 22)
            username: SSH username
            password: SSH password
            private_key: Path to private key file
            passphrase: Passphrase for private key
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.private_key = private_key
        self.passphrase = passphrase
        self.timeout = timeout
        
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.connected = False
        
        Output.Console("SSHConnection", f"SSH connection initialized for {host}:{port}")
    
    def connect(self) -> bool:
        """
        Establish SSH connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if self.private_key:
                if not os.path.exists(self.private_key):
                    Output.Console("SSHConnection", f"Private key file not found: {self.private_key}")
                    return False
                
                key = RSAKey.from_private_key_file(self.private_key, password=self.passphrase)
                self.client.connect(
                    self.host, 
                    self.port, 
                    self.username, 
                    pkey=key, 
                    timeout=self.timeout
                )
            else:
                self.client.connect(
                    self.host, 
                    self.port, 
                    self.username, 
                    password=self.password, 
                    timeout=self.timeout
                )
            
            self.connected = True
            Output.Console("SSHConnection", f"SSH connection established to {self.host}:{self.port}")
            return True
            
        except AuthenticationException:
            Output.Console("SSHConnection", f"Authentication failed for {self.username}@{self.host}")
            return False
        except NoValidConnectionsError:
            Output.Console("SSHConnection", f"No valid connections to {self.host}:{self.port}")
            return False
        except SSHException as e:
            Output.Console("SSHConnection", f"SSH error connecting to {self.host}:{self.port}: {str(e)}")
            return False
        except Exception as e:
            Output.Console("SSHConnection", f"Error connecting to {self.host}:{self.port}: {str(e)}")
            return False
    
    def disconnect(self):
        """Close SSH connection."""
        if self.connected:
            try:
                self.client.close()
                self.connected = False
                Output.Console("SSHConnection", f"SSH connection closed to {self.host}:{self.port}")
            except Exception as e:
                Output.Console("SSHConnection", f"Error closing SSH connection: {str(e)}")
    
    def execute_command(self, command: str, timeout: int = 60) -> Dict[str, Any]:
        """
        Execute command on remote server.
        
        Args:
            command: Command to execute
            timeout: Command timeout in seconds
            
        Returns:
            Dictionary with stdout, stderr, and exit_code
        """
        if not self.connected:
            raise SSHException("SSH connection not established")
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
            
            # Read output
            stdout_data = stdout.read().decode('utf-8')
            stderr_data = stderr.read().decode('utf-8')
            exit_code = stdout.channel.recv_exit_status()
            
            return {
                "stdout": stdout_data,
                "stderr": stderr_data,
                "exit_code": exit_code,
                "success": exit_code == 0
            }
            
        except Exception as e:
            Output.Console("SSHConnection", f"Error executing command '{command}': {str(e)}")
            raise
    
    def execute_interactive(self, commands: List[str], timeout: int = 120) -> Dict[str, Any]:
        """
        Execute interactive commands on remote server.
        
        Args:
            commands: List of commands to execute
            timeout: Total timeout in seconds
            
        Returns:
            Dictionary with output and success status
        """
        if not self.connected:
            raise SSHException("SSH connection not established")
        
        try:
            channel = self.client.invoke_shell()
            channel.settimeout(timeout)
            
            output = ""
            for command in commands:
                channel.send(command + '\n')
                time.sleep(1)  # Wait for command to process
                
                # Read available output
                while channel.recv_ready():
                    output += channel.recv(1024).decode('utf-8')
            
            # Wait for final output
            time.sleep(2)
            while channel.recv_ready():
                output += channel.recv(1024).decode('utf-8')
            
            channel.close()
            
            return {
                "output": output,
                "success": True
            }
            
        except Exception as e:
            Output.Console("SSHConnection", f"Error executing interactive commands: {str(e)}")
            raise
    
    def mkdir(self, path: str, permissions: str = "755") -> bool:
        """
        Create directory on remote server.
        
        Args:
            path: Directory path to create
            permissions: Directory permissions (default: 755)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.execute_command(f"mkdir -p {path}")
            if result["success"]:
                self.execute_command(f"chmod {permissions} {path}")
                return True
            return False
        except Exception as e:
            Output.Console("SSHConnection", f"Error creating directory {path}: {str(e)}")
            return False
    
    def rm(self, path: str, recursive: bool = False, force: bool = False) -> bool:
        """
        Remove file or directory on remote server.
        
        Args:
            path: Path to remove
            recursive: Remove recursively (for directories)
            force: Force removal without confirmation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            flags = ""
            if recursive:
                flags += "r"
            if force:
                flags += "f"
            
            command = f"rm -{flags} {path}" if flags else f"rm {path}"
            result = self.execute_command(command)
            return result["success"]
        except Exception as e:
            Output.Console("SSHConnection", f"Error removing {path}: {str(e)}")
            return False
    
    def ls(self, path: str = ".", detailed: bool = False) -> List[Dict[str, Any]]:
        """
        List files and directories on remote server.
        
        Args:
            path: Path to list
            detailed: Include detailed information
            
        Returns:
            List of file/directory information
        """
        try:
            if detailed:
                result = self.execute_command(f"ls -la {path}")
            else:
                result = self.execute_command(f"ls {path}")
            
            if not result["success"]:
                return []
            
            files = []
            lines = result["stdout"].strip().split('\n')
            
            for line in lines:
                if line and not line.startswith('total'):
                    if detailed:
                        # Parse detailed ls output
                        parts = line.split()
                        if len(parts) >= 9:
                            files.append({
                                "permissions": parts[0],
                                "links": parts[1],
                                "owner": parts[2],
                                "group": parts[3],
                                "size": parts[4],
                                "date": " ".join(parts[5:8]),
                                "name": " ".join(parts[8:])
                            })
                    else:
                        # Simple ls output
                        files.append({"name": line.strip()})
            
            return files
        except Exception as e:
            Output.Console("SSHConnection", f"Error listing {path}: {str(e)}")
            return []
    
    def chmod(self, path: str, permissions: str, recursive: bool = False) -> bool:
        """
        Change file permissions on remote server.
        
        Args:
            path: File or directory path
            permissions: New permissions (e.g., "755")
            recursive: Apply recursively to directories
            
        Returns:
            True if successful, False otherwise
        """
        try:
            flags = "R" if recursive else ""
            command = f"chmod {flags} {permissions} {path}"
            result = self.execute_command(command)
            return result["success"]
        except Exception as e:
            Output.Console("SSHConnection", f"Error changing permissions on {path}: {str(e)}")
            return False
    
    def chown(self, path: str, user: str, group: str = None, recursive: bool = False) -> bool:
        """
        Change file ownership on remote server.
        
        Args:
            path: File or directory path
            user: New owner
            group: New group (optional)
            recursive: Apply recursively to directories
            
        Returns:
            True if successful, False otherwise
        """
        try:
            flags = "R" if recursive else ""
            owner = f"{user}:{group}" if group else user
            command = f"chown {flags} {owner} {path}"
            result = self.execute_command(command)
            return result["success"]
        except Exception as e:
            Output.Console("SSHConnection", f"Error changing ownership on {path}: {str(e)}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information from remote server.
        
        Returns:
            Dictionary with system information
        """
        try:
            info = {}
            
            # OS information
            result = self.execute_command("uname -a")
            if result["success"]:
                info["uname"] = result["stdout"].strip()
            
            # Distribution info
            result = self.execute_command("cat /etc/os-release")
            if result["success"]:
                info["os_release"] = result["stdout"].strip()
            
            # Kernel version
            result = self.execute_command("uname -r")
            if result["success"]:
                info["kernel"] = result["stdout"].strip()
            
            # Architecture
            result = self.execute_command("uname -m")
            if result["success"]:
                info["architecture"] = result["stdout"].strip()
            
            # Memory information
            result = self.execute_command("free -m")
            if result["success"]:
                info["memory"] = result["stdout"].strip()
            
            # Disk usage
            result = self.execute_command("df -h")
            if result["success"]:
                info["disk"] = result["stdout"].strip()
            
            # Uptime
            result = self.execute_command("uptime")
            if result["success"]:
                info["uptime"] = result["stdout"].strip()
            
            # CPU information
            result = self.execute_command("lscpu")
            if result["success"]:
                info["cpu"] = result["stdout"].strip()
            
            return info
        except Exception as e:
            Output.Console("SSHConnection", f"Error getting system info: {str(e)}")
            return {}
    
    def list_processes(self, user: str = None) -> List[Dict[str, Any]]:
        """
        List processes on remote server.
        
        Args:
            user: Filter by user (optional)
            
        Returns:
            List of process information
        """
        try:
            if user:
                result = self.execute_command(f"ps aux | grep {user}")
            else:
                result = self.execute_command("ps aux")
            
            if not result["success"]:
                return []
            
            processes = []
            lines = result["stdout"].strip().split('\n')
            
            for line in lines:
                if line and not line.startswith('USER'):
                    parts = line.split()
                    if len(parts) >= 11:
                        processes.append({
                            "user": parts[0],
                            "pid": parts[1],
                            "cpu": parts[2],
                            "mem": parts[3],
                            "vsz": parts[4],
                            "rss": parts[5],
                            "tty": parts[6],
                            "stat": parts[7],
                            "start": parts[8],
                            "time": parts[9],
                            "command": " ".join(parts[10:])
                        })
            
            return processes
        except Exception as e:
            Output.Console("SSHConnection", f"Error listing processes: {str(e)}")
            return []
    
    def kill_process(self, pid: Union[int, str], signal: str = "SIGTERM") -> bool:
        """
        Kill process on remote server.
        
        Args:
            pid: Process ID
            signal: Signal to send (default: SIGTERM)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            command = f"kill -{signal} {pid}"
            result = self.execute_command(command)
            return result["success"]
        except Exception as e:
            Output.Console("SSHConnection", f"Error killing process {pid}: {str(e)}")
            return False
    
    def service_control(self, service: str, action: str) -> bool:
        """
        Control system service on remote server.
        
        Args:
            service: Service name
            action: Action to perform (start, stop, restart, status, enable, disable)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try systemctl first (systemd)
            command = f"systemctl {action} {service}"
            result = self.execute_command(command)
            
            if result["success"] or "not found" not in result["stderr"]:
                return result["success"]
            
            # Try service command (init.d)
            command = f"service {service} {action}"
            result = self.execute_command(command)
            
            return result["success"]
        except Exception as e:
            Output.Console("SSHConnection", f"Error controlling service {service}: {str(e)}")
            return False
    
    def __del__(self):
        """Cleanup on destruction."""
        self.disconnect()