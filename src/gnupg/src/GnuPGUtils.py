"""
GnuPG Utilities Component
========================

Handles utility operations including dependency checking,
system information, and testing functionality.
"""

import os
import subprocess
import tempfile
from typing import Any, Dict, List, Optional
from Sugar.Lang.Utils.Output import Output

class GnuPGUtils:
    """Manages GnuPG utility operations."""
    
    def __init__(self, plugin):
        self.plugin = plugin
        self.gpg_path = plugin._find_gpg()
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """Execute utility command."""
        if command == "check_dependencies":
            return self._check_dependencies(config)
        elif command == "system_info":
            return self._system_info(config)
        elif command == "test_functionality":
            return self._test_functionality(config)
        elif command == "configure_agent":
            return self._configure_agent(config)
        elif command == "check_agent_status":
            return self._check_agent_status(config)
        else:
            raise ValueError(f"Unknown utility command: {command}")
    
    def _check_dependencies(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check GnuPG dependencies."""
        return self.plugin.dependency_status
    
    def _system_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get GnuPG system information."""
        info = {
            'gpg_path': self.gpg_path,
            'version': None,
            'home_directory': None,
            'supported_algorithms': {
                'pubkey': [],
                'cipher': [],
                'hash': [],
                'compression': []
            }
        }
        
        if self.gpg_path:
            try:
                # Get version
                result = subprocess.run([self.gpg_path, '--version'], 
                                      capture_output=True, text=True, check=True)
                info['version'] = result.stdout.split('\n')[0]
                
                # Get home directory
                result = subprocess.run([self.gpg_path, '--version'], 
                                      capture_output=True, text=True, check=True)
                for line in result.stdout.split('\n'):
                    if 'Home:' in line:
                        info['home_directory'] = line.split('Home:')[1].strip()
                        break
                
                # Get supported algorithms
                result = subprocess.run([self.gpg_path, '--version'], 
                                      capture_output=True, text=True, check=True)
                in_algorithms = False
                for line in result.stdout.split('\n'):
                    if 'Supported algorithms:' in line:
                        in_algorithms = True
                        continue
                    elif in_algorithms and line.strip():
                        if 'Pubkey:' in line:
                            info['supported_algorithms']['pubkey'] = line.split('Pubkey:')[1].strip().split(', ')
                        elif 'Cipher:' in line:
                            info['supported_algorithms']['cipher'] = line.split('Cipher:')[1].strip().split(', ')
                        elif 'Hash:' in line:
                            info['supported_algorithms']['hash'] = line.split('Hash:')[1].strip().split(', ')
                        elif 'Compression:' in line:
                            info['supported_algorithms']['compression'] = line.split('Compression:')[1].strip().split(', ')
                        elif line.startswith('Home:'):
                            break
                
            except subprocess.CalledProcessError:
                pass
        
        return info
    
    def _test_functionality(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test GnuPG functionality."""
        tests = {
            'gpg_available': False,
            'key_generation': False,
            'encryption': False,
            'decryption': False,
            'signing': False,
            'verification': False
        }
        
        # Test 1: GnuPG available
        if self.gpg_path:
            tests['gpg_available'] = True
            
            # Test 2: Key generation
            try:
                result = self._test_key_generation()
                tests['key_generation'] = result['success']
            except Exception:
                pass
            
            # Test 3: Encryption/Decryption
            try:
                result = self._test_encryption_decryption()
                tests['encryption'] = result['encryption_success']
                tests['decryption'] = result['decryption_success']
            except Exception:
                pass
            
            # Test 4: Signing/Verification
            try:
                result = self._test_signing_verification()
                tests['signing'] = result['signing_success']
                tests['verification'] = result['verification_success']
            except Exception:
                pass
        
        return {
            'success': all(tests.values()),
            'tests': tests
        }
    
    def _test_key_generation(self) -> Dict[str, Any]:
        """Test key generation functionality."""
        # Create a test key with minimal settings
        batch_content = """
Key-Type: RSA
Key-Length: 1024
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 1d
Passphrase: test123
%commit
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.batch', delete=False) as f:
            f.write(batch_content)
            batch_file = f.name
        
        try:
            cmd = [self.gpg_path, '--batch', '--gen-key', batch_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            return {
                'success': result.returncode == 0,
                'error': result.stderr if result.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Key generation timed out'
            }
        finally:
            os.unlink(batch_file)
    
    def _test_encryption_decryption(self) -> Dict[str, Any]:
        """Test encryption and decryption functionality."""
        test_message = "This is a test message for GnuPG encryption/decryption testing."
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_message)
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gpg', delete=False) as f:
            encrypted_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            decrypted_file = f.name
        
        try:
            # Test symmetric encryption
            cmd_encrypt = [self.gpg_path, '--symmetric', '--passphrase', 'test123', 
                          '--output', encrypted_file, input_file]
            result_encrypt = subprocess.run(cmd_encrypt, capture_output=True, text=True)
            
            encryption_success = result_encrypt.returncode == 0
            
            # Test symmetric decryption
            if encryption_success:
                cmd_decrypt = [self.gpg_path, '--decrypt', '--passphrase', 'test123',
                              '--output', decrypted_file, encrypted_file]
                result_decrypt = subprocess.run(cmd_decrypt, capture_output=True, text=True)
                
                decryption_success = result_decrypt.returncode == 0
                
                # Verify decrypted content
                if decryption_success:
                    with open(decrypted_file, 'r') as f:
                        decrypted_content = f.read()
                    decryption_success = decrypted_content == test_message
            else:
                decryption_success = False
            
            return {
                'encryption_success': encryption_success,
                'decryption_success': decryption_success,
                'encryption_error': result_encrypt.stderr if not encryption_success else None,
                'decryption_error': result_decrypt.stderr if not decryption_success else None
            }
            
        finally:
            # Clean up temporary files
            for file_path in [input_file, encrypted_file, decrypted_file]:
                if os.path.exists(file_path):
                    os.unlink(file_path)
    
    def _test_signing_verification(self) -> Dict[str, Any]:
        """Test signing and verification functionality."""
        test_message = "This is a test message for GnuPG signing/verification testing."
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_message)
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sig', delete=False) as f:
            signature_file = f.name
        
        try:
            # Test detached signing
            cmd_sign = [self.gpg_path, '--detach-sign', '--armor', '--passphrase', 'test123',
                       '--local-user', 'test@example.com', '--output', signature_file, input_file]
            result_sign = subprocess.run(cmd_sign, capture_output=True, text=True)
            
            signing_success = result_sign.returncode == 0
            
            # Test signature verification
            if signing_success:
                cmd_verify = [self.gpg_path, '--verify', signature_file, input_file]
                result_verify = subprocess.run(cmd_verify, capture_output=True, text=True)
                
                verification_success = result_verify.returncode == 0
            else:
                verification_success = False
            
            return {
                'signing_success': signing_success,
                'verification_success': verification_success,
                'signing_error': result_sign.stderr if not signing_success else None,
                'verification_error': result_verify.stderr if not verification_success else None
            }
            
        finally:
            # Clean up temporary files
            for file_path in [input_file, signature_file]:
                if os.path.exists(file_path):
                    os.unlink(file_path)
    
    def _configure_agent(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure GnuPG agent."""
        enable_ssh = config.get("enable_ssh", True)
        enable_gpg = config.get("enable_gpg", True)
        timeout = config.get("timeout", 3600)
        max_cache_ttl = config.get("max_cache_ttl", 7200)
        default_cache_ttl = config.get("default_cache_ttl", 600)
        
        # Create gpg-agent.conf
        home_dir = os.path.expanduser('~')
        gnupg_dir = os.path.join(home_dir, '.gnupg')
        
        if not os.path.exists(gnupg_dir):
            os.makedirs(gnupg_dir, mode=0o700)
        
        gpg_agent_conf = os.path.join(gnupg_dir, 'gpg-agent.conf')
        
        config_content = f"""
# GnuPG Agent Configuration
default-cache-ttl {default_cache_ttl}
max-cache-ttl {max_cache_ttl}
default-cache-ttl-ssh {default_cache_ttl}
max-cache-ttl-ssh {max_cache_ttl}
"""
        
        if enable_ssh:
            config_content += "enable-ssh-support\n"
        
        try:
            with open(gpg_agent_conf, 'w') as f:
                f.write(config_content)
            
            # Reload gpg-agent
            try:
                subprocess.run([self.gpg_path, '--reload-agent'], 
                             capture_output=True, text=True, check=True)
            except subprocess.CalledProcessError:
                pass  # Agent might not be running
            
            return {
                'success': True,
                'config_file': gpg_agent_conf,
                'settings': {
                    'enable_ssh': enable_ssh,
                    'enable_gpg': enable_gpg,
                    'timeout': timeout,
                    'max_cache_ttl': max_cache_ttl,
                    'default_cache_ttl': default_cache_ttl
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_agent_status(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check GnuPG agent status."""
        check_gpg_agent = config.get("check_gpg_agent", True)
        check_ssh_agent = config.get("check_ssh_agent", True)
        
        status = {
            'gpg_agent': {
                'running': False,
                'pid': None,
                'socket': None
            },
            'ssh_agent': {
                'running': False,
                'pid': None,
                'socket': None
            }
        }
        
        try:
            # Check gpg-agent
            if check_gpg_agent:
                result = subprocess.run([self.gpg_path, '--agent-info'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    status['gpg_agent']['running'] = True
                    # Parse agent info for PID and socket
                    for line in result.stdout.split('\n'):
                        if 'SOCKET=' in line:
                            status['gpg_agent']['socket'] = line.split('SOCKET=')[1].strip()
                        elif 'PID=' in line:
                            status['gpg_agent']['pid'] = line.split('PID=')[1].strip()
            
            # Check ssh-agent
            if check_ssh_agent:
                result = subprocess.run(['ssh-add', '-l'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    status['ssh_agent']['running'] = True
                    # Try to get SSH_AUTH_SOCK
                    ssh_auth_sock = os.environ.get('SSH_AUTH_SOCK')
                    if ssh_auth_sock:
                        status['ssh_agent']['socket'] = ssh_auth_sock
            
        except Exception:
            pass
        
        return status