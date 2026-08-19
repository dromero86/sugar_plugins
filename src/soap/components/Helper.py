"""
SOAP Plugin Helper Components
============================

Helper functions and utilities for the SOAP plugin.
"""

import xml.etree.ElementTree as ET
import base64
import hashlib
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class SOAPEnvelope:
    """Helper class for SOAP envelope operations"""
    method_name: str
    parameters: Dict[str, Any]
    namespace: str = "http://tempuri.org/"
    
    def generate_envelope(self) -> str:
        """Generate SOAP envelope XML"""
        params_xml = ""
        for key, value in self.parameters.items():
            if isinstance(value, dict):
                params_xml += f"<{key}>"
                for sub_key, sub_value in value.items():
                    params_xml += f"<{sub_key}>{sub_value}</{sub_key}>"
                params_xml += f"</{key}>"
            else:
                params_xml += f"<{key}>{value}</{key}>"
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <soap:Header/>
    <soap:Body>
        <{self.method_name} xmlns="{self.namespace}">
            {params_xml}
        </{self.method_name}>
    </soap:Body>
</soap:Envelope>"""

class WSSecurityHelper:
    """Helper class for WS-Security operations"""
    
    @staticmethod
    def generate_username_token(username: str, password: str, 
                               password_type: str = "PasswordText") -> str:
        """Generate WS-Security UsernameToken"""
        nonce = base64.b64encode(str(time.time()).encode()).decode()
        timestamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        
        if password_type == "PasswordDigest":
            password_digest = hashlib.sha1(f"{nonce}{timestamp}{password}".encode()).hexdigest()
            password = base64.b64encode(password_digest.encode()).decode()
        else:
            password = base64.b64encode(password.encode()).decode()
        
        return f"""<wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
    <wsse:UsernameToken>
        <wsse:Username>{username}</wsse:Username>
        <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#{password_type}">{password}</wsse:Password>
        <wsse:Nonce>{nonce}</wsse:Nonce>
        <wsu:Created xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">{timestamp}</wsu:Created>
    </wsse:UsernameToken>
</wsse:Security>"""

class XMLHelper:
    """Helper class for XML operations"""
    
    @staticmethod
    def element_to_dict(element: ET.Element) -> Any:
        """Convert XML element to dictionary"""
        result = {}
        
        for child in element:
            if len(child) > 0:
                result[child.tag] = XMLHelper.element_to_dict(child)
            else:
                result[child.tag] = child.text
        
        return result
    
    @staticmethod
    def dict_to_xml(data: Dict[str, Any]) -> str:
        """Convert dictionary to XML"""
        xml_parts = []
        
        for key, value in data.items():
            if isinstance(value, dict):
                xml_parts.append(f"<{key}>{XMLHelper.dict_to_xml(value)}</{key}>")
            else:
                xml_parts.append(f"<{key}>{value}</{key}>")
        
        return ''.join(xml_parts)
    
    @staticmethod
    def validate_xml(xml_content: str) -> bool:
        """Validate XML content"""
        try:
            ET.fromstring(xml_content)
            return True
        except ET.ParseError:
            return False

class WSDLHelper:
    """Helper class for WSDL operations"""
    
    @staticmethod
    def extract_service_info(wsdl_content: str) -> Dict[str, Any]:
        """Extract service information from WSDL"""
        try:
            root = ET.fromstring(wsdl_content)
            
            wsdl_info = {
                'target_namespace': root.get('targetNamespace', ''),
                'services': [],
                'port_types': [],
                'bindings': [],
                'messages': []
            }
            
            # Extract services
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
        except Exception:
            return {'error': 'Failed to parse WSDL'}

class SchemaHelper:
    """Helper class for XML Schema operations"""
    
    @staticmethod
    def generate_basic_schema(class_name: str, target_namespace: str) -> str:
        """Generate basic XML Schema content"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
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