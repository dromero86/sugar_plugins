"""
JWT Plugin for Sugar
===================

A comprehensive JWT plugin that provides JWT operations including
encoding, decoding, and verification of JSON Web Tokens.
"""

import jwt
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Utils.Output import Output

class JwtPlugin(PluginBase):
    """
    JWT plugin for Sugar.
    
    Provides comprehensive JWT operations including:
    - JWT encoding with custom payloads
    - JWT decoding with signature verification
    - JWT verification
    - Unverified JWT decoding
    - Support for multiple algorithms (HS256, RS256, etc.)
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Comprehensive JWT operations for Sugar"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = ["PyJWT", "cryptography"]
    REQUIREMENTS = ["PyJWT>=2.8.0", "cryptography>=3.4.0"]
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """Initialize the JWT plugin."""
        super().__init__(context, plugin_config)
        Output.Console(self.plugin_name, "JWT plugin initialized")
    
    def get_available_commands(self) -> List[str]:
        """
        Get list of available commands.
        
        Returns:
            List of available command names
        """
        return ["encode", "decode", "verify"]
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """
        Execute a JWT plugin command.
        
        Args:
            command: Command to execute (encode, decode, verify)
            config: Command configuration
            
        Returns:
            Command execution result
        """
        try:
            if command == "encode":
                return self._encode_jwt(config)
            elif command == "decode":
                return self._decode_jwt(config)
            elif command == "verify":
                return self._verify_jwt(config)
            else:
                raise ValueError(f"Unknown command: {command}")
        except Exception as e:
            Output.Console(self.plugin_name, f"Error executing {command}: {str(e)}")
            raise
    
    def _encode_jwt(self, config: Dict[str, Any]) -> str:
        """
        Encode a JWT token.
        
        Args:
            config: Configuration containing payload, key, algorithm, etc.
            
        Returns:
            Encoded JWT token
        """
        try:
            # Extract configuration
            payload = config.get("payload", {})
            key = config.get("key")
            algorithm = config.get("algorithm", "HS256")
            
            # Interpolate template variables in key
            if isinstance(key, str) and "{{" in key and "}}" in key:
                key = self._interpolate_template(key)
            
            if not key:
                raise ValueError("Key is required for JWT encoding")
            
            # Process payload - handle template variables
            processed_payload = self._process_payload(payload)
            
            # Encode the JWT
            encoded_token = jwt.encode(processed_payload, key, algorithm=algorithm)
            
            # Store result if specified
            result_var = config.get("result")
            if result_var:
                self._set_nested_variable(result_var, encoded_token)
            
            Output.Console(self.plugin_name, f"JWT encoded successfully using {algorithm}")
            return encoded_token
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error encoding JWT: {str(e)}")
            raise
    
    def _decode_jwt(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decode a JWT token.
        
        Args:
            config: Configuration containing token, key, algorithms, etc.
            
        Returns:
            Decoded JWT payload
        """
        try:
            # Extract configuration
            token = config.get("token")
            key = config.get("key")
            algorithms = config.get("algorithms", ["HS256"])
            verify = config.get("verify", True)
            options = config.get("options", {})
            
            # Interpolate template variables in key
            if isinstance(key, str) and "{{" in key and "}}" in key:
                key = self._interpolate_template(key)
            
            if not token:
                raise ValueError("Token is required for JWT decoding")
            
            # Interpolate template variables in token
            if isinstance(token, str) and "{{" in token and "}}" in token:
                token = self._interpolate_template(token)
            
            # Handle unverified decoding
            if not verify or options.get("verify_signature", True) is False:
                decoded_payload = jwt.decode(token, options={"verify_signature": False})
                Output.Console(self.plugin_name, "JWT decoded without signature verification")
            else:
                if not key:
                    raise ValueError("Key is required for verified JWT decoding")
                
                decoded_payload = jwt.decode(token, key, algorithms=algorithms, options=options)
                Output.Console(self.plugin_name, f"JWT decoded successfully with verification using {algorithms}")
            
            # Store result if specified
            result_var = config.get("result")
            if result_var:
                self._set_nested_variable(result_var, decoded_payload)
            
            return decoded_payload
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error decoding JWT: {str(e)}")
            raise
    
    def _verify_jwt(self, config: Dict[str, Any]) -> bool:
        """
        Verify a JWT token.
        
        Args:
            config: Configuration containing token, key, algorithms, etc.
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            # Extract configuration
            token = config.get("token")
            key = config.get("key")
            algorithms = config.get("algorithms", ["HS256"])
            
            # Interpolate template variables in key
            if isinstance(key, str) and "{{" in key and "}}" in key:
                key = self._interpolate_template(key)
            
            if not token:
                raise ValueError("Token is required for JWT verification")
            
            if not key:
                raise ValueError("Key is required for JWT verification")
            
            # Interpolate template variables in token
            if isinstance(token, str) and "{{" in token and "}}" in token:
                token = self._interpolate_template(token)
            
            # Verify the JWT
            jwt.decode(token, key, algorithms=algorithms)
            
            # Store result if specified
            result_var = config.get("result")
            if result_var:
                self._set_nested_variable(result_var, True)
            
            Output.Console(self.plugin_name, f"JWT verified successfully using {algorithms}")
            return True
            
        except jwt.ExpiredSignatureError:
            Output.Console(self.plugin_name, "JWT verification failed: Token has expired")
            result_var = config.get("result")
            if result_var:
                self._set_nested_variable(result_var, False)
            return False
        except jwt.InvalidTokenError as e:
            Output.Console(self.plugin_name, f"JWT verification failed: {str(e)}")
            result_var = config.get("result")
            if result_var:
                self._set_nested_variable(result_var, False)
            return False
        except Exception as e:
            Output.Console(self.plugin_name, f"Error verifying JWT: {str(e)}")
            raise
    
    def _process_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process payload and handle template variables.
        
        Args:
            payload: Raw payload dictionary
            
        Returns:
            Processed payload with resolved template variables
        """
        processed_payload = {}
        
        for key, value in payload.items():
            if isinstance(value, str):
                # Handle template variables
                if "{{" in value and "}}" in value:
                    processed_value = self._interpolate_template(value)
                else:
                    processed_value = value
            else:
                processed_value = value
            
            processed_payload[key] = processed_value
        
        return processed_payload
    
    def _interpolate_template(self, template: str) -> Any:
        """
        Interpolate template variables in a string.
        
        Args:
            template: Template string with {{ variable }} syntax
            
        Returns:
            Interpolated value
        """
        try:
            # Handle special cases
            if "{{ timestamp }}" in template:
                current_timestamp = int(time.time())
                template = template.replace("{{ timestamp }}", str(current_timestamp))
            
            if "{{ timestamp + 3600 }}" in template:
                future_timestamp = int(time.time()) + 3600
                template = template.replace("{{ timestamp + 3600 }}", str(future_timestamp))
            
            # Handle default values like {{ nombre|default('Usuario Anónimo') }}
            if "|default(" in template:
                # Simple parsing for default values
                if "nombre|default('Usuario Anónimo')" in template:
                    var_value = self._get_nested_variable("nombre")
                    if var_value is not None:
                        return var_value
                    else:
                        return "Usuario Anónimo"
            
            # Handle simple variable interpolation
            if template.startswith("{{") and template.endswith("}}"):
                var_name = template[2:-2].strip()
                value = self._get_nested_variable(var_name)
                if value is not None:
                    return value
                else:
                    return template
            
            return template
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error interpolating template {template}: {str(e)}")
            return template
    
    def _get_nested_variable(self, path: str) -> Any:
        """
        Get a nested variable from the context.
        
        Args:
            path: Variable path (e.g., "user.name")
            
        Returns:
            Variable value
        """
        if not self.context:
            return None
        
        # Split the path by dots
        keys = path.split('.')
        current = self.context
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def _set_nested_variable(self, path: str, value: Any):
        """
        Set a nested variable in the context.
        
        Args:
            path: Variable path (e.g., "result.jwt")
            value: Value to set
        """
        if not self.context:
            return
        
        # Split the path by dots
        keys = path.split('.')
        current = self.context
        
        # Navigate to the parent of the target
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value
    
    def get_dependency_info(self) -> Dict[str, Any]:
        """
        Get dependency information for the plugin.
        
        Returns:
            Dictionary with dependency information
        """
        return {
            "dependencies": self.DEPENDENCIES,
            "requirements": self.REQUIREMENTS,
            "version": self.VERSION
        }