"""
SSH Tunnel Module
================

Provides SSH tunneling capabilities for the SSH plugin.
"""

import socket
import threading
import time
from typing import Any, Dict, Optional, Tuple

import paramiko
from paramiko import SSHClient

from Sugar.Lang.Utils.Output import Output

class SSHTunnel:
    """
    SSH Tunnel manager for Sugar SSH plugin.
    
    Handles SSH port forwarding and tunneling.
    """
    
    def __init__(self, ssh_plugin, tunnel_id: str, connection_id: str,
                 local_port: int, remote_host: str, remote_port: int,
                 tunnel_type: str = 'local'):
        """
        Initialize SSH Tunnel.
        
        Args:
            ssh_plugin: Reference to the SSH plugin instance
            tunnel_id: Unique tunnel identifier
            connection_id: SSH connection identifier
            local_port: Local port for forwarding
            remote_host: Remote host for forwarding
            remote_port: Remote port for forwarding
            tunnel_type: Type of tunnel ('local' or 'remote')
        """
        self.ssh_plugin = ssh_plugin
        self.tunnel_id = tunnel_id
        self.connection_id = connection_id
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.tunnel_type = tunnel_type
        
        self.transport = None
        self.active = False
        self.thread = None
        self.stop_event = threading.Event()
        
        Output.Console("SSHTunnel", f"Tunnel {tunnel_id} initialized: {tunnel_type} {local_port} -> {remote_host}:{remote_port}")
    
    def start(self) -> Dict[str, Any]:
        """
        Start the SSH tunnel.
        
        Returns:
            Dictionary with tunnel start results
        """
        try:
            connection = self.ssh_plugin.connections.get(self.connection_id)
            if not connection:
                return {
                    'success': False,
                    'error': f'Connection {self.connection_id} not found'
                }
            
            if not connection.is_connected():
                if not connection.connect():
                    return {
                        'success': False,
                        'error': 'Failed to establish connection'
                    }
            
            # Get transport from SSH client
            self.transport = connection.client.get_transport()
            
            if self.tunnel_type == 'local':
                # Local port forwarding
                self.transport.request_port_forward('', self.local_port, 
                                                  self.remote_host, self.remote_port)
            elif self.tunnel_type == 'remote':
                # Remote port forwarding
                self.transport.request_port_forward(self.remote_host, self.remote_port,
                                                  '', self.local_port)
            else:
                return {
                    'success': False,
                    'error': f'Invalid tunnel type: {self.tunnel_type}'
                }
            
            self.active = True
            
            # Start monitoring thread
            self.thread = threading.Thread(target=self._monitor_tunnel)
            self.thread.daemon = True
            self.thread.start()
            
            Output.Console("SSHTunnel", f"Tunnel {self.tunnel_id} started successfully")
            
            return {
                'success': True,
                'message': f'Tunnel {self.tunnel_id} started',
                'tunnel_id': self.tunnel_id,
                'local_port': self.local_port,
                'remote_host': self.remote_host,
                'remote_port': self.remote_port,
                'tunnel_type': self.tunnel_type
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to start tunnel: {str(e)}'
            }
    
    def stop(self) -> Dict[str, Any]:
        """
        Stop the SSH tunnel.
        
        Returns:
            Dictionary with tunnel stop results
        """
        try:
            if not self.active:
                return {
                    'success': True,
                    'message': f'Tunnel {self.tunnel_id} already stopped'
                }
            
            # Signal thread to stop
            self.stop_event.set()
            
            # Close transport
            if self.transport:
                self.transport.close()
                self.transport = None
            
            self.active = False
            
            # Wait for thread to finish
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=5)
            
            Output.Console("SSHTunnel", f"Tunnel {self.tunnel_id} stopped")
            
            return {
                'success': True,
                'message': f'Tunnel {self.tunnel_id} stopped',
                'tunnel_id': self.tunnel_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to stop tunnel: {str(e)}'
            }
    
    def _monitor_tunnel(self):
        """Monitor tunnel activity and handle cleanup."""
        try:
            while not self.stop_event.is_set() and self.active:
                # Check if transport is still active
                if self.transport and not self.transport.is_active():
                    Output.Console("SSHTunnel", f"Tunnel {self.tunnel_id} transport inactive")
                    break
                
                time.sleep(1)
                
        except Exception as e:
            Output.Console("SSHTunnel", f"Tunnel {self.tunnel_id} monitoring error: {str(e)}")
        finally:
            self.active = False
    
    def is_active(self) -> bool:
        """Check if tunnel is active."""
        return self.active and self.transport and self.transport.is_active()
    
    def get_status(self) -> Dict[str, Any]:
        """Get tunnel status information."""
        return {
            'tunnel_id': self.tunnel_id,
            'connection_id': self.connection_id,
            'local_port': self.local_port,
            'remote_host': self.remote_host,
            'remote_port': self.remote_port,
            'tunnel_type': self.tunnel_type,
            'active': self.is_active(),
            'transport_active': self.transport.is_active() if self.transport else False
        }
    
    def __del__(self):
        """Cleanup on deletion."""
        self.stop()
