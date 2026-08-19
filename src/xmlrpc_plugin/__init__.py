"""
XML-RPC Plugin for Sugar Language
Provides XML-RPC client and server capabilities
"""

# Import the XML-RPC implementations from the plugin
from .xml_rpc_client import XMLRPCClient, XMLRPCClientConfig, create_xmlrpc_client, XMLRPCFault, XMLRPCConnectionError
from .xml_rpc_server import XMLRPCServer, XMLRPCServerConfig, create_xmlrpc_server

__version__ = "1.0.0"
__author__ = "Sugar Team"

def register(registry):
    """Register the XML-RPC plugin"""
    registry.register_service("xmlrpc_client", XMLRPCClient)
    registry.register_service("xmlrpc_server", XMLRPCServer)
    registry.register_config("xmlrpc_client", XMLRPCClientConfig)
    registry.register_config("xmlrpc_server", XMLRPCServerConfig)
