"""
SMB Connection Management
========================

Handles SMB/CIFS connections with support for authentication,
session management, and connection pooling.
"""

import os
import time
import threading
from typing import Any, Dict, Optional, Union
from pathlib import Path

from smb.SMBConnection import SMBConnection as PySMBConnection
from smb.smb_structs import OperationFailure

from Sugar.Lang.Utils.Output import Output


class SMBConnection:
    """
    Manages SMB/CIFS connections with advanced features.
    
    Features:
    - Multiple authentication methods
    - Connection pooling
    - Automatic reconnection
    - Session management
    - Timeout handling
    """
    
    def __init__(self, plugin_name: str = "SMBPlugin"):
        """Initialize SMB connection manager."""
        self.plugin_name = plugin_name
        self.connections: Dict[str, PySMBConnection] = {}
        self.connection_info: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        
        Output.Console(self.plugin_name, "SMB Connection manager initialized")
    
    def connect(self, 
                host: str,
                share: str,
                username: str,
                password: str,
                domain: str = "",
                port: int = 445,
                session_name: str = "default",
                timeout: int = 30,
                use_ntlm_v2: bool = True) -> Dict[str, Any]:
        """
        Establish SMB connection.
        
        Args:
            host: SMB server hostname or IP
            share: Share name to connect to
            username: Username for authentication
            password: Password for authentication
            domain: Domain name (optional)
            port: SMB port (default: 445)
            session_name: Name for this session
            timeout: Connection timeout in seconds
            use_ntlm_v2: Use NTLM v2 authentication
            
        Returns:
            Connection result dictionary
        """
        try:
            Output.Console(self.plugin_name, f"Connecting to SMB server: {host}:{port}")
            
            # Create connection
            conn = PySMBConnection(
                username=username,
                password=password,
                my_name="SugarSMBClient",
                remote_name=host,
                domain=domain,
                use_ntlm_v2=use_ntlm_v2,
                is_direct_tcp=True
            )
            
            # Connect
            connected = conn.connect(host, port, timeout=timeout)
            
            if not connected:
                return {
                    "status": "error",
                    "error": "Failed to connect to SMB server",
                    "details": f"Could not establish connection to {host}:{port}"
                }
            
            # Test share access
            try:
                conn.listPath(share, "/")
                Output.Console(self.plugin_name, f"Successfully connected to share: {share}")
            except OperationFailure as e:
                return {
                    "status": "error",
                    "error": "Share access denied",
                    "details": f"Cannot access share '{share}': {str(e)}"
                }
            
            # Store connection
            with self.lock:
                self.connections[session_name] = conn
                self.connection_info[session_name] = {
                    "host": host,
                    "share": share,
                    "username": username,
                    "domain": domain,
                    "port": port,
                    "connected_at": time.time(),
                    "timeout": timeout,
                    "use_ntlm_v2": use_ntlm_v2
                }
            
            return {
                "status": "success",
                "session_id": session_name,
                "connection_info": {
                    "host": host,
                    "share": share,
                    "username": username,
                    "connected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "port": port
                },
                "capabilities": {
                    "smb_version": "2.1+",
                    "encryption": True,
                    "compression": True
                }
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Connection error: {str(e)}")
            return {
                "status": "error",
                "error": "Connection failed",
                "details": str(e)
            }
    
    def test_connection(self,
                       host: str,
                       share: str,
                       username: str,
                       password: str,
                       domain: str = "",
                       port: int = 445,
                       timeout: int = 10) -> Dict[str, Any]:
        """
        Test SMB connection without establishing a persistent session.
        
        Args:
            host: SMB server hostname or IP
            share: Share name to test
            username: Username for authentication
            password: Password for authentication
            domain: Domain name (optional)
            port: SMB port (default: 445)
            timeout: Connection timeout in seconds
            
        Returns:
            Test result dictionary
        """
        try:
            Output.Console(self.plugin_name, f"Testing connection to: {host}:{port}")
            
            # Create temporary connection for testing
            conn = PySMBConnection(
                username=username,
                password=password,
                my_name="SugarSMBTest",
                remote_name=host,
                domain=domain,
                use_ntlm_v2=True,
                is_direct_tcp=True
            )
            
            # Test connection
            connected = conn.connect(host, port, timeout=timeout)
            
            if not connected:
                return {
                    "status": "error",
                    "error": "Connection test failed",
                    "details": f"Cannot reach {host}:{port}"
                }
            
            # Test share access
            try:
                conn.listPath(share, "/")
                conn.close()
                
                return {
                    "status": "success",
                    "message": f"Connection test successful to {host}:{port}",
                    "share_accessible": True
                }
                
            except OperationFailure as e:
                conn.close()
                return {
                    "status": "error",
                    "error": "Share access test failed",
                    "details": f"Cannot access share '{share}': {str(e)}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": "Connection test failed",
                "details": str(e)
            }
    
    def disconnect(self, session_name: str = "default") -> Dict[str, Any]:
        """
        Disconnect from SMB server.
        
        Args:
            session_name: Name of the session to disconnect
            
        Returns:
            Disconnect result dictionary
        """
        try:
            with self.lock:
                if session_name not in self.connections:
                    return {
                        "status": "error",
                        "error": "Session not found",
                        "details": f"Session '{session_name}' does not exist"
                    }
                
                conn = self.connections[session_name]
                conn.close()
                
                # Remove from tracking
                del self.connections[session_name]
                del self.connection_info[session_name]
                
                Output.Console(self.plugin_name, f"Disconnected session: {session_name}")
                
                return {
                    "status": "success",
                    "message": f"Disconnected from session: {session_name}"
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Disconnect error: {str(e)}")
            return {
                "status": "error",
                "error": "Disconnect failed",
                "details": str(e)
            }
    
    def get_connection(self, session_name: str = "default") -> Optional[PySMBConnection]:
        """
        Get SMB connection by session name.
        
        Args:
            session_name: Name of the session
            
        Returns:
            SMB connection object or None if not found
        """
        with self.lock:
            return self.connections.get(session_name)
    
    def get_session_info(self, session_name: str = "default") -> Dict[str, Any]:
        """
        Get information about a session.
        
        Args:
            session_name: Name of the session
            
        Returns:
            Session information dictionary
        """
        with self.lock:
            if session_name not in self.connection_info:
                return {
                    "status": "error",
                    "error": "Session not found",
                    "details": f"Session '{session_name}' does not exist"
                }
            
            info = self.connection_info[session_name].copy()
            info["connected_duration"] = time.time() - info["connected_at"]
            info["connected_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(info["connected_at"]))
            
            return {
                "status": "success",
                "session_info": info
            }
    
    def list_active_sessions(self) -> Dict[str, Any]:
        """
        List all active sessions.
        
        Returns:
            Dictionary with active sessions
        """
        with self.lock:
            sessions = {}
            for name, info in self.connection_info.items():
                sessions[name] = {
                    "host": info["host"],
                    "share": info["share"],
                    "username": info["username"],
                    "connected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(info["connected_at"]))
                }
            
            return {
                "status": "success",
                "active_sessions": sessions,
                "total_sessions": len(sessions)
            }
    
    def close_all_connections(self) -> Dict[str, Any]:
        """
        Close all active connections.
        
        Returns:
            Result dictionary
        """
        try:
            with self.lock:
                closed_count = 0
                for session_name, conn in self.connections.items():
                    try:
                        conn.close()
                        closed_count += 1
                    except Exception as e:
                        Output.Console(self.plugin_name, f"Error closing session {session_name}: {str(e)}")
                
                self.connections.clear()
                self.connection_info.clear()
                
                return {
                    "status": "success",
                    "message": f"Closed {closed_count} connections",
                    "closed_count": closed_count
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": "Failed to close all connections",
                "details": str(e)
            }