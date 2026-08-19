"""
Tests for MCP Server Plugin

This module contains comprehensive tests for the MCP Server plugin
to ensure proper functionality and integration with Sugar Language.
"""

import unittest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import the plugin
from plugins.src.mcp_server.src.MCPServerPlugin import (
    MCPServerPlugin, 
    MCPTool, 
    MCPResource,
    MCPMessageType
)


class TestMCPServerPlugin(unittest.TestCase):
    """Test cases for MCP Server Plugin"""
    
    def setUp(self):
        """Set up test environment"""
        self.plugin = MCPServerPlugin()
        self.test_config = {
            "host": "localhost",
            "port": 3000,
            "protocol": "websocket"
        }
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self.plugin, 'mcp_server') and self.plugin.mcp_server:
            try:
                self.plugin.mcp_server.stop_server()
            except:
                pass
    
    def test_plugin_initialization(self):
        """Test plugin initialization"""
        self.assertIsNotNone(self.plugin)
        self.assertEqual(self.plugin.VERSION, "1.0.0")
        self.assertEqual(self.plugin.DESCRIPTION, "Native MCP Server plugin for Sugar Language")
        self.assertEqual(self.plugin.AUTHOR, "Sugar Team")
        self.assertEqual(self.plugin.LICENSE, "MIT")
    
    def test_get_available_commands(self):
        """Test available commands"""
        commands = self.plugin.get_available_commands()
        expected_commands = [
            "start_server",
            "stop_server", 
            "register_tool",
            "register_resource",
            "list_tools",
            "list_resources",
            "get_server_status",
            "test_connection"
        ]
        
        self.assertEqual(set(commands), set(expected_commands))
    
    def test_register_tool(self):
        """Test tool registration"""
        tool_config = {
            "name": "test_tool",
            "description": "Test tool description",
            "input_schema": {
                "type": "object",
                "properties": {
                    "param": {"type": "string"}
                }
            },
            "handler": lambda x: "test result"
        }
        
        result = self.plugin._register_tool(tool_config)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("test_tool", self.plugin.mcp_tools)
        
        tool = self.plugin.mcp_tools["test_tool"]
        self.assertEqual(tool.name, "test_tool")
        self.assertEqual(tool.description, "Test tool description")
    
    def test_register_resource(self):
        """Test resource registration"""
        resource_config = {
            "uri": "sugar://test/resource.txt",
            "name": "Test Resource",
            "description": "Test resource description",
            "mime_type": "text/plain",
            "handler": lambda x: "test content"
        }
        
        result = self.plugin._register_resource(resource_config)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("sugar://test/resource.txt", self.plugin.mcp_resources)
        
        resource = self.plugin.mcp_resources["sugar://test/resource.txt"]
        self.assertEqual(resource.uri, "sugar://test/resource.txt")
        self.assertEqual(resource.name, "Test Resource")
    
    def test_list_tools(self):
        """Test listing tools"""
        # Register a test tool first
        tool_config = {
            "name": "test_tool",
            "description": "Test tool",
            "input_schema": {},
            "handler": lambda x: "test"
        }
        self.plugin._register_tool(tool_config)
        
        result = self.plugin._list_tools({})
        
        self.assertEqual(result["status"], "success")
        self.assertIn("tools", result)
        self.assertGreater(len(result["tools"]), 0)
        
        # Check if our test tool is in the list
        tool_names = [tool["name"] for tool in result["tools"]]
        self.assertIn("test_tool", tool_names)
    
    def test_list_resources(self):
        """Test listing resources"""
        # Register a test resource first
        resource_config = {
            "uri": "sugar://test/resource.txt",
            "name": "Test Resource",
            "description": "Test resource",
            "mime_type": "text/plain",
            "handler": lambda x: "test"
        }
        self.plugin._register_resource(resource_config)
        
        result = self.plugin._list_resources({})
        
        self.assertEqual(result["status"], "success")
        self.assertIn("resources", result)
        self.assertGreater(len(result["resources"]), 0)
        
        # Check if our test resource is in the list
        resource_uris = [resource["uri"] for resource in result["resources"]]
        self.assertIn("sugar://test/resource.txt", resource_uris)
    
    def test_get_server_status(self):
        """Test getting server status"""
        result = self.plugin._get_server_status({})
        
        self.assertEqual(result["status"], "success")
        self.assertIn("server_running", result)
        self.assertIn("tools_count", result)
        self.assertIn("resources_count", result)
        self.assertIn("clients_count", result)
        self.assertIn("tools", result)
        self.assertIn("resources", result)
        
        # Initial state should be False for server_running
        self.assertFalse(result["server_running"])
    
    def test_test_connection_server_not_running(self):
        """Test connection test when server is not running"""
        result = self.plugin._test_connection({})
        
        self.assertEqual(result["status"], "error")
        self.assertIn("Server is not running", result["message"])
    
    @patch('plugins.src.mcp_server.src.MCPServerPlugin.SocketService')
    def test_start_tcp_server(self, mock_socket_service):
        """Test starting TCP server"""
        # Mock the socket service
        mock_service = Mock()
        mock_socket_service.return_value = mock_service
        
        config = {
            "host": "localhost",
            "port": 3000,
            "protocol": "tcp"
        }
        
        result = self.plugin._start_tcp_server("localhost", 3000, config)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("MCP TCP server started", result["message"])
        self.assertEqual(result["protocol"], "tcp")
        self.assertEqual(result["endpoint"], "tcp://localhost:3000")
        
        # Verify socket service was called
        mock_socket_service.assert_called_once()
        mock_service.start_server.assert_called_once()
    
    def test_stop_server_not_running(self):
        """Test stopping server when not running"""
        result = self.plugin._stop_server({})
        
        self.assertEqual(result["status"], "success")
        self.assertIn("MCP server stopped", result["message"])
    
    def test_handle_initialize(self):
        """Test handling initialize message"""
        message = {
            "id": "1",
            "type": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"listChanged": True}
                },
                "clientInfo": {
                    "name": "Test Client",
                    "version": "1.0.0"
                }
            }
        }
        
        result = self.plugin._handle_initialize(message)
        
        self.assertEqual(result["protocolVersion"], "2024-11-05")
        self.assertIn("capabilities", result)
        self.assertIn("serverInfo", result)
        self.assertEqual(result["serverInfo"]["name"], "Sugar MCP Server")
        self.assertEqual(result["serverInfo"]["version"], "1.0.0")
    
    def test_handle_tools_list(self):
        """Test handling tools/list message"""
        # Register a test tool first
        tool_config = {
            "name": "test_tool",
            "description": "Test tool",
            "input_schema": {"type": "object"},
            "handler": lambda x: "test"
        }
        self.plugin._register_tool(tool_config)
        
        message = {"id": "1", "type": "tools/list"}
        
        result = self.plugin._handle_tools_list(message)
        
        self.assertIn("tools", result)
        self.assertGreater(len(result["tools"]), 0)
        
        # Check if our test tool is in the list
        tool_names = [tool["name"] for tool in result["tools"]]
        self.assertIn("test_tool", tool_names)
    
    def test_handle_tools_call_existing_tool(self):
        """Test handling tools/call for existing tool"""
        # Register a test tool
        def test_handler(arguments):
            return f"Handled: {arguments.get('param', 'default')}"
        
        tool_config = {
            "name": "test_tool",
            "description": "Test tool",
            "input_schema": {"type": "object"},
            "handler": test_handler
        }
        self.plugin._register_tool(tool_config)
        
        message = {
            "id": "1",
            "type": "tools/call",
            "params": {
                "name": "test_tool",
                "arguments": {"param": "test_value"}
            }
        }
        
        result = self.plugin._handle_tools_call(message)
        
        self.assertIn("content", result)
        self.assertEqual(len(result["content"]), 1)
        self.assertEqual(result["content"][0]["type"], "text")
        self.assertEqual(result["content"][0]["text"], "Handled: test_value")
    
    def test_handle_tools_call_nonexistent_tool(self):
        """Test handling tools/call for nonexistent tool"""
        message = {
            "id": "1",
            "type": "tools/call",
            "params": {
                "name": "nonexistent_tool",
                "arguments": {}
            }
        }
        
        with self.assertRaises(ValueError) as context:
            self.plugin._handle_tools_call(message)
        
        self.assertIn("Tool 'nonexistent_tool' not found", str(context.exception))
    
    def test_handle_resources_list(self):
        """Test handling resources/list message"""
        # Register a test resource first
        resource_config = {
            "uri": "sugar://test/resource.txt",
            "name": "Test Resource",
            "description": "Test resource",
            "mime_type": "text/plain",
            "handler": lambda x: "test content"
        }
        self.plugin._register_resource(resource_config)
        
        message = {"id": "1", "type": "resources/list"}
        
        result = self.plugin._handle_resources_list(message)
        
        self.assertIn("resources", result)
        self.assertGreater(len(result["resources"]), 0)
        
        # Check if our test resource is in the list
        resource_uris = [resource["uri"] for resource in result["resources"]]
        self.assertIn("sugar://test/resource.txt", resource_uris)
    
    def test_handle_resources_read_existing_resource(self):
        """Test handling resources/read for existing resource"""
        # Register a test resource
        def test_handler(params):
            return "Test content from handler"
        
        resource_config = {
            "uri": "sugar://test/resource.txt",
            "name": "Test Resource",
            "description": "Test resource",
            "mime_type": "text/plain",
            "handler": test_handler
        }
        self.plugin._register_resource(resource_config)
        
        message = {
            "id": "1",
            "type": "resources/read",
            "params": {
                "uri": "sugar://test/resource.txt"
            }
        }
        
        result = self.plugin._handle_resources_read(message)
        
        self.assertIn("contents", result)
        self.assertEqual(len(result["contents"]), 1)
        self.assertEqual(result["contents"][0]["uri"], "sugar://test/resource.txt")
        self.assertEqual(result["contents"][0]["mimeType"], "text/plain")
        self.assertEqual(result["contents"][0]["text"], "Test content from handler")
    
    def test_handle_resources_read_nonexistent_resource(self):
        """Test handling resources/read for nonexistent resource"""
        message = {
            "id": "1",
            "type": "resources/read",
            "params": {
                "uri": "sugar://nonexistent/resource.txt"
            }
        }
        
        with self.assertRaises(ValueError) as context:
            self.plugin._handle_resources_read(message)
        
        self.assertIn("Resource 'sugar://nonexistent/resource.txt' not found", str(context.exception))
    
    def test_native_tool_handlers(self):
        """Test native tool handlers"""
        # Test read_file handler
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Test content")
            temp_file = f.name
        
        try:
            result = self.plugin._handle_read_file({"file_path": temp_file})
            self.assertEqual(result, "Test content")
        finally:
            os.unlink(temp_file)
        
        # Test write_file handler
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_file = f.name
        
        try:
            result = self.plugin._handle_write_file({
                "file_path": temp_file,
                "content": "Written content"
            })
            self.assertIn("written successfully", result)
            
            # Verify content was written
            with open(temp_file, 'r') as f:
                content = f.read()
            self.assertEqual(content, "Written content")
        finally:
            os.unlink(temp_file)
    
    def test_register_mcp_client(self):
        """Test registering MCP client"""
        mock_socket = Mock()
        client_address = ("127.0.0.1", 12345)
        
        self.plugin._register_mcp_client(mock_socket, client_address)
        
        # Check that a client was registered
        self.assertEqual(len(self.plugin.clients), 1)
        
        # Get the client ID
        client_id = list(self.plugin.clients.keys())[0]
        client_info = self.plugin.clients[client_id]
        
        self.assertEqual(client_info["socket"], mock_socket)
        self.assertEqual(client_info["address"], client_address)
        self.assertIn("connected_at", client_info)
    
    def test_cleanup_mcp_client(self):
        """Test cleaning up MCP client"""
        # Register a client first
        mock_socket = Mock()
        client_address = ("127.0.0.1", 12345)
        self.plugin._register_mcp_client(mock_socket, client_address)
        
        # Verify client was registered
        self.assertEqual(len(self.plugin.clients), 1)
        
        # Clean up the client
        self.plugin._cleanup_mcp_client(client_address)
        
        # Verify client was removed
        self.assertEqual(len(self.plugin.clients), 0)
    
    def test_handle_mcp_message_unknown_type(self):
        """Test handling unknown message type"""
        message = {
            "id": "1",
            "type": "unknown_type",
            "params": {}
        }
        
        # Mock client socket
        mock_socket = Mock()
        
        self.plugin._handle_mcp_message(mock_socket, ("127.0.0.1", 12345), message)
        
        # Verify error response was sent
        mock_socket.send.assert_called_once()
        call_args = mock_socket.send.call_args[0][0]
        response = json.loads(call_args.decode('utf-8').strip())
        
        self.assertEqual(response["id"], "1")
        self.assertEqual(response["type"], "response")
        self.assertIn("error", response)
        self.assertIn("Unknown message type", response["error"]["message"])


class TestMCPTool(unittest.TestCase):
    """Test cases for MCPTool dataclass"""
    
    def test_mcp_tool_creation(self):
        """Test MCPTool creation"""
        def test_handler(args):
            return "test result"
        
        tool = MCPTool(
            name="test_tool",
            description="Test tool description",
            input_schema={"type": "object"},
            handler=test_handler
        )
        
        self.assertEqual(tool.name, "test_tool")
        self.assertEqual(tool.description, "Test tool description")
        self.assertEqual(tool.input_schema, {"type": "object"})
        self.assertEqual(tool.handler, test_handler)


class TestMCPResource(unittest.TestCase):
    """Test cases for MCPResource dataclass"""
    
    def test_mcp_resource_creation(self):
        """Test MCPResource creation"""
        def test_handler(params):
            return "test content"
        
        resource = MCPResource(
            uri="sugar://test/resource.txt",
            name="Test Resource",
            description="Test resource description",
            mime_type="text/plain",
            handler=test_handler
        )
        
        self.assertEqual(resource.uri, "sugar://test/resource.txt")
        self.assertEqual(resource.name, "Test Resource")
        self.assertEqual(resource.description, "Test resource description")
        self.assertEqual(resource.mime_type, "text/plain")
        self.assertEqual(resource.handler, test_handler)


class TestMCPMessageType(unittest.TestCase):
    """Test cases for MCPMessageType enum"""
    
    def test_message_types(self):
        """Test MCP message types"""
        self.assertEqual(MCPMessageType.INITIALIZE.value, "initialize")
        self.assertEqual(MCPMessageType.TOOLS_CALL.value, "tools/call")
        self.assertEqual(MCPMessageType.TOOLS_LIST.value, "tools/list")
        self.assertEqual(MCPMessageType.RESOURCES_READ.value, "resources/read")
        self.assertEqual(MCPMessageType.RESOURCES_LIST.value, "resources/list")
        self.assertEqual(MCPMessageType.PING.value, "ping")
        self.assertEqual(MCPMessageType.PONG.value, "pong")


if __name__ == "__main__":
    unittest.main()
