"""
LDAP Group Management Component
==============================

Handles LDAP group management operations.
"""

from typing import Any, Dict, List, Optional
import ldap
import ldap.modlist

from Sugar.Lang.Utils.Output import Output

class LDAPGroupManagement:
    """LDAP group management operations handler."""
    
    def __init__(self, plugin):
        """Initialize LDAP group management component."""
        self.plugin = plugin
    
    def create_group(self, connection, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new group in LDAP directory.
        
        Args:
            connection: LDAP connection object
            config: Configuration containing group details
            
        Returns:
            Creation result dictionary
        """
        try:
            if not connection.is_connected():
                return {"status": "error", "message": "Connection not available"}
            
            # Extract group details from config
            group_dn = config.get("group_dn")
            cn = config.get("cn")
            description = config.get("description", "")
            group_type = config.get("group_type", "posixGroup")
            
            if not all([group_dn, cn]):
                return {"status": "error", "message": "Missing required group attributes"}
            
            # Prepare group attributes based on type
            if group_type == "posixGroup":
                attrs = {
                    "objectClass": ["top", "posixGroup"],
                    "cn": [cn],
                    "gidNumber": [config.get("gid_number", "1000")],
                    "description": [description] if description else []
                }
            else:  # groupOfNames or groupOfUniqueNames
                attrs = {
                    "objectClass": ["top", group_type],
                    "cn": [cn],
                    "description": [description] if description else [],
                    "member": config.get("members", [])
                }
            
            # Create group entry
            ldif = ldap.modlist.addModlist(attrs)
            connection.connection.add_s(group_dn, ldif)
            
            Output.Console("LDAPGroupManagement", f"Group '{cn}' created successfully")
            
            return {
                "status": "success",
                "message": f"Group '{cn}' created successfully",
                "group_dn": group_dn,
                "cn": cn,
                "group_type": group_type
            }
            
        except Exception as e:
            error_msg = f"Group creation error: {str(e)}"
            Output.Console("LDAPGroupManagement", error_msg)
            return {"status": "error", "message": error_msg}
    
    def modify_group(self, connection, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modify group attributes in LDAP directory.
        
        Args:
            connection: LDAP connection object
            config: Configuration containing modification details
            
        Returns:
            Modification result dictionary
        """
        try:
            if not connection.is_connected():
                return {"status": "error", "message": "Connection not available"}
            
            group_dn = config.get("group_dn")
            modifications = config.get("modifications", {})
            
            if not group_dn or not modifications:
                return {"status": "error", "message": "Group DN and modifications required"}
            
            # Prepare modifications
            mod_list = []
            for attr, values in modifications.items():
                if isinstance(values, list):
                    mod_list.append((ldap.MOD_REPLACE, attr, values))
                else:
                    mod_list.append((ldap.MOD_REPLACE, attr, [values]))
            
            # Apply modifications
            connection.connection.modify_s(group_dn, mod_list)
            
            Output.Console("LDAPGroupManagement", f"Group '{group_dn}' modified successfully")
            
            return {
                "status": "success",
                "message": f"Group '{group_dn}' modified successfully",
                "group_dn": group_dn,
                "modifications": modifications
            }
            
        except Exception as e:
            error_msg = f"Group modification error: {str(e)}"
            Output.Console("LDAPGroupManagement", error_msg)
            return {"status": "error", "message": error_msg}
    
    def delete_group(self, connection, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete a group from LDAP directory.
        
        Args:
            connection: LDAP connection object
            config: Configuration containing group details
            
        Returns:
            Deletion result dictionary
        """
        try:
            if not connection.is_connected():
                return {"status": "error", "message": "Connection not available"}
            
            group_dn = config.get("group_dn")
            
            if not group_dn:
                return {"status": "error", "message": "Group DN required"}
            
            # Delete group entry
            connection.connection.delete_s(group_dn)
            
            Output.Console("LDAPGroupManagement", f"Group '{group_dn}' deleted successfully")
            
            return {
                "status": "success",
                "message": f"Group '{group_dn}' deleted successfully",
                "group_dn": group_dn
            }
            
        except Exception as e:
            error_msg = f"Group deletion error: {str(e)}"
            Output.Console("LDAPGroupManagement", error_msg)
            return {"status": "error", "message": error_msg}
    
    def add_user_to_group(self, connection, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a user to a group.
        
        Args:
            connection: LDAP connection object
            config: Configuration containing user and group details
            
        Returns:
            Add user result dictionary
        """
        try:
            if not connection.is_connected():
                return {"status": "error", "message": "Connection not available"}
            
            group_dn = config.get("group_dn")
            user_dn = config.get("user_dn")
            
            if not group_dn or not user_dn:
                return {"status": "error", "message": "Group DN and User DN required"}
            
            # Add user to group
            mod_list = [(ldap.MOD_ADD, "member", [user_dn.encode()])]
            connection.connection.modify_s(group_dn, mod_list)
            
            Output.Console("LDAPGroupManagement", f"User '{user_dn}' added to group '{group_dn}'")
            
            return {
                "status": "success",
                "message": f"User '{user_dn}' added to group '{group_dn}'",
                "group_dn": group_dn,
                "user_dn": user_dn
            }
            
        except Exception as e:
            error_msg = f"Add user to group error: {str(e)}"
            Output.Console("LDAPGroupManagement", error_msg)
            return {"status": "error", "message": error_msg}
    
    def remove_user_from_group(self, connection, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove a user from a group.
        
        Args:
            connection: LDAP connection object
            config: Configuration containing user and group details
            
        Returns:
            Remove user result dictionary
        """
        try:
            if not connection.is_connected():
                return {"status": "error", "message": "Connection not available"}
            
            group_dn = config.get("group_dn")
            user_dn = config.get("user_dn")
            
            if not group_dn or not user_dn:
                return {"status": "error", "message": "Group DN and User DN required"}
            
            # Remove user from group
            mod_list = [(ldap.MOD_DELETE, "member", [user_dn.encode()])]
            connection.connection.modify_s(group_dn, mod_list)
            
            Output.Console("LDAPGroupManagement", f"User '{user_dn}' removed from group '{group_dn}'")
            
            return {
                "status": "success",
                "message": f"User '{user_dn}' removed from group '{group_dn}'",
                "group_dn": group_dn,
                "user_dn": user_dn
            }
            
        except Exception as e:
            error_msg = f"Remove user from group error: {str(e)}"
            Output.Console("LDAPGroupManagement", error_msg)
            return {"status": "error", "message": error_msg}
    
    def get_group_info(self, connection, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get group information.
        
        Args:
            connection: LDAP connection object
            config: Configuration containing group details
            
        Returns:
            Group information dictionary
        """
        try:
            if not connection.is_connected():
                return {"status": "error", "message": "Connection not available"}
            
            group_dn = config.get("group_dn")
            attributes = config.get("attributes", ["*"])
            
            if not group_dn:
                return {"status": "error", "message": "Group DN required"}
            
            # Search for group
            result = connection.connection.search_s(
                group_dn, ldap.SCOPE_BASE, "(objectClass=*)", attributes
            )
            
            if not result:
                return {"status": "error", "message": f"Group '{group_dn}' not found"}
            
            # Process group attributes
            group_info = {"dn": result[0][0]}
            for attr, values in result[0][1].items():
                if len(values) == 1:
                    group_info[attr] = values[0].decode() if isinstance(values[0], bytes) else values[0]
                else:
                    group_info[attr] = [v.decode() if isinstance(v, bytes) else v for v in values]
            
            Output.Console("LDAPGroupManagement", f"Retrieved info for group '{group_dn}'")
            
            return {
                "status": "success",
                "message": f"Retrieved info for group '{group_dn}'",
                "group_info": group_info
            }
            
        except Exception as e:
            error_msg = f"Get group info error: {str(e)}"
            Output.Console("LDAPGroupManagement", error_msg)
            return {"status": "error", "message": error_msg}
    
    def list_groups(self, connection, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        List all groups in a directory.
        
        Args:
            connection: LDAP connection object
            config: Configuration containing search parameters
            
        Returns:
            Group list dictionary
        """
        try:
            if not connection.is_connected():
                return {"status": "error", "message": "Connection not available"}
            
            base_dn = config.get("base_dn")
            search_filter = config.get("search_filter", "(objectClass=group)")
            attributes = config.get("attributes", ["cn", "description", "member"])
            
            if not base_dn:
                return {"status": "error", "message": "Base DN required"}
            
            # Use search component to find groups
            return self.plugin.search.search_groups(
                connection=connection,
                base_dn=base_dn,
                search_filter=search_filter,
                attributes=attributes
            )
            
        except Exception as e:
            error_msg = f"List groups error: {str(e)}"
            Output.Console("LDAPGroupManagement", error_msg)
            return {"status": "error", "message": error_msg}
    
    def get_group_members(self, connection, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get all members of a group.
        
        Args:
            connection: LDAP connection object
            config: Configuration containing group details
            
        Returns:
            Group members dictionary
        """
        try:
            if not connection.is_connected():
                return {"status": "error", "message": "Connection not available"}
            
            group_dn = config.get("group_dn")
            
            if not group_dn:
                return {"status": "error", "message": "Group DN required"}
            
            # Get group info with member attribute
            result = connection.connection.search_s(
                group_dn, ldap.SCOPE_BASE, "(objectClass=*)", ["member", "cn"]
            )
            
            if not result:
                return {"status": "error", "message": f"Group '{group_dn}' not found"}
            
            # Extract members
            members = []
            if "member" in result[0][1]:
                for member_dn in result[0][1]["member"]:
                    members.append(member_dn.decode() if isinstance(member_dn, bytes) else member_dn)
            
            group_name = result[0][1].get("cn", [b""])[0].decode() if result[0][1].get("cn") else "Unknown"
            
            Output.Console("LDAPGroupManagement", f"Retrieved {len(members)} members for group '{group_name}'")
            
            return {
                "status": "success",
                "message": f"Retrieved {len(members)} members for group '{group_name}'",
                "group_dn": group_dn,
                "group_name": group_name,
                "members": members,
                "member_count": len(members)
            }
            
        except Exception as e:
            error_msg = f"Get group members error: {str(e)}"
            Output.Console("LDAPGroupManagement", error_msg)
            return {"status": "error", "message": error_msg}
    
    def is_user_in_group(self, connection, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if a user is a member of a group.
        
        Args:
            connection: LDAP connection object
            config: Configuration containing user and group details
            
        Returns:
            Membership check result dictionary
        """
        try:
            if not connection.is_connected():
                return {"status": "error", "message": "Connection not available"}
            
            group_dn = config.get("group_dn")
            user_dn = config.get("user_dn")
            
            if not group_dn or not user_dn:
                return {"status": "error", "message": "Group DN and User DN required"}
            
            # Get group members
            members_result = self.get_group_members(connection, {"group_dn": group_dn})
            
            if members_result["status"] != "success":
                return members_result
            
            # Check if user is in members list
            members = members_result.get("members", [])
            is_member = user_dn in members
            
            return {
                "status": "success",
                "message": f"User membership check completed",
                "group_dn": group_dn,
                "user_dn": user_dn,
                "is_member": is_member
            }
            
        except Exception as e:
            error_msg = f"Check user membership error: {str(e)}"
            Output.Console("LDAPGroupManagement", error_msg)
            return {"status": "error", "message": error_msg}