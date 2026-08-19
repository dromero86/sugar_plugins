"""
GnuPG Encryption Component
==========================

Handles all encryption and decryption operations including
symmetric and asymmetric encryption.
"""

import os
import subprocess
import tempfile
from typing import Any, Dict, List, Optional
from Sugar.Lang.Utils.Output import Output

class GnuPGEncryption:
    """Manages GnuPG encryption and decryption operations."""
    
    def __init__(self, plugin):
        self.plugin = plugin
        self.gpg_path = plugin._find_gpg()
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """Execute encryption/decryption command."""
        if command == "encrypt_file":
            return self._encrypt_file(config)
        elif command == "decrypt_file":
            return self._decrypt_file(config)
        elif command == "encrypt_text":
            return self._encrypt_text(config)
        elif command == "decrypt_text":
            return self._decrypt_text(config)
        elif command == "symmetric_encrypt":
            return self._symmetric_encrypt(config)
        elif command == "symmetric_decrypt":
            return self._symmetric_decrypt(config)
        else:
            raise ValueError(f"Unknown encryption command: {command}")
    
    def _encrypt_file(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt a file using asymmetric encryption."""
        input_file = config.get("input_file")
        output_file = config.get("output_file")
        recipient = config.get("recipient")
        armor = config.get("armor", True)
        compress = config.get("compress", True)
        trust_model = config.get("trust_model", "always")
        
        if not input_file or not output_file or not recipient:
            return {
                'success': False,
                'error': "input_file, output_file, and recipient are required"
            }
        
        if not os.path.exists(input_file):
            return {
                'success': False,
                'error': f"Input file not found: {input_file}"
            }
        
        cmd = [self.gpg_path, '--encrypt']
        if armor:
            cmd.append('--armor')
        if compress:
            cmd.append('--compress-algo', 'ZLIB')
        cmd.extend(['--recipient', recipient, '--output', output_file, input_file])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                'success': True,
                'input_file': input_file,
                'output_file': output_file,
                'recipient': recipient
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': e.stderr,
                'return_code': e.returncode
            }
    
    def _decrypt_file(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt a file."""
        input_file = config.get("input_file")
        output_file = config.get("output_file")
        passphrase = config.get("passphrase", "")
        
        if not input_file or not output_file:
            return {
                'success': False,
                'error': "input_file and output_file are required"
            }
        
        if not os.path.exists(input_file):
            return {
                'success': False,
                'error': f"Input file not found: {input_file}"
            }
        
        cmd = [self.gpg_path, '--decrypt', '--output', output_file]
        if passphrase:
            cmd.extend(['--passphrase', passphrase])
        cmd.append(input_file)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                'success': True,
                'input_file': input_file,
                'output_file': output_file
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': e.stderr,
                'return_code': e.returncode
            }
    
    def _encrypt_text(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt text using asymmetric encryption."""
        text = config.get("text")
        recipient = config.get("recipient")
        armor = config.get("armor", True)
        compress = config.get("compress", True)
        
        if not text or not recipient:
            return {
                'success': False,
                'error': "text and recipient are required"
            }
        
        # Create temporary file with text
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(text)
            temp_input = f.name
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gpg', delete=False) as f:
            temp_output = f.name
        
        try:
            # Encrypt the temporary file
            result = self._encrypt_file({
                'input_file': temp_input,
                'output_file': temp_output,
                'recipient': recipient,
                'armor': armor,
                'compress': compress
            })
            
            if result['success']:
                # Read the encrypted content
                with open(temp_output, 'r') as f:
                    encrypted_text = f.read()
                
                return {
                    'success': True,
                    'encrypted_text': encrypted_text,
                    'recipient': recipient
                }
            else:
                return result
                
        finally:
            # Clean up temporary files
            if os.path.exists(temp_input):
                os.unlink(temp_input)
            if os.path.exists(temp_output):
                os.unlink(temp_output)
    
    def _decrypt_text(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt text."""
        encrypted_text = config.get("encrypted_text")
        passphrase = config.get("passphrase", "")
        
        if not encrypted_text:
            return {
                'success': False,
                'error': "encrypted_text is required"
            }
        
        # Create temporary file with encrypted text
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gpg', delete=False) as f:
            f.write(encrypted_text)
            temp_input = f.name
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_output = f.name
        
        try:
            # Decrypt the temporary file
            result = self._decrypt_file({
                'input_file': temp_input,
                'output_file': temp_output,
                'passphrase': passphrase
            })
            
            if result['success']:
                # Read the decrypted content
                with open(temp_output, 'r') as f:
                    decrypted_text = f.read()
                
                return {
                    'success': True,
                    'decrypted_text': decrypted_text
                }
            else:
                return result
                
        finally:
            # Clean up temporary files
            if os.path.exists(temp_input):
                os.unlink(temp_input)
            if os.path.exists(temp_output):
                os.unlink(temp_output)
    
    def _symmetric_encrypt(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt a file using symmetric encryption."""
        input_file = config.get("input_file")
        output_file = config.get("output_file")
        passphrase = config.get("passphrase")
        cipher = config.get("cipher", "AES256")
        armor = config.get("armor", False)
        compress = config.get("compress", True)
        
        if not input_file or not output_file or not passphrase:
            return {
                'success': False,
                'error': "input_file, output_file, and passphrase are required"
            }
        
        if not os.path.exists(input_file):
            return {
                'success': False,
                'error': f"Input file not found: {input_file}"
            }
        
        cmd = [self.gpg_path, '--symmetric', '--cipher-algo', cipher]
        if armor:
            cmd.append('--armor')
        if compress:
            cmd.append('--compress-algo', 'ZLIB')
        cmd.extend(['--passphrase', passphrase, '--output', output_file, input_file])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                'success': True,
                'input_file': input_file,
                'output_file': output_file,
                'cipher': cipher
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': e.stderr,
                'return_code': e.returncode
            }
    
    def _symmetric_decrypt(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt a file using symmetric decryption."""
        input_file = config.get("input_file")
        output_file = config.get("output_file")
        passphrase = config.get("passphrase")
        
        if not input_file or not output_file or not passphrase:
            return {
                'success': False,
                'error': "input_file, output_file, and passphrase are required"
            }
        
        if not os.path.exists(input_file):
            return {
                'success': False,
                'error': f"Input file not found: {input_file}"
            }
        
        cmd = [self.gpg_path, '--decrypt', '--passphrase', passphrase, '--output', output_file, input_file]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                'success': True,
                'input_file': input_file,
                'output_file': output_file
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': e.stderr,
                'return_code': e.returncode
            }