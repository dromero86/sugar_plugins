"""
GnuPG Plugin for Sugar Language v2.0.0
========================================

A comprehensive GnuPG plugin that provides cryptographic operations
including key management, encryption/decryption, digital signatures,
and more.
"""

import os
import subprocess
import tempfile
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output

from .GnuPGKeyManager import GnuPGKeyManager
from .GnuPGEncryption import GnuPGEncryption
from .GnuPGSigning import GnuPGSigning
from .GnuPGUtils import GnuPGUtils

class GnuPGPlugin(PluginBase):
    """
    GnuPG plugin for Sugar.
    
    Provides comprehensive cryptographic operations including:
    - Key generation and management (RSA, DSA, ECDSA, EDDSA)
    - Encryption/decryption (symmetric and asymmetric)
    - Digital signatures and verification
    - Key import/export
    - Trust management
    - Certificate operations
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Comprehensive GnuPG cryptographic operations for Sugar"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    
    # Dependencias del sistema (GnuPG CLI)
    SYSTEM_DEPENDENCIES = ["gpg"]
    
    # Dependencias de Python (opcional, para funcionalidad avanzada)
    DEPENDENCIES = ["python-gnupg"]
    REQUIREMENTS = ["python-gnupg>=0.5.0"]
    
    # Requerimientos de hardware
    HARDWARE_REQUIREMENTS = {
        "min_ram_gb": 1,
        "min_disk_gb": 0.1,
        "min_cpu_cores": 1
    }
    
    # Requerimientos de permisos
    PERMISSION_REQUIREMENTS = {
        "network_access": False,  # Opcional para keyservers
        "write_access": ["~/.gnupg", "/tmp"],
        "read_access": ["~/.gnupg", "./"]
    }
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """Initialize the GnuPG plugin."""
        super().__init__(context, plugin_config)
        
        # Verificar dependencias al inicializar
        self.dependency_status = self._check_all_dependencies()
        
        # Alertar si hay dependencias faltantes
        if not self.dependency_status['all_satisfied']:
            self._log_dependency_warnings()
        
        # Inicializar componentes
        self._initialize_components()
    
    def _check_all_dependencies(self) -> Dict[str, Any]:
        """Check all dependencies including system and Python packages."""
        status = {
            'system_dependencies': self._check_system_dependencies(),
            'python_dependencies': self._check_python_dependencies(),
            'hardware_requirements': self._check_hardware_requirements(),
            'permission_requirements': self._check_permission_requirements(),
            'all_satisfied': True
        }
        
        # Check if all dependencies are satisfied
        for category, result in status.items():
            if category != 'all_satisfied' and not result.get('satisfied', True):
                status['all_satisfied'] = False
        
        return status
    
    def _check_system_dependencies(self) -> Dict[str, Any]:
        """Check if GnuPG is available in the system."""
        gpg_path = self._find_gpg()
        version = None
        
        if gpg_path:
            try:
                result = subprocess.run([gpg_path, '--version'], 
                                      capture_output=True, text=True, check=True)
                version = result.stdout.split('\n')[0]
            except subprocess.CalledProcessError:
                pass
        
        return {
            'satisfied': gpg_path is not None,
            'gpg': {
                'available': gpg_path is not None,
                'path': gpg_path,
                'version': version
            }
        }
    
    def _check_python_dependencies(self) -> Dict[str, Any]:
        """Check Python package dependencies."""
        try:
            import gnupg
            return {
                'satisfied': True,
                'python-gnupg': {
                    'available': True,
                    'version': gnupg.__version__ if hasattr(gnupg, '__version__') else 'unknown'
                }
            }
        except ImportError:
            return {
                'satisfied': False,
                'python-gnupg': {
                    'available': False,
                    'version': None
                }
            }
    
    def _check_hardware_requirements(self) -> Dict[str, Any]:
        """Check hardware requirements."""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'satisfied': True,
                'memory': {
                    'available_gb': memory.total / (1024**3),
                    'required_gb': self.HARDWARE_REQUIREMENTS['min_ram_gb']
                },
                'disk': {
                    'available_gb': disk.free / (1024**3),
                    'required_gb': self.HARDWARE_REQUIREMENTS['min_disk_gb']
                },
                'cpu_cores': psutil.cpu_count()
            }
        except ImportError:
            # psutil not available, assume requirements are met
            return {
                'satisfied': True,
                'note': 'psutil not available, hardware check skipped'
            }
    
    def _check_permission_requirements(self) -> Dict[str, Any]:
        """Check permission requirements."""
        home_dir = os.path.expanduser('~')
        gnupg_dir = os.path.join(home_dir, '.gnupg')
        
        return {
            'satisfied': True,
            'gnupg_dir': {
                'exists': os.path.exists(gnupg_dir),
                'writable': os.access(gnupg_dir, os.W_OK) if os.path.exists(gnupg_dir) else False
            },
            'tmp_dir': {
                'writable': os.access('/tmp', os.W_OK)
            }
        }
    
    def _find_gpg(self) -> Optional[str]:
        """Find GnuPG executable in PATH."""
        try:
            result = subprocess.run(['which', 'gpg'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    def _log_dependency_warnings(self):
        """Log warnings for missing dependencies."""
        Output.Console(self.plugin_name, "Warning: Some dependencies are not satisfied")
        Output.Console(self.plugin_name, "Installation instructions:")
        Output.Console(self.plugin_name, "  Ubuntu/Debian: sudo apt-get install gnupg")
        Output.Console(self.plugin_name, "  CentOS/RHEL: sudo yum install gnupg")
        Output.Console(self.plugin_name, "  macOS: brew install gnupg")
        Output.Console(self.plugin_name, "  Windows: Download from https://gnupg.org/download/")
        Output.Console(self.plugin_name, "  Python: pip install python-gnupg")
    
    def _initialize_components(self):
        """Initialize plugin components."""
        self.key_manager = GnuPGKeyManager(self)
        self.encryption = GnuPGEncryption(self)
        self.signing = GnuPGSigning(self)
        self.utils = GnuPGUtils(self)
        
        Output.Console(self.plugin_name, "GnuPG plugin components initialized")
    
    def get_available_commands(self) -> List[str]:
        """Get list of available commands."""
        return [
            # Key management
            "generate_key", "list_keys", "import_key", "export_key", "delete_key",
            "edit_key", "sign_key", "revoke_key", "trust_key",
            
            # Encryption/Decryption
            "encrypt_file", "decrypt_file", "encrypt_text", "decrypt_text",
            "symmetric_encrypt", "symmetric_decrypt",
            
            # Signing/Verification
            "sign_file", "verify_signature", "clearsign", "detached_sign",
            "sign_text", "verify_text",
            
            # Utility
            "check_dependencies", "system_info", "test_functionality",
            "configure_agent", "check_agent_status"
        ]
    
    def execute(self, operator: str, config: Dict[str, Any]) -> Any:
        """Execute a GnuPG operator."""
        # Verificar dependencias antes de comandos críticos
        if operator in ["generate_key", "encrypt_file", "decrypt_file", "sign_file"]:
            if not self.dependency_status['all_satisfied']:
                raise RuntimeError("Dependencies not satisfied. Please install GnuPG and required packages.")
        
        try:
            # Key management commands
            if operator in ["generate_key", "list_keys", "import_key", "export_key", 
                          "delete_key", "edit_key", "sign_key", "revoke_key", "trust_key"]:
                return self.key_manager.execute(operator, config)
            
            # Encryption/Decryption commands
            elif operator in ["encrypt_file", "decrypt_file", "encrypt_text", "decrypt_text",
                           "symmetric_encrypt", "symmetric_decrypt"]:
                return self.encryption.execute(operator, config)
            
            # Signing/Verification commands
            elif operator in ["sign_file", "verify_signature", "clearsign", "detached_sign",
                           "sign_text", "verify_text"]:
                return self.signing.execute(operator, config)
            
            # Utility commands
            elif operator in ["check_dependencies", "system_info", "test_functionality",
                           "configure_agent", "check_agent_status"]:
                return self.utils.execute(operator, config)
            
            else:
                raise ValueError(f"Unknown operator: {operator}")
                
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing operator '{operator}': {str(e)}")
            raise