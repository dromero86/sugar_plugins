"""
Docker Volume Component
======================

Component for managing Docker volumes.
Provides volume operations like create, remove, inspect, etc.
"""

import json
import subprocess
from typing import Any, Dict, List, Optional

from Sugar.Lang.Utils.Output import Output

class DockerVolume:
    """
    Docker volume management component.
    
    Provides operations for:
    - Creating volumes
    - Removing volumes
    - Inspecting volumes
    - Listing volumes
    - Mounting volumes
    - Unmounting volumes
    """
    
    def __init__(self, plugin):
        """
        Initialize the Docker volume component.
        
        Args:
            plugin: Reference to the main Docker plugin
        """
        self.plugin = plugin
        self.plugin_name = plugin.plugin_name
    
    def create(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a Docker volume.
        
        Args:
            config: Volume configuration
            
        Returns:
            Result dictionary with volume information
        """
        try:
            name = config.get("name")
            driver = config.get("driver", "local")
            labels = config.get("labels", {})
            options = config.get("options", {})
            
            if not name:
                raise ValueError("Volume name is required")
            
            # Build docker volume create command
            cmd = ["docker", "volume", "create"]
            
            # Add driver
            cmd.extend(["--driver", driver])
            
            # Add labels
            for key, value in labels.items():
                cmd.extend(["--label", f"{key}={value}"])
            
            # Add driver options
            for key, value in options.items():
                cmd.extend(["--opt", f"{key}={value}"])
            
            # Add volume name
            cmd.append(name)
            
            # Execute command
            Output.Console(self.plugin_name, f"Creating volume: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                volume_name = result.stdout.strip()
                
                # Get volume info
                volume_info = self.inspect({"name": name})
                
                return {
                    "status": "success",
                    "volume_name": volume_name,
                    "name": name,
                    "driver": driver,
                    "info": volume_info
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr,
                    "command": ' '.join(cmd)
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error creating volume: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def remove(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove a Docker volume.
        
        Args:
            config: Volume configuration
            
        Returns:
            Result dictionary
        """
        try:
            name = config.get("name")
            force = config.get("force", False)
            
            if not name:
                raise ValueError("Volume name is required")
            
            cmd = ["docker", "volume", "rm"]
            
            if force:
                cmd.append("-f")
            
            cmd.append(name)
            
            Output.Console(self.plugin_name, f"Removing volume: {name}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "name": name,
                    "message": f"Volume {name} removed"
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr,
                    "name": name
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error removing volume: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def inspect(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inspect a Docker volume.
        
        Args:
            config: Volume configuration
            
        Returns:
            Volume inspection data
        """
        try:
            name = config.get("name")
            if not name:
                raise ValueError("Volume name is required")
            
            cmd = ["docker", "volume", "inspect", name]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                try:
                    volume_data = json.loads(result.stdout)
                    if volume_data:
                        return {
                            "status": "success",
                            "name": name,
                            "data": volume_data[0]
                        }
                    else:
                        return {
                            "status": "error",
                            "error": "Volume not found",
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
            Output.Console(self.plugin_name, f"Error inspecting volume: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def list_all(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List all Docker volumes.
        
        Args:
            config: Optional configuration
            
        Returns:
            List of volumes
        """
        try:
            cmd = ["docker", "volume", "ls", "--format", "json"]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                volumes = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            volume_data = json.loads(line)
                            volumes.append(volume_data)
                        except json.JSONDecodeError:
                            continue
                
                return {
                    "status": "success",
                    "volumes": volumes,
                    "count": len(volumes)
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error listing volumes: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def prune(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Remove unused Docker volumes.
        
        Args:
            config: Optional configuration
            
        Returns:
            Result dictionary
        """
        try:
            force = config.get("force", True) if config else True
            
            cmd = ["docker", "volume", "prune"]
            
            if force:
                cmd.append("-f")
            
            Output.Console(self.plugin_name, "Pruning unused volumes")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": "Unused volumes pruned",
                    "output": result.stdout
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error pruning volumes: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def backup(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Backup a Docker volume.
        
        Args:
            config: Backup configuration
            
        Returns:
            Result dictionary
        """
        try:
            volume_name = config.get("volume")
            backup_path = config.get("backup_path")
            
            if not volume_name:
                raise ValueError("Volume name is required")
            
            if not backup_path:
                raise ValueError("Backup path is required")
            
            # Create a temporary container to backup the volume
            backup_container_name = f"backup_{volume_name}_{int(time.time())}"
            
            # Run backup container
            backup_cmd = [
                "docker", "run", "--rm", "-v", f"{volume_name}:/data",
                "-v", f"{backup_path}:/backup", "alpine", "tar", "czf",
                f"/backup/{volume_name}.tar.gz", "-C", "/data", "."
            ]
            
            Output.Console(self.plugin_name, f"Creating backup of volume {volume_name}")
            result = subprocess.run(backup_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "volume": volume_name,
                    "backup_path": f"{backup_path}/{volume_name}.tar.gz",
                    "message": f"Volume {volume_name} backed up successfully"
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr,
                    "volume": volume_name
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error backing up volume: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def restore(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Restore a Docker volume from backup.
        
        Args:
            config: Restore configuration
            
        Returns:
            Result dictionary
        """
        try:
            volume_name = config.get("volume")
            backup_path = config.get("backup_path")
            
            if not volume_name:
                raise ValueError("Volume name is required")
            
            if not backup_path:
                raise ValueError("Backup path is required")
            
            # Create volume if it doesn't exist
            volume_exists = self.inspect({"name": volume_name})
            if volume_exists.get("status") != "success":
                self.create({"name": volume_name})
            
            # Create a temporary container to restore the volume
            restore_cmd = [
                "docker", "run", "--rm", "-v", f"{volume_name}:/data",
                "-v", f"{backup_path}:/backup", "alpine", "tar", "xzf",
                f"/backup/{volume_name}.tar.gz", "-C", "/data"
            ]
            
            Output.Console(self.plugin_name, f"Restoring volume {volume_name} from backup")
            result = subprocess.run(restore_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "volume": volume_name,
                    "backup_path": backup_path,
                    "message": f"Volume {volume_name} restored successfully"
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr,
                    "volume": volume_name
                }
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error restoring volume: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }