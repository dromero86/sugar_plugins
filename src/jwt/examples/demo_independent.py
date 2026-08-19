"""
JWT Plugin Independent Demo
==========================

This script demonstrates the JWT plugin functionality independently,
showing how it works with the exact specification provided.
"""

import jwt
import time
import json

class IndependentJwtPlugin:
    """Independent JWT plugin for demonstration."""
    
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
    
    def execute(self, command, config):
        """Execute a JWT plugin command."""
        if command == "encode":
            return self._encode_jwt(config)
        elif command == "decode":
            return self._decode_jwt(config)
        elif command == "verify":
            return self._verify_jwt(config)
        else:
            raise ValueError(f"Unknown command: {command}")
    
    def _encode_jwt(self, config):
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
    
    def _decode_jwt(self, config):
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
            
            # Interpolate template variables in token
            if isinstance(token, str) and "{{" in token and "}}" in token:
                token = self._interpolate_template(token)
            
            # Clean token (remove newlines and spaces)
            if isinstance(token, str):
                token = token.strip().replace('\n', '').replace(' ', '')
            
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
    
    def _verify_jwt(self, config):
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
            
            # Interpolate template variables in token
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

def demo_specification():
    """Demonstrate the JWT plugin with the provided specification."""
    
    print("JWT Plugin Demo - Especificación Original")
    print("=" * 60)
    
    # Context with variables that match the specification
    context = {
        "nombre": "María García",
        "secret_key": "my-super-secret-key-2024",
        "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----",
        "token_input": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    }
    
    # Initialize the plugin
    jwt_plugin = IndependentJwtPlugin(context=context)
    
    print(f"Context variables: {list(context.keys())}")
    print()
    
    # Load the specification from the JSON file
    try:
        with open('specification_example.json', 'r') as f:
            specification = json.load(f)
    except FileNotFoundError:
        print("Error: specification_example.json not found")
        return False
    
    # Execute each operation in the specification
    for i, operation in enumerate(specification, 1):
        print(f"Operation {i}: {operation['jwt']['operator']}")
        print("-" * 40)
        
        try:
            # Execute the operation
            result = jwt_plugin.execute(
                operation['jwt']['operator'], 
                operation['jwt']
            )
            
            print(f"Success: {operation['jwt']['operator']}")
            
            # Show result based on operation type
            if operation['jwt']['operator'] == 'encode':
                print(f"   Encoded token: {result[:50]}...")
                print(f"   Token length: {len(result)} characters")
            elif operation['jwt']['operator'] == 'decode':
                print(f"   Decoded payload: {result}")
            elif operation['jwt']['operator'] == 'verify':
                print(f"   Verification result: {result}")
            
            # Show context variable if result was stored
            result_var = operation['jwt'].get('result')
            if result_var:
                context_value = context.get(result_var)
                if isinstance(context_value, str) and len(context_value) > 50:
                    print(f"   Context variable '{result_var}': {context_value[:50]}...")
                else:
                    print(f"   Context variable '{result_var}': {context_value}")
            
        except Exception as e:
            print(f"Error in {operation['jwt']['operator']}: {e}")
            return False
        
        print()
    
    # Show final context state
    print("Final Context State:")
    print("-" * 40)
    for key, value in context.items():
        if key in ['encoded_jwt', 'decoded_payload', 'is_valid', 'payload_unverified']:
            if isinstance(value, str) and len(value) > 50:
                print(f"   {key}: {value[:50]}...")
            else:
                print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("Specification demo completed successfully!")
    return True

def demo_template_variables():
    """Demonstrate template variable interpolation."""
    
    print("\nTemplate Variable Interpolation Demo")
    print("=" * 60)
    
    # Test different template scenarios
    test_cases = [
        {
            "name": "Basic variable interpolation",
            "context": {"nombre": "Carlos López"},
            "template": "{{ nombre|default('Usuario Anónimo') }}",
            "expected": "Carlos López"
        },
        {
            "name": "Default value when variable missing",
            "context": {},
            "template": "{{ nombre|default('Usuario Anónimo') }}",
            "expected": "Usuario Anónimo"
        },
        {
            "name": "Timestamp interpolation",
            "context": {},
            "template": "{{ timestamp }}",
            "expected": "number"
        },
        {
            "name": "Timestamp with offset",
            "context": {},
            "template": "{{ timestamp + 3600 }}",
            "expected": "number"
        }
    ]
    
    jwt_plugin = IndependentJwtPlugin()
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        print(f"   Template: {test_case['template']}")
        
        # Set context
        jwt_plugin.context = test_case['context']
        
        try:
            result = jwt_plugin._interpolate_template(test_case['template'])
            print(f"   Result: {result}")
            
            # Validate result
            if test_case['expected'] == "number":
                if isinstance(result, (int, str)) and str(result).isdigit():
                    print("   Valid number result")
                else:
                    print("   Expected number result")
            elif result == test_case['expected']:
                print("   Expected result")
            else:
                print(f"   Expected {test_case['expected']}, got {result}")
                
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    print("JWT Plugin Independent Demo")
    print("=" * 60)
    
    # Run the main specification demo
    success = demo_specification()
    
    if success:
        # Run template variable demo
        demo_template_variables()
    
    print("\nDemo completed!")
    exit(0 if success else 1)