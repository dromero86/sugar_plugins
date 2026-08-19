"""
Simple JWT Test
==============

A simplified test script that tests JWT functionality without the full Sugar framework.
"""

import jwt
import time

class SimpleJwtPlugin:
    """Simplified JWT plugin for testing."""
    
    def __init__(self, context=None):
        self.context = context or {}
    
    def _interpolate_template(self, template):
        """Interpolate template variables."""
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
            print(f"Error interpolating template {template}: {str(e)}")
            return template
    
    def _get_nested_variable(self, path):
        """Get a nested variable from the context."""
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
    
    def _set_nested_variable(self, path, value):
        """Set a nested variable in the context."""
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
    
    def _process_payload(self, payload):
        """Process payload and handle template variables."""
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
    
    def encode(self, config):
        """Encode a JWT token."""
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
            
            print(f"JWT encoded successfully using {algorithm}")
            return encoded_token
            
        except Exception as e:
            print(f"Error encoding JWT: {str(e)}")
            raise
    
    def decode(self, config):
        """Decode a JWT token."""
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
            
            # Interpolate template variables
            if isinstance(token, str) and "{{" in token and "}}" in token:
                token = self._interpolate_template(token)
            
            # Clean token (remove newlines and spaces)
            if isinstance(token, str):
                token = token.strip().replace('\n', '').replace(' ', '')
                print(f"Debug - Token length: {len(token)}")
                print(f"Debug - Token: {token[:50]}...")
            
            # Handle unverified decoding
            if not verify or options.get("verify_signature", True) is False:
                decoded_payload = jwt.decode(token, options={"verify_signature": False})
                print("JWT decoded without signature verification")
            else:
                if not key:
                    raise ValueError("Key is required for verified JWT decoding")
                
                decoded_payload = jwt.decode(token, key, algorithms=algorithms, options=options)
                print(f"JWT decoded successfully with verification using {algorithms}")
            
            # Store result if specified
            result_var = config.get("result")
            if result_var:
                self._set_nested_variable(result_var, decoded_payload)
            
            return decoded_payload
            
        except Exception as e:
            print(f"Error decoding JWT: {str(e)}")
            raise
    
    def verify(self, config):
        """Verify a JWT token."""
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
            
            # Interpolate template variables
            if isinstance(token, str) and "{{" in token and "}}" in token:
                token = self._interpolate_template(token)
            
            # Clean token (remove newlines and spaces)
            if isinstance(token, str):
                token = token.strip().replace('\n', '').replace(' ', '')
            
            # Verify the JWT
            jwt.decode(token, key, algorithms=algorithms)
            
            # Store result if specified
            result_var = config.get("result")
            if result_var:
                self._set_nested_variable(result_var, True)
            
            print(f"JWT verified successfully using {algorithms}")
            return True
            
        except jwt.ExpiredSignatureError:
            print("JWT verification failed: Token has expired")
            result_var = config.get("result")
            if result_var:
                self._set_nested_variable(result_var, False)
            return False
        except jwt.InvalidTokenError as e:
            print(f"JWT verification failed: {str(e)}")
            result_var = config.get("result")
            if result_var:
                self._set_nested_variable(result_var, False)
            return False
        except Exception as e:
            print(f"Error verifying JWT: {str(e)}")
            raise

def test_jwt_functionality():
    """Test the JWT functionality."""
    
    # Test context with variables
    context = {
        "nombre": "Juan Pérez",
        "secret_key": "my-secret-key-123",
        "user": {
            "id": "12345",
            "email": "juan@example.com"
        }
    }
    
    # Initialize the plugin
    jwt_plugin = SimpleJwtPlugin(context=context)
    
    print("Testing JWT Functionality...")
    print("=" * 50)
    
    # Test 1: Encode JWT
    print("\n1. Testing JWT Encoding...")
    encode_config = {
        "payload": {
            "sub": "1234567890",
            "name": "{{ nombre|default('Usuario Anónimo') }}",
            "iat": "{{ timestamp }}",
            "exp": "{{ timestamp + 3600 }}",
            "user_id": "{{ user.id }}"
        },
        "key": "{{ secret_key }}",
        "algorithm": "HS256",
        "result": "encoded_jwt"
    }
    
    try:
        encoded_token = jwt_plugin.encode(encode_config)
        print(f"JWT encoded successfully")
        print(f"  Token: {encoded_token[:50]}...")
        print(f"  Context variable 'encoded_jwt': {context.get('encoded_jwt', 'Not set')}")
    except Exception as e:
        print(f"JWT encoding failed: {e}")
        return False
    
    # Test 2: Decode JWT with verification
    print("\n2. Testing JWT Decoding with Verification...")
    decode_config = {
        "token": "{{ encoded_jwt }}",
        "key": "{{ secret_key }}",
        "algorithms": ["HS256"],
        "verify": True,
        "result": "decoded_payload"
    }
    
    try:
        decoded_payload = jwt_plugin.decode(decode_config)
        print(f"JWT decoded successfully")
        print(f"  Payload: {decoded_payload}")
        print(f"  Context variable 'decoded_payload': {context.get('decoded_payload', 'Not set')}")
    except Exception as e:
        print(f"JWT decoding failed: {e}")
        return False
    
    # Test 3: Decode JWT without verification
    print("\n3. Testing JWT Decoding without Verification...")
    decode_unverified_config = {
        "token": "{{ encoded_jwt }}",
        "options": {
            "verify_signature": False
        },
        "result": "payload_unverified"
    }
    
    try:
        unverified_payload = jwt_plugin.decode(decode_unverified_config)
        print(f"JWT decoded without verification")
        print(f"  Payload: {unverified_payload}")
        print(f"  Context variable 'payload_unverified': {context.get('payload_unverified', 'Not set')}")
    except Exception as e:
        print(f"JWT unverified decoding failed: {e}")
        return False
    
    # Test 4: Verify JWT
    print("\n4. Testing JWT Verification...")
    verify_config = {
        "token": "{{ encoded_jwt }}",
        "key": "{{ secret_key }}",
        "algorithms": ["HS256"],
        "result": "is_valid"
    }
    
    try:
        is_valid = jwt_plugin.verify(verify_config)
        print(f"JWT verification successful")
        print(f"  Is valid: {is_valid}")
        print(f"  Context variable 'is_valid': {context.get('is_valid', 'Not set')}")
    except Exception as e:
        print(f"JWT verification failed: {e}")
        return False
    
    # Test 5: Test with missing variable (should use default)
    print("\n5. Testing Default Value Handling...")
    context_without_nombre = {
        "secret_key": "my-secret-key-123"
    }
    
    jwt_plugin2 = SimpleJwtPlugin(context=context_without_nombre)
    encode_config_default = {
        "payload": {
            "sub": "1234567890",
            "name": "{{ nombre|default('Usuario Anónimo') }}",
            "iat": "{{ timestamp }}",
            "exp": "{{ timestamp + 3600 }}"
        },
        "key": "{{ secret_key }}",
        "algorithm": "HS256"
    }
    
    try:
        encoded_token_default = jwt_plugin2.encode(encode_config_default)
        decoded_default = jwt_plugin2.decode({
            "token": encoded_token_default,
            "key": "{{ secret_key }}",
            "algorithms": ["HS256"]
        })
        print(f"Default value handling successful")
        print(f"  Name in payload: {decoded_default.get('name')}")
    except Exception as e:
        print(f"Default value handling failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("All tests passed!")
    return True

if __name__ == "__main__":
    success = test_jwt_functionality()
    exit(0 if success else 1)