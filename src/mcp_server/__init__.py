"""
MCP Server Plugin for Sugar Language

This plugin implements a native Model Context Protocol (MCP) server
that allows Sugar to act as an MCP server for AI assistants and tools.
"""

from .src.MCPServerPlugin import MCPServerPlugin

__version__ = "1.0.0"
__author__ = "Sugar Team"
__description__ = "Native MCP Server plugin for Sugar Language"

# Export the main plugin class
__all__ = ["MCPServerPlugin"]
