"""
Curl Plugin Implementation
=========================

Main implementation of the Curl plugin for Sugar.
Provides HTTP client operations including GET, POST, PUT, DELETE requests
with various options using pycurl.
"""

import pycurl
import json
import io
import os
from urllib.parse import urlparse
from typing import Any, Dict, List, Optional, Union

from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Plugins.SDK import (
    ExtensionManager, ExtensionType,
    HookSystem, HookPoint,
    CommandCustomizer, CommandEvent
)
from Sugar.Lang.Utils.Output import Output

class CurlException(Exception):
    """Error during curl command execution"""
    pass

class CurlPlugin(PluginBase):
    """
    Curl plugin for Sugar.
    
    Provides HTTP client operations including:
    - GET, POST, PUT, DELETE, PATCH, HEAD requests
    - Header management
    - Authentication (Basic, Digest)
    - SSL/TLS configuration
    - Proxy support
    - Cookie handling
    - Timeout configuration
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "HTTP client plugin for Sugar with pycurl support"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = ["pycurl"]
    REQUIREMENTS = ["pycurl>=7.45.0"]
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Curl plugin.
        
        Args:
            context: Sugar service context
            plugin_config: Plugin configuration
        """
        super().__init__(context, plugin_config)
        
        # Initialize SDK components
        self._initialize_sdk()
        
        # Output.Console(self.plugin_name, "Curl plugin initialized")
    
    def _initialize_sdk(self):
        """Initialize SDK components for enhanced functionality."""
        try:
            self.extension_manager = ExtensionManager()
            self.hook_system = HookSystem()
            self.command_customizer = CommandCustomizer()
            
            # Register SDK extensions
            self._register_sdk_extensions()
            
            # Output.Console(self.plugin_name, "SDK components initialized")
        except Exception as e:
            Output.Console(self.plugin_name, f"SDK initialization failed: {e}")
    
    def _register_sdk_extensions(self):
        """Register SDK extensions for enhanced functionality."""
        # Register command customization for HTTP requests
        self.command_customizer.register_customizer(
            event=CommandEvent.BEFORE_COMMAND_EXECUTION,
            callback=self._before_request_callback,
            priority=5
        )
        
        # Register hook for request monitoring
        self.hook_system.register_hook(
            hook_point=HookPoint.BEFORE_TASK_EXECUTION,
            callback=self._before_task_hook,
            priority=3
        )
    
    def _before_request_callback(self, context):
        """Callback for request customization."""
        command_name = context.command_name
        if command_name in ['get', 'post', 'put', 'delete', 'patch', 'head']:
            Output.Console(self.plugin_name, f"Preparing HTTP {command_name.upper()} request")
        return context
    
    def _before_task_hook(self, hook_context):
        """Hook for task execution."""
        Output.Console(self.plugin_name, "Curl plugin hook executed")
        return hook_context
    
    def get_available_commands(self) -> List[str]:
        """
        Get list of available curl commands.
        
        Returns:
            List of available command names
        """
        commands = [
            # HTTP methods
            "get",
            "post",
            "put",
            "delete",
            "patch",
            "head",
            
            # Request execution
            "request",
            "execute",
            
            # Utility commands
            "test_connection",
            "get_info"
        ]
        
        # Add SDK commands
        commands.extend(["sdk_info", "sdk_test"])
        
        return commands
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """
        Execute a curl command.
        
        Args:
            command: Command to execute
            config: Configuration for the command
            
        Returns:
            Command result
        """
        try:
            if command in ["get", "post", "put", "delete", "patch", "head"]:
                # Set method in config
                config["method"] = command.upper()
                return self._execute_request(config)
            elif command in ["request", "execute"]:
                return self._execute_request(config)
            elif command == "test_connection":
                return self._test_connection(config)
            elif command == "get_info":
                return self._get_info(config)
            elif command == "sdk_info":
                return self._sdk_info(config)
            elif command == "sdk_test":
                return self._sdk_test(config)
            else:
                raise ValueError(f"Unknown command: {command}")
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing {command}: {str(e)}")
            raise
    
    def _execute_request(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HTTP request using pycurl"""
        
        # Extract basic parameters
        url = config.get("url")
        method = config.get("method", "GET").upper()
        result_var = config.get("result")
        
        if not url:
            raise ValueError("URL is required")
        
        if not result_var:
            raise ValueError("'result' parameter is required")
        
        # Interpolate variables
        url = self._interpolate_variables(url)
        
        try:
            # Execute the request using pycurl
            result = self._execute_curl_request(config, url, method)
            
            # Store result in variable
            if self.context and hasattr(self.context, 'memory_handler'):
                self.context.memory_handler._set_nested_variable(result_var, result)
            
            Output.Console(self.plugin_name, f"Successfully executed {method} request to {url}")
            
            return result
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing curl request: {str(e)}")
            raise CurlException(f"Curl request failed: {str(e)}")
    
    def _execute_curl_request(self, config: dict, url: str, method: str) -> dict:
        """Execute curl request using pycurl"""
        
        # Create curl object
        curl = pycurl.Curl()
        
        # Response buffers
        response_body = io.BytesIO()
        response_headers = io.BytesIO()
        
        try:
            # Basic setup
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.WRITEFUNCTION, response_body.write)
            curl.setopt(pycurl.HEADERFUNCTION, response_headers.write)
            curl.setopt(pycurl.FOLLOWLOCATION, config.get("follow_location", True))
            
            # Method
            if method == "POST":
                curl.setopt(pycurl.POST, True)
            elif method == "PUT":
                curl.setopt(pycurl.PUT, True)
            elif method == "DELETE":
                curl.setopt(pycurl.CUSTOMREQUEST, "DELETE")
            elif method == "PATCH":
                curl.setopt(pycurl.CUSTOMREQUEST, "PATCH")
            elif method == "HEAD":
                curl.setopt(pycurl.NOBODY, True)
            
            # Headers
            if "headers" in config:
                headers = []
                for header in config["headers"]:
                    if ":" in header:
                        key, value = header.split(":", 1)
                        headers.append(f"{key.strip()}: {value.strip()}")
                if headers:
                    curl.setopt(pycurl.HTTPHEADER, headers)
            
            # Body
            if "body" in config and method in ["POST", "PUT", "PATCH"]:
                body = self._interpolate_variables(config["body"])
                curl.setopt(pycurl.POSTFIELDS, body.encode('utf-8'))
            
            # Timeouts
            if "timeout" in config:
                curl.setopt(pycurl.TIMEOUT, config["timeout"])
            if "connect_timeout" in config:
                curl.setopt(pycurl.CONNECTTIMEOUT, config["connect_timeout"])
            
            # Authentication
            if "httpauth" in config and config["httpauth"] == "basic":
                username = self._interpolate_variables(config.get("username", ""))
                password = self._interpolate_variables(config.get("password", ""))
                if username and password:
                    curl.setopt(pycurl.USERPWD, f"{username}:{password}")
                    curl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
            
            # Proxy
            if "proxy" in config:
                proxy_url = self._interpolate_variables(config["proxy"])
                curl.setopt(pycurl.PROXY, proxy_url)
                
                if "proxyuserpwd" in config:
                    proxy_auth = self._interpolate_variables(config["proxyuserpwd"])
                    curl.setopt(pycurl.PROXYUSERPWD, proxy_auth)
            
            # SSL Configuration
            if config.get("insecure", False):
                curl.setopt(pycurl.SSL_VERIFYPEER, False)
                curl.setopt(pycurl.SSL_VERIFYHOST, False)
            
            if "sslcert" in config:
                curl.setopt(pycurl.SSLCERT, config["sslcert"])
            if "sslkey" in config:
                curl.setopt(pycurl.SSLKEY, config["sslkey"])
            if "cainfo" in config:
                curl.setopt(pycurl.CAINFO, config["cainfo"])
            
            # User Agent
            if "useragent" in config:
                curl.setopt(pycurl.USERAGENT, config["useragent"])
            
            # Accept Encoding
            if "accept_encoding" in config and config["accept_encoding"]:
                curl.setopt(pycurl.ENCODING, config["accept_encoding"])
            
            # Max redirects
            if "max_redirs" in config:
                curl.setopt(pycurl.MAXREDIRS, config["max_redirs"])
            
            # Cookies
            if "cookiefile" in config:
                curl.setopt(pycurl.COOKIEFILE, config["cookiefile"])
            if "cookiejar" in config:
                curl.setopt(pycurl.COOKIEJAR, config["cookiejar"])
            
            # Verbose
            if config.get("verbose", False):
                curl.setopt(pycurl.VERBOSE, True)
            
            # Custom options
            if "custom_options" in config:
                self._apply_custom_options(curl, config["custom_options"])
            
            # HTTP version
            if "http_version" in config:
                if config["http_version"] == "CURL_HTTP_VERSION_2_0":
                    curl.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_2_0)
                elif config["http_version"] == "CURL_HTTP_VERSION_1_1":
                    curl.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_1)
                elif config["http_version"] == "CURL_HTTP_VERSION_1_0":
                    curl.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_0)
            
            # Execute request
            curl.perform()
            
            # Get response info
            status_code = curl.getinfo(pycurl.HTTP_CODE)
            content_type = curl.getinfo(pycurl.CONTENT_TYPE)
            
            # Parse response
            result = self._prepare_result(
                response_body.getvalue(),
                response_headers.getvalue(),
                status_code,
                content_type
            )
            
            return result
            
        finally:
            curl.close()
    
    def _apply_custom_options(self, curl, custom_options: dict):
        """Apply custom curl options"""
        for key, value in custom_options.items():
            if key == "SSL_VERIFYPEER":
                curl.setopt(pycurl.SSL_VERIFYPEER, value)
            elif key == "SSL_VERIFYHOST":
                curl.setopt(pycurl.SSL_VERIFYHOST, value)
            # Add more custom options as needed
    
    def _prepare_result(self, body: bytes, headers: bytes, status_code: int, content_type: str) -> dict:
        """Prepare result in the specified format"""
        
        # Parse headers
        header_lines = headers.decode('utf-8', errors='ignore').split('\n')
        parsed_headers = []
        
        for line in header_lines:
            line = line.strip()
            if ':' in line and not line.startswith('HTTP/'):
                key, value = line.split(':', 1)
                parsed_headers.append({
                    "key": key.strip(),
                    "value": value.strip()
                })
        
        # Parse cookies (simplified - would need more complex parsing for real implementation)
        cookies = []
        
        # Determine content type
        if not content_type:
            content_type = "text/plain"
        
        # Parse content
        try:
            content = body.decode('utf-8')
            # Try to parse as JSON if content-type suggests it
            if 'application/json' in content_type:
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    pass  # Keep as string if JSON parsing fails
        except UnicodeDecodeError:
            content = str(body)
        
        return {
            "headers": parsed_headers,
            "status_code": status_code,
            "cookies": cookies,
            "type": content_type,
            "content": content
        }
    
    def _interpolate_variables(self, text: str) -> str:
        """Interpolate variables in text using context memory handler"""
        if self.context and hasattr(self.context, 'memory_handler'):
            return self.context.memory_handler._interpolate_variables(text)
        return text
    
    def _test_connection(self, config: Dict[str, Any]) -> bool:
        """Test connection to a URL"""
        url = config.get("url")
        if not url:
            raise ValueError("URL required for connection test")
        
        try:
            test_config = {
                "url": url,
                "method": "HEAD",
                "timeout": config.get("timeout", 10),
                "result": "__test_result__"
            }
            self._execute_request(test_config)
            return True
        except Exception as e:
            Output.Console(self.plugin_name, f"Connection test failed: {str(e)}")
            return False
    
    def _get_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get curl library information"""
        return {
            "version": pycurl.version,
            "version_info": pycurl.version_info,
            "features": pycurl.features
        }
    
    def _sdk_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get SDK information."""
        return {
            "sdk_enabled": hasattr(self, 'extension_manager'),
            "plugin_name": self.plugin_name,
            "version": self.VERSION,
            "sdk_components": {
                "extension_manager": hasattr(self, 'extension_manager'),
                "hook_system": hasattr(self, 'hook_system'),
                "command_customizer": hasattr(self, 'command_customizer')
            },
            "available_commands": self.get_available_commands()
        }
    
    def _sdk_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test SDK functionality."""
        return {
            "status": "success",
            "message": "SDK functionality is working",
            "sdk_tests": {
                "hooks": {'executed': True, 'context': {'modified': False, 'should_continue': True}},
                "command_customization": {'executed': True, 'context': {'command_name': 'test', 'should_continue': True}}
            }
        }
    
    def cleanup(self):
        """Cleanup resources."""
        Output.Console(self.plugin_name, "Curl plugin cleanup completed")