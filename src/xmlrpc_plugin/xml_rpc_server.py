"""
XML-RPC Server Service for Sugar Language
Provides server functionality for XML-RPC communication
"""

import http.server
import socketserver
import threading
import time
import logging
import json
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs
import xml.etree.ElementTree as ET

from Sugar.Lang.xml_rpc.xml_rpc_parser import (
    XMLRPCParser, XMLRPCSerializer, XMLRPCTypeConverter,
    XMLRPCMethodCall, XMLRPCMethodResponse, XMLRPCValue
)


@dataclass
class XMLRPCServerConfig:
    """Configuration for XML-RPC server"""
    host: str = "0.0.0.0"
    port: int = 8000
    max_connections: int = 100
    timeout: int = 30
    log_level: str = "info"
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None


@dataclass
class XMLRPCMethod:
    """Represents a registered XML-RPC method"""
    name: str
    handler: Callable
    description: str = ""
    signature: Optional[List[str]] = None
    help_text: Optional[str] = None


@dataclass
class XMLRPCServerMetrics:
    """Metrics for XML-RPC server"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    average_response_time: float = 0.0
    active_connections: int = 0
    max_connections: int = 0
    start_time: float = field(default_factory=time.time)


class XMLRPCHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for XML-RPC server"""
    
    def __init__(self, *args, server_instance=None, **kwargs):
        self.server_instance = server_instance
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests (XML-RPC calls)"""
        if self.server_instance is None:
            self.send_error(500, "Server instance not available")
            return
        
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = self.rfile.read(content_length).decode('utf-8')
            
            # Parse XML-RPC request
            parser = XMLRPCParser()
            method_call = parser.parse_method_call(request_body)
            
            # Log request
            self.server_instance.logger.info(
                f"XML-RPC Request: {method_call.method_name} from {self.client_address[0]}"
            )
            
            # Process request
            start_time = time.time()
            response = self.server_instance.process_request(method_call)
            response_time = time.time() - start_time
            
            # Update metrics
            with self.server_instance.lock:
                self.server_instance.metrics.total_requests += 1
                self.server_instance.metrics.total_response_time += response_time
                self.server_instance.metrics.average_response_time = (
                    self.server_instance.metrics.total_response_time / 
                    self.server_instance.metrics.total_requests
                )
                
                if response.fault:
                    self.server_instance.metrics.failed_requests += 1
                else:
                    self.server_instance.metrics.successful_requests += 1
            
            # Serialize response
            serializer = XMLRPCSerializer()
            response_xml = serializer.serialize_method_response(response)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'text/xml; charset=utf-8')
            self.send_header('Content-Length', str(len(response_xml)))
            self.end_headers()
            self.wfile.write(response_xml.encode('utf-8'))
            
            # Log response
            self.server_instance.logger.info(
                f"XML-RPC Response: {method_call.method_name} completed in {response_time:.3f}s"
            )
            
        except Exception as e:
            self.server_instance.logger.error(f"Error processing request: {e}")
            self.send_error(500, f"Internal server error: {e}")
    
    def do_GET(self):
        """Handle GET requests (server info)"""
        if self.path == "/":
            # Return server information
            info = {
                "server": "Sugar XML-RPC Server",
                "version": "3.0.0",
                "methods": list(self.server_instance.methods.keys()),
                "uptime": time.time() - self.server_instance.metrics.start_time
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(info, indent=2).encode('utf-8'))
        else:
            self.send_error(404, "Not found")
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        if self.server_instance and self.server_instance.logger:
            self.server_instance.logger.info(f"{self.address_string()} - {format % args}")


class XMLRPCServer:
    """XML-RPC server implementation"""
    
    def __init__(self, config: XMLRPCServerConfig):
        self.config = config
        self.methods = {}
        self.metrics = XMLRPCServerMetrics()
        self.lock = threading.Lock()
        self.server = None
        self.server_thread = None
        self.running = False
        
        # Setup logging
        self._setup_logging()
        
        # Register system methods
        self._register_system_methods()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        level = getattr(logging, self.config.log_level.upper())
        self.logger = logging.getLogger(f"XMLRPCServer_{id(self)}")
        self.logger.setLevel(level)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _register_system_methods(self):
        """Register system methods"""
        self.register_method("system.listMethods", self._system_list_methods, 
                           "List all available methods")
        self.register_method("system.methodHelp", self._system_method_help,
                           "Get help for a method")
        self.register_method("system.methodSignature", self._system_method_signature,
                           "Get signature for a method")
        self.register_method("system.getCapabilities", self._system_get_capabilities,
                           "Get server capabilities")
    
    def register_method(self, name: str, handler: Callable, description: str = "",
                       signature: Optional[List[str]] = None, help_text: Optional[str] = None):
        """Register a new XML-RPC method"""
        method = XMLRPCMethod(
            name=name,
            handler=handler,
            description=description,
            signature=signature,
            help_text=help_text
        )
        
        with self.lock:
            self.methods[name] = method
        
        self.logger.info(f"Registered method: {name}")
    
    def unregister_method(self, name: str):
        """Unregister an XML-RPC method"""
        with self.lock:
            if name in self.methods:
                del self.methods[name]
                self.logger.info(f"Unregistered method: {name}")
    
    def process_request(self, method_call: XMLRPCMethodCall) -> XMLRPCMethodResponse:
        """Process an XML-RPC method call"""
        try:
            # Check if method exists
            if method_call.method_name not in self.methods:
                return XMLRPCMethodResponse(fault={
                    "faultCode": -32601,
                    "faultString": f"Method '{method_call.method_name}' not found"
                })
            
            method = self.methods[method_call.method_name]
            
            # Convert parameters to Python values
            params = []
            for param in method_call.params:
                python_value = XMLRPCTypeConverter.xmlrpc_to_python(param)
                params.append(python_value)
            
            # Call handler
            result = method.handler(*params)
            
            # Convert result to XML-RPC value
            if result is not None:
                xmlrpc_value = XMLRPCTypeConverter.python_to_xmlrpc(result)
                return XMLRPCMethodResponse(value=xmlrpc_value)
            else:
                return XMLRPCMethodResponse()
                
        except Exception as e:
            self.logger.error(f"Error processing method {method_call.method_name}: {e}")
            return XMLRPCMethodResponse(fault={
                "faultCode": -32603,
                "faultString": f"Internal error: {str(e)}"
            })
    
    def start(self):
        """Start the XML-RPC server"""
        if self.running:
            self.logger.warning("Server is already running")
            return
        
        try:
            # Create server
            handler_class = type('XMLRPCHandler', (XMLRPCHandler,), {
                'server_instance': self
            })
            
            self.server = socketserver.ThreadingTCPServer(
                (self.config.host, self.config.port),
                handler_class,
                bind_and_activate=False
            )
            
            # Set server options
            self.server.allow_reuse_address = True
            self.server.request_queue_size = self.config.max_connections
            
            # Setup SSL if configured
            if self.config.ssl_cert and self.config.ssl_key:
                import ssl
                context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                context.load_cert_chain(self.config.ssl_cert, self.config.ssl_key)
                self.server.socket = context.wrap_socket(self.server.socket, server_side=True)
            
            # Start server in thread
            self.server_thread = threading.Thread(target=self._run_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.running = True
            self.logger.info(f"XML-RPC server started on {self.config.host}:{self.config.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            raise
    
    def _run_server(self):
        """Run the server (internal method)"""
        try:
            self.server.serve_forever()
        except Exception as e:
            self.logger.error(f"Server error: {e}")
        finally:
            self.running = False
    
    def stop(self):
        """Stop the XML-RPC server"""
        if not self.running:
            self.logger.warning("Server is not running")
            return
        
        try:
            if self.server:
                self.server.shutdown()
                self.server.server_close()
            
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=5)
            
            self.running = False
            self.logger.info("XML-RPC server stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping server: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get server metrics"""
        with self.lock:
            uptime = time.time() - self.metrics.start_time
            return {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "success_rate": (
                    self.metrics.successful_requests / max(self.metrics.total_requests, 1)
                ),
                "average_response_time": self.metrics.average_response_time,
                "active_connections": self.metrics.active_connections,
                "max_connections": self.metrics.max_connections,
                "uptime": uptime,
                "requests_per_second": self.metrics.total_requests / max(uptime, 1),
                "registered_methods": len(self.methods)
            }
    
    # System methods
    def _system_list_methods(self) -> List[str]:
        """System method: list all available methods"""
        return list(self.methods.keys())
    
    def _system_method_help(self, method_name: str) -> str:
        """System method: get help for a method"""
        if method_name in self.methods:
            method = self.methods[method_name]
            return method.help_text or method.description
        return f"Method '{method_name}' not found"
    
    def _system_method_signature(self, method_name: str) -> List[List[str]]:
        """System method: get signature for a method"""
        if method_name in self.methods:
            method = self.methods[method_name]
            if method.signature:
                return [method.signature]
        return []
    
    def _system_get_capabilities(self) -> Dict[str, Any]:
        """System method: get server capabilities"""
        return {
            "xmlrpc": {
                "specUrl": "http://www.xmlrpc.com/spec",
                "specVersion": "1.0"
            },
            "faults_interop": {
                "specUrl": "http://xmlrpc-epi.sourceforge.net/specs/rfc.fault_codes.php",
                "specVersion": "20010516"
            },
            "introspect": {
                "specUrl": "http://xmlrpc-c.sourceforge.net/doc/introspection.html",
                "specVersion": "1.0"
            }
        }


# Factory function for creating servers
def create_xmlrpc_server(config_dict: Dict[str, Any]) -> XMLRPCServer:
    """Create XML-RPC server from configuration dictionary"""
    config = XMLRPCServerConfig(**config_dict)
    return XMLRPCServer(config)
