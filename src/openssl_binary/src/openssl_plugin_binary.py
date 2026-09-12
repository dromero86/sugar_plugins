#!/usr/bin/env python3
"""
OpenSSL Binary Plugin
====================

A standalone OpenSSL plugin that can be compiled as a binary executable.
This plugin provides cryptographic operations without requiring Python on the client system.
"""

import os
import sys
import json
import subprocess
import tempfile
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
import platform

from Sugar.Lang.Plugins import PluginBase

class OpenSSLBinaryPlugin(PluginBase):
    """OpenSSL binary plugin implementation."""
    
    VERSION = "1.0.0"
    DESCRIPTION = "OpenSSL cryptographic operations"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = ["openssl"]
    REQUIREMENTS = []
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        super().__init__(context, plugin_config)
        self.openssl_path = self._find_openssl()
        self.plugin_name = "openssl_binary"
        self.version = "1.0.0"
        self.description = "OpenSSL cryptographic operations"
        self.author = "Sugar Team"
        self.license = "MIT"
        
    def _find_openssl(self) -> Optional[str]:
        """Find OpenSSL executable."""
        try:
            result = subprocess.run(['which', 'openssl'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata."""
        return {
            'name': self.plugin_name,
            'version': self.VERSION,
            'description': self.DESCRIPTION,
            'author': self.AUTHOR,
            'license': self.LICENSE,
            'dependencies': self.DEPENDENCIES,
            'requirements': self.REQUIREMENTS,
            'commands': self.get_available_commands()
        }
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """Get plugin information for PluginBase compatibility."""
        return self.get_metadata()
    
    def command(self, command_name: str, config: Dict[str, Any]) -> Any:
        """Execute a plugin command."""
        return self.execute_command(command_name, config)
    
    def execute(self, operator: str, config: Dict[str, Any]) -> Any:
        """
        Execute a plugin operator (required by PluginBase).
        
        Args:
            operator: The operator to execute
            config: Configuration dictionary for the operator
            
        Returns:
            The result of the operator execution
        """
        return self.execute_command(operator, config)
    
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
            "hash"
        ]
    
    def execute_command(self, command: str, config: Dict[str, Any]) -> Any:
        """Execute an OpenSSL command."""
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
                return self._genrsa(config)
            elif command == "genpkey":
                return self._genpkey(config)
            elif command == "req_new":
                return self._req_new(config)
            elif command == "x509_selfsign":
                return self._x509_selfsign(config)
            elif command == "verify_cert":
                return self._verify_cert(config)
            elif command == "convert":
                return self._convert(config)
            elif command == "encrypt":
                return self._encrypt(config)
            elif command == "decrypt":
                return self._decrypt(config)
            elif command == "sign":
                return self._sign(config)
            elif command == "verify":
                return self._verify(config)
            elif command == "hash":
                return self._hash(config)
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
    
    def _run_openssl_command(self, args: List[str], input_data: Optional[str] = None) -> Dict[str, Any]:
        """Run an OpenSSL command."""
        try:
            cmd = [self.openssl_path] + args
            result = subprocess.run(
                cmd,
                input=input_data,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Command timed out'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _genrsa(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate RSA private key."""
        key_size = config.get('key_size', 2048)
        output_file = config.get('output_file', 'private_key.pem')
        passphrase = config.get('passphrase')
        
        args = ['genrsa', '-out', output_file, str(key_size)]
        if passphrase:
            args.extend(['-aes256', '-passout', f'pass:{passphrase}'])
        
        result = self._run_openssl_command(args)
        
        if result['success']:
            return {
                'success': True,
                'output_file': output_file,
                'key_size': key_size,
                'message': f'RSA private key generated: {output_file}'
            }
        else:
            return result
    
    def _genpkey(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate private key using modern algorithms."""
        algorithm = config.get('algorithm', 'rsa')
        key_size = config.get('key_size', 2048)
        output_file = config.get('output_file', 'private_key.pem')
        passphrase = config.get('passphrase')
        
        args = ['genpkey', '-algorithm', algorithm, '-out', output_file]
        if algorithm == 'rsa':
            args.extend(['-pkeyopt', f'rsa_keygen_bits:{key_size}'])
        elif algorithm == 'ec':
            args.extend(['-pkeyopt', 'ec_paramgen_curve:P-256'])
        
        if passphrase:
            args.extend(['-aes256', '-pass', f'pass:{passphrase}'])
        
        result = self._run_openssl_command(args)
        
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
    
    def _req_new(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create Certificate Signing Request."""
        key_file = config.get('key_file')
        output_file = config.get('output_file', 'certificate.csr')
        subject = config.get('subject', '/C=ES/ST=Madrid/L=Madrid/O=MyCompany/CN=example.com')
        passphrase = config.get('passphrase')
        
        if not key_file:
            return {
                'success': False,
                'error': 'key_file is required'
            }
        
        args = ['req', '-new', '-key', key_file, '-out', output_file, '-subj', subject]
        if passphrase:
            args.extend(['-passin', f'pass:{passphrase}'])
        
        result = self._run_openssl_command(args)
        
        if result['success']:
            return {
                'success': True,
                'output_file': output_file,
                'subject': subject,
                'message': f'CSR generated: {output_file}'
            }
        else:
            return result
    
    def _x509_selfsign(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create self-signed certificate."""
        csr_file = config.get('csr_file')
        key_file = config.get('key_file')
        output_file = config.get('output_file', 'certificate.crt')
        days = config.get('days', 365)
        passphrase = config.get('passphrase')
        
        if not csr_file or not key_file:
            return {
                'success': False,
                'error': 'csr_file and key_file are required'
            }
        
        args = ['x509', '-req', '-in', csr_file, '-signkey', key_file, 
                '-out', output_file, '-days', str(days)]
        if passphrase:
            args.extend(['-passin', f'pass:{passphrase}'])
        
        result = self._run_openssl_command(args)
        
        if result['success']:
            return {
                'success': True,
                'output_file': output_file,
                'days': days,
                'message': f'Self-signed certificate generated: {output_file}'
            }
        else:
            return result
    
    def _verify_cert(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a certificate."""
        cert_file = config.get('cert_file')
        ca_file = config.get('ca_file')
        
        if not cert_file:
            return {
                'success': False,
                'error': 'cert_file is required'
            }
        
        args = ['verify']
        if ca_file:
            args.extend(['-CAfile', ca_file])
        args.append(cert_file)
        
        result = self._run_openssl_command(args)
        
        return {
            'success': result['success'],
            'valid': result['success'],
            'output': result['stdout'],
            'error': result['stderr'] if not result['success'] else None
        }
    
    def _convert(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert certificate format."""
        input_file = config.get('input_file')
        output_file = config.get('output_file')
        input_format = config.get('input_format', 'PEM')
        output_format = config.get('output_format', 'PEM')
        
        if not input_file or not output_file:
            return {
                'success': False,
                'error': 'input_file and output_file are required'
            }
        
        args = ['x509', '-in', input_file, '-out', output_file]
        if input_format != 'PEM':
            args.extend(['-inform', input_format])
        if output_format != 'PEM':
            args.extend(['-outform', output_format])
        
        result = self._run_openssl_command(args)
        
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
    
    def _encrypt(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt data or file."""
        input_file = config.get('input_file')
        output_file = config.get('output_file')
        algorithm = config.get('algorithm', 'aes-256-cbc')
        password = config.get('password')
        
        if not input_file or not output_file or not password:
            return {
                'success': False,
                'error': 'input_file, output_file, and password are required'
            }
        
        args = ['enc', '-aes-256-cbc', '-in', input_file, '-out', output_file, 
                '-pass', f'pass:{password}']
        
        result = self._run_openssl_command(args)
        
        if result['success']:
            return {
                'success': True,
                'output_file': output_file,
                'algorithm': algorithm,
                'message': f'File encrypted: {output_file}'
            }
        else:
            return result
    
    def _decrypt(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt data or file."""
        input_file = config.get('input_file')
        output_file = config.get('output_file')
        password = config.get('password')
        
        if not input_file or not output_file or not password:
            return {
                'success': False,
                'error': 'input_file, output_file, and password are required'
            }
        
        args = ['enc', '-d', '-aes-256-cbc', '-in', input_file, '-out', output_file,
                '-pass', f'pass:{password}']
        
        result = self._run_openssl_command(args)
        
        if result['success']:
            return {
                'success': True,
                'output_file': output_file,
                'message': f'File decrypted: {output_file}'
            }
        else:
            return result
    
    def _sign(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Sign a file."""
        input_file = config.get('input_file')
        output_file = config.get('output_file')
        key_file = config.get('key_file')
        passphrase = config.get('passphrase')
        
        if not input_file or not output_file or not key_file:
            return {
                'success': False,
                'error': 'input_file, output_file, and key_file are required'
            }
        
        args = ['dgst', '-sha256', '-sign', key_file, '-out', output_file, input_file]
        if passphrase:
            args.extend(['-passin', f'pass:{passphrase}'])
        
        result = self._run_openssl_command(args)
        
        if result['success']:
            return {
                'success': True,
                'output_file': output_file,
                'message': f'File signed: {output_file}'
            }
        else:
            return result
    
    def _verify(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a signature."""
        input_file = config.get('input_file')
        signature_file = config.get('signature_file')
        pubkey_file = config.get('pubkey_file')
        
        if not input_file or not signature_file or not pubkey_file:
            return {
                'success': False,
                'error': 'input_file, signature_file, and pubkey_file are required'
            }
        
        args = ['dgst', '-sha256', '-verify', pubkey_file, '-signature', signature_file, input_file]
        
        result = self._run_openssl_command(args)
        
        return {
            'success': result['success'],
            'valid': result['success'],
            'output': result['stdout'],
            'error': result['stderr'] if not result['success'] else None
        }
    
    def _hash(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate hash of a file."""
        input_file = config.get('input_file')
        algorithm = config.get('algorithm', 'sha256')
        
        if not input_file:
            return {
                'success': False,
                'error': 'input_file is required'
            }
        
        args = ['dgst', f'-{algorithm}', input_file]
        
        result = self._run_openssl_command(args)
        
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

def main():
    """Main entry point for the binary plugin."""
    parser = argparse.ArgumentParser(description='OpenSSL Binary Plugin')
    parser.add_argument('--metadata', action='store_true', help='Show plugin metadata')
    parser.add_argument('--list-commands', action='store_true', help='List available commands')
    parser.add_argument('--check-dependencies', action='store_true', help='Check dependencies')
    parser.add_argument('--help', action='store_true', help='Show help')
    parser.add_argument('--execute', help='Execute command from JSON file')
    
    args = parser.parse_args()
    
    plugin = OpenSSLBinaryPlugin()
    
    if args.metadata:
        print(json.dumps(plugin.get_metadata(), indent=2))
    elif args.list_commands:
        print(json.dumps(plugin.get_available_commands()))
    elif args.check_dependencies:
        print(json.dumps(plugin.check_dependencies(), indent=2))
    elif args.help:
        print("OpenSSL Binary Plugin")
        print("====================")
        print("Available commands:")
        for cmd in plugin.get_available_commands():
            print(f"  - {cmd}")
        print("\nUsage: plugin --execute input.json")
    elif args.execute:
        try:
            with open(args.execute, 'r') as f:
                input_data = json.load(f)
            
            command = input_data.get('command')
            config = input_data.get('config', {})
            
            if not command:
                print(json.dumps({'success': False, 'error': 'No command specified'}))
                sys.exit(1)
            
            result = plugin.execute_command(command, config)
            print(json.dumps(result, indent=2))
            
        except Exception as e:
            print(json.dumps({'success': False, 'error': str(e)}))
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()