"""
SMB Plugin for Sugar
===================

A comprehensive SMB/CIFS plugin that provides file and directory operations
over SMB protocol with support for SMB2/SMB3, authentication, encryption,
and advanced features like parallel transfers and automatic failover.
"""

from .src.SMBPlugin import SMBPlugin

__version__ = "1.0.0"
__author__ = "Sugar Team"
__description__ = "Comprehensive SMB/CIFS operations for Sugar"

# Plugin class for Sugar to load
Plugin = SMBPlugin