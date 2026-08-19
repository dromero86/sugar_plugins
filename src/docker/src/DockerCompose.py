"""
Docker Compose Component
=======================

Component for managing Docker Compose operations.
Provides compose-specific functionality and utilities.
"""

import json
import yaml
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from Sugar.Lang.Utils.Output import Output

class DockerCompose:
    """
    Docker Compose management component.
    
    Provides operations for:
    - Converting Sugar compositions to docker-compose.yml
    - Running docker-compose commands
    - Managing compose projects
    - Validating compose files
    """
    
    def __init__(self, plugin):
        """
        Initialize the Docker Compose component.
        
        Args:
            plugin: Reference to the main Docker plugin
        """
        self.plugin = plugin
        self.plugin_name = plugin.plugin_name
    
    def generate_compose_file(self, composition: Dict[str, Any], output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a docker-compose.yml file from a Sugar composition.
        
        Args:
            composition: Sugar composition configuration
            output_path: Optional output path for the compose file
            
        Returns:
            Result dictionary with compose file information
        """
        try:
            # Convert Sugar composition to docker-compose format
            compose_data = {
                "version": composition.get("version", "3.8"),
                "services": {},
                "networks": {},
                "volumes": {}
            }
            
            # Convert services
            services = composition.get("services", {})
            for service_name, service_config in services.items():
                compose_data["services"][service_name] = {
                    "image": service_config.image,
                    "ports": service_config.ports,
                    "environment": service_config.environment,
                    "volumes": service_config.volumes,
                    "networks": service_config.networks,
                    "depends_on": service_config.depends_on,
                    "restart": service_config.restart,
                    "command": service_config.command,
                    "working_dir": service_config.working_dir,
                    "user": service_config.user,
                    "healthcheck": service_config.healthcheck,
                    "labels": service_config.labels,
                    "deploy": service_config.deploy
                }
                # Remove None values
                compose_data["services"][service_name] = {
                    k: v for k, v in compose_data["services"][service_name].items() 
                    if v is not None
                }
            
            # Convert networks
            networks = composition.get("networks", {})
            for network_name, network_config in networks.items():
                if network_config.external:
                    compose_data["networks"][network_name] = {"external": True}
                else:
                    compose_data["networks"][network_name] = {
                        "driver": network_config.driver,
                        "labels": network_config.labels
                    }
                    # Remove None values
                    compose_data["networks"][network_name] = {
                        k: v for k, v in compose_data["networks"][network_name].items() 
                        if v is not None
                    }
            
            # Convert volumes
            volumes = composition.get("volumes", {})
            for volume_name, volume_config in volumes.items():
                if volume_config.external:
                    compose_data["volumes"][volume_name] = {"external": True}
                else:
                    compose_data["volumes"][volume_name] = {
                        "driver": volume_config.driver,
                        "labels": volume_config.labels
                    }
                    # Remove None values
                    compose_data["volumes"][volume_name] = {
                        k: v for k, v in compose_data["volumes"][volume_name].items() 
                        if v is not None
                    }
            
            # Generate output path if not provided
            if not output_path:
                composition_name = composition.get("name", "composition")
                output_path = f"docker-compose-{composition_name}.yml"
            
            # Write compose file
            with open(output_path, 'w') as f:
                yaml.dump(compose_data, f, default_flow_style=False, sort_keys=False)
            
            return {
                "status": "success",
                "compose_file": output_path,
                "compose_data": compose_data,
                "message": f"Docker Compose file generated: {output_path}"
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error generating compose file: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def run_compose_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a docker-compose command.
        
        Args:
            config: Compose command configuration
            
        Returns:
            Result dictionary
        """
        try:
            command = config.get("command")
            compose_file = config.get("compose_file", "docker-compose.yml")
            project_name = config.get("project_name")
            working_dir = config.get("working_dir")
            
            if not command:
                raise ValueError("Compose command is required")
            
            # Build docker-compose command
            cmd = ["docker-compose"]
            
            # Add project name
            if project_name:
                cmd.extend(["-p", project_name])
            
            # Add compose file
            if compose_file != "docker-compose.yml":
                cmd.extend(["-f", compose_file])
            
            # Add command
            cmd.append(command)
            
            # Add additional arguments
            args = config.get("args", [])
            if args:
                cmd.extend(args)
            
            # Execute command
            Output.Console(self.plugin_name, f"Running docker-compose command: {' '.join(cmd)}")
            
            if working_dir:
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=working_dir)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "command": ' '.join(cmd),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error running docker-compose command: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def validate_compose_file(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a docker-compose.yml file.
        
        Args:
            config: Validation configuration
            
        Returns:
            Validation result
        """
        try:
            compose_file = config.get("compose_file", "docker-compose.yml")
            
            if not os.path.exists(compose_file):
                return {
                    "status": "error",
                    "error": f"Compose file not found: {compose_file}"
                }
            
            # Try to parse the YAML file
            try:
                with open(compose_file, 'r') as f:
                    compose_data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                return {
                    "status": "error",
                    "error": f"Invalid YAML syntax: {str(e)}",
                    "compose_file": compose_file
                }
            
            # Validate structure
            validation_errors = []
            validation_warnings = []
            
            # Check required fields
            if "services" not in compose_data:
                validation_errors.append("Missing 'services' section")
            
            # Validate services
            services = compose_data.get("services", {})
            for service_name, service_config in services.items():
                if not isinstance(service_config, dict):
                    validation_errors.append(f"Service '{service_name}' must be a dictionary")
                    continue
                
                if "image" not in service_config:
                    validation_warnings.append(f"Service '{service_name}' missing image specification")
                
                # Check dependencies
                depends_on = service_config.get("depends_on", [])
                if depends_on:
                    for dep in depends_on:
                        if dep not in services:
                            validation_errors.append(f"Service '{service_name}' depends on non-existent service '{dep}'")
                
                # Check networks
                networks = service_config.get("networks", [])
                if networks:
                    compose_networks = compose_data.get("networks", {})
                    for network in networks:
                        if network not in compose_networks:
                            validation_warnings.append(f"Service '{service_name}' references non-existent network '{network}'")
            
            # Validate networks
            networks = compose_data.get("networks", {})
            for network_name, network_config in networks.items():
                if isinstance(network_config, dict):
                    if not network_config.get("external", False) and "driver" not in network_config:
                        validation_warnings.append(f"Network '{network_name}' missing driver specification")
            
            # Validate volumes
            volumes = compose_data.get("volumes", {})
            for volume_name, volume_config in volumes.items():
                if isinstance(volume_config, dict):
                    if not volume_config.get("external", False) and "driver" not in volume_config:
                        validation_warnings.append(f"Volume '{volume_name}' missing driver specification")
            
            is_valid = len(validation_errors) == 0
            
            return {
                "status": "success",
                "valid": is_valid,
                "compose_file": compose_file,
                "errors": validation_errors,
                "warnings": validation_warnings,
                "services_count": len(services),
                "networks_count": len(networks),
                "volumes_count": len(volumes)
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error validating compose file: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def convert_from_compose(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a docker-compose.yml file to Sugar composition format.
        
        Args:
            config: Conversion configuration
            
        Returns:
            Sugar composition data
        """
        try:
            compose_file = config.get("compose_file", "docker-compose.yml")
            composition_name = config.get("name")
            
            if not os.path.exists(compose_file):
                return {
                    "status": "error",
                    "error": f"Compose file not found: {compose_file}"
                }
            
            # Parse compose file
            with open(compose_file, 'r') as f:
                compose_data = yaml.safe_load(f)
            
            # Convert to Sugar format
            if not composition_name:
                composition_name = Path(compose_file).stem.replace("docker-compose-", "")
            
            sugar_composition = {
                "name": composition_name,
                "version": compose_data.get("version", "3.8"),
                "services": compose_data.get("services", {}),
                "networks": compose_data.get("networks", {}),
                "volumes": compose_data.get("volumes", {})
            }
            
            return {
                "status": "success",
                "composition": sugar_composition,
                "compose_file": compose_file,
                "message": f"Converted {compose_file} to Sugar composition format"
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error converting from compose: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_compose_services(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get list of services from a docker-compose.yml file.
        
        Args:
            config: Configuration
        
        Returns:
            List of services
        """
        try:
            compose_file = config.get("compose_file", "docker-compose.yml")
            
            if not os.path.exists(compose_file):
                return {
                    "status": "error",
                    "error": f"Compose file not found: {compose_file}"
                }
            
            # Parse compose file
            with open(compose_file, 'r') as f:
                compose_data = yaml.safe_load(f)
            
            services = compose_data.get("services", {})
            service_list = []
            
            for service_name, service_config in services.items():
                service_info = {
                    "name": service_name,
                    "image": service_config.get("image"),
                    "ports": service_config.get("ports", []),
                    "networks": service_config.get("networks", []),
                    "volumes": service_config.get("volumes", []),
                    "depends_on": service_config.get("depends_on", [])
                }
                service_list.append(service_info)
            
            return {
                "status": "success",
                "compose_file": compose_file,
                "services": service_list,
                "count": len(service_list)
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error getting compose services: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }