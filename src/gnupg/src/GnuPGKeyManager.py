"""
GnuPG Key Management Component
=============================

Handles all key-related operations including generation, import/export,
listing, and management.
"""

import os
import subprocess
import tempfile
import re
from typing import Any, Dict, List, Optional
from Sugar.Lang.Utils.Output import Output

class GnuPGKeyManager:
    """Manages GnuPG key operations."""
    
    def __init__(self, plugin):
        self.plugin = plugin
        self.gpg_path = plugin._find_gpg()
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """Execute key management command."""
        if command == "generate_key":
            return self._generate_key(config)
        elif command == "list_keys":
            return self._list_keys(config)
        elif command == "import_key":
            return self._import_key(config)
        elif command == "export_key":
            return self._export_key(config)
        elif command == "delete_key":
            return self._delete_key(config)
        elif command == "edit_key":
            return self._edit_key(config)
        elif command == "sign_key":
            return self._sign_key(config)
        elif command == "revoke_key":
            return self._revoke_key(config)
        elif command == "trust_key":
            return self._trust_key(config)
        else:
            raise ValueError(f"Unknown key management command: {command}")
    
    def _generate_key(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a new GnuPG key."""
        key_type = config.get("key_type", "RSA")
        key_length = config.get("key_length", 2048)
        name_real = config.get("name_real", "")
        name_email = config.get("name_email", "")
        name_comment = config.get("name_comment", "")
        expire_date = config.get("expire_date", "0")
        passphrase = config.get("passphrase", "")
        
        # Create batch file for key generation
        batch_content = f"""
Key-Type: {key_type}
Key-Length: {key_length}
Name-Real: {name_real}
Name-Email: {name_email}
Name-Comment: {name_comment}
Expire-Date: {expire_date}
Passphrase: {passphrase}
%commit
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.batch', delete=False) as f:
            f.write(batch_content)
            batch_file = f.name
        
        try:
            cmd = [self.gpg_path, '--batch', '--gen-key', batch_file]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Extract key fingerprint from output
            fingerprint = self._extract_fingerprint(result.stdout)
            
            return {
                'success': True,
                'fingerprint': fingerprint,
                'key_type': key_type,
                'key_length': key_length,
                'name_real': name_real,
                'name_email': name_email
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': e.stderr,
                'return_code': e.returncode
            }
        finally:
            os.unlink(batch_file)
    
    def _list_keys(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """List GnuPG keys."""
        show_secret = config.get("show_secret", False)
        fingerprint = config.get("fingerprint", True)
        
        cmd = [self.gpg_path, '--list-keys']
        if show_secret:
            cmd.append('--list-secret-keys')
        if fingerprint:
            cmd.append('--fingerprint')
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            keys = self._parse_key_list(result.stdout)
            
            return {
                'success': True,
                'keys': keys,
                'count': len(keys)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': e.stderr,
                'return_code': e.returncode
            }
    
    def _import_key(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Import a key from file."""
        key_file = config.get("key_file")
        trust_level = config.get("trust_level", "marginal")
        
        if not key_file or not os.path.exists(key_file):
            return {
                'success': False,
                'error': f"Key file not found: {key_file}"
            }
        
        cmd = [self.gpg_path, '--import', key_file]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Set trust level if specified
            if trust_level != "marginal":
                fingerprint = self._extract_imported_fingerprint(result.stdout)
                if fingerprint:
                    self._set_trust_level(fingerprint, trust_level)
            
            return {
                'success': True,
                'imported_keys': self._parse_import_output(result.stdout)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': e.stderr,
                'return_code': e.returncode
            }
    
    def _export_key(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Export a key to file."""
        key_id = config.get("key_id")
        output_file = config.get("output_file")
        armor = config.get("armor", True)
        secret = config.get("secret", False)
        
        if not key_id or not output_file:
            return {
                'success': False,
                'error': "key_id and output_file are required"
            }
        
        cmd = [self.gpg_path, '--export']
        if secret:
            cmd.append('--export-secret-key')
        if armor:
            cmd.append('--armor')
        cmd.extend([key_id, '--output', output_file])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                'success': True,
                'output_file': output_file,
                'key_id': key_id
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': e.stderr,
                'return_code': e.returncode
            }
    
    def _delete_key(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a key."""
        key_id = config.get("key_id")
        secret = config.get("secret", False)
        
        if not key_id:
            return {
                'success': False,
                'error': "key_id is required"
            }
        
        cmd = [self.gpg_path, '--delete-key']
        if secret:
            cmd.append('--delete-secret-key')
        cmd.append(key_id)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                'success': True,
                'deleted_key': key_id
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': e.stderr,
                'return_code': e.returncode
            }
    
    def _sign_key(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Sign a public key."""
        key_id = config.get("key_id")
        signer_key_id = config.get("signer_key_id")
        passphrase = config.get("passphrase", "")
        trust_level = config.get("trust_level", "full")
        expire_date = config.get("expire_date", "1y")
        
        if not key_id or not signer_key_id:
            return {
                'success': False,
                'error': "key_id and signer_key_id are required"
            }
        
        # Create batch file for key signing
        batch_content = f"""
sign
{key_id}
{trust_level}
{expire_date}
y
save
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.batch', delete=False) as f:
            f.write(batch_content)
            batch_file = f.name
        
        try:
            cmd = [self.gpg_path, '--batch', '--passphrase', passphrase, '--edit-key', signer_key_id]
            with open(batch_file, 'r') as f:
                result = subprocess.run(cmd, input=f.read(), capture_output=True, text=True, check=True)
            
            return {
                'success': True,
                'signed_key': key_id,
                'signer': signer_key_id
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': e.stderr,
                'return_code': e.returncode
            }
        finally:
            os.unlink(batch_file)
    
    def _revoke_key(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a revocation certificate."""
        key_id = config.get("key_id")
        output_file = config.get("output_file")
        passphrase = config.get("passphrase", "")
        reason = config.get("reason", "key_compromised")
        description = config.get("description", "")
        
        if not key_id or not output_file:
            return {
                'success': False,
                'error': "key_id and output_file are required"
            }
        
        # Create batch file for revocation
        batch_content = f"""
revsig
{reason}
{description}
y
save
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.batch', delete=False) as f:
            f.write(batch_content)
            batch_file = f.name
        
        try:
            cmd = [self.gpg_path, '--batch', '--passphrase', passphrase, '--output', output_file, '--gen-revoke', key_id]
            with open(batch_file, 'r') as f:
                result = subprocess.run(cmd, input=f.read(), capture_output=True, text=True, check=True)
            
            return {
                'success': True,
                'revocation_file': output_file,
                'revoked_key': key_id
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': e.stderr,
                'return_code': e.returncode
            }
        finally:
            os.unlink(batch_file)
    
    def _trust_key(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Set trust level for a key."""
        key_id = config.get("key_id")
        trust_level = config.get("trust_level", "marginal")
        
        if not key_id:
            return {
                'success': False,
                'error': "key_id is required"
            }
        
        return self._set_trust_level(key_id, trust_level)
    
    def _set_trust_level(self, key_id: str, trust_level: str) -> Dict[str, Any]:
        """Set trust level for a key."""
        trust_values = {
            "unknown": "0",
            "expired": "1", 
            "undefined": "2",
            "never": "3",
            "marginal": "4",
            "full": "5",
            "ultimate": "6"
        }
        
        trust_value = trust_values.get(trust_level, "4")
        
        # Create batch file for trust setting
        batch_content = f"""
trust
{trust_value}
y
save
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.batch', delete=False) as f:
            f.write(batch_content)
            batch_file = f.name
        
        try:
            cmd = [self.gpg_path, '--batch', '--edit-key', key_id]
            with open(batch_file, 'r') as f:
                result = subprocess.run(cmd, input=f.read(), capture_output=True, text=True, check=True)
            
            return {
                'success': True,
                'key_id': key_id,
                'trust_level': trust_level
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': e.stderr,
                'return_code': e.returncode
            }
        finally:
            os.unlink(batch_file)
    
    def _extract_fingerprint(self, output: str) -> Optional[str]:
        """Extract fingerprint from gpg output."""
        lines = output.split('\n')
        for line in lines:
            if 'pub' in line and '/' in line:
                parts = line.split()
                for part in parts:
                    if len(part) == 40 and part.isalnum():
                        return part
        return None
    
    def _extract_imported_fingerprint(self, output: str) -> Optional[str]:
        """Extract fingerprint from import output."""
        match = re.search(r'key\s+([A-F0-9]{40})', output)
        return match.group(1) if match else None
    
    def _parse_key_list(self, output: str) -> List[Dict[str, Any]]:
        """Parse key list output."""
        keys = []
        current_key = {}
        
        for line in output.split('\n'):
            if line.startswith('pub') or line.startswith('sec'):
                if current_key:
                    keys.append(current_key)
                current_key = {
                    'type': 'secret' if line.startswith('sec') else 'public',
                    'key_id': line.split('/')[1].split()[0] if '/' in line else None,
                    'created': line.split()[-1] if len(line.split()) > 2 else None
                }
            elif line.startswith('uid'):
                if 'uids' not in current_key:
                    current_key['uids'] = []
                uid = line.split(']')[1].strip() if ']' in line else line.split('uid')[1].strip()
                current_key['uids'].append(uid)
            elif line.startswith('fpr'):
                current_key['fingerprint'] = line.split()[-1]
        
        if current_key:
            keys.append(current_key)
        
        return keys
    
    def _parse_import_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse import output."""
        imported_keys = []
        lines = output.split('\n')
        
        for line in lines:
            if 'imported' in line.lower():
                parts = line.split()
                if len(parts) >= 2:
                    imported_keys.append({
                        'key_id': parts[1],
                        'status': 'imported'
                    })
        
        return imported_keys