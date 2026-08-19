"""
GnuPG Signing Component
======================

Handles all digital signature operations including signing,
verification, and clearsign.
"""

import os
import subprocess
import tempfile
import re
from typing import Any, Dict, List, Optional
from Sugar.Lang.Utils.Output import Output

class GnuPGSigning:
    """Manages GnuPG digital signature operations."""
    
    def __init__(self, plugin):
        self.plugin = plugin
        self.gpg_path = plugin._find_gpg()
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """Execute signing/verification command."""
        if command == "sign_file":
            return self._sign_file(config)
        elif command == "verify_signature":
            return self._verify_signature(config)
        elif command == "clearsign":
            return self._clearsign(config)
        elif command == "detached_sign":
            return self._detached_sign(config)
        elif command == "sign_text":
            return self._sign_text(config)
        elif command == "verify_text":
            return self._verify_text(config)
        else:
            raise ValueError(f"Unknown signing command: {command}")
    
    def _sign_file(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Sign a file (binary signature)."""
        input_file = config.get("input_file")
        output_file = config.get("output_file")
        key_id = config.get("key_id")
        passphrase = config.get("passphrase", "")
        armor = config.get("armor", True)
        hash_algorithm = config.get("hash_algorithm", "SHA256")
        
        if not input_file or not output_file or not key_id:
            return {
                'success': False,
                'error': "input_file, output_file, and key_id are required"
            }
        
        if not os.path.exists(input_file):
            return {
                'success': False,
                'error': f"Input file not found: {input_file}"
            }
        
        cmd = [self.gpg_path, '--sign']
        if armor:
            cmd.append('--armor')
        cmd.extend(['--digest-algo', hash_algorithm])
        if passphrase:
            cmd.extend(['--passphrase', passphrase])
        cmd.extend(['--local-user', key_id, '--output', output_file, input_file])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                'success': True,
                'input_file': input_file,
                'output_file': output_file,
                'key_id': key_id,
                'hash_algorithm': hash_algorithm
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': e.stderr,
                'return_code': e.returncode
            }
    
    def _verify_signature(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a signature."""
        input_file = config.get("input_file")
        signature_file = config.get("signature_file")
        key_file = config.get("key_file")
        
        if not input_file:
            return {
                'success': False,
                'error': "input_file is required"
            }
        
        if not os.path.exists(input_file):
            return {
                'success': False,
                'error': f"Input file not found: {input_file}"
            }
        
        cmd = [self.gpg_path, '--verify']
        
        # If signature file is provided, use detached signature
        if signature_file:
            if not os.path.exists(signature_file):
                return {
                    'success': False,
                    'error': f"Signature file not found: {signature_file}"
                }
            cmd.append(signature_file)
            cmd.append(input_file)
        else:
            # Assume input file contains the signature
            cmd.append(input_file)
        
        # Import key file if provided
        if key_file and os.path.exists(key_file):
            try:
                import_cmd = [self.gpg_path, '--import', key_file]
                subprocess.run(import_cmd, capture_output=True, text=True, check=True)
            except subprocess.CalledProcessError:
                pass  # Key might already be imported
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse verification output
            verification_info = self._parse_verification_output(result.stdout, result.stderr)
            
            return {
                'success': True,
                'verified': verification_info['verified'],
                'signer': verification_info['signer'],
                'signature_date': verification_info['signature_date'],
                'key_id': verification_info['key_id'],
                'details': verification_info['details']
            }
            
        except subprocess.CalledProcessError as e:
            # Parse error output for verification details
            verification_info = self._parse_verification_output(e.stdout, e.stderr)
            
            return {
                'success': False,
                'verified': verification_info['verified'],
                'error': e.stderr,
                'return_code': e.returncode,
                'details': verification_info['details']
            }
    
    def _clearsign(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a clearsigned file."""
        input_file = config.get("input_file")
        output_file = config.get("output_file")
        key_id = config.get("key_id")
        passphrase = config.get("passphrase", "")
        hash_algorithm = config.get("hash_algorithm", "SHA256")
        
        if not input_file or not output_file or not key_id:
            return {
                'success': False,
                'error': "input_file, output_file, and key_id are required"
            }
        
        if not os.path.exists(input_file):
            return {
                'success': False,
                'error': f"Input file not found: {input_file}"
            }
        
        cmd = [self.gpg_path, '--clearsign']
        cmd.extend(['--digest-algo', hash_algorithm])
        if passphrase:
            cmd.extend(['--passphrase', passphrase])
        cmd.extend(['--local-user', key_id, '--output', output_file, input_file])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                'success': True,
                'input_file': input_file,
                'output_file': output_file,
                'key_id': key_id,
                'hash_algorithm': hash_algorithm
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': e.stderr,
                'return_code': e.returncode
            }
    
    def _detached_sign(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detached signature."""
        input_file = config.get("input_file")
        signature_file = config.get("signature_file")
        key_id = config.get("key_id")
        passphrase = config.get("passphrase", "")
        armor = config.get("armor", True)
        hash_algorithm = config.get("hash_algorithm", "SHA256")
        
        if not input_file or not signature_file or not key_id:
            return {
                'success': False,
                'error': "input_file, signature_file, and key_id are required"
            }
        
        if not os.path.exists(input_file):
            return {
                'success': False,
                'error': f"Input file not found: {input_file}"
            }
        
        cmd = [self.gpg_path, '--detach-sign']
        if armor:
            cmd.append('--armor')
        cmd.extend(['--digest-algo', hash_algorithm])
        if passphrase:
            cmd.extend(['--passphrase', passphrase])
        cmd.extend(['--local-user', key_id, '--output', signature_file, input_file])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                'success': True,
                'input_file': input_file,
                'signature_file': signature_file,
                'key_id': key_id,
                'hash_algorithm': hash_algorithm
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': e.stderr,
                'return_code': e.returncode
            }
    
    def _sign_text(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Sign text content."""
        text = config.get("text")
        key_id = config.get("key_id")
        passphrase = config.get("passphrase", "")
        armor = config.get("armor", True)
        hash_algorithm = config.get("hash_algorithm", "SHA256")
        
        if not text or not key_id:
            return {
                'success': False,
                'error': "text and key_id are required"
            }
        
        # Create temporary file with text
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(text)
            temp_input = f.name
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sig', delete=False) as f:
            temp_output = f.name
        
        try:
            # Create detached signature
            result = self._detached_sign({
                'input_file': temp_input,
                'signature_file': temp_output,
                'key_id': key_id,
                'passphrase': passphrase,
                'armor': armor,
                'hash_algorithm': hash_algorithm
            })
            
            if result['success']:
                # Read the signature content
                with open(temp_output, 'r') as f:
                    signature_text = f.read()
                
                return {
                    'success': True,
                    'signature_text': signature_text,
                    'key_id': key_id,
                    'hash_algorithm': hash_algorithm
                }
            else:
                return result
                
        finally:
            # Clean up temporary files
            if os.path.exists(temp_input):
                os.unlink(temp_input)
            if os.path.exists(temp_output):
                os.unlink(temp_output)
    
    def _verify_text(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Verify text signature."""
        text = config.get("text")
        signature_text = config.get("signature_text")
        key_file = config.get("key_file")
        
        if not text or not signature_text:
            return {
                'success': False,
                'error': "text and signature_text are required"
            }
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(text)
            temp_input = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sig', delete=False) as f:
            f.write(signature_text)
            temp_sig = f.name
        
        try:
            # Verify the signature
            result = self._verify_signature({
                'input_file': temp_input,
                'signature_file': temp_sig,
                'key_file': key_file
            })
            
            return result
            
        finally:
            # Clean up temporary files
            if os.path.exists(temp_input):
                os.unlink(temp_input)
            if os.path.exists(temp_sig):
                os.unlink(temp_sig)
    
    def _parse_verification_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse GnuPG verification output."""
        output = stdout + stderr
        lines = output.split('\n')
        
        verification_info = {
            'verified': False,
            'signer': None,
            'signature_date': None,
            'key_id': None,
            'details': []
        }
        
        for line in lines:
            line = line.strip()
            
            # Check for successful verification
            if 'Good signature' in line:
                verification_info['verified'] = True
                verification_info['details'].append('Good signature')
                
                # Extract signer information
                match = re.search(r'from "([^"]+)"', line)
                if match:
                    verification_info['signer'] = match.group(1)
                
                # Extract key ID
                match = re.search(r'([A-F0-9]{16,40})', line)
                if match:
                    verification_info['key_id'] = match.group(1)
            
            # Check for signature date
            elif 'Signature made' in line:
                match = re.search(r'Signature made (.+)', line)
                if match:
                    verification_info['signature_date'] = match.group(1)
            
            # Check for errors
            elif 'BAD signature' in line:
                verification_info['details'].append('Bad signature')
            elif 'No public key' in line:
                verification_info['details'].append('No public key')
            elif 'Can\'t check signature' in line:
                verification_info['details'].append('Cannot check signature')
        
        return verification_info