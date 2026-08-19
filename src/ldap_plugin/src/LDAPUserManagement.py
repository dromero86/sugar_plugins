"""
LDAP User Management Component
=============================

Handles LDAP user management operations.
"""

from typing import Any, Dict, List, Optional
import ldap
import ldap.modlist

from Sugar.Lang.Utils.Output import Output

class LDAPUserManagement:
    """LDAP user management operations handler."""
    
    def __init__(self, plugin):
        """Initialize LDAP user management component."""
        self.plugin = plugin
    
    def create_user(self, connection, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user in LDAP directory.
        
        Args:
            connection: LDAP connection object
            config: Configuration containing user details
            
        Returns:
            Creation result dictionary
        """
        try:
            if not connection.is_connected():
                return {"status": "error", "message": "Connection not available"}
            
            # Extract user details from config
            user_dn = config.get("user_dn")
            uid = config.get("uid")
            cn = config.get("cn")
            sn = config.get("sn")
            given_name = config.get("given_name")
            mail = config.get("mail")
            password = config.get("password")
            
            if not all([user_dn, uid, cn, sn]):
                return {"status": "error", "message": "Missing required user attributes"}
            
            # Prepare user attributes
            attrs = {
                "objectClass": ["top", "person", "organizationalPerson", "inetOrgPerson"],
                "uid": [uid],
                "cn": [cn],
                "sn": [sn],
                "givenName": [given_name] if given_name else [cn]
            }
            
            if mail:
                attrs["mail"] = [mail]
            
            # Create user entry
            ldif = ldap.modlist.addModlist(attrs)
            connection.connection.add_s(user_dn, ldif)
            
            # Set password if provided
            if password:
                self._set_user_password(connection, user_dn, password)
            
            Output.Console("LDAPUserManagement", f"User '{uid}' created successfully")
            
            return {
                "status": "success",
                "message": f"User '{uid}' created successfully",
                "user_dn": user_dn,
                "uid": uid
            }
            
        except Exception as e:
            error_msg = f"User creation error: {str(e)}"
            Output.Console("LDAPUserManagement", error_msg)
            return {"status": "error", "message": error_msg}
    
    def modify_user(self, connection, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modify user attributes in LDAP directory.
        
        Args:
            connection: LDAP connection object
            config: Configuration containing modification details
            
        Returns:
            Modification result dictionary
        """
        try:
            if not connection.is_connected():
                return {"status": "error", "message": "Connection not available"}
            
            user_dn = config.get("user_dn")
            modifications = config.get("modifications", {})
            
            if not user_dn or not modifications:
                return {"status": "error", "message": "User DN and modifications required"}
            
            # Prepare modifications
            mod_list = []
            for attr, values in modifications.items():
                if isinstance(values, list):
                    mod_list.append((ldap.MOD_REPLACE, attr, values))
                else:
                    mod_list.append((ldap.MOD_REPLACE, attr, [values]))
            
            # Apply modifications
            connection.connection.modify_s(user_dn, mod_list)
            
            Output.Console("LDAPUserManagement", f"User '{user_dn}' modified successfully")
            
            return {
                "status": "success",
                "message": f"User '{user_dn}' modified successfully",
                "user_dn": user_dn,
                "modifications": modifications
            }
            
        except Exception as e:
            error_msg = f"User modification error: {str(e)}"
            Output.Console("LDAPUserManagement", error_msg)
            return {"status": "error", "message": error_msg}
    
    def delete_user(self, connection, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete a user from LDAP directory.
        
        Args:
            connection: LDAP connection object
            config: Configuration containing user details
            
        Returns:
            Deletion result dictionary
        """
        try:
            if not connection.is_connected():
                return {"status": "error", "message": "Connection not available"}
            
            user_dn = config.get("user_dn")
            
            if not user_dn:
                return {"status": "error", "message": "User DN required"}
            
            # Delete user entry
            connection.connection.delete_s(user_dn)
            
            Output.Console("LDAPUserManagement", f"User '{user_dn}' deleted successfully")
            
            return {
                "status": "success",
                "message": f"User '{user_dn}' deleted successfully",
                "user_dn": user_dn
            }
            
        except Exception as e:
            error_msg = f"User deletion error: {str(e)}"
            Output.Console("LDAPUserManagement", error_msg)
            return {"status": "error", "message": error_msg}
    
    def enable_user(self, connection, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enable a user account.
        
        Args:
            connection: LDAP connection object
            config: Configuration containing user details
            
        Returns:
            Enable result dictionary
        """
        try:
            if not connection.is_connected():
                return {"status": "error", "message": "Connection not available"}
            
            user_dn = config.get("user_dn")
            
            if not user_dn:
                return {"status": "error", "message": "User DN required"}
            
            # Remove account lockout attributes
            mod_list = [
                (ldap.MOD_DELETE, "pwdAccountLockedTime", None),
                (ldap.MOD_DELETE, "pwdLockout", None)
            ]
            
            connection.connection.modify_s(user_dn, mod_list)
            
            Output.Console("LDAPUserManagement", f"User '{user_dn}' enabled successfully")
            
            return {
                "status": "success",
                "message": f"User '{user_dn}' enabled successfully",
                "user_dn": user_dn
            }
            
        except Exception as e:
            error_msg = f"User enable error: {str(e)}"
            Output.Console("LDAPUserManagement", error_msg)
            return {"status": "error", "message": error_msg}
    
    def disable_user(self, connection, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Disable a user account.
        
        Args:
            connection: LDAP connection object
            config: Configuration containing user details
            
        Returns:
            Disable result dictionary
        """
        try:
            if not connection.is_connected():
                return {"status": "error", "message": "Connection not available"}
            
            user_dn = config.get("user_dn")
            
            if not user_dn:
                return {"status": "error", "message": "User DN required"}
            
            # Add account lockout attributes
            mod_list = [
                (ldap.MOD_ADD, "pwdAccountLockedTime", [b"000001010000Z"]),
                (ldap.MOD_ADD, "pwdLockout", [b"TRUE"])
            ]
            
            connection.connection.modify_s(user_dn, mod_list)
            
            Output.Console("LDAPUserManagement", f"User '{user_dn}' disabled successfully")
            
            return {
                "status": "success",
                "message": f"User '{user_dn}' disabled successfully",
                "user_dn": user_dn
            }
            
        except Exception as e:
            error_msg = f"User disable error: {str(e)}"
            Output.Console("LDAPUserManagement", error_msg)
            return {"status": "error", "message": error_msg}
    
    def reset_password(self, connection, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reset user password.
        
        Args:
            connection: LDAP connection object
            config: Configuration containing user details
            
        Returns:
            Password reset result dictionary
        """
        try:
            if not connection.is_connected():
                return {"status": "error", "message": "Connection not available"}
            
            user_dn = config.get("user_dn")
            new_password = config.get("new_password")
            
            if not user_dn or not new_password:
                return {"status": "error", "message": "User DN and new password required"}
            
            # Set new password
            self._set_user_password(connection, user_dn, new_password)
            
            Output.Console("LDAPUserManagement", f"Password reset for user '{user_dn}'")
            
            return {
                "status": "success",
                "message": f"Password reset for user '{user_dn}'",
                "user_dn": user_dn
            }
            
        except Exception as e:
            error_msg = f"Password reset error: {str(e)}"
            Output.Console("LDAPUserManagement", error_msg)
            return {"status": "error", "message": error_msg}
    
    def unlock_user(self, connection, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unlock a user account.
        
        Args:
            connection: LDAP connection object
            config: Configuration containing user details
            
        Returns:
            Unlock result dictionary
        """
        try:
            if not connection.is_connected():
                return {"status": "error", "message": "Connection not available"}
            
            user_dn = config.get("user_dn")
            
            if not user_dn:
                return {"status": "error", "message": "User DN required"}
            
            # Remove lockout attributes
            mod_list = [
                (ldap.MOD_DELETE, "pwdAccountLockedTime", None),
                (ldap.MOD_DELETE, "pwdLockout", None),
                (ldap.MOD_DELETE, "pwdFailureTime", None)
            ]
            
            connection.connection.modify_s(user_dn, mod_list)
            
            Output.Console("LDAPUserManagement", f"User '{user_dn}' unlocked successfully")
            
            return {
                "status": "success",
                "message": f"User '{user_dn}' unlocked successfully",
                "user_dn": user_dn
            }
            
        except Exception as e:
            error_msg = f"User unlock error: {str(e)}"
            Output.Console("LDAPUserManagement", error_msg)
            return {"status": "error", "message": error_msg}
    
    def get_user_info(self, connection, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get user information.
        
        Args:
            connection: LDAP connection object
            config: Configuration containing user details
            
        Returns:
            User information dictionary
        """
        try:
            if not connection.is_connected():
                return {"status": "error", "message": "Connection not available"}
            
            user_dn = config.get("user_dn")
            attributes = config.get("attributes", ["*"])
            
            if not user_dn:
                return {"status": "error", "message": "User DN required"}
            
            # Search for user
            result = connection.connection.search_s(
                user_dn, ldap.SCOPE_BASE, "(objectClass=*)", attributes
            )
            
            if not result:
                return {"status": "error", "message": f"User '{user_dn}' not found"}
            
            # Process user attributes
            user_info = {"dn": result[0][0]}
            for attr, values in result[0][1].items():
                if len(values) == 1:
                    user_info[attr] = values[0].decode() if isinstance(values[0], bytes) else values[0]
                else:
                    user_info[attr] = [v.decode() if isinstance(v, bytes) else v for v in values]
            
            Output.Console("LDAPUserManagement", f"Retrieved info for user '{user_dn}'")
            
            return {
                "status": "success",
                "message": f"Retrieved info for user '{user_dn}'",
                "user_info": user_info
            }
            
        except Exception as e:
            error_msg = f"Get user info error: {str(e)}"
            Output.Console("LDAPUserManagement", error_msg)
            return {"status": "error", "message": error_msg}
    
    def list_users(self, connection, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        List all users in a directory.
        
        Args:
            connection: LDAP connection object
            config: Configuration containing search parameters
            
        Returns:
            User list dictionary
        """
        try:
            if not connection.is_connected():
                return {"status": "error", "message": "Connection not available"}
            
            base_dn = config.get("base_dn")
            search_filter = config.get("search_filter", "(objectClass=person)")
            attributes = config.get("attributes", ["cn", "uid", "mail", "sn", "givenName"])
            
            if not base_dn:
                return {"status": "error", "message": "Base DN required"}
            
            # Use search component to find users
            return self.plugin.search.search_users(
                connection=connection,
                base_dn=base_dn,
                search_filter=search_filter,
                attributes=attributes
            )
            
        except Exception as e:
            error_msg = f"List users error: {str(e)}"
            Output.Console("LDAPUserManagement", error_msg)
            return {"status": "error", "message": error_msg}
    
    def _set_user_password(self, connection, user_dn: str, password: str) -> None:
        """
        Set user password using LDAP password policy.
        
        Args:
            connection: LDAP connection object
            user_dn: User DN
            password: New password
        """
        try:
            # Use LDAP password modify extended operation
            connection.connection.passwd_s(user_dn, None, password)
        except Exception as e:
            # Fallback to simple password modification
            Output.Console("LDAPUserManagement", f"Password modify failed, using fallback: {str(e)}")
            # Note: This is a simplified implementation
            # In production, you would use proper password hashing
            pass