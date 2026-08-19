"""
LDAP Search Component
====================

Handles LDAP search operations and query functionality.
"""

from typing import Any, Dict, List, Optional
import ldap

from Sugar.Lang.Utils.Output import Output

class LDAPSearch:
    """LDAP search operations handler."""
    
    def __init__(self, plugin):
        """Initialize LDAP search component."""
        self.plugin = plugin
    
    def search(self, connection, base_dn: str, search_filter: str, 
               attributes: List[str] = None, scope: str = "subtree") -> Dict[str, Any]:
        """
        Perform LDAP search.
        
        Args:
            connection: LDAP connection object
            base_dn: Base DN for search
            search_filter: LDAP search filter
            attributes: List of attributes to retrieve
            scope: Search scope (base, onelevel, subtree)
            
        Returns:
            Search results dictionary
        """
        try:
            if not connection.is_connected():
                return {"status": "error", "message": "Connection not available"}
            
            # Set default attributes
            if attributes is None:
                attributes = ["*"]
            
            # Convert scope string to LDAP constant
            scope_map = {
                "base": ldap.SCOPE_BASE,
                "onelevel": ldap.SCOPE_ONELEVEL,
                "subtree": ldap.SCOPE_SUBTREE
            }
            ldap_scope = scope_map.get(scope, ldap.SCOPE_SUBTREE)
            
            # Perform search
            results = connection.connection.search_s(
                base_dn, ldap_scope, search_filter, attributes
            )
            
            # Process results
            processed_results = []
            for dn, attrs in results:
                entry = {"dn": dn}
                for attr, values in attrs.items():
                    if len(values) == 1:
                        entry[attr] = values[0].decode() if isinstance(values[0], bytes) else values[0]
                    else:
                        entry[attr] = [v.decode() if isinstance(v, bytes) else v for v in values]
                processed_results.append(entry)
            
            Output.Console("LDAPSearch", f"Search completed with {len(processed_results)} results")
            
            return {
                "status": "success",
                "message": f"Search completed with {len(processed_results)} results",
                "results": processed_results,
                "count": len(processed_results),
                "base_dn": base_dn,
                "search_filter": search_filter,
                "scope": scope
            }
            
        except Exception as e:
            error_msg = f"Search error: {str(e)}"
            Output.Console("LDAPSearch", error_msg)
            return {"status": "error", "message": error_msg}
    
    def search_users(self, connection, base_dn: str, search_filter: str = None,
                    attributes: List[str] = None) -> Dict[str, Any]:
        """
        Search for users in LDAP directory.
        
        Args:
            connection: LDAP connection object
            base_dn: Base DN for search
            search_filter: Custom search filter (optional)
            attributes: List of attributes to retrieve
            
        Returns:
            User search results
        """
        if search_filter is None:
            search_filter = "(objectClass=person)"
        
        if attributes is None:
            attributes = ["cn", "uid", "mail", "sn", "givenName", "objectClass"]
        
        return self.search(connection, base_dn, search_filter, attributes, "subtree")
    
    def search_groups(self, connection, base_dn: str, search_filter: str = None,
                     attributes: List[str] = None) -> Dict[str, Any]:
        """
        Search for groups in LDAP directory.
        
        Args:
            connection: LDAP connection object
            base_dn: Base DN for search
            search_filter: Custom search filter (optional)
            attributes: List of attributes to retrieve
            
        Returns:
            Group search results
        """
        if search_filter is None:
            search_filter = "(objectClass=group)"
        
        if attributes is None:
            attributes = ["cn", "description", "member", "objectClass"]
        
        return self.search(connection, base_dn, search_filter, attributes, "subtree")
    
    def search_computers(self, connection, base_dn: str, search_filter: str = None,
                        attributes: List[str] = None) -> Dict[str, Any]:
        """
        Search for computers in LDAP directory.
        
        Args:
            connection: LDAP connection object
            base_dn: Base DN for search
            search_filter: Custom search filter (optional)
            attributes: List of attributes to retrieve
            
        Returns:
            Computer search results
        """
        if search_filter is None:
            search_filter = "(objectClass=computer)"
        
        if attributes is None:
            attributes = ["cn", "dNSHostName", "operatingSystem", "objectClass"]
        
        return self.search(connection, base_dn, search_filter, attributes, "subtree")
    
    def search_by_uid(self, connection, base_dn: str, uid: str,
                     attributes: List[str] = None) -> Dict[str, Any]:
        """
        Search for user by UID.
        
        Args:
            connection: LDAP connection object
            base_dn: Base DN for search
            uid: User ID to search for
            attributes: List of attributes to retrieve
            
        Returns:
            User search results
        """
        search_filter = f"(uid={uid})"
        return self.search_users(connection, base_dn, search_filter, attributes)
    
    def search_by_email(self, connection, base_dn: str, email: str,
                       attributes: List[str] = None) -> Dict[str, Any]:
        """
        Search for user by email address.
        
        Args:
            connection: LDAP connection object
            base_dn: Base DN for search
            email: Email address to search for
            attributes: List of attributes to retrieve
            
        Returns:
            User search results
        """
        search_filter = f"(mail={email})"
        return self.search_users(connection, base_dn, search_filter, attributes)
    
    def search_by_group_name(self, connection, base_dn: str, group_name: str,
                            attributes: List[str] = None) -> Dict[str, Any]:
        """
        Search for group by name.
        
        Args:
            connection: LDAP connection object
            base_dn: Base DN for search
            group_name: Group name to search for
            attributes: List of attributes to retrieve
            
        Returns:
            Group search results
        """
        search_filter = f"(cn={group_name})"
        return self.search_groups(connection, base_dn, search_filter, attributes)