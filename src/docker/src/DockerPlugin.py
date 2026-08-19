"""
Docker Plugin Implementation
===========================

Main plugin class for Docker functionality.
Provides container management, service composition, and Docker Compose-like functionality.
"""

import os
import json
import yaml
import tempfile
import subprocess
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict

from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output

from .DockerCompose import DockerCompose
from .DockerContainer import DockerContainer
from .DockerNetwork import DockerNetwork
from .DockerVolume import DockerVolume

@dataclass
class ServiceConfig:
    """Configuration for a Docker service."""
    name: str
    image: str
    ports: Optional[List[str]] = None
    environment: Optional[Dict[str, str]] = None
    volumes: Optional[List[str]] = None
    networks: Optional[List[str]] = None
    depends_on: Optional[List[str]] = None
    restart: Optional[str] = None
    command: Optional[str] = None
    working_dir: Optional[str] = None
    user: Optional[str] = None
    healthcheck: Optional[Dict[str, Any]] = None
    labels: Optional[Dict[str, str]] = None
    deploy: Optional[Dict[str, Any]] = None

@dataclass
class NetworkConfig:
    """Configuration for a Docker network."""
    name: str
    driver: str = "bridge"
    external: bool = False
    labels: Optional[Dict[str, str]] = None

@dataclass
class VolumeConfig:
    """Configuration for a Docker volume."""
    name: str
    driver: str = "local"
    external: bool = False
    labels: Optional[Dict[str, str]] = None

class DockerPlugin(PluginBase):
    """
    Docker plugin for Sugar.
    
    Provides Docker functionality including:
    - Container management
    - Service composition (Docker Compose-like)
    - Network management
    - Volume management
    - Health monitoring
    - Service orchestration
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Docker plugin for Sugar with Docker Compose-like functionality"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = ["docker", "pyyaml"]
    REQUIREMENTS = ["docker>=6.0.0", "pyyaml>=6.0"]
    
    # System dependencies
    SYSTEM_DEPENDENCIES = ["docker"]
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Docker plugin.
        
        Args:
            context: Sugar service context
            plugin_config: Plugin configuration
        """
        super().__init__(context, plugin_config)
        
        # Check if Docker is available
        self.docker_available = self._check_docker_availability()
        
        if self.docker_available:
            # Initialize components
            self.compose = DockerCompose(self)
            self.container = DockerContainer(self)
            self.network = DockerNetwork(self)
            self.volume = DockerVolume(self)
            Output.Console(self.plugin_name, "Docker plugin initialized with real Docker support")
        else:
            Output.Console(self.plugin_name, "Docker not available - running in simulation mode")
        
        # Store compositions and services
        self.compositions: Dict[str, Dict[str, Any]] = {}
        self.services: Dict[str, ServiceConfig] = {}
        self.networks: Dict[str, NetworkConfig] = {}
        self.volumes: Dict[str, VolumeConfig] = {}
        
        # Active containers and services (simulated)
        self.active_containers: Dict[str, Dict[str, Any]] = {}  # container_id -> container_info
        self.active_services: Dict[str, Dict[str, Any]] = {}
        
        Output.Console(self.plugin_name, "Docker plugin components initialized")
    
    def _check_docker_availability(self) -> bool:
        """Check if Docker is available on the system."""
        try:
            # Check if docker command exists
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                return False
            
            # Check if docker daemon is running
            result = subprocess.run(["docker", "info"], capture_output=True, text=True)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.SubprocessError):
            return False
    
    def get_available_commands(self) -> List[str]:
        """
        Get list of available commands.
        
        Returns:
            List of available command names
        """
        return [
            # Main Docker command
            "docker",
            
            # Composition commands
            "create_composition", "start_composition", "stop_composition", 
            "restart_composition", "destroy_composition", "status_composition",
            
            # Service commands
            "create_service", "start_service", "stop_service", "restart_service",
            "destroy_service", "status_service", "logs_service", "exec_service",
            
            # Container commands
            "run_container", "stop_container", "remove_container", "inspect_container",
            "logs_container", "exec_container", "stats_container",
            
            # Network commands
            "create_network", "remove_network", "list_networks", "inspect_network",
            
            # Volume commands
            "create_volume", "remove_volume", "list_volumes", "inspect_volume",
            
            # Utility commands
            "list_services", "list_compositions", "health_check", "cleanup",
            "export_compose", "import_compose", "validate_composition"
        ]
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """
        Execute a Docker plugin command.
        
        Args:
            command: The command to execute
            config: Configuration dictionary for the command
            
        Returns:
            The result of the command execution
        """
        try:
            # Interpolate variables in config
            config = self._interpolate_config(config)
            
            # Handle main docker command
            if command == "docker":
                operator = config.get("operator")
                if not operator:
                    raise ValueError("Docker operator is required")
                
                # Remove operator from config to get parameters
                params = {k: v for k, v in config.items() if k != "operator"}
                
                # Execute the specific operator
                return self.execute(operator, params)
            
            # Handle specific commands
            elif command == "run_container":
                if self.docker_available:
                    return self._run_container_real(config)
                else:
                    return self._run_container_simulated(config)
            elif command == "stop_container":
                if self.docker_available:
                    return self._stop_container_real(config)
                else:
                    return self._stop_container_simulated(config)
            elif command == "remove_container":
                if self.docker_available:
                    return self._remove_container_real(config)
                else:
                    return self._remove_container_simulated(config)
            elif command == "inspect_container":
                if self.docker_available:
                    return self._inspect_container_real(config)
                else:
                    return self._inspect_container_simulated(config)
            elif command == "logs_container":
                if self.docker_available:
                    return self._logs_container_real(config)
                else:
                    return self._logs_container_simulated(config)
            elif command == "exec_container":
                if self.docker_available:
                    return self._exec_container_real(config)
                else:
                    return self._exec_container_simulated(config)
            elif command == "stats_container":
                if self.docker_available:
                    return self._stats_container_real(config)
                else:
                    return self._stats_container_simulated(config)
            elif command == "create_composition":
                return self._create_composition(config)
            elif command == "start_composition":
                return self._start_composition_simulated(config)
            elif command == "stop_composition":
                return self._stop_composition_simulated(config)
            elif command == "status_composition":
                return self._status_composition_simulated(config)
            elif command == "list_services":
                return self._list_services()
            elif command == "list_compositions":
                return self._list_compositions()
            elif command == "health_check":
                return self._health_check_simulated(config)
            elif command == "cleanup":
                return self._cleanup_simulated(config)
            else:
                raise ValueError(f"Unknown command: {command}")
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing command '{command}': {str(e)}")
            raise
    
    def _interpolate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Interpolate variables in configuration."""
        if not config:
            return config
            
        try:
            interpolated = {}
            for key, value in config.items():
                if isinstance(value, str):
                    interpolated[key] = self._interpolate_nested_variables(value)
                elif isinstance(value, dict):
                    interpolated[key] = self._interpolate_config(value)
                elif isinstance(value, list):
                    interpolated[key] = [
                        self._interpolate_nested_variables(item) if isinstance(item, str) else item
                        for item in value
                    ]
                else:
                    interpolated[key] = value
            
            return interpolated
        except Exception as e:
            Output.Console(self.plugin_name, f"Error interpolating variables: {str(e)}")
            return config
    
    def _interpolate_nested_variables(self, value: str) -> str:
        """Interpolate nested variables like {{container_result.container_id}}."""
        if not isinstance(value, str):
            return value
        
        import re
        
        # Pattern to match {{variable.subproperty}}
        pattern = r'\{\{([^}]+)\}\}'
        
        def replace_nested_var(match):
            var_path = match.group(1).strip()
            try:
                # Split by dots to handle nested properties
                parts = var_path.split('.')
                var_name = parts[0]
                
                # Get the base variable
                if hasattr(self.context, 'memory_handler'):
                    base_value = self.context.memory_handler.get_variable(var_name, "")
                elif hasattr(self.context, 'get_variable'):
                    base_value = self.context.get_variable(var_name, "")
                else:
                    return match.group(0)  # Return original if no memory handler
                
                # Navigate through nested properties
                current_value = base_value
                for part in parts[1:]:
                    if isinstance(current_value, dict) and part in current_value:
                        current_value = current_value[part]
                    elif hasattr(current_value, part):
                        current_value = getattr(current_value, part)
                    else:
                        Output.Console(self.plugin_name, f"Property '{part}' not found in {var_name}")
                        return match.group(0)
                
                return str(current_value)
            except Exception as e:
                Output.Console(self.plugin_name, f"Error interpolating nested variable '{var_path}': {str(e)}")
                return match.group(0)
        
        return re.sub(pattern, replace_nested_var, value)
    
    def _run_container_simulated(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate running a Docker container."""
        name = config.get("name", f"container_{uuid.uuid4().hex[:8]}")
        image = config.get("image", "unknown:latest")
        
        container_id = f"sim_{uuid.uuid4().hex[:12]}"
        
        # Create simulated container info
        container_info = {
            "id": container_id,
            "name": name,
            "image": image,
            "status": "running",
            "created": time.time(),
            "ports": config.get("ports", []),
            "environment": config.get("environment", {}),
            "labels": config.get("labels", {}),
            "networks": config.get("networks", []),
            "volumes": config.get("volumes", []),
            "command": config.get("command"),
            "working_dir": config.get("working_dir"),
            "user": config.get("user"),
            "restart": config.get("restart")
        }
        
        self.active_containers[container_id] = container_info
        
        Output.Console(self.plugin_name, f"Simulated container {name} ({container_id}) started")
        
        return {
            "status": "success",
            "container_id": container_id,
            "name": name,
            "image": image,
            "message": f"Container {name} started successfully (simulated)"
        }
    
    def _run_container_real(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a real Docker container."""
        name = config.get("name", f"container_{uuid.uuid4().hex[:8]}")
        image = config.get("image", "unknown:latest")
        
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
        env = config.get("environment", {})
        for key, value in env.items():
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
        
        # Add labels
        labels = config.get("labels", {})
        for key, value in labels.items():
            cmd.extend(["--label", f"{key}={value}"])
        
        # Add command
        command = config.get("command")
        if command:
            cmd.extend(["--entrypoint", command])
        
        # Add working directory
        working_dir = config.get("working_dir")
        if working_dir:
            cmd.extend(["-w", working_dir])
        
        # Add user
        user = config.get("user")
        if user:
            cmd.extend(["-u", user])
        
        # Add image
        cmd.append(image)
        
        # Execute command
        try:
            Output.Console(self.plugin_name, f"Running real Docker container: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                container_id = result.stdout.strip()
                Output.Console(self.plugin_name, f"Real container {name} ({container_id}) started")
                
                return {
                    "status": "success",
                    "container_id": container_id,
                    "name": name,
                    "image": image,
                    "message": f"Container {name} started successfully"
                }
            else:
                Output.Console(self.plugin_name, f"Error running container: {result.stderr}")
                return {
                    "status": "error",
                    "error": result.stderr,
                    "return_code": result.returncode
                }
        except Exception as e:
            Output.Console(self.plugin_name, f"Exception running container: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _stop_container_simulated(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate stopping a Docker container."""
        container_id = config.get("container_id")
        if not container_id:
            return {"status": "error", "error": "Container ID is required"}
        
        # Check if container_id is still a template (not interpolated)
        if "{{" in str(container_id):
            Output.Console(self.plugin_name, f"Container ID not interpolated: {container_id}")
            return {"status": "error", "error": f"Container ID not interpolated: {container_id}"}
        
        if container_id not in self.active_containers:
            Output.Console(self.plugin_name, f"Container {container_id} not found in active containers: {list(self.active_containers.keys())}")
            return {"status": "error", "error": f"Container {container_id} not found"}
        
        container_info = self.active_containers[container_id]
        container_info["status"] = "stopped"
        
        Output.Console(self.plugin_name, f"Simulated container {container_info['name']} stopped")
        
        return {
            "status": "success",
            "container_id": container_id,
            "message": f"Container {container_info['name']} stopped (simulated)"
        }
    
    def _stop_container_real(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Stop a real Docker container."""
        container_id = config.get("container_id")
        if not container_id:
            return {"status": "error", "error": "Container ID is required"}
        
        # Check if container_id is still a template (not interpolated)
        if "{{" in str(container_id):
            Output.Console(self.plugin_name, f"Container ID not interpolated: {container_id}")
            return {"status": "error", "error": f"Container ID not interpolated: {container_id}"}
        
        cmd = ["docker", "stop", container_id]
        
        try:
            Output.Console(self.plugin_name, f"Stopping real Docker container: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                Output.Console(self.plugin_name, f"Real container {container_id} stopped")
                return {
                    "status": "success",
                    "container_id": container_id,
                    "message": f"Container {container_id} stopped successfully"
                }
            else:
                Output.Console(self.plugin_name, f"Error stopping container: {result.stderr}")
                return {
                    "status": "error",
                    "error": result.stderr,
                    "return_code": result.returncode
                }
        except Exception as e:
            Output.Console(self.plugin_name, f"Exception stopping container: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _remove_container_simulated(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate removing a Docker container."""
        container_id = config.get("container_id")
        if not container_id:
            return {"status": "error", "error": "Container ID is required"}
        
        # Check if container_id is still a template (not interpolated)
        if "{{" in str(container_id):
            Output.Console(self.plugin_name, f"Container ID not interpolated: {container_id}")
            return {"status": "error", "error": f"Container ID not interpolated: {container_id}"}
        
        if container_id not in self.active_containers:
            Output.Console(self.plugin_name, f"Container {container_id} not found in active containers: {list(self.active_containers.keys())}")
            return {"status": "error", "error": f"Container {container_id} not found"}
        
        container_info = self.active_containers.pop(container_id)
        
        Output.Console(self.plugin_name, f"Simulated container {container_info['name']} removed")
        
        return {
            "status": "success",
            "container_id": container_id,
            "message": f"Container {container_info['name']} removed (simulated)"
        }
    
    def _remove_container_real(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Remove a real Docker container."""
        container_id = config.get("container_id")
        force = config.get("force", False)
        
        if not container_id:
            return {"status": "error", "error": "Container ID is required"}
        
        # Check if container_id is still a template (not interpolated)
        if "{{" in str(container_id):
            Output.Console(self.plugin_name, f"Container ID not interpolated: {container_id}")
            return {"status": "error", "error": f"Container ID not interpolated: {container_id}"}
        
        cmd = ["docker", "rm"]
        if force:
            cmd.append("-f")
        cmd.append(container_id)
        
        try:
            Output.Console(self.plugin_name, f"Removing real Docker container: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                Output.Console(self.plugin_name, f"Real container {container_id} removed")
                return {
                    "status": "success",
                    "container_id": container_id,
                    "message": f"Container {container_id} removed successfully"
                }
            else:
                Output.Console(self.plugin_name, f"Error removing container: {result.stderr}")
                return {
                    "status": "error",
                    "error": result.stderr,
                    "return_code": result.returncode
                }
        except Exception as e:
            Output.Console(self.plugin_name, f"Exception removing container: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _inspect_container_simulated(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate inspecting a Docker container."""
        container_id = config.get("container_id")
        if not container_id:
            return {"status": "error", "error": "Container ID is required"}
        
        # Check if container_id is still a template (not interpolated)
        if "{{" in str(container_id):
            Output.Console(self.plugin_name, f"Container ID not interpolated: {container_id}")
            return {"status": "error", "error": f"Container ID not interpolated: {container_id}"}
        
        if container_id not in self.active_containers:
            Output.Console(self.plugin_name, f"Container {container_id} not found in active containers: {list(self.active_containers.keys())}")
            return {"status": "error", "error": f"Container {container_id} not found"}
        
        container_info = self.active_containers[container_id]
        
        Output.Console(self.plugin_name, f"Simulated inspection of container {container_info['name']} ({container_id})")
        
        return {
            "status": "success",
            "container_id": container_id,
            "data": {
                "Id": container_id,
                "Name": f"/{container_info['name']}",
                "Image": container_info['image'],
                "State": {
                    "Status": container_info['status'],
                    "Running": container_info['status'] == "running",
                    "StartedAt": container_info['created']
                },
                "Config": {
                    "Image": container_info['image'],
                    "Cmd": container_info['command'],
                    "WorkingDir": container_info['working_dir'],
                    "User": container_info['user'],
                    "Env": [f"{k}={v}" for k, v in container_info['environment'].items()],
                    "Labels": container_info['labels']
                },
                "NetworkSettings": {
                    "Ports": {port: [{"HostIp": "0.0.0.0", "HostPort": port.split(":")[0]}] for port in container_info['ports']},
                    "Networks": {network: {"IPAddress": "172.17.0.2"} for network in container_info['networks']}
                }
            }
        }
    
    def _inspect_container_real(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Inspect a real Docker container."""
        container_id = config.get("container_id")
        if not container_id:
            return {"status": "error", "error": "Container ID is required"}
        
        # Check if container_id is still a template (not interpolated)
        if "{{" in str(container_id):
            Output.Console(self.plugin_name, f"Container ID not interpolated: {container_id}")
            return {"status": "error", "error": f"Container ID not interpolated: {container_id}"}
        
        cmd = ["docker", "inspect", container_id]
        
        try:
            Output.Console(self.plugin_name, f"Inspecting real Docker container: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                Output.Console(self.plugin_name, f"Real container {container_id} inspected")
                return {
                    "status": "success",
                    "container_id": container_id,
                    "data": data[0] if data else {}
                }
            else:
                Output.Console(self.plugin_name, f"Error inspecting container: {result.stderr}")
                return {
                    "status": "error",
                    "error": result.stderr,
                    "return_code": result.returncode
                }
        except Exception as e:
            Output.Console(self.plugin_name, f"Exception inspecting container: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _logs_container_simulated(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate getting logs from a Docker container."""
        container_id = config.get("container_id")
        if not container_id:
            return {"status": "error", "error": "Container ID is required"}
        
        # Check if container_id is still a template (not interpolated)
        if "{{" in str(container_id):
            Output.Console(self.plugin_name, f"Container ID not interpolated: {container_id}")
            return {"status": "error", "error": f"Container ID not interpolated: {container_id}"}
        
        if container_id not in self.active_containers:
            Output.Console(self.plugin_name, f"Container {container_id} not found in active containers: {list(self.active_containers.keys())}")
            return {"status": "error", "error": f"Container {container_id} not found"}
        
        container_info = self.active_containers[container_id]
        
        Output.Console(self.plugin_name, f"Simulated logs for container {container_info['name']} ({container_id})")
        
        # Generate simulated logs
        simulated_logs = f"""
2024-01-01T12:00:00.000Z [INFO] Container {container_info['name']} started
2024-01-01T12:00:01.000Z [INFO] Image: {container_info['image']}
2024-01-01T12:00:02.000Z [INFO] Ports: {', '.join(container_info['ports'])}
2024-01-01T12:00:03.000Z [INFO] Environment variables: {len(container_info['environment'])} set
2024-01-01T12:00:04.000Z [INFO] Container {container_info['name']} is running
""".strip()
        
        return {
            "status": "success",
            "container_id": container_id,
            "logs": simulated_logs,
            "stderr": ""
        }
    
    def _logs_container_real(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get logs from a real Docker container."""
        container_id = config.get("container_id")
        tail = config.get("tail", "all")
        follow = config.get("follow", False)
        
        if not container_id:
            return {"status": "error", "error": "Container ID is required"}
        
        # Check if container_id is still a template (not interpolated)
        if "{{" in str(container_id):
            Output.Console(self.plugin_name, f"Container ID not interpolated: {container_id}")
            return {"status": "error", "error": f"Container ID not interpolated: {container_id}"}
        
        cmd = ["docker", "logs"]
        if tail != "all":
            cmd.extend(["--tail", str(tail)])
        if follow:
            cmd.append("-f")
        cmd.append(container_id)
        
        try:
            Output.Console(self.plugin_name, f"Getting logs from real Docker container: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                Output.Console(self.plugin_name, f"Real container {container_id} logs retrieved")
                return {
                    "status": "success",
                    "container_id": container_id,
                    "logs": result.stdout,
                    "stderr": result.stderr
                }
            else:
                Output.Console(self.plugin_name, f"Error getting logs: {result.stderr}")
                return {
                    "status": "error",
                    "error": result.stderr,
                    "return_code": result.returncode
                }
        except Exception as e:
            Output.Console(self.plugin_name, f"Exception getting logs: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _exec_container_simulated(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate executing a command in a Docker container."""
        container_id = config.get("container_id")
        command = config.get("command")
        
        if not container_id:
            return {"status": "error", "error": "Container ID is required"}
        
        if not command:
            return {"status": "error", "error": "Command is required"}
        
        # Check if container_id is still a template (not interpolated)
        if "{{" in str(container_id):
            Output.Console(self.plugin_name, f"Container ID not interpolated: {container_id}")
            return {"status": "error", "error": f"Container ID not interpolated: {container_id}"}
        
        if container_id not in self.active_containers:
            Output.Console(self.plugin_name, f"Container {container_id} not found in active containers: {list(self.active_containers.keys())}")
            return {"status": "error", "error": f"Container {container_id} not found"}
        
        container_info = self.active_containers[container_id]
        
        Output.Console(self.plugin_name, f"Simulated exec command '{command}' in container {container_info['name']} ({container_id})")
        
        # Generate simulated command output
        if "ps" in command:
            stdout = f"""
PID   USER     TIME  COMMAND
    1 root      0:00 nginx: master process nginx -g daemon off;
    6 nginx     0:00 nginx: worker process
    7 nginx     0:00 nginx: worker process
    8 nginx     0:00 nginx: worker process
    9 nginx     0:00 nginx: worker process
""".strip()
        elif "ls" in command:
            stdout = """
bin
dev
etc
home
lib
media
mnt
opt
proc
root
run
sbin
srv
sys
tmp
usr
var
""".strip()
        else:
            stdout = f"Command '{command}' executed successfully in container {container_info['name']}"
        
        return {
            "status": "success",
            "container_id": container_id,
            "command": command,
            "stdout": stdout,
            "stderr": "",
            "return_code": 0
        }
    
    def _exec_container_real(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command in a real Docker container."""
        container_id = config.get("container_id")
        command = config.get("command")
        interactive = config.get("interactive", False)
        
        if not container_id:
            return {"status": "error", "error": "Container ID is required"}
        
        if not command:
            return {"status": "error", "error": "Command is required"}
        
        # Check if container_id is still a template (not interpolated)
        if "{{" in str(container_id):
            Output.Console(self.plugin_name, f"Container ID not interpolated: {container_id}")
            return {"status": "error", "error": f"Container ID not interpolated: {container_id}"}
        
        cmd = ["docker", "exec"]
        if interactive:
            cmd.extend(["-it"])
        cmd.extend([container_id] + command.split())
        
        try:
            Output.Console(self.plugin_name, f"Executing command in real Docker container: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            Output.Console(self.plugin_name, f"Real container {container_id} command executed")
            return {
                "status": "success",
                "container_id": container_id,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except Exception as e:
            Output.Console(self.plugin_name, f"Exception executing command: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _stats_container_simulated(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate getting statistics from a Docker container."""
        container_id = config.get("container_id")
        if not container_id:
            return {"status": "error", "error": "Container ID is required"}
        
        if container_id not in self.active_containers:
            return {"status": "error", "error": f"Container {container_id} not found"}
        
        container_info = self.active_containers[container_id]
        
        # Generate simulated stats
        simulated_stats = f"""
CONTAINER ID   NAME                CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O         PIDS
{container_id[:12]}   {container_info['name']:<16}   0.50%     15.2MiB / 1.944GiB   0.76%     1.44kB / 648B     0B / 0B           5
""".strip()
        
        return {
            "status": "success",
            "container_id": container_id,
            "stats": simulated_stats
        }
    
    def _stats_container_real(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics from a real Docker container."""
        container_id = config.get("container_id")
        if not container_id:
            return {"status": "error", "error": "Container ID is required"}
        
        # Check if container_id is still a template (not interpolated)
        if "{{" in str(container_id):
            Output.Console(self.plugin_name, f"Container ID not interpolated: {container_id}")
            return {"status": "error", "error": f"Container ID not interpolated: {container_id}"}
        
        cmd = ["docker", "stats", "--no-stream", container_id]
        
        try:
            Output.Console(self.plugin_name, f"Getting stats from real Docker container: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                Output.Console(self.plugin_name, f"Real container {container_id} stats retrieved")
                return {
                    "status": "success",
                    "container_id": container_id,
                    "stats": result.stdout
                }
            else:
                Output.Console(self.plugin_name, f"Error getting stats: {result.stderr}")
                return {
                    "status": "error",
                    "error": result.stderr,
                    "return_code": result.returncode
                }
        except Exception as e:
            Output.Console(self.plugin_name, f"Exception getting stats: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _create_composition(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Docker composition."""
        composition_name = config.get("name")
        if not composition_name:
            raise ValueError("Composition name is required")
        
        # Parse services
        services_config = config.get("services", {})
        services = {}
        
        for service_name, service_data in services_config.items():
            service_config = ServiceConfig(
                name=service_name,
                image=service_data.get("image"),
                ports=service_data.get("ports"),
                environment=service_data.get("environment"),
                volumes=service_data.get("volumes"),
                networks=service_data.get("networks"),
                depends_on=service_data.get("depends_on"),
                restart=service_data.get("restart"),
                command=service_data.get("command"),
                working_dir=service_data.get("working_dir"),
                user=service_data.get("user"),
                healthcheck=service_data.get("healthcheck"),
                labels=service_data.get("labels"),
                deploy=service_data.get("deploy")
            )
            services[service_name] = service_config
        
        # Parse networks
        networks_config = config.get("networks", {})
        networks = {}
        
        for network_name, network_data in networks_config.items():
            if isinstance(network_data, str):
                network_config = NetworkConfig(name=network_name, driver=network_data)
            else:
                network_config = NetworkConfig(
                    name=network_name,
                    driver=network_data.get("driver", "bridge"),
                    external=network_data.get("external", False),
                    labels=network_data.get("labels")
                )
            networks[network_name] = network_config
        
        # Parse volumes
        volumes_config = config.get("volumes", {})
        volumes = {}
        
        for volume_name, volume_data in volumes_config.items():
            if isinstance(volume_data, str):
                volume_config = VolumeConfig(name=volume_name, driver=volume_data)
            else:
                volume_config = VolumeConfig(
                    name=volume_name,
                    driver=volume_data.get("driver", "local"),
                    external=volume_data.get("external", False),
                    labels=volume_data.get("labels")
                )
            volumes[volume_name] = volume_config
        
        # Store composition
        composition = {
            "name": composition_name,
            "services": services,
            "networks": networks,
            "volumes": volumes,
            "version": config.get("version", "3.8"),
            "created_at": time.time(),
            "status": "created"
        }
        
        self.compositions[composition_name] = composition
        
        # Store individual components
        self.services.update(services)
        self.networks.update(networks)
        self.volumes.update(volumes)
        
        result = {
            "status": "success",
            "composition_name": composition_name,
            "services_count": len(services),
            "networks_count": len(networks),
            "volumes_count": len(volumes),
            "message": f"Composition '{composition_name}' created successfully"
        }
        
        if "result" in config:
            self.set_variable(config["result"], result)
        
        Output.Console(self.plugin_name, f"Composition '{composition_name}' created with {len(services)} services")
        return result
    
    def _start_composition_simulated(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate starting a Docker composition."""
        composition_name = config.get("name")
        if not composition_name:
            raise ValueError("Composition name is required")
        
        if composition_name not in self.compositions:
            raise ValueError(f"Composition '{composition_name}' not found")
        
        composition = self.compositions[composition_name]
        services = composition["services"]
        
        started_services = []
        failed_services = []
        
        for service_name, service_config in services.items():
            try:
                # Simulate starting service
                container_id = f"sim_{uuid.uuid4().hex[:12]}"
                
                container_info = {
                    "id": container_id,
                    "name": service_name,
                    "image": service_config.image,
                    "status": "running",
                    "created": time.time(),
                    "ports": service_config.ports or [],
                    "environment": service_config.environment or {},
                    "labels": service_config.labels or {},
                    "networks": service_config.networks or [],
                    "volumes": service_config.volumes or [],
                    "command": service_config.command,
                    "working_dir": service_config.working_dir,
                    "user": service_config.user,
                    "restart": service_config.restart
                }
                
                self.active_containers[container_id] = container_info
                started_services.append(service_name)
                
                Output.Console(self.plugin_name, f"Service '{service_name}' started successfully (simulated)")
                
            except Exception as e:
                failed_services.append(service_name)
                Output.Console(self.plugin_name, f"Failed to start service '{service_name}': {str(e)}")
        
        # Update composition status
        composition["status"] = "running" if not failed_services else "partial"
        composition["started_services"] = started_services
        composition["failed_services"] = failed_services
        
        result = {
            "status": "success" if not failed_services else "partial",
            "composition_name": composition_name,
            "started_services": started_services,
            "failed_services": failed_services,
            "message": f"Composition '{composition_name}' started with {len(started_services)} services (simulated)"
        }
        
        if "result" in config:
            self.set_variable(config["result"], result)
        
        return result
    
    def _stop_composition_simulated(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate stopping a Docker composition."""
        composition_name = config.get("name")
        if not composition_name:
            raise ValueError("Composition name is required")
        
        if composition_name not in self.compositions:
            raise ValueError(f"Composition '{composition_name}' not found")
        
        composition = self.compositions[composition_name]
        services = composition["services"]
        
        stopped_services = []
        failed_services = []
        
        # Stop all containers for this composition
        for container_id, container_info in list(self.active_containers.items()):
            if container_info["name"] in services:
                try:
                    container_info["status"] = "stopped"
                    stopped_services.append(container_info["name"])
                except Exception as e:
                    failed_services.append(container_info["name"])
        
        # Update composition status
        composition["status"] = "stopped" if not failed_services else "partial"
        composition["stopped_services"] = stopped_services
        composition["failed_services"] = failed_services
        
        result = {
            "status": "success" if not failed_services else "partial",
            "composition_name": composition_name,
            "stopped_services": stopped_services,
            "failed_services": failed_services,
            "message": f"Composition '{composition_name}' stopped (simulated)"
        }
        
        if "result" in config:
            self.set_variable(config["result"], result)
        
        return result
    
    def _status_composition_simulated(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate getting status of a Docker composition."""
        composition_name = config.get("name")
        if not composition_name:
            raise ValueError("Composition name is required")
        
        if composition_name not in self.compositions:
            raise ValueError(f"Composition '{composition_name}' not found")
        
        composition = self.compositions[composition_name]
        services_status = {}
        
        for service_name in composition["services"].keys():
            # Find container for this service
            service_running = False
            container_id = None
            
            for cid, container_info in self.active_containers.items():
                if container_info["name"] == service_name:
                    service_running = container_info["status"] == "running"
                    container_id = cid
                    break
            
            services_status[service_name] = {
                "status": "running" if service_running else "stopped",
                "container_id": container_id
            }
        
        result = {
            "composition_name": composition_name,
            "overall_status": composition["status"],
            "services_status": services_status,
            "created_at": composition["created_at"]
        }
        
        if "result" in config:
            self.set_variable(config["result"], result)
        
        return result
    
    def _list_services(self) -> Dict[str, Any]:
        """List all services."""
        return {
            "services": list(self.services.keys()),
            "active_services": list(self.active_services.keys()),
            "total_services": len(self.services),
            "active_count": len(self.active_services)
        }
    
    def _list_compositions(self) -> Dict[str, Any]:
        """List all compositions."""
        compositions_info = {}
        for name, composition in self.compositions.items():
            compositions_info[name] = {
                "status": composition["status"],
                "services_count": len(composition["services"]),
                "created_at": composition["created_at"]
            }
        
        return {
            "compositions": compositions_info,
            "total_compositions": len(self.compositions)
        }
    
    def _health_check_simulated(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate health check on services."""
        composition_name = config.get("composition_name")
        service_name = config.get("service_name")
        
        if composition_name:
            return self._health_check_composition_simulated(composition_name)
        elif service_name:
            return self._health_check_service_simulated(service_name)
        else:
            return self._health_check_all_simulated()
    
    def _health_check_composition_simulated(self, composition_name: str) -> Dict[str, Any]:
        """Simulate health check for a specific composition."""
        if composition_name not in self.compositions:
            return {"status": "error", "message": f"Composition '{composition_name}' not found"}
        
        composition = self.compositions[composition_name]
        health_results = {}
        
        for service_name in composition["services"].keys():
            health_results[service_name] = self._health_check_service_simulated(service_name)
        
        overall_health = all(
            result.get("healthy", False) 
            for result in health_results.values()
        )
        
        return {
            "composition_name": composition_name,
            "overall_healthy": overall_health,
            "services_health": health_results
        }
    
    def _health_check_service_simulated(self, service_name: str) -> Dict[str, Any]:
        """Simulate health check for a specific service."""
        # Find container for this service
        for container_id, container_info in self.active_containers.items():
            if container_info["name"] == service_name:
                return {
                    "healthy": container_info["status"] == "running",
                    "status": container_info["status"],
                    "health_status": "healthy" if container_info["status"] == "running" else "unhealthy"
                }
        
        return {"healthy": False, "status": "not_running"}
    
    def _health_check_all_simulated(self) -> Dict[str, Any]:
        """Simulate health check for all active services."""
        health_results = {}
        
        for container_id, container_info in self.active_containers.items():
            health_results[container_info["name"]] = self._health_check_service_simulated(container_info["name"])
        
        overall_health = all(
            result.get("healthy", False) 
            for result in health_results.values()
        )
        
        return {
            "overall_healthy": overall_health,
            "services_health": health_results,
            "total_services": len(health_results),
            "healthy_count": sum(1 for r in health_results.values() if r.get("healthy", False))
        }
    
    def _cleanup_simulated(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate cleaning up unused resources."""
        remove_containers = config.get("remove_containers", True)
        remove_networks = config.get("remove_networks", True)
        remove_volumes = config.get("remove_volumes", False)
        
        cleanup_results = {
            "containers_removed": 0,
            "networks_removed": 0,
            "volumes_removed": 0,
            "errors": []
        }
        
        if remove_containers:
            # Remove stopped containers
            stopped_containers = [cid for cid, info in self.active_containers.items() if info["status"] == "stopped"]
            for container_id in stopped_containers:
                del self.active_containers[container_id]
                cleanup_results["containers_removed"] += 1
        
        result = {
            "status": "success",
            "cleanup_results": cleanup_results,
            "message": "Cleanup completed (simulated)"
        }
        
        if "result" in config:
            self.set_variable(config["result"], result)
        
        return result