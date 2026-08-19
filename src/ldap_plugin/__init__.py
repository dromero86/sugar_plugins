"""
LDAP Plugin for Sugar
====================

Lightweight Directory Access Protocol (LDAP) plugin for Sugar.
Provides directory service operations, user authentication, and group management.
"""

from .src.LDAPPlugin import LDAPPlugin

__version__ = "1.0.0"
__author__ = "Sugar Team"
__license__ = "MIT"

# Export the main plugin class
__all__ = ["LDAPPlugin"]