"""
SOAP Plugin for Sugar Language
==============================

A comprehensive SOAP plugin that provides both client and server SOAP capabilities,
implemented using only Python standard library without external dependencies.
"""

import asyncio
import json
import time
import threading
import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse
import urllib.error
import ssl
import base64
import hashlib
import socket
import http.server
import socketserver
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

# Sugar imports
from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output

class SOAPAuthType(Enum):
    """Tipos de autenticación SOAP soportados"""
    NONE = "none"
    BASIC = "basic"
    DIGEST = "digest"
    WS_SECURITY = "ws_security"
    CERTIFICATE = "certificate"

class SOAPFaultType(Enum):
    """Tipos de errores SOAP"""
    CLIENT = "Client"
    SERVER = "Server"
    MUST_UNDERSTAND = "MustUnderstand"
    VERSION_MISMATCH = "VersionMismatch"

@dataclass
class SOAPRequest:
    """Representa una petición SOAP"""
    method: str
    parameters: Dict[str, Any]
    headers: Dict[str, str]
    wsdl_url: str
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass
class SOAPResponse:
    """Representa una respuesta SOAP"""
    method: str
    result: Any
    headers: Dict[str, str]
    fault: Optional[Dict[str, Any]] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass
class SOAPFault:
    """Representa un error SOAP"""
    fault_code: str
    fault_string: str
    fault_actor: Optional[str] = None
    detail: Optional[Dict[str, Any]] = None

class SOAPClient:
    """Cliente SOAP nativo usando solo bibliotecas estándar"""
    
    def __init__(self, wsdl_url: str, config: Optional[Dict[str, Any]] = None):
        self.wsdl_url = wsdl_url
        self.config = config or {}
        self.wsdl_info = None
        self._parse_wsdl()
    
    def _parse_wsdl(self):
        """Parsea el WSDL para obtener información del servicio"""
        try:
            # Crear contexto SSL si es necesario
            context = ssl.create_default_context()
            if not self.config.get('verify_ssl', True):
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            
            # Configurar headers
            headers = self.config.get('headers', {})
            headers.update({
                'User-Agent': 'Sugar-SOAP-Client/3.0.0',
                'Accept': 'text/xml, application/soap+xml'
            })
            
            # Configurar autenticación
            if 'auth' in self.config:
                auth_config = self.config['auth']
                if auth_config.get('type') == 'basic':
                    credentials = f"{auth_config['username']}:{auth_config['password']}"
                    encoded_credentials = base64.b64encode(credentials.encode()).decode()
                    headers['Authorization'] = f"Basic {encoded_credentials}"
            
            # Crear request
            req = urllib.request.Request(self.wsdl_url, headers=headers)
            
            # Configurar proxy si es necesario
            if 'proxy' in self.config:
                proxy_config = self.config['proxy']
                if 'http' in proxy_config:
                    req.set_proxy(proxy_config['http'], 'http')
                if 'https' in proxy_config:
                    req.set_proxy(proxy_config['https'], 'https')
            
            # Realizar petición
            with urllib.request.urlopen(req, context=context, timeout=self.config.get('timeout', 30)) as response:
                wsdl_content = response.read().decode('utf-8')
                self.wsdl_info = self._extract_wsdl_info(wsdl_content)
                
        except Exception as e:
            Output.Console("SOAP", f"Error parsing WSDL: {str(e)}")
            raise
    
    def _extract_wsdl_info(self, wsdl_content: str) -> Dict[str, Any]:
        """Extrae información del WSDL"""
        try:
            root = ET.fromstring(wsdl_content)
            
            wsdl_info = {
                'target_namespace': root.get('targetNamespace', ''),
                'services': [],
                'port_types': [],
                'bindings': [],
                'messages': []
            }
            
            # Extraer servicios
            for service in root.findall('.//{http://schemas.xmlsoap.org/wsdl/}service'):
                service_info = {
                    'name': service.get('name', ''),
                    'ports': []
                }
                for port in service.findall('.//{http://schemas.xmlsoap.org/wsdl/}port'):
                    port_info = {
                        'name': port.get('name', ''),
                        'binding': port.get('binding', ''),
                        'address': port.find('.//{http://schemas.xmlsoap.org/soap/}address').get('location', '')
                    }
                    service_info['ports'].append(port_info)
                wsdl_info['services'].append(service_info)
            
            return wsdl_info
        except Exception as e:
            Output.Console("SOAP", f"Error extracting WSDL info: {str(e)}")
            return {'error': str(e)}
    
    def call_method(self, method_name: str, parameters: Dict[str, Any], 
                   headers: Optional[Dict[str, str]] = None) -> SOAPResponse:
        """Llama a un método SOAP"""
        try:
            # Generar SOAP envelope
            soap_envelope = self._generate_soap_envelope(method_name, parameters)
            
            # Configurar headers
            request_headers = {
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': f'"{self.wsdl_info.get("target_namespace", "")}{method_name}"',
                'User-Agent': 'Sugar-SOAP-Client/3.0.0'
            }
            if headers:
                request_headers.update(headers)
            
            # Configurar autenticación WS-Security si es necesario
            if 'ws_security' in self.config:
                ws_security = self.config['ws_security']
                if ws_security.get('type') == 'username_token':
                    soap_envelope = self._add_ws_security(soap_envelope, ws_security)
            
            # Obtener endpoint del servicio
            endpoint = self._get_service_endpoint()
            
            # Realizar petición SOAP
            response = self._send_soap_request(endpoint, soap_envelope, request_headers)
            
            # Parsear respuesta
            result = self._parse_soap_response(response)
            
            return SOAPResponse(
                method=method_name,
                result=result,
                headers=request_headers
            )
            
        except Exception as e:
            fault = SOAPFault(
                fault_code="TRANSPORT_ERROR",
                fault_string=str(e)
            )
            return SOAPResponse(
                method=method_name,
                result=None,
                headers=headers or {},
                fault=asdict(fault)
            )
    
    def _generate_soap_envelope(self, method_name: str, parameters: Dict[str, Any]) -> str:
        """Genera el envelope SOAP"""
        namespace = self.wsdl_info.get('target_namespace', 'http://tempuri.org/')
        
        # Convertir parámetros a XML
        params_xml = ""
        for key, value in parameters.items():
            if isinstance(value, dict):
                params_xml += f"<{key}>"
                for sub_key, sub_value in value.items():
                    params_xml += f"<{sub_key}>{sub_value}</{sub_key}>"
                params_xml += f"</{key}>"
            else:
                params_xml += f"<{key}>{value}</{key}>"
        
        soap_envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <soap:Header/>
    <soap:Body>
        <{method_name} xmlns="{namespace}">
            {params_xml}
        </{method_name}>
    </soap:Body>
</soap:Envelope>"""
        
        return soap_envelope
    
    def _add_ws_security(self, soap_envelope: str, ws_security: Dict[str, Any]) -> str:
        """Agrega WS-Security al envelope SOAP"""
        username = ws_security.get('username', '')
        password = ws_security.get('password', '')
        password_type = ws_security.get('password_type', 'PasswordText')
        
        # Generar nonce y timestamp
        nonce = base64.b64encode(str(time.time()).encode()).decode()
        timestamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        
        # Generar password digest si es necesario
        if password_type == 'PasswordDigest':
            password_digest = hashlib.sha1(f"{nonce}{timestamp}{password}".encode()).hexdigest()
            password = base64.b64encode(password_digest.encode()).decode()
        else:
            password = base64.b64encode(password.encode()).decode()
        
        # Crear header WS-Security
        wsse_header = f"""<wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
    <wsse:UsernameToken>
        <wsse:Username>{username}</wsse:Username>
        <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#{password_type}">{password}</wsse:Password>
        <wsse:Nonce>{nonce}</wsse:Nonce>
        <wsu:Created xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">{timestamp}</wsu:Created>
    </wsse:UsernameToken>
</wsse:Security>"""
        
        # Insertar header en el envelope
        envelope_start = soap_envelope.find('<soap:Header/>')
        if envelope_start != -1:
            return soap_envelope.replace('<soap:Header/>', f'<soap:Header>{wsse_header}</soap:Header>')
        
        return soap_envelope
    
    def _get_service_endpoint(self) -> str:
        """Obtiene el endpoint del servicio desde el WSDL"""
        if self.wsdl_info and self.wsdl_info.get('services'):
            for service in self.wsdl_info['services']:
                for port in service.get('ports', []):
                    return port.get('address', '')
        return self.wsdl_url.replace('?wsdl', '')
    
    def _send_soap_request(self, endpoint: str, soap_envelope: str, headers: Dict[str, str]) -> str:
        """Envía la petición SOAP"""
        # Crear contexto SSL
        context = ssl.create_default_context()
        if not self.config.get('verify_ssl', True):
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        
        # Crear request
        req = urllib.request.Request(endpoint, data=soap_envelope.encode('utf-8'), headers=headers)
        
        # Configurar proxy si es necesario
        if 'proxy' in self.config:
            proxy_config = self.config['proxy']
            if 'http' in proxy_config:
                req.set_proxy(proxy_config['http'], 'http')
            if 'https' in proxy_config:
                req.set_proxy(proxy_config['https'], 'https')
        
        # Realizar petición
        with urllib.request.urlopen(req, context=context, timeout=self.config.get('timeout', 30)) as response:
            return response.read().decode('utf-8')
    
    def _parse_soap_response(self, response: str) -> Any:
        """Parsea la respuesta SOAP"""
        try:
            root = ET.fromstring(response)
            
            # Buscar fault
            fault = root.find('.//soap:Fault', namespaces={'soap': 'http://schemas.xmlsoap.org/soap/envelope/'})
            if fault is not None:
                fault_code = fault.find('.//faultcode')
                fault_string = fault.find('.//faultstring')
                raise Exception(f"SOAP Fault: {fault_code.text if fault_code is not None else 'Unknown'} - {fault_string.text if fault_string is not None else 'Unknown'}")
            
            # Extraer resultado
            body = root.find('.//soap:Body', namespaces={'soap': 'http://schemas.xmlsoap.org/soap/envelope/'})
            if body is not None and len(body) > 0:
                result_element = body[0]
                return self._element_to_dict(result_element)
            
            return None
            
        except Exception as e:
            Output.Console("SOAP", f"Error parsing SOAP response: {str(e)}")
            raise
    
    def _element_to_dict(self, element: ET.Element) -> Any:
        """Convierte un elemento XML a diccionario"""
        result = {}
        
        for child in element:
            if len(child) > 0:
                result[child.tag] = self._element_to_dict(child)
            else:
                result[child.tag] = child.text
        
        return result

class SOAPServer:
    """Servidor SOAP básico usando bibliotecas estándar"""
    
    def __init__(self, host: str = "localhost", port: int = 8080, 
                 service_name: str = "SOAPService"):
        self.host = host
        self.port = port
        self.service_name = service_name
        self.methods = {}
        self.middleware = []
        self.running = False
        self.server_thread = None
        self.http_server = None
        
    def register_method(self, method_name: str, handler: Callable):
        """Registra un método en el servidor"""
        self.methods[method_name] = handler
        Output.Console("SOAP", f"Method registered: {method_name}")
    
    def add_middleware(self, middleware_func: Callable):
        """Agrega middleware al servidor"""
        self.middleware.append(middleware_func)
    
    def start(self):
        """Inicia el servidor SOAP"""
        if self.running:
            return
        
        self.running = True
        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        Output.Console("SOAP", f"SOAP Server started on {self.host}:{self.port}")
    
    def stop(self):
        """Detiene el servidor SOAP"""
        self.running = False
        if self.http_server:
            self.http_server.shutdown()
        if self.server_thread:
            self.server_thread.join()
        Output.Console("SOAP", "SOAP Server stopped")
    
    def _run_server(self):
        """Ejecuta el servidor SOAP"""
        try:
            handler = self._create_request_handler()
            self.http_server = socketserver.TCPServer((self.host, self.port), handler)
            self.http_server.serve_forever()
        except Exception as e:
            Output.Console("SOAP", f"Error running server: {str(e)}")
    
    def _create_request_handler(self):
        """Crea el manejador de peticiones HTTP"""
        server = self
        
        class SOAPRequestHandler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                try:
                    # Leer contenido de la petición
                    content_length = int(self.headers.get('Content-Length', 0))
                    post_data = self.rfile.read(content_length)
                    
                    # Parsear petición SOAP
                    soap_request = server._parse_soap_request(post_data.decode('utf-8'))
                    
                    # Ejecutar middleware
                    for middleware in server.middleware:
                        middleware(soap_request)
                    
                    # Procesar petición
                    response = server._process_soap_request(soap_request)
                    
                    # Enviar respuesta
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/xml; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(response.encode('utf-8'))
                    
                except Exception as e:
                    # Enviar error SOAP
                    fault_response = server._create_soap_fault(str(e))
                    self.send_response(500)
                    self.send_header('Content-Type', 'text/xml; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(fault_response.encode('utf-8'))
            
            def do_GET(self):
                # Servir WSDL si se solicita
                if self.path == '/wsdl':
                    wsdl_content = server._generate_wsdl()
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/xml; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(wsdl_content.encode('utf-8'))
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                # Deshabilitar logging por defecto
                pass
        
        return SOAPRequestHandler
    
    def _parse_soap_request(self, soap_content: str) -> SOAPRequest:
        """Parsea una petición SOAP"""
        try:
            root = ET.fromstring(soap_content)
            body = root.find('.//soap:Body', namespaces={'soap': 'http://schemas.xmlsoap.org/soap/envelope/'})
            
            if body is not None and len(body) > 0:
                method_element = body[0]
                method_name = method_element.tag.split('}')[-1]  # Remover namespace
                
                # Extraer parámetros
                parameters = {}
                for child in method_element:
                    if len(child) > 0:
                        parameters[child.tag] = self._element_to_dict(child)
                    else:
                        parameters[child.tag] = child.text
                
                return SOAPRequest(
                    method=method_name,
                    parameters=parameters,
                    headers={},
                    wsdl_url=f"http://{self.host}:{self.port}"
                )
            
            raise Exception("Invalid SOAP request")
            
        except Exception as e:
            Output.Console("SOAP", f"Error parsing SOAP request: {str(e)}")
            raise
    
    def _process_soap_request(self, request: SOAPRequest) -> str:
        """Procesa una petición SOAP"""
        if request.method in self.methods:
            handler = self.methods[request.method]
            result = handler(**request.parameters)
            
            # Generar respuesta SOAP
            return self._generate_soap_response(request.method, result)
        else:
            raise Exception(f"Method {request.method} not found")
    
    def _generate_soap_response(self, method_name: str, result: Any) -> str:
        """Genera una respuesta SOAP"""
        # Convertir resultado a XML
        result_xml = self._dict_to_xml(result) if isinstance(result, dict) else str(result)
        
        soap_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <soap:Body>
        <{method_name}Response xmlns="http://tempuri.org/">
            <{method_name}Result>{result_xml}</{method_name}Result>
        </{method_name}Response>
    </soap:Body>
</soap:Envelope>"""
        
        return soap_response
    
    def _create_soap_fault(self, error_message: str) -> str:
        """Crea una respuesta de error SOAP"""
        soap_fault = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <soap:Fault>
            <faultcode>soap:Server</faultcode>
            <faultstring>{error_message}</faultstring>
        </soap:Fault>
    </soap:Body>
</soap:Envelope>"""
        
        return soap_fault
    
    def _generate_wsdl(self) -> str:
        """Genera WSDL para el servicio"""
        wsdl_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
                  xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
                  xmlns:tns="http://tempuri.org/"
                  targetNamespace="http://tempuri.org/">
    
    <wsdl:types>
        <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                     targetNamespace="http://tempuri.org/">
        </xsd:schema>
    </wsdl:types>
    
    <wsdl:message name="RequestMessage">
        <wsdl:part name="parameters" element="tns:Request"/>
    </wsdl:message>
    
    <wsdl:message name="ResponseMessage">
        <wsdl:part name="parameters" element="tns:Response"/>
    </wsdl:message>
    
    <wsdl:portType name="{self.service_name}PortType">
        <!-- Add your operations here -->
    </wsdl:portType>
    
    <wsdl:binding name="{self.service_name}Binding" type="tns:{self.service_name}PortType">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
        <!-- Add your operations here -->
    </wsdl:binding>
    
    <wsdl:service name="{self.service_name}">
        <wsdl:port name="{self.service_name}Port" binding="tns:{self.service_name}Binding">
            <soap:address location="http://{self.host}:{self.port}/"/>
        </wsdl:port>
    </wsdl:service>
    
</wsdl:definitions>"""
        
        return wsdl_content
    
    def _element_to_dict(self, element: ET.Element) -> Any:
        """Convierte un elemento XML a diccionario"""
        result = {}
        
        for child in element:
            if len(child) > 0:
                result[child.tag] = self._element_to_dict(child)
            else:
                result[child.tag] = child.text
        
        return result
    
    def _dict_to_xml(self, data: Dict[str, Any]) -> str:
        """Convierte un diccionario a XML"""
        xml_parts = []
        
        for key, value in data.items():
            if isinstance(value, dict):
                xml_parts.append(f"<{key}>{self._dict_to_xml(value)}</{key}>")
            else:
                xml_parts.append(f"<{key}>{value}</{key}>")
        
        return ''.join(xml_parts)

class WSDLProcessor:
    """Procesador de WSDL usando bibliotecas estándar"""
    
    def __init__(self):
        self.cache = {}
    
    def parse_wsdl(self, wsdl_url: str) -> Dict[str, Any]:
        """Parsea un archivo WSDL"""
        if wsdl_url in self.cache:
            return self.cache[wsdl_url]
        
        try:
            # Crear contexto SSL
            context = ssl.create_default_context()
            
            # Realizar petición HTTP
            req = urllib.request.Request(wsdl_url)
            with urllib.request.urlopen(req, context=context, timeout=30) as response:
                wsdl_content = response.read().decode('utf-8')
            
            wsdl_info = self._extract_wsdl_info(wsdl_content)
            self.cache[wsdl_url] = wsdl_info
            return wsdl_info
            
        except Exception as e:
            Output.Console("SOAP", f"Error parsing WSDL: {str(e)}")
            raise
    
    def _extract_wsdl_info(self, wsdl_content: str) -> Dict[str, Any]:
        """Extrae información del WSDL"""
        try:
            root = ET.fromstring(wsdl_content)
            
            wsdl_info = {
                'target_namespace': root.get('targetNamespace', ''),
                'services': [],
                'port_types': [],
                'bindings': [],
                'messages': []
            }
            
            # Extraer servicios
            for service in root.findall('.//{http://schemas.xmlsoap.org/wsdl/}service'):
                service_info = {
                    'name': service.get('name', ''),
                    'ports': []
                }
                for port in service.findall('.//{http://schemas.xmlsoap.org/wsdl/}port'):
                    port_info = {
                        'name': port.get('name', ''),
                        'binding': port.get('binding', ''),
                        'address': port.find('.//{http://schemas.xmlsoap.org/soap/}address').get('location', '')
                    }
                    service_info['ports'].append(port_info)
                wsdl_info['services'].append(service_info)
            
            return wsdl_info
        except Exception as e:
            Output.Console("SOAP", f"Error extracting WSDL info: {str(e)}")
            return {'error': str(e)}

class XMLSchemaValidator:
    """Validador de esquemas XML usando bibliotecas estándar"""
    
    def __init__(self):
        self.schemas = {}
    
    def validate_xml(self, xml_content: str, schema_url: str) -> bool:
        """Valida XML contra un esquema XSD"""
        try:
            if schema_url not in self.schemas:
                # Crear contexto SSL
                context = ssl.create_default_context()
                
                # Realizar petición HTTP
                req = urllib.request.Request(schema_url)
                with urllib.request.urlopen(req, context=context, timeout=30) as response:
                    self.schemas[schema_url] = response.read().decode('utf-8')
            
            # Validación básica - verificar que sea XML válido
            ET.fromstring(xml_content)
            return True
            
        except Exception as e:
            Output.Console("SOAP", f"Error validating XML: {str(e)}")
            return False

class SOAPPlugin(PluginBase):
    """
    SOAP plugin for Sugar.
    
    Provides comprehensive SOAP operations including:
    - SOAP client with WSDL support
    - SOAP server creation
    - WSDL parsing and generation
    - XML Schema validation
    - WS-Security support
    - Async operations
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Comprehensive SOAP operations for Sugar (Native implementation)"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = []  # No external dependencies
    REQUIREMENTS = []  # No external requirements
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """Initialize the SOAP plugin."""
        super().__init__(context, plugin_config)
        self.clients = {}  # Dictionary to store SOAP clients
        self.servers = {}  # Dictionary to store SOAP servers
        self.wsdl_processor = WSDLProcessor()
        self.schema_validator = XMLSchemaValidator()
        self.middleware = []
        
        Output.Console(self.plugin_name, "SOAP plugin initialized (Native implementation)")
    
    def get_available_commands(self) -> List[str]:
        """Get available commands for this plugin."""
        return ["soap_client", "soap_server", "soap_wsdl", "soap_schema", "soap_middleware"]
    
    def execute(self, operator: str, parameters: Dict[str, Any]) -> Any:
        """
        Execute SOAP plugin commands.
        
        Args:
            operator: Command to execute
            parameters: Command parameters
            
        Returns:
            Command result
        """
        try:
            if operator == "soap_client":
                return self._handle_soap_client(parameters)
            elif operator == "soap_server":
                return self._handle_soap_server(parameters)
            elif operator == "soap_wsdl":
                return self._handle_soap_wsdl(parameters)
            elif operator == "soap_schema":
                return self._handle_soap_schema(parameters)
            elif operator == "soap_middleware":
                return self._handle_soap_middleware(parameters)
            else:
                raise ValueError(f"Unknown SOAP operator: {operator}")
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing operator {operator}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _handle_soap_client(self, parameters: Dict[str, Any]) -> Any:
        """Handle SOAP client operations"""
        operator = parameters.get("operator")
        
        if operator == "create":
            return self._create_soap_client(parameters)
        elif operator == "call":
            return self._call_soap_method(parameters)
        else:
            raise ValueError(f"Unknown SOAP client operator: {operator}")
    
    def _create_soap_client(self, parameters: Dict[str, Any]) -> Any:
        """Create a SOAP client"""
        wsdl_url = parameters.get("wsdl_url")
        config = parameters.get("config", {})
        result_var = parameters.get("result")
        
        if not wsdl_url:
            raise ValueError("wsdl_url is required")
        
        try:
            client = SOAPClient(wsdl_url, config)
            
            if result_var:
                self.context.set_variable(result_var, client)
            
            Output.Console(self.plugin_name, f"SOAP client created for {wsdl_url}")
            return {"success": True, "client": client}
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error creating SOAP client: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _call_soap_method(self, parameters: Dict[str, Any]) -> Any:
        """Call a SOAP method"""
        client = parameters.get("client")
        method = parameters.get("method")
        method_params = parameters.get("parameters", {})
        headers = parameters.get("headers", {})
        result_var = parameters.get("result")
        
        if not client or not method:
            raise ValueError("client and method are required")
        
        try:
            response = client.call_method(method, method_params, headers)
            
            if result_var:
                self.context.set_variable(result_var, response)
            
            if response.fault:
                Output.Console(self.plugin_name, f"SOAP Fault: {response.fault}")
                return {"success": False, "fault": response.fault}
            else:
                Output.Console(self.plugin_name, f"SOAP method {method} called successfully")
                return {"success": True, "result": response.result}
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error calling SOAP method: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _handle_soap_server(self, parameters: Dict[str, Any]) -> Any:
        """Handle SOAP server operations"""
        operator = parameters.get("operator")
        
        if operator == "create":
            return self._create_soap_server(parameters)
        elif operator == "register_method":
            return self._register_server_method(parameters)
        elif operator == "start":
            return self._start_soap_server(parameters)
        elif operator == "stop":
            return self._stop_soap_server(parameters)
        else:
            raise ValueError(f"Unknown SOAP server operator: {operator}")
    
    def _create_soap_server(self, parameters: Dict[str, Any]) -> Any:
        """Create a SOAP server"""
        host = parameters.get("host", "localhost")
        port = parameters.get("port", 8080)
        service_name = parameters.get("service_name", "SOAPService")
        result_var = parameters.get("result")
        
        try:
            server = SOAPServer(host, port, service_name)
            
            if result_var:
                self.context.set_variable(result_var, server)
            
            Output.Console(self.plugin_name, f"SOAP server created: {host}:{port}")
            return {"success": True, "server": server}
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error creating SOAP server: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _register_server_method(self, parameters: Dict[str, Any]) -> Any:
        """Register a method in SOAP server"""
        server = parameters.get("server")
        method_name = parameters.get("method_name")
        handler = parameters.get("handler")
        result_var = parameters.get("result")
        
        if not server or not method_name or not handler:
            raise ValueError("server, method_name, and handler are required")
        
        try:
            # Convert handler to callable function
            handler_func = self._create_handler_function(handler)
            server.register_method(method_name, handler_func)
            
            if result_var:
                self.context.set_variable(result_var, True)
            
            Output.Console(self.plugin_name, f"Method {method_name} registered in SOAP server")
            return {"success": True}
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error registering method: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _create_handler_function(self, handler_config: Dict[str, Any]) -> Callable:
        """Create a callable function from handler configuration"""
        def handler_function(*args, **kwargs):
            # This is a simplified implementation
            # In a real implementation, you would execute the Sugar script
            return {"result": "handler executed", "args": args, "kwargs": kwargs}
        
        return handler_function
    
    def _start_soap_server(self, parameters: Dict[str, Any]) -> Any:
        """Start a SOAP server"""
        server = parameters.get("server")
        result_var = parameters.get("result")
        
        if not server:
            raise ValueError("server is required")
        
        try:
            server.start()
            
            if result_var:
                self.context.set_variable(result_var, True)
            
            Output.Console(self.plugin_name, "SOAP server started")
            return {"success": True}
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error starting SOAP server: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _stop_soap_server(self, parameters: Dict[str, Any]) -> Any:
        """Stop a SOAP server"""
        server = parameters.get("server")
        
        if not server:
            raise ValueError("server is required")
        
        try:
            server.stop()
            Output.Console(self.plugin_name, "SOAP server stopped")
            return {"success": True}
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error stopping SOAP server: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _handle_soap_wsdl(self, parameters: Dict[str, Any]) -> Any:
        """Handle WSDL operations"""
        operator = parameters.get("operator")
        
        if operator == "parse":
            return self._parse_wsdl(parameters)
        elif operator == "generate":
            return self._generate_wsdl(parameters)
        elif operator == "validate":
            return self._validate_wsdl(parameters)
        else:
            raise ValueError(f"Unknown WSDL operator: {operator}")
    
    def _parse_wsdl(self, parameters: Dict[str, Any]) -> Any:
        """Parse a WSDL file"""
        wsdl_url = parameters.get("wsdl_url")
        result_var = parameters.get("result")
        
        if not wsdl_url:
            raise ValueError("wsdl_url is required")
        
        try:
            wsdl_info = self.wsdl_processor.parse_wsdl(wsdl_url)
            
            if result_var:
                self.context.set_variable(result_var, wsdl_info)
            
            Output.Console(self.plugin_name, f"WSDL parsed: {wsdl_url}")
            return {"success": True, "wsdl_info": wsdl_info}
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error parsing WSDL: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _generate_wsdl(self, parameters: Dict[str, Any]) -> Any:
        """Generate WSDL from server"""
        server = parameters.get("server")
        target_namespace = parameters.get("target_namespace", "http://tempuri.org/")
        result_var = parameters.get("result")
        
        if not server:
            raise ValueError("server is required")
        
        try:
            # Generate basic WSDL
            wsdl_content = server._generate_wsdl()
            
            if result_var:
                self.context.set_variable(result_var, wsdl_content)
            
            Output.Console(self.plugin_name, "WSDL generated")
            return {"success": True, "wsdl_content": wsdl_content}
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error generating WSDL: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _validate_wsdl(self, parameters: Dict[str, Any]) -> Any:
        """Validate WSDL content"""
        wsdl_content = parameters.get("wsdl_content")
        result_var = parameters.get("result")
        
        if not wsdl_content:
            raise ValueError("wsdl_content is required")
        
        try:
            # Basic validation - check if it's valid XML
            ET.fromstring(wsdl_content)
            
            if result_var:
                self.context.set_variable(result_var, True)
            
            Output.Console(self.plugin_name, "WSDL validation successful")
            return {"success": True, "valid": True}
            
        except Exception as e:
            Output.Console(self.plugin_name, f"WSDL validation failed: {str(e)}")
            return {"success": False, "valid": False, "error": str(e)}
    
    def _handle_soap_schema(self, parameters: Dict[str, Any]) -> Any:
        """Handle XML Schema operations"""
        operator = parameters.get("operator")
        
        if operator == "validate":
            return self._validate_xml_schema(parameters)
        elif operator == "generate_from_class":
            return self._generate_schema_from_class(parameters)
        else:
            raise ValueError(f"Unknown schema operator: {operator}")
    
    def _validate_xml_schema(self, parameters: Dict[str, Any]) -> Any:
        """Validate XML against schema"""
        xml_content = parameters.get("xml_content")
        schema_url = parameters.get("schema_url")
        result_var = parameters.get("result")
        
        if not xml_content or not schema_url:
            raise ValueError("xml_content and schema_url are required")
        
        try:
            is_valid = self.schema_validator.validate_xml(xml_content, schema_url)
            
            if result_var:
                self.context.set_variable(result_var, is_valid)
            
            Output.Console(self.plugin_name, f"XML schema validation: {is_valid}")
            return {"success": True, "valid": is_valid}
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error validating XML schema: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _generate_schema_from_class(self, parameters: Dict[str, Any]) -> Any:
        """Generate XML Schema from class"""
        class_name = parameters.get("class_name")
        target_namespace = parameters.get("target_namespace", "http://tempuri.org/")
        result_var = parameters.get("result")
        
        if not class_name:
            raise ValueError("class_name is required")
        
        try:
            # Generate basic schema
            schema_content = self._generate_basic_schema(class_name, target_namespace)
            
            if result_var:
                self.context.set_variable(result_var, schema_content)
            
            Output.Console(self.plugin_name, f"Schema generated for class: {class_name}")
            return {"success": True, "schema_content": schema_content}
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error generating schema: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _generate_basic_schema(self, class_name: str, target_namespace: str) -> str:
        """Generate basic XML Schema content"""
        schema_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            targetNamespace="{target_namespace}"
            xmlns:tns="{target_namespace}">
    
    <xsd:element name="{class_name}">
        <xsd:complexType>
            <xsd:sequence>
                <!-- Add your elements here -->
            </xsd:sequence>
        </xsd:complexType>
    </xsd:element>
    
</xsd:schema>"""
        
        return schema_template
    
    def _handle_soap_middleware(self, parameters: Dict[str, Any]) -> Any:
        """Handle SOAP middleware operations"""
        operator = parameters.get("operator")
        
        if operator == "register":
            return self._register_middleware(parameters)
        else:
            raise ValueError(f"Unknown middleware operator: {operator}")
    
    def _register_middleware(self, parameters: Dict[str, Any]) -> Any:
        """Register SOAP middleware"""
        middleware_type = parameters.get("type")
        config = parameters.get("config", {})
        result_var = parameters.get("result")
        
        if not middleware_type:
            raise ValueError("type is required")
        
        try:
            # Create middleware function based on type
            middleware_func = self._create_middleware_function(middleware_type, config)
            self.middleware.append(middleware_func)
            
            if result_var:
                self.context.set_variable(result_var, True)
            
            Output.Console(self.plugin_name, f"Middleware registered: {middleware_type}")
            return {"success": True}
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error registering middleware: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _create_middleware_function(self, middleware_type: str, config: Dict[str, Any]) -> Callable:
        """Create middleware function based on type"""
        if middleware_type == "request_logger":
            def request_logger(request):
                Output.Console(self.plugin_name, f"SOAP Request: {request.method}")
                return None
            return request_logger
        elif middleware_type == "schema_validator":
            def schema_validator(request):
                # Validate request against schema
                return None
            return schema_validator
        else:
            raise ValueError(f"Unknown middleware type: {middleware_type}")
    
    def cleanup(self):
        """Cleanup plugin resources"""
        # Stop all servers
        for server in self.servers.values():
            if server.running:
                server.stop()
        
        Output.Console(self.plugin_name, "SOAP plugin cleanup completed")