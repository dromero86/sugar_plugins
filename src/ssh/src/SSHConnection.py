"""
SSH Connection Module
====================

Provides SSH connection management for the SSH plugin.
"""

import os
import time
import threading
from typing import Any, Dict, Optional, Union
from pathlib import Path

import paramiko
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.ssh_exception import SSHException, AuthenticationException, NoValidConnectionsError

from Sugar.Lang.Utils.Output import Output

class SSHConnection:
    """
    SSH Connection manager for Sugar SSH plugin.
    
    Handles SSH connections, authentication, and connection pooling.
    """
    
    def __init__(self, host: str, port: int = 22, username: str = None, 
                 password: str = None, key_file: str = None, timeout: int = 30):
        """
        Initialize SSH connection.
        
        Args:
            host: SSH server hostname or IP
            port: SSH port (default: 22)
            username: SSH username
            password: SSH password
            key_file: Path to private key file
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_file = key_file
        self.timeout = timeout
        
        self.client = None
        self.connected = False
        self.last_used = None
        self.connection_id = f"{username}@{host}:{port}"
        
        Output.Console("SSHConnection", f"Initialized connection to {self.connection_id}")
    
    def connect(self) -> bool:
        """
        Establish SSH connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.client = SSHClient()
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            
            # Prepare connection parameters
            connect_kwargs = {
                'hostname': self.host,
                'port': self.port,
                'timeout': self.timeout
            }
            
            if self.username:
                connect_kwargs['username'] = self.username
            
            if self.password:
                connect_kwargs['password'] = self.password
            
            if self.key_file and os.path.exists(self.key_file):
                try:
                    key = RSAKey.from_private_key_file(self.key_file)
                    connect_kwargs['pkey'] = key
                except Exception as e:
                    Output.Console("SSHConnection", f"Error loading key file: {str(e)}")
            
            # Establish connection
            self.client.connect(**connect_kwargs)
            self.connected = True
            self.last_used = time.time()
            
            Output.Console("SSHConnection", f"Successfully connected to {self.connection_id}")
            return True
            
        except AuthenticationException as e:
            Output.Console("SSHConnection", f"Authentication failed for {self.connection_id}: {str(e)}")
            return False
        except NoValidConnectionsError as e:
            Output.Console("SSHConnection", f"Connection failed for {self.connection_id}: {str(e)}")
            return False
        except Exception as e:
            Output.Console("SSHConnection", f"Unexpected error connecting to {self.connection_id}: {str(e)}")
            return False
    
    def disconnect(self):
        """Close SSH connection."""
        if self.client and self.connected:
            try:
                self.client.close()
                self.connected = False
                Output.Console("SSHConnection", f"Disconnected from {self.connection_id}")
            except Exception as e:
                Output.Console("SSHConnection", f"Error disconnecting from {self.connection_id}: {str(e)}")
    
    def execute_command(self, command: str, timeout: int = None) -> Dict[str, Any]:
        """
        Execute command on remote server.
        
        Args:
            command: Command to execute
            timeout: Command timeout (uses connection timeout if None)
            
        Returns:
            Dictionary with command results
        """
        if not self.connected:
            if not self.connect():
                return {
                    'success': False,
                    'error': 'Failed to establish connection',
                    'stdout': '',
                    'stderr': '',
                    'exit_code': -1
                }
        
        try:
            # Update last used timestamp
            self.last_used = time.time()
            
            # Execute command
            cmd_timeout = timeout or self.timeout
            stdin, stdout, stderr = self.client.exec_command(command, timeout=cmd_timeout)
            
            # Get output
            stdout_data = stdout.read().decode('utf-8', errors='ignore')
            stderr_data = stderr.read().decode('utf-8', errors='ignore')
            exit_code = stdout.channel.recv_exit_status()
            
            return {
                'success': exit_code == 0,
                'stdout': stdout_data,
                'stderr': stderr_data,
                'exit_code': exit_code,
                'command': command
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'stdout': '',
                'stderr': '',
                'exit_code': -1,
                'command': command
            }
    
    def upload_file(self, local_path: str, remote_path: str) -> Dict[str, Any]:
        """
        Upload file to remote server.
        
        Args:
            local_path: Local file path
            remote_path: Remote file path
            
        Returns:
            Dictionary with upload results
        """
        if not self.connected:
            if not self.connect():
                return {
                    'success': False,
                    'error': 'Failed to establish connection'
                }
        
        try:
            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            
            self.last_used = time.time()
            
            return {
                'success': True,
                'message': f'File uploaded: {local_path} -> {remote_path}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Upload failed: {str(e)}'
            }
    
    def download_file(self, remote_path: str, local_path: str) -> Dict[str, Any]:
        """
        Download file from remote server.
        
        Args:
            remote_path: Remote file path
            local_path: Local file path
            
        Returns:
            Dictionary with download results
        """
        if not self.connected:
            if not self.connect():
                return {
                    'success': False,
                    'error': 'Failed to establish connection'
                }
        
        try:
            sftp = self.client.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            
            self.last_used = time.time()
            
            return {
                'success': True,
                'message': f'File downloaded: {remote_path} -> {local_path}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Download failed: {str(e)}'
            }
    
    def is_connected(self) -> bool:
        """Check if connection is active."""
        return self.connected and self.client is not None
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information."""
        return {
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'connected': self.connected,
            'last_used': self.last_used,
            'connection_id': self.connection_id
        }
    
    def __del__(self):
        """Cleanup on deletion."""
        self.disconnect()
