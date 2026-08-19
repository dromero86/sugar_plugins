"""
XML-RPC Client Service for Sugar Language
Provides client functionality for XML-RPC communication
"""

import requests
import time
import logging
import threading
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from urllib.parse import urlparse
import ssl
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed

from Sugar.Lang.xml_rpc.xml_rpc_parser import (
    XMLRPCParser, XMLRPCSerializer, XMLRPCTypeConverter,
    XMLRPCMethodCall, XMLRPCMethodResponse, XMLRPCValue
)


@dataclass
class XMLRPCClientConfig:
    """Configuration for XML-RPC client"""
    endpoint: str
    timeout: int = 30
    verify_ssl: bool = True
    auth: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    persistent: bool = False
    max_retries: int = 3
    retry_delay: int = 1000
    compression: Optional[Dict[str, Any]] = None
    logging: Optional[Dict[str, Any]] = None


@dataclass
class XMLRPCClientMetrics:
    """Metrics for XML-RPC client"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    average_response_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    last_request_time: Optional[float] = None
    start_time: float = field(default_factory=time.time)


class XMLRPCClient:
    """XML-RPC client implementation"""
    
    def __init__(self, config: XMLRPCClientConfig):
        self.config = config
        self.parser = XMLRPCParser()
        self.serializer = XMLRPCSerializer()
        self.session = requests.Session()
        self.metrics = XMLRPCClientMetrics()
        self.cache = {}
        self.lock = threading.Lock()
        
        # Setup logging
        self._setup_logging()
        
        # Setup session
        self._setup_session()
        
        # Setup compression
        if config.compression and config.compression.get("enabled"):
            self._setup_compression()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        if self.config.logging:
            level = getattr(logging, self.config.logging.get("level", "INFO").upper())
            self.logger = logging.getLogger(f"XMLRPCClient_{id(self)}")
            self.logger.setLevel(level)
            
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
        else:
            self.logger = logging.getLogger(f"XMLRPCClient_{id(self)}")
            self.logger.addHandler(logging.NullHandler())
    
    def _setup_session(self):
        """Setup requests session"""
        # Set default headers
        default_headers = {
            "Content-Type": "text/xml",
            "User-Agent": "Sugar-XMLRPC-Client/3.0.0"
        }
        
        if self.config.headers:
            default_headers.update(self.config.headers)
        
        self.session.headers.update(default_headers)
        
        # Setup authentication
        if self.config.auth:
            auth_type = self.config.auth.get("type", "basic")
            
            if auth_type == "basic":
                username = self.config.auth.get("username", "")
                password = self.config.auth.get("password", "")
                self.session.auth = (username, password)
            
            elif auth_type == "token":
                token = self.config.auth.get("token", "")
                self.session.headers["Authorization"] = f"Bearer {token}"
            
            elif auth_type == "digest":
                username = self.config.auth.get("username", "")
                password = self.config.auth.get("password", "")
                from requests.auth import HTTPDigestAuth
                self.session.auth = HTTPDigestAuth(username, password)
        
        # Setup SSL verification
        if not self.config.verify_ssl:
            self.session.verify = False
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def _setup_compression(self):
        """Setup compression for requests"""
        compression_config = self.config.compression
        algorithm = compression_config.get("algorithm", "gzip")
        min_size = compression_config.get("min_size", 1024)
        
        # Add compression headers
        if algorithm == "gzip":
            self.session.headers["Accept-Encoding"] = "gzip, deflate"
        elif algorithm == "deflate":
            self.session.headers["Accept-Encoding"] = "deflate"
    
    def call(self, method_name: str, params: List[Any] = None) -> Any:
        """Call XML-RPC method"""
        if params is None:
            params = []
        
        # Convert parameters to XML-RPC values
        xmlrpc_params = []
        for param in params:
            xmlrpc_value = XMLRPCTypeConverter.python_to_xmlrpc(param)
            xmlrpc_params.append(xmlrpc_value)
        
        # Create method call
        method_call = XMLRPCMethodCall(method_name, xmlrpc_params)
        
        # Serialize request
        request_xml = self.serializer.serialize_method_call(method_call)
        
        # Log request if enabled
        if self.config.logging and self.config.logging.get("log_requests"):
            self.logger.info(f"XML-RPC Request: {method_name} with {len(params)} params")
        
        # Send request
        start_time = time.time()
        try:
            response = self.session.post(
                self.config.endpoint,
                data=request_xml,
                timeout=self.config.timeout
            )
            
            # Update metrics
            with self.lock:
                self.metrics.total_requests += 1
                self.metrics.last_request_time = time.time()
                response_time = time.time() - start_time
                self.metrics.total_response_time += response_time
                self.metrics.average_response_time = (
                    self.metrics.total_response_time / self.metrics.total_requests
                )
            
            # Check HTTP status
            response.raise_for_status()
            
            # Parse response
            response_xml = response.text
            method_response = self.parser.parse_method_response(response_xml)
            
            # Log response if enabled
            if self.config.logging and self.config.logging.get("log_responses"):
                self.logger.info(f"XML-RPC Response: {method_name} completed in {response_time:.3f}s")
            
            # Update success metrics
            with self.lock:
                self.metrics.successful_requests += 1
            
            # Check for fault
            if method_response.fault:
                fault_code = method_response.fault.get("faultCode", -1)
                fault_string = method_response.fault.get("faultString", "Unknown fault")
                
                # Log error if enabled
                if self.config.logging and self.config.logging.get("log_errors"):
                    self.logger.error(f"XML-RPC Fault: {fault_string} (Code: {fault_code})")
                
                # Update failure metrics
                with self.lock:
                    self.metrics.failed_requests += 1
                
                raise XMLRPCFault(fault_code, fault_string)
            
            # Return result
            if method_response.value:
                return XMLRPCTypeConverter.xmlrpc_to_python(method_response.value)
            return None
            
        except requests.exceptions.RequestException as e:
            # Update failure metrics
            with self.lock:
                self.metrics.failed_requests += 1
            
            # Log error if enabled
            if self.config.logging and self.config.logging.get("log_errors"):
                self.logger.error(f"XML-RPC Request failed: {e}")
            
            raise XMLRPCConnectionError(f"Connection error: {e}")
    
    def call_with_cache(self, method_name: str, params: List[Any] = None, 
                       cache_config: Optional[Dict[str, Any]] = None) -> Any:
        """Call XML-RPC method with caching"""
        if params is None:
            params = []
        
        if cache_config and cache_config.get("enabled"):
            cache_key = cache_config.get("key")
            if not cache_key:
                # Generate cache key from method and params
                import hashlib
                cache_data = f"{method_name}:{str(params)}"
                cache_key = hashlib.md5(cache_data.encode()).hexdigest()
            
            ttl = cache_config.get("ttl", 300)
            current_time = time.time()
            
            # Check cache
            if cache_key in self.cache:
                cached_data, cached_time = self.cache[cache_key]
                if current_time - cached_time < ttl:
                    with self.lock:
                        self.metrics.cache_hits += 1
                    return cached_data
            
            # Call method
            result = self.call(method_name, params)
            
            # Cache result
            self.cache[cache_key] = (result, current_time)
            
            with self.lock:
                self.metrics.cache_misses += 1
            
            return result
        else:
            return self.call(method_name, params)
    
    def call_async(self, method_name: str, params: List[Any] = None) -> Any:
        """Call XML-RPC method asynchronously"""
        if params is None:
            params = []
        
        # For now, use ThreadPoolExecutor for async calls
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.call, method_name, params)
            return future.result()
    
    def call_multiple(self, calls: List[Dict[str, Any]]) -> List[Any]:
        """Call multiple XML-RPC methods in parallel"""
        results = []
        
        with ThreadPoolExecutor(max_workers=min(len(calls), 10)) as executor:
            futures = []
            
            for call in calls:
                method_name = call["method"]
                params = call.get("params", [])
                future = executor.submit(self.call, method_name, params)
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({"error": str(e)})
        
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get client metrics"""
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
                "cache_hits": self.metrics.cache_hits,
                "cache_misses": self.metrics.cache_misses,
                "cache_hit_rate": (
                    self.metrics.cache_hits / max(self.metrics.cache_hits + self.metrics.cache_misses, 1)
                ),
                "last_request_time": self.metrics.last_request_time,
                "uptime": uptime,
                "requests_per_second": self.metrics.total_requests / max(uptime, 1)
            }
    
    def clear_cache(self):
        """Clear the cache"""
        with self.lock:
            self.cache.clear()
    
    def disconnect(self):
        """Disconnect and cleanup"""
        self.session.close()
        self.clear_cache()


class XMLRPCFault(Exception):
    """XML-RPC fault exception"""
    def __init__(self, fault_code: int, fault_string: str):
        self.fault_code = fault_code
        self.fault_string = fault_string
        super().__init__(f"XML-RPC Fault {fault_code}: {fault_string}")


class XMLRPCConnectionError(Exception):
    """XML-RPC connection error"""
    pass


# Factory function for creating clients
def create_xmlrpc_client(config_dict: Dict[str, Any]) -> XMLRPCClient:
    """Create XML-RPC client from configuration dictionary"""
    config = XMLRPCClientConfig(**config_dict)
    return XMLRPCClient(config)
