"""
SSH File Transfer Module
=======================

Provides file transfer capabilities for the SSH plugin.
"""

import os
import time
from typing import Any, Dict, List, Optional
from pathlib import Path

import paramiko
from paramiko import SFTPClient

from Sugar.Lang.Utils.Output import Output

class SSHFileTransfer:
    """
    SSH File Transfer manager for Sugar SSH plugin.
    
    Handles file uploads, downloads, and file operations via SFTP.
    """
    
    def __init__(self, ssh_plugin):
        """
        Initialize SSH File Transfer.
        
        Args:
            ssh_plugin: Reference to the SSH plugin instance
        """
        self.ssh_plugin = ssh_plugin
        # Output.Console("SSHFileTransfer", "SSH File Transfer initialized")
    
    def upload_file(self, connection_id: str, local_path: str, remote_path: str, 
                   overwrite: bool = True) -> Dict[str, Any]:
        """
        Upload file to remote server.
        
        Args:
            connection_id: SSH connection identifier
            local_path: Local file path
            remote_path: Remote file path
            overwrite: Whether to overwrite existing files
            
        Returns:
            Dictionary with upload results
        """
        try:
            connection = self.ssh_plugin.connections.get(connection_id)
            if not connection:
                return {
                    'success': False,
                    'error': f'Connection {connection_id} not found'
                }
            
            if not connection.is_connected():
                if not connection.connect():
                    return {
                        'success': False,
                        'error': 'Failed to establish connection'
                    }
            
            # Check if local file exists
            if not os.path.exists(local_path):
                return {
                    'success': False,
                    'error': f'Local file not found: {local_path}'
                }
            
            # Open SFTP session
            sftp = connection.client.open_sftp()
            
            # Check if remote file exists
            if not overwrite:
                try:
                    sftp.stat(remote_path)
                    sftp.close()
                    return {
                        'success': False,
                        'error': f'Remote file already exists: {remote_path}'
                    }
                except FileNotFoundError:
                    pass  # File doesn't exist, proceed with upload
            
            # Upload file
            sftp.put(local_path, remote_path)
            sftp.close()
            
            # Get file info
            local_size = os.path.getsize(local_path)
            
            return {
                'success': True,
                'message': f'File uploaded successfully',
                'local_path': local_path,
                'remote_path': remote_path,
                'size': local_size
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Upload failed: {str(e)}'
            }
    
    def download_file(self, connection_id: str, remote_path: str, local_path: str,
                     overwrite: bool = True) -> Dict[str, Any]:
        """
        Download file from remote server.
        
        Args:
            connection_id: SSH connection identifier
            remote_path: Remote file path
            local_path: Local file path
            overwrite: Whether to overwrite existing files
            
        Returns:
            Dictionary with download results
        """
        try:
            connection = self.ssh_plugin.connections.get(connection_id)
            if not connection:
                return {
                    'success': False,
                    'error': f'Connection {connection_id} not found'
                }
            
            if not connection.is_connected():
                if not connection.connect():
                    return {
                        'success': False,
                        'error': 'Failed to establish connection'
                    }
            
            # Open SFTP session
            sftp = connection.client.open_sftp()
            
            # Check if remote file exists
            try:
                remote_stat = sftp.stat(remote_path)
            except FileNotFoundError:
                sftp.close()
                return {
                    'success': False,
                    'error': f'Remote file not found: {remote_path}'
                }
            
            # Check if local file exists
            if os.path.exists(local_path) and not overwrite:
                sftp.close()
                return {
                    'success': False,
                    'error': f'Local file already exists: {local_path}'
                }
            
            # Ensure local directory exists
            local_dir = os.path.dirname(local_path)
            if local_dir and not os.path.exists(local_dir):
                os.makedirs(local_dir, exist_ok=True)
            
            # Download file
            sftp.get(remote_path, local_path)
            sftp.close()
            
            return {
                'success': True,
                'message': f'File downloaded successfully',
                'local_path': local_path,
                'remote_path': remote_path,
                'size': remote_stat.st_size
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Download failed: {str(e)}'
            }
    
    def list_directory(self, connection_id: str, remote_path: str = '.') -> Dict[str, Any]:
        """
        List directory contents on remote server.
        
        Args:
            connection_id: SSH connection identifier
            remote_path: Remote directory path
            
        Returns:
            Dictionary with directory listing
        """
        try:
            connection = self.ssh_plugin.connections.get(connection_id)
            if not connection:
                return {
                    'success': False,
                    'error': f'Connection {connection_id} not found'
                }
            
            if not connection.is_connected():
                if not connection.connect():
                    return {
                        'success': False,
                        'error': 'Failed to establish connection'
                    }
            
            # Open SFTP session
            sftp = connection.client.open_sftp()
            
            # List directory
            files = []
            directories = []
            
            for item in sftp.listdir_attr(remote_path):
                item_info = {
                    'name': item.filename,
                    'size': item.st_size,
                    'permissions': oct(item.st_mode)[-3:],
                    'modified': time.ctime(item.st_mtime)
                }
                
                if item.st_mode & 0o40000:  # Directory
                    directories.append(item_info)
                else:  # File
                    files.append(item_info)
            
            sftp.close()
            
            return {
                'success': True,
                'path': remote_path,
                'files': files,
                'directories': directories,
                'total_files': len(files),
                'total_directories': len(directories)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'List directory failed: {str(e)}'
            }
    
    def delete_file(self, connection_id: str, remote_path: str) -> Dict[str, Any]:
        """
        Delete file on remote server.
        
        Args:
            connection_id: SSH connection identifier
            remote_path: Remote file path
            
        Returns:
            Dictionary with delete results
        """
        try:
            connection = self.ssh_plugin.connections.get(connection_id)
            if not connection:
                return {
                    'success': False,
                    'error': f'Connection {connection_id} not found'
                }
            
            if not connection.is_connected():
                if not connection.connect():
                    return {
                        'success': False,
                        'error': 'Failed to establish connection'
                    }
            
            # Open SFTP session
            sftp = connection.client.open_sftp()
            
            # Delete file
            sftp.remove(remote_path)
            sftp.close()
            
            return {
                'success': True,
                'message': f'File deleted: {remote_path}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Delete failed: {str(e)}'
            }
    
    def create_directory(self, connection_id: str, remote_path: str) -> Dict[str, Any]:
        """
        Create directory on remote server.
        
        Args:
            connection_id: SSH connection identifier
            remote_path: Remote directory path
            
        Returns:
            Dictionary with create results
        """
        try:
            connection = self.ssh_plugin.connections.get(connection_id)
            if not connection:
                return {
                    'success': False,
                    'error': f'Connection {connection_id} not found'
                }
            
            if not connection.is_connected():
                if not connection.connect():
                    return {
                        'success': False,
                        'error': 'Failed to establish connection'
                    }
            
            # Open SFTP session
            sftp = connection.client.open_sftp()
            
            # Create directory
            sftp.mkdir(remote_path)
            sftp.close()
            
            return {
                'success': True,
                'message': f'Directory created: {remote_path}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Create directory failed: {str(e)}'
            }
