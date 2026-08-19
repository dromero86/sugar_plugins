"""
Unit tests for SOAP Plugin
=========================

Tests for the SOAP plugin functionality.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import the plugin
from ..src.SOAPPlugin import SOAPPlugin, SOAPClient, SOAPServer
from ..components.Helper import SOAPEnvelope, WSSecurityHelper, XMLHelper, WSDLHelper

class TestSOAPPlugin(unittest.TestCase):
    """Test cases for SOAPPlugin class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.plugin = SOAPPlugin()
        self.mock_context = Mock()
        self.plugin.context = self.mock_context
    
    def test_plugin_initialization(self):
        """Test plugin initialization"""
        self.assertIsNotNone(self.plugin)
        self.assertEqual(self.plugin.VERSION, "1.0.0")
        self.assertEqual(self.plugin.DESCRIPTION, "Comprehensive SOAP operations for Sugar (Native implementation)")
        self.assertEqual(self.plugin.AUTHOR, "Sugar Team")
        self.assertEqual(self.plugin.LICENSE, "MIT")
        self.assertEqual(self.plugin.DEPENDENCIES, [])
        self.assertEqual(self.plugin.REQUIREMENTS, [])
    
    def test_get_available_commands(self):
        """Test available commands"""
        commands = self.plugin.get_available_commands()
        expected_commands = ["soap_client", "soap_server", "soap_wsdl", "soap_schema", "soap_middleware"]
        self.assertEqual(commands, expected_commands)
    
    def test_execute_unknown_command(self):
        """Test executing unknown command"""
        with self.assertRaises(ValueError):
            self.plugin.execute("unknown_command", {})
    
    def test_soap_client_create(self):
        """Test SOAP client creation"""
        parameters = {
            "wsdl_url": "https://example.com/service?wsdl",
            "result": "test_client"
        }
        
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = Mock()
            mock_response.read.return_value = b'<wsdl>test</wsdl>'
            mock_urlopen.return_value.__enter__.return_value = mock_response
            
            result = self.plugin._create_soap_client(parameters)
            
            self.assertTrue(result["success"])
            self.mock_context.set_variable.assert_called_with("test_client", unittest.mock.ANY)
    
    def test_soap_server_create(self):
        """Test SOAP server creation"""
        parameters = {
            "host": "localhost",
            "port": 8080,
            "service_name": "TestService",
            "result": "test_server"
        }
        
        result = self.plugin._create_soap_server(parameters)
        
        self.assertTrue(result["success"])
        self.mock_context.set_variable.assert_called_with("test_server", unittest.mock.ANY)

class TestSOAPEnvelope(unittest.TestCase):
    """Test cases for SOAPEnvelope helper"""
    
    def test_generate_envelope_simple(self):
        """Test generating SOAP envelope with simple parameters"""
        envelope = SOAPEnvelope(
            method_name="TestMethod",
            parameters={"param1": "value1", "param2": 123}
        )
        
        xml = envelope.generate_envelope()
        
        self.assertIn("TestMethod", xml)
        self.assertIn("<param1>value1</param1>", xml)
        self.assertIn("<param2>123</param2>", xml)
        self.assertIn("soap:Envelope", xml)
        self.assertIn("soap:Body", xml)
    
    def test_generate_envelope_complex(self):
        """Test generating SOAP envelope with complex parameters"""
        envelope = SOAPEnvelope(
            method_name="TestMethod",
            parameters={
                "user": {
                    "id": 123,
                    "name": "Test User"
                }
            }
        )
        
        xml = envelope.generate_envelope()
        
        self.assertIn("TestMethod", xml)
        self.assertIn("<user>", xml)
        self.assertIn("<id>123</id>", xml)
        self.assertIn("<name>Test User</name>", xml)

class TestWSSecurityHelper(unittest.TestCase):
    """Test cases for WSSecurityHelper"""
    
    def test_generate_username_token_password_text(self):
        """Test generating UsernameToken with PasswordText"""
        token = WSSecurityHelper.generate_username_token(
            username="testuser",
            password="testpass",
            password_type="PasswordText"
        )
        
        self.assertIn("wsse:Security", token)
        self.assertIn("wsse:UsernameToken", token)
        self.assertIn("<wsse:Username>testuser</wsse:Username>", token)
        self.assertIn("PasswordText", token)
    
    def test_generate_username_token_password_digest(self):
        """Test generating UsernameToken with PasswordDigest"""
        token = WSSecurityHelper.generate_username_token(
            username="testuser",
            password="testpass",
            password_type="PasswordDigest"
        )
        
        self.assertIn("wsse:Security", token)
        self.assertIn("wsse:UsernameToken", token)
        self.assertIn("<wsse:Username>testuser</wsse:Username>", token)
        self.assertIn("PasswordDigest", token)

class TestXMLHelper(unittest.TestCase):
    """Test cases for XMLHelper"""
    
    def test_validate_xml_valid(self):
        """Test XML validation with valid XML"""
        valid_xml = "<root><child>value</child></root>"
        self.assertTrue(XMLHelper.validate_xml(valid_xml))
    
    def test_validate_xml_invalid(self):
        """Test XML validation with invalid XML"""
        invalid_xml = "<root><child>value</child>"
        self.assertFalse(XMLHelper.validate_xml(invalid_xml))
    
    def test_dict_to_xml_simple(self):
        """Test converting dictionary to XML"""
        data = {"name": "test", "value": 123}
        xml = XMLHelper.dict_to_xml(data)
        
        self.assertIn("<name>test</name>", xml)
        self.assertIn("<value>123</value>", xml)

class TestWSDLHelper(unittest.TestCase):
    """Test cases for WSDLHelper"""
    
    def test_extract_service_info_valid_wsdl(self):
        """Test extracting service info from valid WSDL"""
        wsdl_content = """<?xml version="1.0"?>
<wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
                  xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
                  targetNamespace="http://tempuri.org/">
    <wsdl:service name="TestService">
        <wsdl:port name="TestPort" binding="tns:TestBinding">
            <soap:address location="http://localhost:8080/"/>
        </wsdl:port>
    </wsdl:service>
</wsdl:definitions>"""
        
        info = WSDLHelper.extract_service_info(wsdl_content)
        
        self.assertEqual(info['target_namespace'], 'http://tempuri.org/')
        self.assertEqual(len(info['services']), 1)
        self.assertEqual(info['services'][0]['name'], 'TestService')
    
    def test_extract_service_info_invalid_wsdl(self):
        """Test extracting service info from invalid WSDL"""
        invalid_wsdl = "invalid xml content"
        info = WSDLHelper.extract_service_info(invalid_wsdl)
        
        self.assertIn('error', info)

class TestSchemaHelper(unittest.TestCase):
    """Test cases for SchemaHelper"""
    
    def test_generate_basic_schema(self):
        """Test generating basic XML Schema"""
        schema = SchemaHelper.generate_basic_schema(
            class_name="TestClass",
            target_namespace="http://example.com/"
        )
        
        self.assertIn("TestClass", schema)
        self.assertIn("http://example.com/", schema)
        self.assertIn("xsd:schema", schema)
        self.assertIn("xsd:complexType", schema)

if __name__ == '__main__':
    unittest.main()