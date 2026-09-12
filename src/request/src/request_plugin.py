"""
Request Plugin for Sugar
=======================

A comprehensive HTTP request plugin that provides HTTP client operations
including requests, sessions, and response handling.
"""

import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from typing import Any, Dict, List, Optional, Union
from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output

class RequestPlugin(PluginBase):
    """
    Request plugin for Sugar.
    
    Provides comprehensive HTTP operations including:
    - HTTP requests (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
    - Session management
    - Response handling
    - Cookie management
    - Retry strategies
    - SSL verification
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Comprehensive HTTP request operations for Sugar"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = ["requests", "urllib3"]
    REQUIREMENTS = ["requests>=2.25.0", "urllib3>=1.26.0"]
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """Initialize the Request plugin."""
        super().__init__(context, plugin_config)
        self.sessions = {}  # Dictionary to store persistent sessions
        self.meta_config = {}  # Store meta configuration
        self.preconfigured_sessions = {}  # Store preconfigured sessions
        
        Output.Console(self.plugin_name, "Request plugin initialized")
    
    def meta_hook(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Meta hook for Request plugin configuration.
        Called by the meta plugin to configure HTTP sessions and options before execution.
        
        Args:
            config: Configuration from meta section
            
        Returns:
            Configuration result
        """
        try:
            Output.Console(self.plugin_name, f"Processing meta hook configuration: {config}")
            
            # Store meta configuration
            self.meta_config = config
            
            # Process sessions
            sessions = config.get("sessions", {})
            
            # Process preconfigured sessions
            for session_name, session_config in sessions.items():
                if isinstance(session_config, dict):
                    self.preconfigured_sessions[session_name] = session_config
                    Output.Console(self.plugin_name, f"Preconfigured Request session: {session_name}")
                    
                    # Auto-create if specified
                    if session_config.get("auto_create", False):
                        try:
                            self._auto_create_session(session_name, session_config)
                        except Exception as e:
                            Output.Console(self.plugin_name, f"Auto-create failed for {session_name}: {str(e)}")
            
            # Process global options
            global_options = config.get("options", {})
            if global_options:
                self.global_options = global_options
                Output.Console(self.plugin_name, f"Global Request options configured: {global_options}")
            
            return {
                "success": True,
                "sessions_configured": len(self.preconfigured_sessions),
                "auto_created": len([s for s in self.preconfigured_sessions.values() if s.get("auto_create", False)]),
                "global_options": bool(global_options)
            }
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error in meta hook: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _auto_create_session(self, session_name: str, session_config: Dict[str, Any]) -> bool:
        """Auto-create a preconfigured Request session."""
        try:
            # Create session config
            request_config = {
                "name": session_name,
                "base_url": session_config.get("base_url"),
                "headers": session_config.get("headers", {}),
                "cookies": session_config.get("cookies", []),
                "timeout": session_config.get("timeout", 30),
                "verify_ssl": session_config.get("verify_ssl", True),
                "retry_strategy": session_config.get("retry_strategy", {})
            }
            
            # Create session
            result = self._create_session(request_config)
            if result.get("success", False):
                Output.Console(self.plugin_name, f"Auto-created Request session: {session_name}")
                return True
            else:
                Output.Console(self.plugin_name, f"Auto-create failed for Request session {session_name}: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error in auto-create for {session_name}: {str(e)}")
            return False
    
    def get_available_commands(self) -> List[str]:
        """
        Get list of available Request commands.
        
        Returns:
            List of available command names
        """
        return [
            "request",
            "get",
            "post",
            "put",
            "delete",
            "patch",
            "head",
            "options",
            "session",
            "create_session",
            "load_session",
            "save_session"
        ]
    
    def execute(self, operator: str, config: Dict[str, Any]) -> Any:
        """
        Execute Request operator.
        
        Args:
            operator: Command to execute
            config: Configuration for the operator
            
        Returns:
            Result of the operator execution
        """
        if operator == "request":
            return self._handle_request(config)
        elif operator in ["get", "post", "put", "delete", "patch", "head", "options"]:
            return self._handle_method_request(operator.upper(), config)
        elif operator == "session":
            return self._handle_session(config)
        elif operator == "create_session":
            return self._create_session(config)
        elif operator == "load_session":
            return self._load_session(config)
        elif operator == "save_session":
            return self._save_session(config)
        else:
            raise ValueError(f"Unknown Request operator: {operator}")
    
    def _handle_request(self, config: dict) -> Dict[str, Any]:
        """Handle HTTP request with method specified in config"""
        # Determine method and URL
        method, url = None, None
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        
        for m in methods:
            if m in config:
                method = m
                url = config[m]
                break
        
        if not method or not url:
            return {
                "success": False,
                "error": "HTTP method/URL not specified",
                "message": "Must specify one of: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS"
            }
        
        return self._handle_method_request(method, config)
    
    def _handle_method_request(self, method: str, config: dict) -> Dict[str, Any]:
        """Handle HTTP request with specific method"""
        try:
            # Get URL from config
            url = None
            methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
            for m in methods:
                if m in config:
                    url = config[m]
                    break
            
            if not url:
                return {
                    "success": False,
                    "error": "URL not specified",
                    "message": f"No URL found for {method} request"
                }
            
            # Interpolate variables in URL
            url = self._interpolate(url)
            
            # Prepare headers
            headers = {}
            if "headers" in config:
                headers = {
                    k: self._interpolate(v) 
                    for k, v in config["headers"].items()
                }
            
            # Prepare cookies
            cookies = {}
            if "cookies" in config:
                for cookie in config["cookies"]:
                    name = self._interpolate(cookie["name"])
                    value = self._interpolate(cookie["value"])
                    cookies[name] = value
            
            # Prepare body
            body = None
            if "body" in config:
                body = config["body"]
                # Convert to JSON if dict/list and header indicates
                if isinstance(body, (dict, list)) and "application/json" in headers.get("Content-Type", ""):
                    body = json.dumps(body)
            
            # Prepare request parameters
            kwargs = {
                "url": url,
                "headers": headers,
                "cookies": cookies,
                "timeout": config.get("timeout", 30),
                "verify": config.get("verify_ssl", True)
            }
            
            # Add body if present
            if body:
                if "json" in headers.get("Content-Type", ""):
                    kwargs["json"] = config["body"] if isinstance(config["body"], (dict, list)) else body
                else:
                    kwargs["data"] = body
            
            # Make the request
            response = requests.request(method, **kwargs)
            
            # Prepare response data
            response_data = {
                "status": response.status_code,
                "headers": dict(response.headers),
                "cookies": response.cookies.get_dict(),
                "body": response.json() if "application/json" in response.headers.get("Content-Type", "") else response.text,
                "url": response.url,
                "method": method
            }
            
            # Store response if specified
            if "store" in config:
                self._store_response(response_data, config["store"], config.get("response_map", {}))
            
            self._log(f"Request {method} request to {url} - Status: {response.status_code}")
            
            return {
                "success": True,
                "response": response_data,
                "message": f"Request {method} request successful"
            }
            
        except Exception as e:
            error_msg = f"Request {method} request failed: {str(e)}"
            self._log(error_msg)
            return {
                "success": False,
                "error": str(e),
                "message": error_msg
            }
    
    def _handle_session(self, config: dict) -> Dict[str, Any]:
        """Handle Request session operations"""
        session_name = config.get("name", "default")
        persist = config.get("persist", False)
        session_config = config.get("config", {})
        tasks = config.get("task", [])
        
        try:
            # Load existing session or create new one
            if config.get("load"):
                session = self.sessions.get(self._get_nested_variable(config["load"]))
                if not session:
                    return {
                        "success": False,
                        "error": "Session not found",
                        "message": f"Session '{config['load']}' not found"
                    }
            else:
                session = self._create_session_internal(session_config)
            
            # Execute tasks in session
            results = []
            for task in tasks:
                if "request" in task:
                    result = self._handle_session_request(session, task["request"], session_config.get("base_url", ""))
                    results.append(result)
            
            # Save session if persistent
            if persist or config.get("save"):
                session_key = config.get("save", session_name)
                self.sessions[session_key] = session
                self._set_nested_variable(session_key, {
                    "cookies": session.cookies.get_dict(),
                    "headers": dict(session.headers)
                })
            
            return {
                "success": True,
                "results": results,
                "message": f"Session '{session_name}' operations completed"
            }
            
        except Exception as e:
            error_msg = f"Session operation failed: {str(e)}"
            self._log(error_msg)
            return {
                "success": False,
                "error": str(e),
                "message": error_msg
            }
    
    def _create_session(self, config: dict) -> Dict[str, Any]:
        """Create a new Request session"""
        try:
            session = self._create_session_internal(config)
            session_name = config.get("name", "default")
            
            # Store session
            self.sessions[session_name] = session
            
            return {
                "success": True,
                "session_name": session_name,
                "message": f"Session '{session_name}' created successfully"
            }
            
        except Exception as e:
            error_msg = f"Session creation failed: {str(e)}"
            self._log(error_msg)
            return {
                "success": False,
                "error": str(e),
                "message": error_msg
            }
    
    def _create_session_internal(self, config: dict) -> requests.Session:
        """Create a requests.Session with configuration"""
        session = requests.Session()
        
        # Base configuration
        if "base_url" in config:
            session.base_url = config["base_url"]
        
        # Default headers
        if "default_headers" in config:
            session.headers.update(config["default_headers"])
        
        # Advanced configuration
        retry_strategy = Retry(
            total=config.get("max_retries", 3),
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session
    
    def _handle_session_request(self, session: requests.Session, request_config: dict, base_url: str) -> Dict[str, Any]:
        """Handle Request request within a session"""
        try:
            method, endpoint = next(iter(request_config.items()))
            
            # Build complete URL
            url = f"{base_url}{endpoint}" if base_url else endpoint
            
            # Prepare request parameters
            kwargs = {
                "url": url,
                "headers": request_config.get("headers", {}),
                "cookies": self._parse_cookies(request_config.get("cookies", [])),
                "timeout": request_config.get("timeout", 30),
                "verify": request_config.get("verify_ssl", True)
            }
            
            # Handle request body
            if "body" in request_config:
                content_type = kwargs["headers"].get("Content-Type", "application/json")
                if "json" in content_type:
                    kwargs["json"] = request_config["body"]
                else:
                    kwargs["data"] = request_config["body"]
            
            # Make the request
            response = session.request(method, **kwargs)
            
            # Store response if specified
            if "store" in request_config:
                self._store_response(response, request_config["store"], request_config.get("response_map", {}))
            
            return {
                "success": True,
                "method": method,
                "url": url,
                "status": response.status_code,
                "message": f"Session request {method} {url} successful"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Session request failed: {str(e)}"
            }
    
    def _load_session(self, config: dict) -> Dict[str, Any]:
        """Load a saved session"""
        session_name = config.get("name", "default")
        
        if session_name in self.sessions:
            return {
                "success": True,
                "session_name": session_name,
                "message": f"Session '{session_name}' loaded successfully"
            }
        else:
            return {
                "success": False,
                "error": "Session not found",
                "message": f"Session '{session_name}' not found"
            }
    
    def _save_session(self, config: dict) -> Dict[str, Any]:
        """Save session data to memory"""
        session_name = config.get("name", "default")
        session = self.sessions.get(session_name)
        
        if session:
            session_data = {
                "cookies": session.cookies.get_dict(),
                "headers": dict(session.headers)
            }
            
            if "store" in config:
                self._set_nested_variable(config["store"], session_data)
            
            return {
                "success": True,
                "session_name": session_name,
                "message": f"Session '{session_name}' saved successfully"
            }
        else:
            return {
                "success": False,
                "error": "Session not found",
                "message": f"Session '{session_name}' not found"
            }
    
    def _parse_cookies(self, cookies_config: list) -> dict:
        """Parse cookies configuration"""
        return {c["name"]: c["value"] for c in cookies_config}
    
    def _store_response(self, response_data: dict, store_var: str, response_map: dict):
        """Store response data in memory"""
        if response_map:
            for part, var_name in response_map.items():
                self._set_nested_variable(var_name, response_data.get(part))
        else:
            self._set_nested_variable(store_var, response_data)
    
    def _interpolate(self, value: str) -> str:
        """Interpolate variables using memory handler"""
        if self.context and hasattr(self.context, 'memory_handler'):
            return self.context.memory_handler._interpolate_variables(value)
        return value
    
    def _get_nested_variable(self, path: str) -> Any:
        """Get nested variable from memory"""
        if self.context and hasattr(self.context, 'memory_handler'):
            return self.context.memory_handler._get_nested_variable(path)
        return None
    
    def _set_nested_variable(self, path: str, value: Any):
        """Set nested variable in memory"""
        if self.context and hasattr(self.context, 'memory_handler'):
            self.context.memory_handler._set_nested_variable(path, value)
    
    def _log(self, message: str) -> None:
        """Safely log a message using Output.Console or print."""
        try:
            Output.Console(self.plugin_name, message)
        except AttributeError:
            # Handle case where Output or plugin_name is not available (e.g., in tests)
            print(f"[RequestPlugin] {message}")
    
    def get_dependency_info(self) -> Dict[str, Any]:
        """
        Get dependency information.
        
        Returns:
            Dictionary with dependency status
        """
        try:
            import requests
            import urllib3
            return {
                'requests': {
                    'available': True,
                    'version': requests.__version__
                },
                'urllib3': {
                    'available': True,
                    'version': urllib3.__version__
                },
                'message': 'Request plugin dependencies available'
            }
        except ImportError as e:
            return {
                'requests': {
                    'available': False,
                    'error': str(e)
                },
                'urllib3': {
                    'available': False,
                    'error': str(e)
                },
                'message': 'Request plugin dependencies not available'
            } 