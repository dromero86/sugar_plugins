"""
LDAP Connection Component
========================

Handles LDAP server connections, authentication, and basic operations.
"""

import ssl
from typing import Any, Dict, Optional

# Import LDAP modules from the main plugin
try:
    from .LDAPPlugin import LDAP_AVAILABLE, LDAPError, INVALID_CREDENTIALS, NO_SUCH_OBJECT
    if LDAP_AVAILABLE:
        import ldap
except ImportError:
    # Fallback if main plugin not available
    LDAP_AVAILABLE = False
    LDAPError = Exception
    INVALID_CREDENTIALS = Exception
    NO_SUCH_OBJECT = Exception

from Sugar.Lang.Utils.Output import Output

class LDAPConnection:
    """LDAP connection handler."""
    
    def __init__(self, server: str, port: int = 389, username: str = None, 
                 password: str = None, use_ssl: bool = False, use_tls: bool = False):
        """Initialize LDAP connection."""
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.use_tls = use_tls
        self.connection = None
        self.bound = False
        
        # Build connection string
        if use_ssl:
            self.uri = f"ldaps://{server}:{port}"
        else:
            self.uri = f"ldap://{server}:{port}"
    
    def connect(self) -> Dict[str, Any]:
        """Establish connection to LDAP server."""
        try:
            if not LDAP_AVAILABLE:
                return {"status": "error", "message": "LDAP library not available"}
            
            # Create LDAP connection
            self.connection = ldap.initialize(self.uri)
            
            # Set connection options
            self.connection.set_option(ldap.OPT_NETWORK_TIMEOUT, 10)
            self.connection.set_option(ldap.OPT_TIMEOUT, 10)
            self.connection.set_option(ldap.OPT_REFERRALS, 0)
            
            # Use TLS if specified
            if self.use_tls:
                self.connection.start_tls_s()
            
            # Bind if credentials provided
            if self.username and self.password:
                result = self.bind(self.username, self.password)
                if result["status"] != "success":
                    return result
            
            Output.Console("LDAPConnection", f"Connected to {self.uri}")
            
            return {
                "status": "success",
                "message": f"Connected to {self.uri}",
                "uri": self.uri,
                "bound": self.bound
            }
            
        except LDAPError as e:
            error_msg = f"LDAP connection error: {str(e)}"
            Output.Console("LDAPConnection", error_msg)
            return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = f"Connection error: {str(e)}"
            Output.Console("LDAPConnection", error_msg)
            return {"status": "error", "message": error_msg}
    
    def disconnect(self) -> Dict[str, Any]:
        """Disconnect from LDAP server."""
        try:
            if self.connection:
                self.connection.unbind_s()
                self.connection = None
                self.bound = False
                Output.Console("LDAPConnection", "Disconnected from LDAP server")
            
            return {"status": "success", "message": "Disconnected from LDAP server"}
            
        except Exception as e:
            error_msg = f"Disconnection error: {str(e)}"
            Output.Console("LDAPConnection", error_msg)
            return {"status": "error", "message": error_msg}
    
    def bind(self, username: str, password: str) -> Dict[str, Any]:
        """Bind to LDAP with credentials."""
        try:
            if not self.connection:
                return {"status": "error", "message": "No active connection"}
            
            # Perform bind
            self.connection.simple_bind_s(username, password)
            self.bound = True
            self.username = username
            self.password = password
            
            Output.Console("LDAPConnection", f"Successfully bound as {username}")
            
            return {
                "status": "success",
                "message": f"Successfully bound as {username}",
                "username": username
            }
            
        except INVALID_CREDENTIALS:
            error_msg = "Invalid credentials"
            Output.Console("LDAPConnection", error_msg)
            return {"status": "error", "message": error_msg}
        except LDAPError as e:
            error_msg = f"Bind error: {str(e)}"
            Output.Console("LDAPConnection", error_msg)
            return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = f"Unexpected bind error: {str(e)}"
            Output.Console("LDAPConnection", error_msg)
            return {"status": "error", "message": error_msg}
    
    def unbind(self) -> Dict[str, Any]:
        """Unbind from LDAP."""
        try:
            if self.connection and self.bound:
                self.connection.unbind_s()
                self.bound = False
                Output.Console("LDAPConnection", "Successfully unbound")
            
            return {"status": "success", "message": "Successfully unbound"}
            
        except Exception as e:
            error_msg = f"Unbind error: {str(e)}"
            Output.Console("LDAPConnection", error_msg)
            return {"status": "error", "message": error_msg}
    
    def authenticate(self, username: str, password: str, base_dn: str = None) -> Dict[str, Any]:
        """Authenticate user against LDAP."""
        try:
            if not self.connection:
                return {"status": "error", "message": "No active connection"}
            
            # If base_dn is provided, search for user DN
            if base_dn:
                user_dn = self._find_user_dn(username, base_dn)
                if not user_dn:
                    return {"status": "error", "message": f"User '{username}' not found"}
                bind_dn = user_dn
            else:
                bind_dn = username
            
            # Try to bind with user credentials
            result = self.bind(bind_dn, password)
            
            if result["status"] == "success":
                Output.Console("LDAPConnection", f"User '{username}' authenticated successfully")
                return {
                    "status": "success",
                    "message": f"User '{username}' authenticated successfully",
                    "username": username,
                    "user_dn": bind_dn
                }
            else:
                return result
                
        except Exception as e:
            error_msg = f"Authentication error: {str(e)}"
            Output.Console("LDAPConnection", error_msg)
            return {"status": "error", "message": error_msg}
    
    def test_connection(self) -> Dict[str, Any]:
        """Test LDAP connection."""
        try:
            if not self.connection:
                return {"status": "error", "message": "No active connection"}
            
            # Try to search for root DSE
            self.connection.search_s("", ldap.SCOPE_BASE, "(objectClass=*)", ["*"])
            
            Output.Console("LDAPConnection", "Connection test successful")
            
            return {
                "status": "success",
                "message": "Connection test successful",
                "bound": self.bound,
                "uri": self.uri
            }
            
        except Exception as e:
            error_msg = f"Connection test failed: {str(e)}"
            Output.Console("LDAPConnection", error_msg)
            return {"status": "error", "message": error_msg}
    
    def get_schema(self) -> Dict[str, Any]:
        """Get LDAP schema information."""
        try:
            if not self.connection:
                return {"status": "error", "message": "No active connection"}
            
            # Get subschema subentry
            subschema = self.connection.search_s("", ldap.SCOPE_BASE, "(objectClass=*)", ["subschemaSubentry"])
            
            if not subschema:
                return {"status": "error", "message": "Could not retrieve subschema"}
            
            subschema_dn = subschema[0][1].get("subschemaSubentry", [b""])[0].decode()
            
            # Get schema information
            schema_info = self.connection.search_s(subschema_dn, ldap.SCOPE_BASE, "(objectClass=*)", ["*"])
            
            Output.Console("LDAPConnection", "Schema information retrieved successfully")
            
            return {
                "status": "success",
                "message": "Schema information retrieved successfully",
                "subschema_dn": subschema_dn,
                "schema_info": schema_info
            }
            
        except Exception as e:
            error_msg = f"Schema retrieval error: {str(e)}"
            Output.Console("LDAPConnection", error_msg)
            return {"status": "error", "message": error_msg}
    
    def get_base_dn(self) -> Dict[str, Any]:
        """Get base DN information."""
        try:
            if not self.connection:
                return {"status": "error", "message": "No active connection"}
            
            # Get naming contexts
            root_dse = self.connection.search_s("", ldap.SCOPE_BASE, "(objectClass=*)", ["namingContexts"])
            
            if not root_dse:
                return {"status": "error", "message": "Could not retrieve naming contexts"}
            
            naming_contexts = root_dse[0][1].get("namingContexts", [])
            base_dns = [ctx.decode() for ctx in naming_contexts]
            
            Output.Console("LDAPConnection", f"Retrieved {len(base_dns)} base DNs")
            
            return {
                "status": "success",
                "message": f"Retrieved {len(base_dns)} base DNs",
                "base_dns": base_dns,
                "count": len(base_dns)
            }
            
        except Exception as e:
            error_msg = f"Base DN retrieval error: {str(e)}"
            Output.Console("LDAPConnection", error_msg)
            return {"status": "error", "message": error_msg}
    
    def is_connected(self) -> bool:
        """Check if connection is active."""
        return self.connection is not None
    
    def _find_user_dn(self, username: str, base_dn: str) -> Optional[str]:
        """Find user DN by username."""
        try:
            # Search for user
            filter_str = f"(uid={username})"
            result = self.connection.search_s(base_dn, ldap.SCOPE_SUBTREE, filter_str, ["dn"])
            
            if result:
                return result[0][0]
            
            return None
            
        except Exception as e:
            Output.Console("LDAPConnection", f"Error finding user DN: {str(e)}")
            return None