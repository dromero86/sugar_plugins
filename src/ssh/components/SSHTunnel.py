"""
SSH Tunnel Handler
=================

Handles SSH tunneling operations for port forwarding.
"""

import socket
import threading
import time
from typing import Optional

from Sugar.Lang.Utils.Output import Output

class SSHTunnel:
    """
    SSH tunnel handler for port forwarding.
    
    Supports both local and reverse port forwarding.
    """
    
    def __init__(self, connection, local_port: int = None, remote_host: str = None, 
                 remote_port: int = None, local_host: str = "127.0.0.1", reverse: bool = False):
        """
        Initialize SSH tunnel.
        
        Args:
            connection: SSH connection object
            local_port: Local port for forwarding
            remote_host: Remote host for forwarding
            remote_port: Remote port for forwarding
            local_host: Local host for forwarding (default: 127.0.0.1)
            reverse: True for reverse tunnel, False for local tunnel
        """
        self.connection = connection
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.local_host = local_host
        self.reverse = reverse
        
        self.tunnel_thread = None
        self.running = False
        self.server_socket = None
        
        Output.Console("SSHTunnel", f"SSH tunnel initialized: {self._get_description()}")
    
    def start(self) -> bool:
        """
        Start the SSH tunnel.
        
        Returns:
            True if tunnel started successfully, False otherwise
        """
        try:
            if self.reverse:
                return self._start_reverse_tunnel()
            else:
                return self._start_local_tunnel()
        except Exception as e:
            Output.Console("SSHTunnel", f"Error starting tunnel: {str(e)}")
            return False
    
    def stop(self):
        """Stop the SSH tunnel."""
        self.running = False
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
        
        if self.tunnel_thread and self.tunnel_thread.is_alive():
            self.tunnel_thread.join(timeout=5)
        
        Output.Console("SSHTunnel", f"SSH tunnel stopped: {self._get_description()}")
    
    def _start_local_tunnel(self) -> bool:
        """
        Start local port forwarding tunnel.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create local server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.local_host, self.local_port))
            self.server_socket.listen(5)
            
            self.running = True
            self.tunnel_thread = threading.Thread(target=self._local_tunnel_worker)
            self.tunnel_thread.daemon = True
            self.tunnel_thread.start()
            
            Output.Console("SSHTunnel", f"Local tunnel started: {self.local_host}:{self.local_port} -> {self.remote_host}:{self.remote_port}")
            return True
            
        except Exception as e:
            Output.Console("SSHTunnel", f"Error starting local tunnel: {str(e)}")
            return False
    
    def _start_reverse_tunnel(self) -> bool:
        """
        Start reverse port forwarding tunnel.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use paramiko's transport for reverse tunnel
            transport = self.connection.client.get_transport()
            
            # Request reverse tunnel
            transport.request_port_forward(
                self.remote_host, 
                self.remote_port, 
                self.local_host, 
                self.local_port
            )
            
            self.running = True
            Output.Console("SSHTunnel", f"Reverse tunnel started: {self.remote_host}:{self.remote_port} -> {self.local_host}:{self.local_port}")
            return True
            
        except Exception as e:
            Output.Console("SSHTunnel", f"Error starting reverse tunnel: {str(e)}")
            return False
    
    def _local_tunnel_worker(self):
        """
        Worker thread for local tunnel.
        """
        while self.running:
            try:
                # Accept client connection
                client_socket, client_addr = self.server_socket.accept()
                
                # Create tunnel thread for this connection
                tunnel_thread = threading.Thread(
                    target=self._handle_tunnel_connection,
                    args=(client_socket,)
                )
                tunnel_thread.daemon = True
                tunnel_thread.start()
                
            except Exception as e:
                if self.running:
                    Output.Console("SSHTunnel", f"Error in tunnel worker: {str(e)}")
                break
    
    def _handle_tunnel_connection(self, client_socket):
        """
        Handle individual tunnel connection.
        
        Args:
            client_socket: Client socket connection
        """
        try:
            # Create remote connection through SSH
            transport = self.connection.client.get_transport()
            remote_socket = transport.open_channel(
                'direct-tcpip',
                (self.remote_host, self.remote_port),
                ('', 0)
            )
            
            # Start bidirectional data transfer
            self._transfer_data(client_socket, remote_socket)
            
        except Exception as e:
            Output.Console("SSHTunnel", f"Error handling tunnel connection: {str(e)}")
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def _transfer_data(self, socket1, socket2):
        """
        Transfer data between two sockets.
        
        Args:
            socket1: First socket
            socket2: Second socket
        """
        def forward(src, dst):
            try:
                while self.running:
                    data = src.recv(4096)
                    if not data:
                        break
                    dst.send(data)
            except:
                pass
            finally:
                try:
                    src.close()
                    dst.close()
                except:
                    pass
        
        # Start bidirectional transfer
        thread1 = threading.Thread(target=forward, args=(socket1, socket2))
        thread2 = threading.Thread(target=forward, args=(socket2, socket1))
        
        thread1.daemon = True
        thread2.daemon = True
        
        thread1.start()
        thread2.start()
        
        # Wait for threads to complete
        thread1.join()
        thread2.join()
    
    def _get_description(self) -> str:
        """
        Get tunnel description.
        
        Returns:
            String description of the tunnel
        """
        if self.reverse:
            return f"{self.remote_host}:{self.remote_port} -> {self.local_host}:{self.local_port}"
        else:
            return f"{self.local_host}:{self.local_port} -> {self.remote_host}:{self.remote_port}"
    
    def is_running(self) -> bool:
        """
        Check if tunnel is running.
        
        Returns:
            True if tunnel is running, False otherwise
        """
        return self.running
    
    def __del__(self):
        """Cleanup on destruction."""
        self.stop()