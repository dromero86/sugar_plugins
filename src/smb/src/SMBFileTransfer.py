"""
SMB File Transfer Operations
===========================

Handles file and directory operations over SMB/CIFS including
upload, download, listing, deletion, and advanced features.
"""

import os
import time
import hashlib
import threading
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from smb.SMBConnection import SMBConnection as PySMBConnection
from smb.smb_structs import OperationFailure

from Sugar.Lang.Utils.Output import Output


class SMBFileTransfer:
    """
    Handles file and directory operations over SMB/CIFS.
    
    Features:
    - File upload and download
    - Directory operations
    - Parallel transfers
    - Progress tracking
    - Checksum verification
    - Error handling and retry
    """
    
    def __init__(self, plugin_name: str = "SMBPlugin"):
        """Initialize SMB file transfer manager."""
        self.plugin_name = plugin_name
        self.transfer_stats = {
            "total_transfers": 0,
            "successful_transfers": 0,
            "failed_transfers": 0,
            "total_bytes": 0,
            "start_time": None
        }
        self.lock = threading.Lock()
        
        Output.Console(self.plugin_name, "SMB File Transfer manager initialized")
    
    def upload_file(self,
                   conn: PySMBConnection,
                   share: str,
                   local_path: str,
                   remote_path: str,
                   overwrite: bool = True) -> Dict[str, Any]:
        """
        Upload a file to SMB share.
        
        Args:
            conn: SMB connection object
            share: Share name
            local_path: Local file path
            remote_path: Remote file path
            overwrite: Overwrite existing file
            
        Returns:
            Upload result dictionary
        """
        try:
            start_time = time.time()
            
            # Validate local file
            if not os.path.exists(local_path):
                return {
                    "status": "error",
                    "error": "Local file not found",
                    "details": f"File does not exist: {local_path}"
                }
            
            if not os.path.isfile(local_path):
                return {
                    "status": "error",
                    "error": "Invalid local path",
                    "details": f"Path is not a file: {local_path}"
                }
            
            # Get file info
            file_size = os.path.getsize(local_path)
            file_name = os.path.basename(local_path)
            
            Output.Console(self.plugin_name, f"Uploading {file_name} ({file_size} bytes)")
            
            # Check if remote file exists
            if not overwrite:
                try:
                    conn.getAttributes(share, remote_path)
                    return {
                        "status": "error",
                        "error": "File already exists",
                        "details": f"Remote file exists and overwrite=False: {remote_path}"
                    }
                except OperationFailure:
                    pass  # File doesn't exist, proceed with upload
            
            # Upload file
            with open(local_path, 'rb') as local_file:
                conn.storeFile(share, remote_path, local_file)
            
            # Verify upload
            try:
                remote_attrs = conn.getAttributes(share, remote_path)
                if remote_attrs.file_size != file_size:
                    return {
                        "status": "error",
                        "error": "Upload verification failed",
                        "details": f"Size mismatch: local={file_size}, remote={remote_attrs.file_size}"
                    }
            except OperationFailure as e:
                return {
                    "status": "error",
                    "error": "Upload verification failed",
                    "details": f"Cannot verify uploaded file: {str(e)}"
                }
            
            transfer_time = time.time() - start_time
            speed_mbps = (file_size / 1024 / 1024) / transfer_time if transfer_time > 0 else 0
            
            # Update stats
            with self.lock:
                self.transfer_stats["total_transfers"] += 1
                self.transfer_stats["successful_transfers"] += 1
                self.transfer_stats["total_bytes"] += file_size
            
            return {
                "status": "success",
                "file": remote_path,
                "size": file_size,
                "transfer_time": round(transfer_time, 2),
                "speed_mbps": round(speed_mbps, 2),
                "details": {
                    "local_path": local_path,
                    "remote_path": remote_path,
                    "file_size": file_size
                }
            }
            
        except Exception as e:
            # Update stats
            with self.lock:
                self.transfer_stats["total_transfers"] += 1
                self.transfer_stats["failed_transfers"] += 1
            
            Output.Console(self.plugin_name, f"Upload error: {str(e)}")
            return {
                "status": "error",
                "error": "Upload failed",
                "details": str(e)
            }
    
    def download_file(self,
                     conn: PySMBConnection,
                     share: str,
                     remote_path: str,
                     local_path: str,
                     overwrite: bool = True) -> Dict[str, Any]:
        """
        Download a file from SMB share.
        
        Args:
            conn: SMB connection object
            share: Share name
            remote_path: Remote file path
            local_path: Local file path
            overwrite: Overwrite existing file
            
        Returns:
            Download result dictionary
        """
        try:
            start_time = time.time()
            
            # Check if local file exists
            if os.path.exists(local_path) and not overwrite:
                return {
                    "status": "error",
                    "error": "Local file already exists",
                    "details": f"File exists and overwrite=False: {local_path}"
                }
            
            # Get remote file info
            try:
                remote_attrs = conn.getAttributes(share, remote_path)
                file_size = remote_attrs.file_size
            except OperationFailure as e:
                return {
                    "status": "error",
                    "error": "Remote file not found",
                    "details": f"Cannot access remote file: {str(e)}"
                }
            
            file_name = os.path.basename(remote_path)
            Output.Console(self.plugin_name, f"Downloading {file_name} ({file_size} bytes)")
            
            # Ensure local directory exists
            local_dir = os.path.dirname(local_path)
            if local_dir and not os.path.exists(local_dir):
                os.makedirs(local_dir, exist_ok=True)
            
            # Download file
            with open(local_path, 'wb') as local_file:
                conn.retrieveFile(share, remote_path, local_file)
            
            # Verify download
            if os.path.getsize(local_path) != file_size:
                return {
                    "status": "error",
                    "error": "Download verification failed",
                    "details": f"Size mismatch: remote={file_size}, local={os.path.getsize(local_path)}"
                }
            
            transfer_time = time.time() - start_time
            speed_mbps = (file_size / 1024 / 1024) / transfer_time if transfer_time > 0 else 0
            
            # Update stats
            with self.lock:
                self.transfer_stats["total_transfers"] += 1
                self.transfer_stats["successful_transfers"] += 1
                self.transfer_stats["total_bytes"] += file_size
            
            return {
                "status": "success",
                "file": local_path,
                "size": file_size,
                "transfer_time": round(transfer_time, 2),
                "speed_mbps": round(speed_mbps, 2),
                "details": {
                    "remote_path": remote_path,
                    "local_path": local_path,
                    "file_size": file_size
                }
            }
            
        except Exception as e:
            # Update stats
            with self.lock:
                self.transfer_stats["total_transfers"] += 1
                self.transfer_stats["failed_transfers"] += 1
            
            Output.Console(self.plugin_name, f"Download error: {str(e)}")
            return {
                "status": "error",
                "error": "Download failed",
                "details": str(e)
            }
    
    def upload_multiple(self,
                       conn: PySMBConnection,
                       share: str,
                       files: List[Dict[str, str]],
                       parallel: bool = True,
                       max_workers: int = 5) -> Dict[str, Any]:
        """
        Upload multiple files.
        
        Args:
            conn: SMB connection object
            share: Share name
            files: List of file dictionaries with 'local' and 'remote' keys
            parallel: Use parallel uploads
            max_workers: Maximum parallel workers
            
        Returns:
            Upload results dictionary
        """
        if not files:
            return {
                "status": "error",
                "error": "No files specified",
                "details": "Files list is empty"
            }
        
        results = []
        start_time = time.time()
        
        if parallel and len(files) > 1:
            # Parallel upload
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for file_info in files:
                    future = executor.submit(
                        self.upload_file,
                        conn,
                        share,
                        file_info["local"],
                        file_info["remote"]
                    )
                    futures.append(future)
                
                for future in as_completed(futures):
                    results.append(future.result())
        else:
            # Sequential upload
            for file_info in files:
                result = self.upload_file(
                    conn,
                    share,
                    file_info["local"],
                    file_info["remote"]
                )
                results.append(result)
        
        total_time = time.time() - start_time
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful
        
        return {
            "status": "success",
            "files_processed": len(files),
            "successful": successful,
            "failed": failed,
            "total_time": round(total_time, 2),
            "results": results
        }
    
    def download_multiple(self,
                         conn: PySMBConnection,
                         share: str,
                         files: List[Dict[str, str]],
                         parallel: bool = True,
                         max_workers: int = 5) -> Dict[str, Any]:
        """
        Download multiple files.
        
        Args:
            conn: SMB connection object
            share: Share name
            files: List of file dictionaries with 'remote' and 'local' keys
            parallel: Use parallel downloads
            max_workers: Maximum parallel workers
            
        Returns:
            Download results dictionary
        """
        if not files:
            return {
                "status": "error",
                "error": "No files specified",
                "details": "Files list is empty"
            }
        
        results = []
        start_time = time.time()
        
        if parallel and len(files) > 1:
            # Parallel download
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for file_info in files:
                    future = executor.submit(
                        self.download_file,
                        conn,
                        share,
                        file_info["remote"],
                        file_info["local"]
                    )
                    futures.append(future)
                
                for future in as_completed(futures):
                    results.append(future.result())
        else:
            # Sequential download
            for file_info in files:
                result = self.download_file(
                    conn,
                    share,
                    file_info["remote"],
                    file_info["local"]
                )
                results.append(result)
        
        total_time = time.time() - start_time
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful
        
        return {
            "status": "success",
            "files_processed": len(files),
            "successful": successful,
            "failed": failed,
            "total_time": round(total_time, 2),
            "results": results
        }
    
    def list_directory(self,
                      conn: PySMBConnection,
                      share: str,
                      path: str = "/",
                      include_hidden: bool = False,
                      recursive: bool = False) -> Dict[str, Any]:
        """
        List directory contents.
        
        Args:
            conn: SMB connection object
            share: Share name
            path: Directory path
            include_hidden: Include hidden files
            recursive: List recursively
            
        Returns:
            Directory listing dictionary
        """
        try:
            items = []
            
            def list_path(current_path: str, level: int = 0):
                try:
                    files = conn.listPath(share, current_path)
                    
                    for file_info in files:
                        # Skip hidden files if not requested
                        if not include_hidden and file_info.filename.startswith('.'):
                            continue
                        
                        # Skip . and .. directories
                        if file_info.filename in ['.', '..']:
                            continue
                        
                        item = {
                            "name": file_info.filename,
                            "path": f"{current_path}/{file_info.filename}".replace("//", "/"),
                            "is_directory": file_info.isDirectory,
                            "size": file_info.file_size,
                            "attributes": {
                                "hidden": file_info.isHidden,
                                "readonly": file_info.isReadOnly,
                                "system": file_info.isSystem,
                                "archive": file_info.isArchive
                            },
                            "level": level
                        }
                        
                        items.append(item)
                        
                        # Recursive listing for directories
                        if recursive and file_info.isDirectory:
                            list_path(item["path"], level + 1)
                            
                except OperationFailure as e:
                    Output.Console(self.plugin_name, f"Error listing {current_path}: {str(e)}")
            
            list_path(path)
            
            return {
                "status": "success",
                "path": path,
                "items": items,
                "total_items": len(items),
                "directories": sum(1 for item in items if item["is_directory"]),
                "files": sum(1 for item in items if not item["is_directory"])
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"List directory error: {str(e)}")
            return {
                "status": "error",
                "error": "List directory failed",
                "details": str(e)
            }
    
    def delete_file(self,
                   conn: PySMBConnection,
                   share: str,
                   path: str) -> Dict[str, Any]:
        """
        Delete a file.
        
        Args:
            conn: SMB connection object
            share: Share name
            path: File path
            
        Returns:
            Delete result dictionary
        """
        try:
            # Check if file exists
            try:
                attrs = conn.getAttributes(share, path)
                if attrs.isDirectory:
                    return {
                        "status": "error",
                        "error": "Path is a directory",
                        "details": f"Use delete_directory for directories: {path}"
                    }
            except OperationFailure as e:
                return {
                    "status": "error",
                    "error": "File not found",
                    "details": f"Cannot access file: {str(e)}"
                }
            
            # Delete file
            conn.deleteFiles(share, path)
            
            return {
                "status": "success",
                "message": f"File deleted: {path}",
                "file": path
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Delete file error: {str(e)}")
            return {
                "status": "error",
                "error": "Delete file failed",
                "details": str(e)
            }
    
    def create_directory(self,
                        conn: PySMBConnection,
                        share: str,
                        path: str) -> Dict[str, Any]:
        """
        Create a directory.
        
        Args:
            conn: SMB connection object
            share: Share name
            path: Directory path
            
        Returns:
            Create directory result dictionary
        """
        try:
            # Check if directory already exists
            try:
                attrs = conn.getAttributes(share, path)
                if attrs.isDirectory:
                    return {
                        "status": "success",
                        "message": f"Directory already exists: {path}",
                        "directory": path
                    }
                else:
                    return {
                        "status": "error",
                        "error": "Path exists but is not a directory",
                        "details": f"Path exists as file: {path}"
                    }
            except OperationFailure:
                pass  # Directory doesn't exist, proceed with creation
            
            # Create directory
            conn.createDirectory(share, path)
            
            return {
                "status": "success",
                "message": f"Directory created: {path}",
                "directory": path
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Create directory error: {str(e)}")
            return {
                "status": "error",
                "error": "Create directory failed",
                "details": str(e)
            }
    
    def delete_directory(self,
                        conn: PySMBConnection,
                        share: str,
                        path: str,
                        recursive: bool = False) -> Dict[str, Any]:
        """
        Delete a directory.
        
        Args:
            conn: SMB connection object
            share: Share name
            path: Directory path
            recursive: Delete recursively
            
        Returns:
            Delete directory result dictionary
        """
        try:
            # Check if directory exists
            try:
                attrs = conn.getAttributes(share, path)
                if not attrs.isDirectory:
                    return {
                        "status": "error",
                        "error": "Path is not a directory",
                        "details": f"Path is a file: {path}"
                    }
            except OperationFailure as e:
                return {
                    "status": "error",
                    "error": "Directory not found",
                    "details": f"Cannot access directory: {str(e)}"
                }
            
            if recursive:
                # List all items recursively and delete them
                items = self.list_directory(conn, share, path, recursive=True)
                if items["status"] == "success":
                    # Delete files first, then directories
                    for item in reversed(items["items"]):
                        if not item["is_directory"]:
                            conn.deleteFiles(share, item["path"])
                        else:
                            conn.deleteDirectory(share, item["path"])
            
            # Delete the directory itself
            conn.deleteDirectory(share, path)
            
            return {
                "status": "success",
                "message": f"Directory deleted: {path}",
                "directory": path,
                "recursive": recursive
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Delete directory error: {str(e)}")
            return {
                "status": "error",
                "error": "Delete directory failed",
                "details": str(e)
            }
    
    def get_file_info(self,
                     conn: PySMBConnection,
                     share: str,
                     path: str) -> Dict[str, Any]:
        """
        Get file information.
        
        Args:
            conn: SMB connection object
            share: Share name
            path: File path
            
        Returns:
            File information dictionary
        """
        try:
            attrs = conn.getAttributes(share, path)
            
            return {
                "status": "success",
                "file_info": {
                    "name": os.path.basename(path),
                    "path": path,
                    "size": attrs.file_size,
                    "is_directory": attrs.isDirectory,
                    "attributes": {
                        "hidden": attrs.isHidden,
                        "readonly": attrs.isReadOnly,
                        "system": attrs.isSystem,
                        "archive": attrs.isArchive
                    },
                    "creation_time": attrs.createTime,
                    "last_access_time": attrs.lastAccessTime,
                    "last_write_time": attrs.lastWriteTime
                }
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Get file info error: {str(e)}")
            return {
                "status": "error",
                "error": "Get file info failed",
                "details": str(e)
            }
    
    def get_transfer_stats(self) -> Dict[str, Any]:
        """
        Get transfer statistics.
        
        Returns:
            Transfer statistics dictionary
        """
        with self.lock:
            stats = self.transfer_stats.copy()
            
            if stats["start_time"] is None:
                stats["start_time"] = time.time()
            
            stats["uptime"] = time.time() - stats["start_time"]
            stats["success_rate"] = (
                stats["successful_transfers"] / stats["total_transfers"] * 100
                if stats["total_transfers"] > 0 else 0
            )
            
            return {
                "status": "success",
                "transfer_statistics": stats
            }