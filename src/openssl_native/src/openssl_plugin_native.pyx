# cython: language_level=3
# distutils: language=c++

"""
OpenSSL Native Plugin (Cython)
=============================

A native OpenSSL plugin compiled with Cython for high performance.
"""

import os
import subprocess
import json
from typing import Dict, List, Any, Optional
import platform

# Cython imports
cimport cython
from cpython cimport dict, list, str
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map

# Plugin metadata
VERSION = "1.0.0"
DESCRIPTION = "High-performance OpenSSL operations"
AUTHOR = "Sugar Team"
LICENSE = "MIT"
DEPENDENCIES = ["openssl"]
REQUIREMENTS = []


cdef class OpenSSLNativePlugin:
    """High-performance OpenSSL plugin implemented in Cython."""
    
    cdef:
        str openssl_path
        str plugin_name
        dict _cache
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        self.openssl_path = self._find_openssl()
        self.plugin_name = "openssl_native"
        self._cache = {}
    
    cdef str _find_openssl(self):
        """Find OpenSSL executable using Cython for speed."""
        cdef:
            list possible_paths = ["openssl", "/usr/bin/openssl", "/usr/local/bin/openssl"]
            str path
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, 'version'], 
                                      capture_output=True, text=True, check=True)
                return path
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        return None
    
    def get_available_commands(self) -> List[str]:
        """Get list of available commands."""
        return [
            "genrsa",
            "genpkey", 
            "req_new",
            "x509_selfsign",
            "verify_cert",
            "convert",
            "encrypt",
            "decrypt",
            "sign",
            "verify",
            "hash",
            "fast_hash",  # Optimized hash function
            "batch_verify"  # Batch certificate verification
        ]
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """Execute an OpenSSL command with Cython optimizations."""
        if not self.openssl_path:
            return {
                'success': False,
                'error': 'OpenSSL not found. Please install OpenSSL.',
                'install_instructions': {
                    'ubuntu_debian': 'sudo apt-get install openssl',
                    'centos_rhel': 'sudo yum install openssl',
                    'fedora': 'sudo dnf install openssl',
                    'macos': 'brew install openssl',
                    'windows': 'Download from https://www.openssl.org/'
                }
            }
        
        try:
            if command == "genrsa":
                return self._genrsa_optimized(config)
            elif command == "genpkey":
                return self._genpkey_optimized(config)
            elif command == "req_new":
                return self._req_new_optimized(config)
            elif command == "x509_selfsign":
                return self._x509_selfsign_optimized(config)
            elif command == "verify_cert":
                return self._verify_cert_optimized(config)
            elif command == "convert":
                return self._convert_optimized(config)
            elif command == "encrypt":
                return self._encrypt_optimized(config)
            elif command == "decrypt":
                return self._decrypt_optimized(config)
            elif command == "sign":
                return self._sign_optimized(config)
            elif command == "verify":
                return self._verify_optimized(config)
            elif command == "hash":
                return self._hash_optimized(config)
            elif command == "fast_hash":
                return self._fast_hash_optimized(config)
            elif command == "batch_verify":
                return self._batch_verify_optimized(config)
            else:
                return {
                    'success': False,
                    'error': f'Unknown command: {command}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    cdef dict _run_openssl_command_optimized(self, list args, str input_data=None):
        """Run OpenSSL command with Cython optimizations."""
        cdef:
            dict result = {}
            int returncode
        
        try:
            cmd = [self.openssl_path] + args
            process = subprocess.run(
                cmd,
                input=input_data,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            returncode = process.returncode
            
            result = {
                'success': returncode == 0,
                'stdout': process.stdout,
                'stderr': process.stderr,
                'returncode': returncode
            }
            
        except subprocess.TimeoutExpired:
            result = {
                'success': False,
                'error': 'Command timed out'
            }
        except Exception as e:
            result = {
                'success': False,
                'error': str(e)
            }
        
        return result
    
    cdef dict _genrsa_optimized(self, dict config):
        """Generate RSA private key with optimizations."""
        cdef:
            int key_size = config.get('key_size', 2048)
            str output_file = config.get('output_file', 'private_key.pem')
            str passphrase = config.get('passphrase', '')
            list args = ['genrsa', '-out', output_file, str(key_size)]
        
        if passphrase:
            args.extend(['-aes256', '-passout', f'pass:{passphrase}'])
        
        result = self._run_openssl_command_optimized(args)
        
        if result['success']:
            return {
                'success': True,
                'output_file': output_file,
                'key_size': key_size,
                'message': f'RSA private key generated: {output_file}'
            }
        else:
            return result
    
    cdef dict _genpkey_optimized(self, dict config):
        """Generate private key using modern algorithms."""
        cdef:
            str algorithm = config.get('algorithm', 'rsa')
            int key_size = config.get('key_size', 2048)
            str output_file = config.get('output_file', 'private_key.pem')
            str passphrase = config.get('passphrase', '')
            list args = ['genpkey', '-algorithm', algorithm, '-out', output_file]
        
        if algorithm == 'rsa':
            args.extend(['-pkeyopt', f'rsa_keygen_bits:{key_size}'])
        elif algorithm == 'ec':
            args.extend(['-pkeyopt', 'ec_paramgen_curve:P-256'])
        
        if passphrase:
            args.extend(['-aes256', '-pass', f'pass:{passphrase}'])
        
        result = self._run_openssl_command_optimized(args)
        
        if result['success']:
            return {
                'success': True,
                'output_file': output_file,
                'algorithm': algorithm,
                'key_size': key_size,
                'message': f'{algorithm.upper()} private key generated: {output_file}'
            }
        else:
            return result
    
    cdef dict _req_new_optimized(self, dict config):
        """Create Certificate Signing Request."""
        cdef:
            str key_file = config.get('key_file', '')
            str output_file = config.get('output_file', 'certificate.csr')
            str subject = config.get('subject', '/C=ES/ST=Madrid/L=Madrid/O=MyCompany/CN=example.com')
            str passphrase = config.get('passphrase', '')
            list args = ['req', '-new', '-key', key_file, '-out', output_file, '-subj', subject]
        
        if not key_file:
            return {
                'success': False,
                'error': 'key_file is required'
            }
        
        if passphrase:
            args.extend(['-passin', f'pass:{passphrase}'])
        
        result = self._run_openssl_command_optimized(args)
        
        if result['success']:
            return {
                'success': True,
                'output_file': output_file,
                'subject': subject,
                'message': f'CSR generated: {output_file}'
            }
        else:
            return result
    
    cdef dict _x509_selfsign_optimized(self, dict config):
        """Create self-signed certificate."""
        cdef:
            str csr_file = config.get('csr_file', '')
            str key_file = config.get('key_file', '')
            str output_file = config.get('output_file', 'certificate.crt')
            int days = config.get('days', 365)
            str passphrase = config.get('passphrase', '')
            list args = ['x509', '-req', '-in', csr_file, '-signkey', key_file, 
                        '-out', output_file, '-days', str(days)]
        
        if not csr_file or not key_file:
            return {
                'success': False,
                'error': 'csr_file and key_file are required'
            }
        
        if passphrase:
            args.extend(['-passin', f'pass:{passphrase}'])
        
        result = self._run_openssl_command_optimized(args)
        
        if result['success']:
            return {
                'success': True,
                'output_file': output_file,
                'days': days,
                'message': f'Self-signed certificate generated: {output_file}'
            }
        else:
            return result
    
    cdef dict _verify_cert_optimized(self, dict config):
        """Verify a certificate."""
        cdef:
            str cert_file = config.get('cert_file', '')
            str ca_file = config.get('ca_file', '')
            list args = ['verify']
        
        if not cert_file:
            return {
                'success': False,
                'error': 'cert_file is required'
            }
        
        if ca_file:
            args.extend(['-CAfile', ca_file])
        args.append(cert_file)
        
        result = self._run_openssl_command_optimized(args)
        
        return {
            'success': result['success'],
            'valid': result['success'],
            'output': result['stdout'],
            'error': result['stderr'] if not result['success'] else None
        }
    
    cdef dict _convert_optimized(self, dict config):
        """Convert certificate format."""
        cdef:
            str input_file = config.get('input_file', '')
            str output_file = config.get('output_file', '')
            str input_format = config.get('input_format', 'PEM')
            str output_format = config.get('output_format', 'PEM')
            list args = ['x509', '-in', input_file, '-out', output_file]
        
        if not input_file or not output_file:
            return {
                'success': False,
                'error': 'input_file and output_file are required'
            }
        
        if input_format != 'PEM':
            args.extend(['-inform', input_format])
        if output_format != 'PEM':
            args.extend(['-outform', output_format])
        
        result = self._run_openssl_command_optimized(args)
        
        if result['success']:
            return {
                'success': True,
                'output_file': output_file,
                'input_format': input_format,
                'output_format': output_format,
                'message': f'Certificate converted: {input_file} -> {output_file}'
            }
        else:
            return result
    
    cdef dict _encrypt_optimized(self, dict config):
        """Encrypt data or file."""
        cdef:
            str input_file = config.get('input_file', '')
            str output_file = config.get('output_file', '')
            str algorithm = config.get('algorithm', 'aes-256-cbc')
            str password = config.get('password', '')
            list args = ['enc', '-aes-256-cbc', '-in', input_file, '-out', output_file, 
                        '-pass', f'pass:{password}']
        
        if not input_file or not output_file or not password:
            return {
                'success': False,
                'error': 'input_file, output_file, and password are required'
            }
        
        result = self._run_openssl_command_optimized(args)
        
        if result['success']:
            return {
                'success': True,
                'output_file': output_file,
                'algorithm': algorithm,
                'message': f'File encrypted: {output_file}'
            }
        else:
            return result
    
    cdef dict _decrypt_optimized(self, dict config):
        """Decrypt data or file."""
        cdef:
            str input_file = config.get('input_file', '')
            str output_file = config.get('output_file', '')
            str password = config.get('password', '')
            list args = ['enc', '-d', '-aes-256-cbc', '-in', input_file, '-out', output_file,
                        '-pass', f'pass:{password}']
        
        if not input_file or not output_file or not password:
            return {
                'success': False,
                'error': 'input_file, output_file, and password are required'
            }
        
        result = self._run_openssl_command_optimized(args)
        
        if result['success']:
            return {
                'success': True,
                'output_file': output_file,
                'message': f'File decrypted: {output_file}'
            }
        else:
            return result
    
    cdef dict _sign_optimized(self, dict config):
        """Sign a file."""
        cdef:
            str input_file = config.get('input_file', '')
            str output_file = config.get('output_file', '')
            str key_file = config.get('key_file', '')
            str passphrase = config.get('passphrase', '')
            list args = ['dgst', '-sha256', '-sign', key_file, '-out', output_file, input_file]
        
        if not input_file or not output_file or not key_file:
            return {
                'success': False,
                'error': 'input_file, output_file, and key_file are required'
            }
        
        if passphrase:
            args.extend(['-passin', f'pass:{passphrase}'])
        
        result = self._run_openssl_command_optimized(args)
        
        if result['success']:
            return {
                'success': True,
                'output_file': output_file,
                'message': f'File signed: {output_file}'
            }
        else:
            return result
    
    cdef dict _verify_optimized(self, dict config):
        """Verify a signature."""
        cdef:
            str input_file = config.get('input_file', '')
            str signature_file = config.get('signature_file', '')
            str pubkey_file = config.get('pubkey_file', '')
            list args = ['dgst', '-sha256', '-verify', pubkey_file, '-signature', signature_file, input_file]
        
        if not input_file or not signature_file or not pubkey_file:
            return {
                'success': False,
                'error': 'input_file, signature_file, and pubkey_file are required'
            }
        
        result = self._run_openssl_command_optimized(args)
        
        return {
            'success': result['success'],
            'valid': result['success'],
            'output': result['stdout'],
            'error': result['stderr'] if not result['success'] else None
        }
    
    cdef dict _hash_optimized(self, dict config):
        """Calculate hash of a file."""
        cdef:
            str input_file = config.get('input_file', '')
            str algorithm = config.get('algorithm', 'sha256')
            list args = ['dgst', f'-{algorithm}', input_file]
        
        if not input_file:
            return {
                'success': False,
                'error': 'input_file is required'
            }
        
        result = self._run_openssl_command_optimized(args)
        
        if result['success']:
            # Parse hash from output
            lines = result['stdout'].strip().split('\n')
            hash_line = lines[0] if lines else ''
            hash_value = hash_line.split('=')[1].strip() if '=' in hash_line else ''
            
            return {
                'success': True,
                'algorithm': algorithm,
                'hash': hash_value,
                'file': input_file
            }
        else:
            return result
    
    cdef dict _fast_hash_optimized(self, dict config):
        """Fast hash calculation with caching."""
        cdef:
            str input_file = config.get('input_file', '')
            str algorithm = config.get('algorithm', 'sha256')
            str cache_key = f"{input_file}:{algorithm}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Calculate hash
        result = self._hash_optimized(config)
        
        # Cache result
        self._cache[cache_key] = result
        
        return result
    
    cdef dict _batch_verify_optimized(self, dict config):
        """Batch certificate verification."""
        cdef:
            list cert_files = config.get('cert_files', [])
            str ca_file = config.get('ca_file', '')
            dict results = {}
            str cert_file
        
        if not cert_files:
            return {
                'success': False,
                'error': 'cert_files list is required'
            }
        
        for cert_file in cert_files:
            cert_config = {
                'cert_file': cert_file,
                'ca_file': ca_file
            }
            results[cert_file] = self._verify_cert_optimized(cert_config)
        
        return {
            'success': True,
            'results': results,
            'total': len(cert_files),
            'valid': sum(1 for r in results.values() if r.get('valid', False))
        }
    
    def get_help(self) -> str:
        """Get help information."""
        return """OpenSSL Native Plugin (Cython)

High-performance OpenSSL operations compiled with Cython.

Available commands:
  - genrsa: Generate RSA private key
  - genpkey: Generate private key (modern algorithms)
  - req_new: Create Certificate Signing Request
  - x509_selfsign: Create self-signed certificate
  - verify_cert: Verify a certificate
  - convert: Convert certificate format
  - encrypt: Encrypt data or file
  - decrypt: Decrypt data or file
  - sign: Sign a file
  - verify: Verify a signature
  - hash: Calculate hash of a file
  - fast_hash: Fast hash with caching
  - batch_verify: Batch certificate verification

Performance optimizations:
  - Cython compilation for speed
  - Cached hash calculations
  - Optimized command execution
  - Batch operations support
"""
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check if dependencies are satisfied."""
        openssl_available = self.openssl_path is not None
        openssl_version = None
        
        if openssl_available:
            try:
                result = subprocess.run([self.openssl_path, 'version'], 
                                      capture_output=True, text=True, check=True)
                openssl_version = result.stdout.strip()
            except subprocess.CalledProcessError:
                pass
        
        return {
            'status': 'ok' if openssl_available else 'missing_dependencies',
            'dependencies': {
                'openssl': {
                    'available': openssl_available,
                    'path': self.openssl_path,
                    'version': openssl_version
                }
            },
            'missing': [] if openssl_available else ['openssl'],
            'install_instructions': {
                'openssl': {
                    'ubuntu_debian': 'sudo apt-get install openssl',
                    'centos_rhel': 'sudo yum install openssl',
                    'fedora': 'sudo dnf install openssl',
                    'macos': 'brew install openssl',
                    'windows': 'Download from https://www.openssl.org/'
                }
            }
        }


# Factory function for creating plugin instances
def create_plugin(context=None, plugin_config=None):
    """Create a new OpenSSL native plugin instance."""
    return OpenSSLNativePlugin(context, plugin_config)


# Module-level functions for direct access
def get_available_commands():
    """Get list of available commands."""
    plugin = OpenSSLNativePlugin()
    return plugin.get_available_commands()


def execute(command: str, config: Dict[str, Any]) -> Any:
    """Execute a command."""
    plugin = OpenSSLNativePlugin()
    return plugin.execute(command, config)


def get_help() -> str:
    """Get help information."""
    plugin = OpenSSLNativePlugin()
    return plugin.get_help()


def check_dependencies() -> Dict[str, Any]:
    """Check dependencies."""
    plugin = OpenSSLNativePlugin()
    return plugin.check_dependencies()