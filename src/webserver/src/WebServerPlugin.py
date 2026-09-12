"""
WebServer Plugin Implementation
==============================

Main implementation of the WebServer plugin for Sugar.
Provides HTTP server functionality with routing, middleware, and response handling.
"""

import os
import re
import json
import base64
import mimetypes
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Union
from urllib.parse import parse_qs, urlparse, unquote
from http.server import HTTPServer, BaseHTTPRequestHandler
from http import HTTPStatus
import threading
import time

from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output

class Request:
    """Request object representing an HTTP request."""
    
    def __init__(self, method: str, path: str, headers: Dict[str, str], body: bytes = b""):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body
        self._parsed_url = urlparse(path)
        self._query_params = None
        self._post_data = None
        self._url_params = {}
        
    @property
    def get(self) -> Dict[str, str]:
        """Get query parameters."""
        if self._query_params is None:
            self._query_params = parse_qs(self._parsed_url.query)
            # Convert lists to single values for convenience
            return {k: v[0] if len(v) == 1 else v for k, v in self._query_params.items()}
        return self._query_params
    
    @property
    def post(self) -> Dict[str, str]:
        """Get POST data."""
        if self._post_data is None:
            if self.body:
                try:
                    content_type = self.headers.get('Content-Type', '')
                    if 'application/json' in content_type:
                        self._post_data = json.loads(self.body.decode('utf-8'))
                    elif 'application/x-www-form-urlencoded' in content_type:
                        self._post_data = parse_qs(self.body.decode('utf-8'))
                        self._post_data = {k: v[0] if len(v) == 1 else v for k, v in self._post_data.items()}
                    else:
                        self._post_data = {}
                except:
                    self._post_data = {}
            else:
                self._post_data = {}
        return self._post_data
    
    @property
    def url(self) -> Dict[str, str]:
        """Get URL parameters from route patterns."""
        return self._url_params
    
    def set_url_params(self, params: Dict[str, str]):
        """Set URL parameters extracted from route patterns."""
        self._url_params = params

class Response:
    """Response object for handling HTTP responses."""
    
    def __init__(self):
        self.status_code = 200
        self.headers = {}
        self.cookies = []
        self.data = None
        self.content_type = "text/plain"
        self.redirect_url = None
        self.redirect_status = 302
    
    def set_cookie(self, name: str, value: str, **kwargs):
        """Set a cookie."""
        cookie = {
            'name': name,
            'value': value,
            'domain': kwargs.get('domain'),
            'path': kwargs.get('path', '/'),
            'expires': kwargs.get('expires'),
            'httpOnly': kwargs.get('httpOnly', False),
            'secure': kwargs.get('secure', False),
            'sameSite': kwargs.get('sameSite')
        }
        self.cookies.append(cookie)
    
    def set_header(self, name: str, value: str):
        """Set a response header."""
        self.headers[name] = value

class WebServerHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the web server."""
    
    def __init__(self, *args, webserver_plugin=None, **kwargs):
        self.webserver_plugin = webserver_plugin
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        self._handle_request('GET')
    
    def do_POST(self):
        self._handle_request('POST')
    
    def do_PUT(self):
        self._handle_request('PUT')
    
    def do_PATCH(self):
        self._handle_request('PATCH')
    
    def do_DELETE(self):
        self._handle_request('DELETE')
    
    def do_HEAD(self):
        self._handle_request('HEAD')
    
    def do_OPTIONS(self):
        self._handle_request('OPTIONS')
    
    def do_CONNECT(self):
        self._handle_request('CONNECT')
    
    def do_TRACE(self):
        self._handle_request('TRACE')
    
    def _handle_request(self, method: str):
        """Handle HTTP request."""
        if self.webserver_plugin:
            self.webserver_plugin._handle_request(self, method)
        else:
            self.send_error(500, "WebServer plugin not available")

class WebServerPlugin(PluginBase):
    """
    WebServer plugin for Sugar.
    
    Provides HTTP server functionality with routing, middleware support,
    and various response types. Inspired by Express.js.
    """
    
    VERSION = "1.1.0"
    DESCRIPTION = "Web server plugin for Sugar with Express.js-like functionality"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = ["flask", "werkzeug"]
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the WebServer plugin.
        
        Args:
            context: Sugar service context
            plugin_config: Plugin configuration
        """
        super().__init__(context, plugin_config)
        
        # Initialize components
        self.server = None
        self.server_thread = None
        self.routes = []
        self.middleware = []
        self.static_dirs = []
        self.auth_config = {}
        self.meta_config = {}  # Store meta configuration
        
        Output.Console(self.plugin_name, "WebServer plugin initialized")
    
    def meta_hook(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Meta hook for WebServer plugin configuration.
        Called by the meta plugin to configure the webserver before execution.
        
        Args:
            config: Configuration from meta section
            
        Returns:
            Configuration result
        """
        try:
            Output.Console(self.plugin_name, f"Processing meta hook configuration: {config}")
            
            # Store meta configuration
            self.meta_config = config
            
            # Process options
            options = config.get("options", {})
            
            # Store static directory configuration
            if "static" in options:
                self.static_dirs.append(options["static"])
                Output.Console(self.plugin_name, f"Static directory configured: {options['static']}")
            
            # Store authentication configuration
            if "insecure_passw" in options:
                self.auth_config = options["insecure_passw"]
                Output.Console(self.plugin_name, f"Authentication configured for user: {self.auth_config.get('user', 'unknown')}")
            
            # Store port configuration
            if "port" in options:
                self.default_port = options["port"]
                Output.Console(self.plugin_name, f"Default port configured: {self.default_port}")
            
            return {
                "success": True,
                "static_dirs": self.static_dirs,
                "auth_configured": bool(self.auth_config),
                "default_port": getattr(self, 'default_port', 8080)
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error in meta hook: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_available_commands(self) -> List[str]:
        """Get available commands."""
        return ["start", "stop", "send", "set_cookies", "redirect"]
    
    def execute(self, operator: str, config: Dict[str, Any]) -> Any:
        """Execute a plugin operator."""
        if operator == "start":
            return self._start_server(config)
        elif operator == "stop":
            return self._stop_server()
        elif operator == "send":
            return self._send_response(config)
        elif operator == "set_cookies":
            return self._set_cookies(config)
        elif operator == "redirect":
            return self._redirect(config)
        else:
            raise ValueError(f"Unknown operator: {operator}")
    
    def _start_server(self, config: Dict[str, Any]) -> bool:
        """Start the web server."""
        try:
            # Extract configuration
            port = config.get("port", 80)
            static_path = config.get("static")
            auth_config = config.get("insecure_passw")
            routes_config = config.get("routes", [])
            
            # Set up static file serving
            if static_path:
                self.static_path = Path(static_path)
                if not self.static_path.exists():
                    Output.Console(self.plugin_name, f"Static path does not exist: {static_path}")
                    return False
            
            # Set up authentication
            if auth_config:
                self.auth_config = auth_config
            
            # Set up routes
            self.routes = []
            for route_config in routes_config:
                route = self._parse_route_config(route_config)
                if route:
                    self.routes.append(route)
            
            # Create and start server
            server_address = ('', port)
            
            # Create custom handler class with plugin reference
            class Handler(WebServerHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, webserver_plugin=self, **kwargs)
            
            self.server = HTTPServer(server_address, Handler)
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            
            self.is_running = True
            Output.Console(self.plugin_name, f"Web server started on port {port}")
            return True
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error starting server: {e}")
            return False
    
    def _stop_server(self) -> bool:
        """Stop the web server."""
        try:
            if self.server:
                self.server.shutdown()
                self.server.server_close()
                self.is_running = False
                Output.Console(self.plugin_name, "Web server stopped")
                return True
            return False
        except Exception as e:
            Output.Console(self.plugin_name, f"Error stopping server: {e}")
            return False
    
    def _run_server(self):
        """Run the server in a separate thread."""
        try:
            self.server.serve_forever()
        except Exception as e:
            Output.Console(self.plugin_name, f"Server error: {e}")
    
    def _parse_route_config(self, route_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse route configuration."""
        try:
            route_path = route_config.get("route", "")
            method = route_config.get("method", "AUTO").upper()
            func_config = route_config.get("func", {})
            
            # Convert route pattern to regex
            pattern = self._route_to_regex(route_path)
            
            return {
                "pattern": pattern,
                "original_path": route_path,
                "method": method,
                "func_config": func_config
            }
        except Exception as e:
            Output.Console(self.plugin_name, f"Error parsing route config: {e}")
            return None
    
    def _route_to_regex(self, route_path: str) -> str:
        """Convert route path to regex pattern."""
        # Handle URL-friendly patterns like {user} or {user:(.*)}
        pattern = re.sub(r'\{([^:}]+)(?::([^}]+))?\}', r'(?P<\1>[^/]+)', route_path)
        pattern = f"^{pattern}$"
        return pattern
    
    def _handle_request(self, handler: WebServerHandler, method: str):
        """Handle incoming HTTP request."""
        try:
            # Parse request
            path = handler.path
            headers = dict(handler.headers)
            
            # Read request body
            content_length = int(headers.get('Content-Length', 0))
            body = handler.rfile.read(content_length) if content_length > 0 else b""
            
            # Create request object
            request = Request(method, path, headers, body)
            
            # Check authentication
            if self.auth_config and not self._check_auth(handler):
                handler.send_response(401)
                handler.send_header('WWW-Authenticate', 'Basic realm="Login Required"')
                handler.end_headers()
                return
            
            # Check static file serving
            if self.static_path and self._serve_static_file(handler, path):
                return
            
            # Find matching route
            route = self._find_matching_route(request)
            if route:
                self._execute_route(route, request, handler)
            else:
                handler.send_error(404, "Route not found")
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error handling request: {e}")
            handler.send_error(500, "Internal server error")
    
    def _check_auth(self, handler: WebServerHandler) -> bool:
        """Check basic authentication."""
        auth_header = handler.headers.get('Authorization', '')
        if not auth_header.startswith('Basic '):
            return False
        
        try:
            credentials = base64.b64decode(auth_header[6:]).decode('utf-8')
            username, password = credentials.split(':', 1)
            
            expected_user = self.auth_config.get('user')
            expected_pass = self.auth_config.get('pass')
            
            return username == expected_user and password == expected_pass
        except:
            return False
    
    def _serve_static_file(self, handler: WebServerHandler, path: str) -> bool:
        """Serve static files."""
        try:
            if path == '/':
                path = '/index.html'
            
            file_path = self.static_path / path.lstrip('/')
            if file_path.exists() and file_path.is_file():
                # Determine content type
                content_type, _ = mimetypes.guess_type(str(file_path))
                if not content_type:
                    content_type = 'application/octet-stream'
                
                handler.send_response(200)
                handler.send_header('Content-Type', content_type)
                handler.end_headers()
                
                with open(file_path, 'rb') as f:
                    handler.wfile.write(f.read())
                return True
        except Exception as e:
            Output.Console(self.plugin_name, f"Error serving static file: {e}")
        
        return False
    
    def _find_matching_route(self, request: Request) -> Optional[Dict[str, Any]]:
        """Find matching route for request."""
        for route in self.routes:
            # Check method
            if route["method"] != "AUTO" and route["method"] != request.method:
                continue
            
            # Check path pattern
            match = re.match(route["pattern"], request.path)
            if match:
                # Extract URL parameters
                request.set_url_params(match.groupdict())
                return route
        
        return None
    
    def _execute_route(self, route: Dict[str, Any], request: Request, handler: WebServerHandler):
        """Execute route function."""
        try:
            # Create response object
            response = Response()
            
            # Store request and response in context for function execution
            if self.context and hasattr(self.context, 'memory_handler'):
                current_vars = self.context.memory_handler.get_key(0) or {}
                current_vars['req'] = request
                current_vars['res'] = response
                self.context.memory_handler.assign_key(0, current_vars)
            
            # Execute function
            func_config = route["func_config"]
            if "function" in func_config:
                self._execute_function(func_config["function"], request, response)
            
            # Send response
            self._send_http_response(handler, response)
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing route: {e}")
            handler.send_error(500, "Internal server error")
    
    def _execute_function(self, func_config: Dict[str, Any], request: Request, response: Response):
        """Execute function configuration."""
        try:
            # Get function arguments
            args = func_config.get("args", [])
            task = func_config.get("task", [])
            
            # Execute tasks
            for task_item in task:
                self._execute_task(task_item, request, response)
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing function: {e}")
            raise
    
    def _execute_task(self, task_item: Dict[str, Any], request: Request, response: Response):
        """Execute a single task."""
        try:
            for task_type, task_config in task_item.items():
                if task_type == "webserver":
                    self._execute_webserver_task(task_config, request, response)
                elif task_type in ["print", "let", "function"]:
                    # Handle basic Sugar tasks
                    if self.context and hasattr(self.context, 'task_handler'):
                        self.contextexecute_task(task_type, task_config)
                else:
                    # Handle other Sugar tasks
                    if self.context and hasattr(self.context, 'task_handler'):
                        self.contextexecute_task(task_type, task_config)
                        
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing task: {e}")
            raise
    
    def _execute_webserver_task(self, task_config: Dict[str, Any], request: Request, response: Response):
        """Execute webserver-specific task."""
        operator = task_config.get("operator")
        
        if operator == "send":
            self._handle_send_operator(task_config, response)
        elif operator == "set_cookies":
            self._handle_set_cookies_operator(task_config, response)
        elif operator == "redirect":
            self._handle_redirect_operator(task_config, response)
    
    def _handle_send_operator(self, task_config: Dict[str, Any], response: Response):
        """Handle send operator."""
        write_config = task_config.get("write", {})
        
        # Set status code
        if "status" in write_config:
            response.status_code = write_config["status"]
        
        # Set content type
        if "type" in write_config:
            response.content_type = write_config["type"]
        
        # Set custom MIME type
        if "mime" in write_config:
            response.content_type = write_config["mime"]
        
        # Set data
        if "data" in write_config:
            response.data = write_config["data"]
    
    def _handle_set_cookies_operator(self, task_config: Dict[str, Any], response: Response):
        """Handle set_cookies operator."""
        cookies = task_config.get("value", [])
        for cookie_config in cookies:
            response.set_cookie(
                name=cookie_config["name"],
                value=cookie_config["value"],
                domain=cookie_config.get("domain"),
                path=cookie_config.get("path"),
                expires=cookie_config.get("expire"),
                httpOnly=cookie_config.get("httpOnly", False),
                secure=cookie_config.get("secure", False),
                sameSite=cookie_config.get("sameSite")
            )
    
    def _handle_redirect_operator(self, task_config: Dict[str, Any], response: Response):
        """Handle redirect operator."""
        response.redirect_url = task_config.get("url")
        response.redirect_status = task_config.get("status", 302)
    
    def _send_http_response(self, handler: WebServerHandler, response: Response):
        """Send HTTP response."""
        try:
            # Handle redirect
            if response.redirect_url:
                handler.send_response(response.redirect_status)
                handler.send_header('Location', response.redirect_url)
                handler.end_headers()
                return
            
            # Set status code
            handler.send_response(response.status_code)
            
            # Set headers
            for name, value in response.headers.items():
                handler.send_header(name, value)
            
            # Set cookies
            for cookie in response.cookies:
                cookie_str = f"{cookie['name']}={cookie['value']}"
                if cookie.get('domain'):
                    cookie_str += f"; Domain={cookie['domain']}"
                if cookie.get('path'):
                    cookie_str += f"; Path={cookie['path']}"
                if cookie.get('expires'):
                    cookie_str += f"; Expires={cookie['expires']}"
                if cookie.get('httpOnly'):
                    cookie_str += "; HttpOnly"
                if cookie.get('secure'):
                    cookie_str += "; Secure"
                if cookie.get('sameSite'):
                    cookie_str += f"; SameSite={cookie['sameSite']}"
                
                handler.send_header('Set-Cookie', cookie_str)
            
            # Set content type
            content_type = self._get_content_type(response.content_type)
            handler.send_header('Content-Type', content_type)
            
            handler.end_headers()
            
            # Send data
            if response.data is not None:
                data = self._prepare_data(response.data, response.content_type)
                handler.wfile.write(data)
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error sending response: {e}")
            handler.send_error(500, "Internal server error")
    
    def _get_content_type(self, content_type: str) -> str:
        """Get MIME content type."""
        content_types = {
            "html": "text/html",
            "text": "text/plain",
            "json": "application/json",
            "javascript": "application/javascript",
            "css": "text/css",
            "xml": "application/xml",
            "image": "image/jpeg",  # Default image type
            "video": "video/mp4",   # Default video type
            "audio": "audio/mpeg",  # Default audio type
            "pdf": "application/pdf",
            "octet-stream": "application/octet-stream"
        }
        return content_types.get(content_type, "text/plain")
    
    def _prepare_data(self, data: Any, content_type: str) -> bytes:
        """Prepare data for sending."""
        if content_type == "json":
            return json.dumps(data).encode('utf-8')
        elif content_type in ["image", "video", "audio", "pdf", "octet-stream"]:
            # Handle file paths
            if isinstance(data, str) and os.path.exists(data):
                with open(data, 'rb') as f:
                    return f.read()
            else:
                return str(data).encode('utf-8')
        else:
            return str(data).encode('utf-8')
    
    def _send_response(self, config: Dict[str, Any]) -> bool:
        """Send response (for internal use)."""
        # This method is used when called from Sugar functions
        return True
    
    def _set_cookies(self, config: Dict[str, Any]) -> bool:
        """Set cookies (for internal use)."""
        # This method is used when called from Sugar functions
        return True
    
    def _redirect(self, config: Dict[str, Any]) -> bool:
        """Redirect (for internal use)."""
        # This method is used when called from Sugar functions
        return True
    
    def cleanup(self):
        """Cleanup plugin resources."""
        self._stop_server()
        super().cleanup() 