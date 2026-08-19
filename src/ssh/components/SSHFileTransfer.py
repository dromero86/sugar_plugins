"""
SSH File Transfer Handler
========================

Handles file and directory transfer operations using SCP and SFTP.
"""

import os
import glob
from pathlib import Path
from typing import Any, Dict, List, Optional

import paramiko
from paramiko import SFTPClient

from Sugar.Lang.Utils.Output import Output

class SSHFileTransfer:
    """
    SSH file transfer handler for SCP and SFTP operations.
    
    Provides methods for:
    - File upload/download
    - Directory upload/download
    - Progress tracking
    - Error handling
    """
    
    def __init__(self, plugin):
        """
        Initialize SSH file transfer handler.
        
        Args:
            plugin: Reference to the main SSH plugin
        """
        self.plugin = plugin
        Output.Console("SSHFileTransfer", "SSH file transfer handler initialized")
    
    def transfer_file(self, operation: str, config: Dict[str, Any]) -> bool:
        """
        Transfer single file using SCP.
        
        Args:
            operation: "upload" or "download"
            config: Transfer configuration
            
        Returns:
            True if successful, False otherwise
        """
        required_keys = ["session", "local_path", "remote_path"]
        if not self.plugin.validate_config(config, required_keys):
            raise ValueError(f"Missing required keys: {required_keys}")
        
        session_name = config["session"]
        local_path = config["local_path"]
        remote_path = config["remote_path"]
        
        if not hasattr(self.plugin, 'connections') or session_name not in self.plugin.connections:
            raise ValueError(f"SSH session '{session_name}' not found")
        
        connection = self.plugin.connections[session_name]
        
        try:
            if operation == "upload":
                return self._upload_file(connection, local_path, remote_path)
            elif operation == "download":
                return self._download_file(connection, remote_path, local_path)
            else:
                Output.Console("SSHFileTransfer", f"Unknown transfer operation: {operation}")
                return False
                
        except Exception as e:
            Output.Console("SSHFileTransfer", f"Error in file transfer: {str(e)}")
            return False
    
    def transfer_directory(self, operation: str, config: Dict[str, Any]) -> bool:
        """
        Transfer directory using SCP.
        
        Args:
            operation: "upload_dir" or "download_dir"
            config: Transfer configuration
            
        Returns:
            True if successful, False otherwise
        """
        required_keys = ["session", "local_dir", "remote_dir"]
        if not self.plugin.validate_config(config, required_keys):
            raise ValueError(f"Missing required keys: {required_keys}")
        
        session_name = config["session"]
        local_dir = config["local_dir"]
        remote_dir = config["remote_dir"]
        exclude_patterns = config.get("exclude", [])
        
        if not hasattr(self.plugin, 'connections') or session_name not in self.plugin.connections:
            raise ValueError(f"SSH session '{session_name}' not found")
        
        connection = self.plugin.connections[session_name]
        
        try:
            if operation == "upload_dir":
                return self._upload_directory(connection, local_dir, remote_dir, exclude_patterns)
            elif operation == "download_dir":
                return self._download_directory(connection, remote_dir, local_dir, exclude_patterns)
            else:
                Output.Console("SSHFileTransfer", f"Unknown directory transfer operation: {operation}")
                return False
                
        except Exception as e:
            Output.Console("SSHFileTransfer", f"Error in directory transfer: {str(e)}")
            return False
    
    def _upload_file(self, connection, local_path: str, remote_path: str) -> bool:
        """
        Upload single file to remote server.
        
        Args:
            connection: SSH connection object
            local_path: Local file path
            remote_path: Remote file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(local_path):
                Output.Console("SSHFileTransfer", f"Local file not found: {local_path}")
                return False
            
            scp = paramiko.SCPClient(connection.client.get_transport(), progress=self._progress_callback)
            scp.put(local_path, remote_path)
            scp.close()
            
            Output.Console("SSHFileTransfer", f"File uploaded: {local_path} -> {remote_path}")
            return True
            
        except Exception as e:
            Output.Console("SSHFileTransfer", f"Error uploading file {local_path}: {str(e)}")
            return False
    
    def _download_file(self, connection, remote_path: str, local_path: str) -> bool:
        """
        Download single file from remote server.
        
        Args:
            connection: SSH connection object
            remote_path: Remote file path
            local_path: Local file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure local directory exists
            local_dir = os.path.dirname(local_path)
            if local_dir and not os.path.exists(local_dir):
                os.makedirs(local_dir, exist_ok=True)
            
            scp = paramiko.SCPClient(connection.client.get_transport(), progress=self._progress_callback)
            scp.get(remote_path, local_path)
            scp.close()
            
            Output.Console("SSHFileTransfer", f"File downloaded: {remote_path} -> {local_path}")
            return True
            
        except Exception as e:
            Output.Console("SSHFileTransfer", f"Error downloading file {remote_path}: {str(e)}")
            return False
    
    def _upload_directory(self, connection, local_dir: str, remote_dir: str, exclude_patterns: List[str]) -> bool:
        """
        Upload directory to remote server.
        
        Args:
            connection: SSH connection object
            local_dir: Local directory path
            remote_dir: Remote directory path
            exclude_patterns: Patterns to exclude from transfer
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(local_dir):
                Output.Console("SSHFileTransfer", f"Local directory not found: {local_dir}")
                return False
            
            if not os.path.isdir(local_dir):
                Output.Console("SSHFileTransfer", f"Local path is not a directory: {local_dir}")
                return False
            
            # Create remote directory
            connection.mkdir(remote_dir)
            
            # Get list of files to transfer
            files_to_transfer = []
            for root, dirs, files in os.walk(local_dir):
                # Filter out excluded patterns
                dirs[:] = [d for d in dirs if not self._is_excluded(d, exclude_patterns)]
                
                for file in files:
                    if not self._is_excluded(file, exclude_patterns):
                        local_file = os.path.join(root, file)
                        # Calculate relative path
                        rel_path = os.path.relpath(local_file, local_dir)
                        remote_file = os.path.join(remote_dir, rel_path).replace('\\', '/')
                        files_to_transfer.append((local_file, remote_file))
            
            # Transfer files
            scp = paramiko.SCPClient(connection.client.get_transport(), progress=self._progress_callback)
            
            for local_file, remote_file in files_to_transfer:
                # Ensure remote directory exists
                remote_file_dir = os.path.dirname(remote_file)
                if remote_file_dir:
                    connection.mkdir(remote_file_dir)
                
                scp.put(local_file, remote_file)
            
            scp.close()
            
            Output.Console("SSHFileTransfer", f"Directory uploaded: {local_dir} -> {remote_dir}")
            return True
            
        except Exception as e:
            Output.Console("SSHFileTransfer", f"Error uploading directory {local_dir}: {str(e)}")
            return False
    
    def _download_directory(self, connection, remote_dir: str, local_dir: str, exclude_patterns: List[str]) -> bool:
        """
        Download directory from remote server.
        
        Args:
            connection: SSH connection object
            remote_dir: Remote directory path
            local_dir: Local directory path
            exclude_patterns: Patterns to exclude from transfer
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure local directory exists
            if not os.path.exists(local_dir):
                os.makedirs(local_dir, exist_ok=True)
            
            # Get list of files on remote server
            remote_files = self._get_remote_files(connection, remote_dir)
            
            if not remote_files:
                Output.Console("SSHFileTransfer", f"No files found in remote directory: {remote_dir}")
                return True
            
            # Filter out excluded patterns
            files_to_transfer = []
            for remote_file in remote_files:
                filename = os.path.basename(remote_file)
                if not self._is_excluded(filename, exclude_patterns):
                    rel_path = os.path.relpath(remote_file, remote_dir)
                    local_file = os.path.join(local_dir, rel_path)
                    files_to_transfer.append((remote_file, local_file))
            
            # Transfer files
            scp = paramiko.SCPClient(connection.client.get_transport(), progress=self._progress_callback)
            
            for remote_file, local_file in files_to_transfer:
                # Ensure local directory exists
                local_file_dir = os.path.dirname(local_file)
                if local_file_dir and not os.path.exists(local_file_dir):
                    os.makedirs(local_file_dir, exist_ok=True)
                
                scp.get(remote_file, local_file)
            
            scp.close()
            
            Output.Console("SSHFileTransfer", f"Directory downloaded: {remote_dir} -> {local_dir}")
            return True
            
        except Exception as e:
            Output.Console("SSHFileTransfer", f"Error downloading directory {remote_dir}: {str(e)}")
            return False
    
    def _get_remote_files(self, connection, remote_dir: str) -> List[str]:
        """
        Get list of files in remote directory recursively.
        
        Args:
            connection: SSH connection object
            remote_dir: Remote directory path
            
        Returns:
            List of remote file paths
        """
        try:
            files = []
            result = connection.execute_command(f"find {remote_dir} -type f")
            
            if result["success"]:
                for line in result["stdout"].strip().split('\n'):
                    if line.strip():
                        files.append(line.strip())
            
            return files
        except Exception as e:
            Output.Console("SSHFileTransfer", f"Error getting remote files: {str(e)}")
            return []
    
    def _is_excluded(self, filename: str, exclude_patterns: List[str]) -> bool:
        """
        Check if filename matches any exclude pattern.
        
        Args:
            filename: File name to check
            exclude_patterns: List of patterns to exclude
            
        Returns:
            True if file should be excluded, False otherwise
        """
        for pattern in exclude_patterns:
            if glob.fnmatch.fnmatch(filename, pattern):
                return True
        return False
    
    def _progress_callback(self, filename: str, size: int, sent: int):
        """
        Progress callback for file transfers.
        
        Args:
            filename: Name of file being transferred
            size: Total size of file
            sent: Bytes sent so far
        """
        if size > 0:
            percentage = (sent / size) * 100
            Output.Console("SSHFileTransfer", f"Transferring {filename}: {percentage:.1f}% ({sent}/{size} bytes)")
        else:
            Output.Console("SSHFileTransfer", f"Transferring {filename}: {sent} bytes")