"""
Docker Plugin for Sugar
======================

A comprehensive Docker plugin that provides Docker Compose-like functionality
in Sugar's declarative language. Allows creating, managing, and orchestrating
Docker containers, services, networks, and volumes.

Features:
- Container management (run, stop, remove, inspect, logs, exec)
- Service composition (create, start, stop, restart, destroy)
- Network management (create, remove, inspect, list)
- Volume management (create, remove, inspect, list, backup, restore)
- Health monitoring and status checking
- Docker Compose file generation and import
- Service orchestration with dependency management
- Resource cleanup and maintenance

Dependencies:
- docker>=6.0.0
- pyyaml>=6.0
- docker (system dependency)

Author: Sugar Team
License: MIT
Version: 1.0.0
"""

from .src.DockerPlugin import DockerPlugin

__all__ = ['DockerPlugin']
__version__ = '1.0.0'
__author__ = 'Sugar Team'
__license__ = 'MIT'