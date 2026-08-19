"""
GnuPG Plugin for Sugar Language v2.0.0
========================================

A comprehensive GnuPG plugin that provides cryptographic operations
including key management, encryption/decryption, digital signatures,
and more.
"""

from .src.GnuPGPlugin import GnuPGPlugin

__version__ = "1.0.0"
__author__ = "Sugar Team"
__license__ = "MIT"

# Export the main plugin class
__all__ = ["GnuPGPlugin"]