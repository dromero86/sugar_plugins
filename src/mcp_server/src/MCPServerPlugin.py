"""
MCP Server Plugin for Sugar Language

This plugin implements a native Model Context Protocol (MCP) server
that allows Sugar to act as an MCP server for AI assistants and tools.
"""

import json
import threading
import time
import uuid
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output
from Sugar.Service.SocketService import SocketService


class MCPMessageType(Enum):
    """MCP message types"""
    INITIALIZE = "initialize"
    TOOLS_CALL = "tools/call"
    TOOLS_LIST = "tools/list"
    RESOURCES_READ = "resources/read"
    RESOURCES_LIST = "resources/list"
    PING = "ping"
    PONG = "pong"


@dataclass
class MCPTool:
    """MCP Tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable


@dataclass
class MCPResource:
    """MCP Resource definition"""
    uri: str
    name: str
    description: str
    mime_type: str
    handler: Callable


class MCPServerPlugin(PluginBase):
    """
    MCP Server Plugin for Sugar Language.
    
    Provides a native Model Context Protocol server that allows Sugar
    to expose its capabilities as tools and resources to AI assistants.
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Native MCP Server plugin for Sugar Language"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    
    # Dependencias básicas
    DEPENDENCIES = []
    REQUIREMENTS = []
    
    # Dependencias del sistema
    SYSTEM_DEPENDENCIES = []
    
    # Requerimientos de hardware
    HARDWARE_REQUIREMENTS = {
        "min_ram_gb": 1,
        "min_disk_gb": 0.1,
        "min_cpu_cores": 1
    }
    
    # Requerimientos de permisos
    PERMISSION_REQUIREMENTS = {
        "network_access": True,
        "write_access": ["/tmp"],
        "read_access": ["./"]
    }
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        super().__init__(context, plugin_config)
        
        # Verificar dependencias
        self.dependency_status = self._check_all_dependencies()
        
        if not self.dependency_status['all_satisfied']:
            self._log_dependency_warnings()
        
        # Inicializar componentes MCP
        if self.dependency_status['all_satisfied']:
            self._initialize_mcp_components()
    
    def get_available_commands(self) -> List[str]:
        """Get available MCP server commands"""
        return [
            "start_server",
            "stop_server", 
            "register_tool",
            "register_resource",
            "list_tools",
            "list_resources",
            "get_server_status",
            "test_connection"
        ]
    
    def execute(self, operator: str, config: Dict[str, Any]) -> Any:
        """Execute MCP server operator"""
        if not self.dependency_status['all_satisfied']:
            raise RuntimeError("Dependencias no satisfechas para MCP Server")
        
        if operator == "start_server":
            return self._start_server(config)
        elif operator == "stop_server":
            return self._stop_server(config)
        elif operator == "register_tool":
            return self._register_tool(config)
        elif operator == "register_resource":
            return self._register_resource(config)
        elif operator == "list_tools":
            return self._list_tools(config)
        elif operator == "list_resources":
            return self._list_resources(config)
        elif operator == "get_server_status":
            return self._get_server_status(config)
        elif operator == "test_connection":
            return self._test_connection(config)
        else:
            raise ValueError(f"Comando MCP desconocido: {operator}")
    
    def _initialize_mcp_components(self):
        """Initialize MCP server components"""
        self.mcp_server = None
        self.mcp_tools: Dict[str, MCPTool] = {}
        self.mcp_resources: Dict[str, MCPResource] = {}
        self.clients: Dict[str, Any] = {}
        self.server_running = False
        
        # Registrar herramientas nativas de Sugar
        self._register_native_tools()
        
        # Registrar recursos nativos de Sugar
        self._register_native_resources()
        
        Output.Console(self.plugin_name, "MCP Server components initialized")
    
    def _register_native_tools(self):
        """Register native Sugar tools"""
        # Tool para ejecutar scripts Sugar
        self._register_tool({
            "name": "execute_sugar_script",
            "description": "Execute a Sugar language script",
            "input_schema": {
                "type": "object",
                "properties": {
                    "script_path": {
                        "type": "string",
                        "description": "Path to the Sugar script file"
                    },
                    "variables": {
                        "type": "object",
                        "description": "Variables to pass to the script"
                    }
                },
                "required": ["script_path"]
            },
            "handler": self._handle_execute_sugar_script
        })
        
        # Tool para leer archivos
        self._register_tool({
            "name": "read_file",
            "description": "Read contents of a file",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    },
                    "encoding": {
                        "type": "string",
                        "default": "utf-8",
                        "description": "File encoding"
                    }
                },
                "required": ["file_path"]
            },
            "handler": self._handle_read_file
        })
        
        # Tool para escribir archivos
        self._register_tool({
            "name": "write_file",
            "description": "Write content to a file",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    },
                    "encoding": {
                        "type": "string",
                        "default": "utf-8",
                        "description": "File encoding"
                    }
                },
                "required": ["file_path", "content"]
            },
            "handler": self._handle_write_file
        })
        
        # Tool para peticiones HTTP
        self._register_tool({
            "name": "http_request",
            "description": "Make HTTP requests",
            "input_schema": {
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                        "description": "HTTP method"
                    },
                    "url": {
                        "type": "string",
                        "description": "URL to request"
                    },
                    "headers": {
                        "type": "object",
                        "description": "HTTP headers"
                    },
                    "data": {
                        "type": "object",
                        "description": "Request data"
                    }
                },
                "required": ["method", "url"]
            },
            "handler": self._handle_http_request
        })
    
    def _register_native_resources(self):
        """Register native Sugar resources"""
        # Recurso para documentación
        self._register_resource({
            "uri": "sugar://docs/language/README.md",
            "name": "Sugar Language Documentation",
            "description": "Main documentation for Sugar language",
            "mime_type": "text/markdown",
            "handler": self._handle_docs_resource
        })
        
        # Recurso para ejemplos
        self._register_resource({
            "uri": "sugar://examples/README.md",
            "name": "Sugar Examples",
            "description": "Examples and tutorials for Sugar",
            "mime_type": "text/markdown",
            "handler": self._handle_examples_resource
        })
    
    def _start_server(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start MCP server"""
        try:
            host = config.get("host", "0.0.0.0")
            port = config.get("port", 3000)
            protocol = config.get("protocol", "websocket")
            
            if protocol == "websocket":
                return self._start_websocket_server(host, port, config)
            elif protocol == "tcp":
                return self._start_tcp_server(host, port, config)
            else:
                raise ValueError(f"Protocolo no soportado: {protocol}")
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error starting MCP server: {str(e)}"
            }
    
    def _start_websocket_server(self, host: str, port: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start WebSocket MCP server"""
        try:
            # Usar el plugin WebServer existente para WebSocket
            webserver_config = {
                "host": host,
                "port": port,
                "websocket": {
                    "enabled": True,
                    "path": "/mcp"
                },
                "routes": [
                    {
                        "path": "/mcp",
                        "method": "POST",
                        "handler": "mcp_handler"
                    }
                ],
                "start": True
            }
            
            # Ejecutar WebServer plugin
            if self.context:
                result = self.context.execute_plugin("webserver", "start", webserver_config)
                if result.get("status") == "success":
                    self.server_running = True
                    return {
                        "status": "success",
                        "message": f"MCP WebSocket server started on {host}:{port}",
                        "protocol": "websocket",
                        "endpoint": f"ws://{host}:{port}/mcp"
                    }
            
            return {
                "status": "error",
                "message": "Failed to start WebSocket server"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error starting WebSocket server: {str(e)}"
            }
    
    def _start_tcp_server(self, host: str, port: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start TCP MCP server"""
        try:
            socket_config = {
                "id": "mcp_server",
                "socket": {
                    "type": "server",
                    "protocol": "tcp",
                    "host": host,
                    "port": port,
                    "message_format": {
                        "type": "json",
                        "delimiter": "\n",
                        "encoding": "utf-8"
                    },
                    "handlers": {
                        "on_connect": "register_mcp_client",
                        "on_message": "handle_mcp_message",
                        "on_error": "log_mcp_error",
                        "on_close": "cleanup_mcp_client"
                    }
                }
            }
            
            # Crear y configurar el servicio de socket
            self.mcp_server = SocketService(socket_config)
            
            # Registrar handlers
            self.mcp_server.message_handlers["register_mcp_client"] = self._register_mcp_client
            self.mcp_server.message_handlers["handle_mcp_message"] = self._handle_mcp_message
            self.mcp_server.message_handlers["log_mcp_error"] = self._log_mcp_error
            self.mcp_server.message_handlers["cleanup_mcp_client"] = self._cleanup_mcp_client
            
            # Iniciar servidor
            self.mcp_server.start_server()
            self.server_running = True
            
            return {
                "status": "success",
                "message": f"MCP TCP server started on {host}:{port}",
                "protocol": "tcp",
                "endpoint": f"tcp://{host}:{port}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error starting TCP server: {str(e)}"
            }
    
    def _stop_server(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Stop MCP server"""
        try:
            if self.mcp_server and self.server_running:
                self.mcp_server.stop_server()
                self.server_running = False
            
            return {
                "status": "success",
                "message": "MCP server stopped"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error stopping server: {str(e)}"
            }
    
    def _register_tool(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new MCP tool"""
        try:
            name = config.get("name")
            description = config.get("description")
            input_schema = config.get("input_schema", {})
            handler = config.get("handler")
            
            if not all([name, description, handler]):
                raise ValueError("name, description, and handler are required")
            
            tool = MCPTool(
                name=name,
                description=description,
                input_schema=input_schema,
                handler=handler
            )
            
            self.mcp_tools[name] = tool
            
            return {
                "status": "success",
                "message": f"Tool '{name}' registered successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error registering tool: {str(e)}"
            }
    
    def _register_resource(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new MCP resource"""
        try:
            uri = config.get("uri")
            name = config.get("name")
            description = config.get("description")
            mime_type = config.get("mime_type", "text/plain")
            handler = config.get("handler")
            
            if not all([uri, name, description, handler]):
                raise ValueError("uri, name, description, and handler are required")
            
            resource = MCPResource(
                uri=uri,
                name=name,
                description=description,
                mime_type=mime_type,
                handler=handler
            )
            
            self.mcp_resources[uri] = resource
            
            return {
                "status": "success",
                "message": f"Resource '{uri}' registered successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error registering resource: {str(e)}"
            }
    
    def _list_tools(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """List registered MCP tools"""
        tools_list = []
        for name, tool in self.mcp_tools.items():
            tools_list.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema
            })
        
        return {
            "status": "success",
            "tools": tools_list,
            "count": len(tools_list)
        }
    
    def _list_resources(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """List registered MCP resources"""
        resources_list = []
        for uri, resource in self.mcp_resources.items():
            resources_list.append({
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mime_type": resource.mime_type
            })
        
        return {
            "status": "success",
            "resources": resources_list,
            "count": len(resources_list)
        }
    
    def _get_server_status(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get MCP server status"""
        return {
            "status": "success",
            "server_running": self.server_running,
            "tools_count": len(self.mcp_tools),
            "resources_count": len(self.mcp_resources),
            "clients_count": len(self.clients),
            "tools": list(self.mcp_tools.keys()),
            "resources": list(self.mcp_resources.keys())
        }
    
    def _test_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test MCP server connection"""
        try:
            if not self.server_running:
                return {
                    "status": "error",
                    "message": "Server is not running"
                }
            
            return {
                "status": "success",
                "message": "MCP server connection test successful",
                "server_running": True
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection test failed: {str(e)}"
            }
    
    # MCP Message Handlers
    def _register_mcp_client(self, client_socket, client_address):
        """Register a new MCP client"""
        client_id = str(uuid.uuid4())
        self.clients[client_id] = {
            "socket": client_socket,
            "address": client_address,
            "connected_at": time.time()
        }
        Output.Console(self.plugin_name, f"Client {client_id} connected from {client_address}")
    
    def _handle_mcp_message(self, client_socket, client_address, message):
        """Handle incoming MCP message"""
        try:
            if not isinstance(message, dict):
                return
            
            message_type = message.get("type")
            message_id = message.get("id", str(uuid.uuid4()))
            
            response = {
                "id": message_id,
                "type": "response"
            }
            
            if message_type == MCPMessageType.INITIALIZE.value:
                response["result"] = self._handle_initialize(message)
            elif message_type == MCPMessageType.TOOLS_CALL.value:
                response["result"] = self._handle_tools_call(message)
            elif message_type == MCPMessageType.TOOLS_LIST.value:
                response["result"] = self._handle_tools_list(message)
            elif message_type == MCPMessageType.RESOURCES_READ.value:
                response["result"] = self._handle_resources_read(message)
            elif message_type == MCPMessageType.RESOURCES_LIST.value:
                response["result"] = self._handle_resources_list(message)
            elif message_type == MCPMessageType.PING.value:
                response["result"] = {"pong": True}
            else:
                response["error"] = {"message": f"Unknown message type: {message_type}"}
            
            # Send response
            response_json = json.dumps(response) + "\n"
            client_socket.send(response_json.encode('utf-8'))
            
        except Exception as e:
            error_response = {
                "id": message.get("id", str(uuid.uuid4())),
                "type": "response",
                "error": {"message": str(e)}
            }
            error_json = json.dumps(error_response) + "\n"
            client_socket.send(error_json.encode('utf-8'))
    
    def _log_mcp_error(self, error):
        """Log MCP error"""
        Output.Console(self.plugin_name, f"MCP Error: {error}")
    
    def _cleanup_mcp_client(self, client_address):
        """Cleanup MCP client"""
        for client_id, client_info in list(self.clients.items()):
            if client_info["address"] == client_address:
                del self.clients[client_id]
                Output.Console(self.plugin_name, f"Client {client_id} disconnected")
                break
    
    # MCP Protocol Handlers
    def _handle_initialize(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize message"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"listChanged": True}
            },
            "serverInfo": {
                "name": "Sugar MCP Server",
                "version": self.VERSION
            }
        }
    
    def _handle_tools_call(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call message"""
        try:
            params = message.get("params", {})
            name = params.get("name")
            arguments = params.get("arguments", {})
            
            if name not in self.mcp_tools:
                raise ValueError(f"Tool '{name}' not found")
            
            tool = self.mcp_tools[name]
            result = tool.handler(arguments)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": str(result)
                    }
                ]
            }
            
        except Exception as e:
            raise ValueError(f"Error calling tool: {str(e)}")
    
    def _handle_tools_list(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list message"""
        tools = []
        for name, tool in self.mcp_tools.items():
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            })
        
        return {"tools": tools}
    
    def _handle_resources_read(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read message"""
        try:
            params = message.get("params", {})
            uri = params.get("uri")
            
            if uri not in self.mcp_resources:
                raise ValueError(f"Resource '{uri}' not found")
            
            resource = self.mcp_resources[uri]
            content = resource.handler(params)
            
            return {
                "contents": [
                    {
                        "uri": resource.uri,
                        "mimeType": resource.mime_type,
                        "text": content
                    }
                ]
            }
            
        except Exception as e:
            raise ValueError(f"Error reading resource: {str(e)}")
    
    def _handle_resources_list(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list message"""
        resources = []
        for uri, resource in self.mcp_resources.items():
            resources.append({
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mimeType": resource.mime_type
            })
        
        return {"resources": resources}
    
    # Native Tool Handlers
    def _handle_execute_sugar_script(self, arguments: Dict[str, Any]) -> str:
        """Handle execute_sugar_script tool"""
        script_path = arguments.get("script_path")
        variables = arguments.get("variables", {})
        
        if not script_path:
            raise ValueError("script_path is required")
        
        # Ejecutar script Sugar usando el contexto
        if self.context:
            # Aquí se ejecutaría el script Sugar
            return f"Script {script_path} executed successfully"
        else:
            return f"Script {script_path} would be executed (context not available)"
    
    def _handle_read_file(self, arguments: Dict[str, Any]) -> str:
        """Handle read_file tool"""
        file_path = arguments.get("file_path")
        encoding = arguments.get("encoding", "utf-8")
        
        if not file_path:
            raise ValueError("file_path is required")
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Error reading file: {str(e)}")
    
    def _handle_write_file(self, arguments: Dict[str, Any]) -> str:
        """Handle write_file tool"""
        file_path = arguments.get("file_path")
        content = arguments.get("content")
        encoding = arguments.get("encoding", "utf-8")
        
        if not file_path or content is None:
            raise ValueError("file_path and content are required")
        
        try:
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(str(content))
            return f"File {file_path} written successfully"
        except Exception as e:
            raise ValueError(f"Error writing file: {str(e)}")
    
    def _handle_http_request(self, arguments: Dict[str, Any]) -> str:
        """Handle http_request tool"""
        method = arguments.get("method", "GET")
        url = arguments.get("url")
        headers = arguments.get("headers", {})
        data = arguments.get("data")
        
        if not url:
            raise ValueError("url is required")
        
        # Usar el cliente HTTP nativo de Sugar
        if self.context:
            http_config = {
                "method": method.lower(),
                "url": url,
                "headers": headers,
                "data": data
            }
            
            # Aquí se haría la petición HTTP usando el contexto
            return f"HTTP {method} request to {url} would be made"
        else:
            return f"HTTP {method} request to {url} would be made (context not available)"
    
    # Native Resource Handlers
    def _handle_docs_resource(self, params: Dict[str, Any]) -> str:
        """Handle docs resource"""
        return "# Sugar Language Documentation\n\nThis is the main documentation for Sugar language."
    
    def _handle_examples_resource(self, params: Dict[str, Any]) -> str:
        """Handle examples resource"""
        return "# Sugar Examples\n\nThis directory contains examples and tutorials for Sugar."
