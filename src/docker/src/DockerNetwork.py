"""
Docker Network Component
=======================

Component for managing Docker networks.
Provides network operations like create, remove, inspect, etc.
"""

import json
import subprocess
from typing import Any, Dict, List, Optional

from Sugar.Lang.Utils.Output import Output

class DockerNetwork:
    """
    Docker network management component.
    
    Provides operations for:
    - Creating networks
    - Removing networks
    - Inspecting networks
    - Listing networks
    - Connecting containers to networks
    - Disconnecting containers from networks
    """
    
    def __init__(self, plugin):
        """
        Initialize the Docker network component.
        
        Args:
            plugin: Reference to the main Docker plugin
        """
        self.plugin = plugin
        self.plugin_name = plugin.plugin_name
    
    def create(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a Docker network.
        
        Args:
            config: Network configuration
            
        Returns:
            Result dictionary with network information
        """
        try:
            name = config.get("name")
            driver = config.get("driver", "bridge")
            subnet = config.get("subnet")
            gateway = config.get("gateway")
            ip_range = config.get("ip_range")
            labels = config.get("labels", {})
            
            if not name:
                raise ValueError("Network name is required")
            
            # Build docker network create command
            cmd = ["docker", "network", "create"]
            
            # Add driver
            cmd.extend(["--driver", driver])
            
            # Add subnet
            if subnet:
                cmd.extend(["--subnet", subnet])
            
            # Add gateway
            if gateway:
                cmd.extend(["--gateway", gateway])
            
            # Add IP range
            if ip_range:
                cmd.extend(["--ip-range", ip_range])
            
            # Add labels
            for key, value in labels.items():
                cmd.extend(["--label", f"{key}={value}"])
            
            # Add network name
            cmd.append(name)
            
            # Execute command
            Output.Console(self.plugin_name, f"Creating network: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                network_id = result.stdout.strip()
                
                # Get network info
                network_info = self.inspect({"name": name})
                
                return {
                    "status": "success",
                    "network_id": network_id,
                    "name": name,
                    "driver": driver,
                    "info": network_info
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr,
                    "command": ' '.join(cmd)
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error creating network: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def remove(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove a Docker network.
        
        Args:
            config: Network configuration
            
        Returns:
            Result dictionary
        """
        try:
            name = config.get("name")
            if not name:
                raise ValueError("Network name is required")
            
            cmd = ["docker", "network", "rm", name]
            
            Output.Console(self.plugin_name, f"Removing network: {name}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "name": name,
                    "message": f"Network {name} removed"
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr,
                    "name": name
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error removing network: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def inspect(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inspect a Docker network.
        
        Args:
            config: Network configuration
            
        Returns:
            Network inspection data
        """
        try:
            name = config.get("name")
            if not name:
                raise ValueError("Network name is required")
            
            cmd = ["docker", "network", "inspect", name]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                try:
                    network_data = json.loads(result.stdout)
                    if network_data:
                        return {
                            "status": "success",
                            "name": name,
                            "data": network_data[0]
                        }
                    else:
                        return {
                            "status": "error",
                            "error": "Network not found",
                            "name": name
                        }
                except json.JSONDecodeError:
                    return {
                        "status": "error",
                        "error": "Invalid JSON response",
                        "name": name
                    }
            else:
                return {
                    "status": "error",
                    "error": result.stderr,
                    "name": name
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error inspecting network: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def list_all(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List all Docker networks.
        
        Args:
            config: Optional configuration
            
        Returns:
            List of networks
        """
        try:
            cmd = ["docker", "network", "ls", "--format", "json"]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                networks = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            network_data = json.loads(line)
                            networks.append(network_data)
                        except json.JSONDecodeError:
                            continue
                
                return {
                    "status": "success",
                    "networks": networks,
                    "count": len(networks)
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error listing networks: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def connect(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Connect a container to a network.
        
        Args:
            config: Connection configuration
            
        Returns:
            Result dictionary
        """
        try:
            network_name = config.get("network")
            container_name = config.get("container")
            ip_address = config.get("ip_address")
            aliases = config.get("aliases", [])
            
            if not network_name:
                raise ValueError("Network name is required")
            
            if not container_name:
                raise ValueError("Container name is required")
            
            cmd = ["docker", "network", "connect"]
            
            # Add IP address
            if ip_address:
                cmd.extend(["--ip", ip_address])
            
            # Add aliases
            for alias in aliases:
                cmd.extend(["--alias", alias])
            
            # Add network and container
            cmd.extend([network_name, container_name])
            
            Output.Console(self.plugin_name, f"Connecting container {container_name} to network {network_name}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "network": network_name,
                    "container": container_name,
                    "message": f"Container {container_name} connected to network {network_name}"
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr,
                    "network": network_name,
                    "container": container_name
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error connecting container to network: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def disconnect(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Disconnect a container from a network.
        
        Args:
            config: Disconnection configuration
            
        Returns:
            Result dictionary
        """
        try:
            network_name = config.get("network")
            container_name = config.get("container")
            force = config.get("force", False)
            
            if not network_name:
                raise ValueError("Network name is required")
            
            if not container_name:
                raise ValueError("Container name is required")
            
            cmd = ["docker", "network", "disconnect"]
            
            if force:
                cmd.append("-f")
            
            cmd.extend([network_name, container_name])
            
            Output.Console(self.plugin_name, f"Disconnecting container {container_name} from network {network_name}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "network": network_name,
                    "container": container_name,
                    "message": f"Container {container_name} disconnected from network {network_name}"
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr,
                    "network": network_name,
                    "container": container_name
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error disconnecting container from network: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def prune(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Remove unused Docker networks.
        
        Args:
            config: Optional configuration
            
        Returns:
            Result dictionary
        """
        try:
            force = config.get("force", True) if config else True
            
            cmd = ["docker", "network", "prune"]
            
            if force:
                cmd.append("-f")
            
            Output.Console(self.plugin_name, "Pruning unused networks")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": "Unused networks pruned",
                    "output": result.stdout
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error pruning networks: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }