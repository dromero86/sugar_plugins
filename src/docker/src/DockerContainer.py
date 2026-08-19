"""
Docker Container Component
=========================

Component for managing Docker containers.
Provides container operations like run, stop, remove, inspect, etc.
"""

import json
import subprocess
import time
from typing import Any, Dict, List, Optional

from Sugar.Lang.Utils.Output import Output

class DockerContainer:
    """
    Docker container management component.
    
    Provides operations for:
    - Running containers
    - Stopping containers
    - Removing containers
    - Inspecting containers
    - Getting logs
    - Executing commands
    - Getting statistics
    """
    
    def __init__(self, plugin):
        """
        Initialize the Docker container component.
        
        Args:
            plugin: Reference to the main Docker plugin
        """
        self.plugin = plugin
        self.plugin_name = plugin.plugin_name
    
    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a Docker container.
        
        Args:
            config: Container configuration
            
        Returns:
            Result dictionary with container information
        """
        try:
            name = config.get("name")
            image = config.get("image")
            
            if not image:
                raise ValueError("Image is required")
            
            # Build docker run command
            cmd = ["docker", "run", "-d"]
            
            # Add name if specified
            if name:
                cmd.extend(["--name", name])
            
            # Add ports
            ports = config.get("ports", [])
            for port in ports:
                cmd.extend(["-p", port])
            
            # Add environment variables
            environment = config.get("environment", {})
            for key, value in environment.items():
                cmd.extend(["-e", f"{key}={value}"])
            
            # Add volumes
            volumes = config.get("volumes", [])
            for volume in volumes:
                cmd.extend(["-v", volume])
            
            # Add networks
            networks = config.get("networks", [])
            for network in networks:
                cmd.extend(["--network", network])
            
            # Add restart policy
            restart = config.get("restart")
            if restart:
                cmd.extend(["--restart", restart])
            
            # Add working directory
            working_dir = config.get("working_dir")
            if working_dir:
                cmd.extend(["-w", working_dir])
            
            # Add user
            user = config.get("user")
            if user:
                cmd.extend(["-u", user])
            
            # Add labels
            labels = config.get("labels", {})
            for key, value in labels.items():
                cmd.extend(["--label", f"{key}={value}"])
            
            # Add image
            cmd.append(image)
            
            # Add command
            command = config.get("command")
            if command:
                if isinstance(command, str):
                    cmd.extend(command.split())
                elif isinstance(command, list):
                    cmd.extend(command)
            
            # Execute command
            Output.Console(self.plugin_name, f"Running container: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                container_id = result.stdout.strip()
                
                # Wait a moment for container to start
                time.sleep(1)
                
                # Get container info
                container_info = self.inspect({"container_id": container_id})
                
                return {
                    "status": "success",
                    "container_id": container_id,
                    "name": name,
                    "image": image,
                    "info": container_info
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr,
                    "command": ' '.join(cmd)
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error running container: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def stop(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stop a Docker container.
        
        Args:
            config: Container configuration
            
        Returns:
            Result dictionary
        """
        try:
            container_id = config.get("container_id")
            if not container_id:
                raise ValueError("Container ID is required")
            
            timeout = config.get("timeout", 10)
            
            cmd = ["docker", "stop", "-t", str(timeout), container_id]
            
            Output.Console(self.plugin_name, f"Stopping container: {container_id}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "container_id": container_id,
                    "message": f"Container {container_id} stopped"
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr,
                    "container_id": container_id
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error stopping container: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def remove(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove a Docker container.
        
        Args:
            config: Container configuration
            
        Returns:
            Result dictionary
        """
        try:
            container_id = config.get("container_id")
            if not container_id:
                raise ValueError("Container ID is required")
            
            force = config.get("force", False)
            volumes = config.get("volumes", False)
            
            cmd = ["docker", "rm"]
            
            if force:
                cmd.append("-f")
            
            if volumes:
                cmd.append("-v")
            
            cmd.append(container_id)
            
            Output.Console(self.plugin_name, f"Removing container: {container_id}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "container_id": container_id,
                    "message": f"Container {container_id} removed"
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr,
                    "container_id": container_id
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error removing container: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def inspect(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inspect a Docker container.
        
        Args:
            config: Container configuration
            
        Returns:
            Container inspection data
        """
        try:
            container_id = config.get("container_id")
            if not container_id:
                raise ValueError("Container ID is required")
            
            cmd = ["docker", "inspect", container_id]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                try:
                    container_data = json.loads(result.stdout)
                    if container_data:
                        return {
                            "status": "success",
                            "container_id": container_id,
                            "data": container_data[0]
                        }
                    else:
                        return {
                            "status": "error",
                            "error": "Container not found",
                            "container_id": container_id
                        }
                except json.JSONDecodeError:
                    return {
                        "status": "error",
                        "error": "Invalid JSON response",
                        "container_id": container_id
                    }
            else:
                return {
                    "status": "error",
                    "error": result.stderr,
                    "container_id": container_id
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error inspecting container: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def logs(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get logs from a Docker container.
        
        Args:
            config: Container configuration
            
        Returns:
            Container logs
        """
        try:
            container_id = config.get("container_id")
            if not container_id:
                raise ValueError("Container ID is required")
            
            follow = config.get("follow", False)
            tail = config.get("tail", "all")
            timestamps = config.get("timestamps", False)
            
            cmd = ["docker", "logs"]
            
            if follow:
                cmd.append("-f")
            
            if timestamps:
                cmd.append("-t")
            
            if tail != "all":
                cmd.extend(["--tail", str(tail)])
            
            cmd.append(container_id)
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "container_id": container_id,
                    "logs": result.stdout,
                    "stderr": result.stderr
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr,
                    "container_id": container_id
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error getting container logs: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def exec_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a command in a Docker container.
        
        Args:
            config: Container configuration
            
        Returns:
            Command execution result
        """
        try:
            container_id = config.get("container_id")
            command = config.get("command")
            interactive = config.get("interactive", False)
            user = config.get("user")
            working_dir = config.get("working_dir")
            
            if not container_id:
                raise ValueError("Container ID is required")
            
            if not command:
                raise ValueError("Command is required")
            
            cmd = ["docker", "exec"]
            
            if interactive:
                cmd.extend(["-i", "-t"])
            
            if user:
                cmd.extend(["-u", user])
            
            if working_dir:
                cmd.extend(["-w", working_dir])
            
            cmd.append(container_id)
            
            # Add command
            if isinstance(command, str):
                cmd.extend(command.split())
            elif isinstance(command, list):
                cmd.extend(command)
            
            Output.Console(self.plugin_name, f"Executing command in container {container_id}: {' '.join(cmd[3:])}")
            
            if interactive:
                # For interactive commands, run without capture
                result = subprocess.run(cmd)
                return {
                    "status": "success" if result.returncode == 0 else "error",
                    "container_id": container_id,
                    "command": command,
                    "return_code": result.returncode
                }
            else:
                # For non-interactive commands, capture output
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                return {
                    "status": "success" if result.returncode == 0 else "error",
                    "container_id": container_id,
                    "command": command,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing command in container: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def stats(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get statistics from a Docker container.
        
        Args:
            config: Container configuration
            
        Returns:
            Container statistics
        """
        try:
            container_id = config.get("container_id")
            if not container_id:
                raise ValueError("Container ID is required")
            
            no_stream = config.get("no_stream", True)
            
            cmd = ["docker", "stats"]
            
            if no_stream:
                cmd.append("--no-stream")
            
            cmd.append(container_id)
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "container_id": container_id,
                    "stats": result.stdout
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr,
                    "container_id": container_id
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error getting container stats: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def list_all(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List all Docker containers.
        
        Args:
            config: Optional configuration
            
        Returns:
            List of containers
        """
        try:
            all_containers = config.get("all", False) if config else False
            
            cmd = ["docker", "ps"]
            
            if all_containers:
                cmd.append("-a")
            
            cmd.extend(["--format", "json"])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            container_data = json.loads(line)
                            containers.append(container_data)
                        except json.JSONDecodeError:
                            continue
                
                return {
                    "status": "success",
                    "containers": containers,
                    "count": len(containers)
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error listing containers: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }