"""
JWT Plugin Specification Demo
============================

This script demonstrates how to use the JWT plugin with the exact specification
provided by the user.
"""

import sys
import os
import json

# Add the parent directory to the path to import the plugin
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from plugins.jwt.jwt_plugin import JwtPlugin

def demo_specification():
    """Demonstrate the JWT plugin with the provided specification."""
    
    # Context with variables that match the specification
    context = {
        "nombre": "María García",
        "secret_key": "my-super-secret-key-2024",
        "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----",
        "token_input": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    }
    
    # Initialize the plugin
    jwt_plugin = JwtPlugin(context=context)
    
    print("JWT Plugin Specification Demo")
    print("=" * 50)
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
        print("-" * 30)
        
        try:
            # Execute the operation
            result = jwt_plugin.execute(
                operation['jwt']['operator'], 
                operation['jwt']
            )
            
            print(f"Success: {operation['jwt']['operator']}")
            
            # Show result based on operation type
            if operation['jwt']['operator'] == 'encode':
                print(f"  Encoded token: {result[:50]}...")
            elif operation['jwt']['operator'] == 'decode':
                print(f"  Decoded payload: {result}")
            elif operation['jwt']['operator'] == 'verify':
                print(f"  Verification result: {result}")
            
            # Show context variable if result was stored
            result_var = operation['jwt'].get('result')
            if result_var:
                context_value = context.get(result_var)
                print(f"  Context variable '{result_var}': {context_value}")
            
        except Exception as e:
            print(f"Error in {operation['jwt']['operator']}: {e}")
            return False
        
        print()
    
    # Show final context state
    print("Final Context State:")
    print("-" * 30)
    for key, value in context.items():
        if key in ['encoded_jwt', 'decoded_payload', 'is_valid', 'payload_unverified']:
            if isinstance(value, str) and len(value) > 50:
                print(f"  {key}: {value[:50]}...")
            else:
                print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    print("Specification demo completed successfully!")
    return True

def demo_template_variables():
    """Demonstrate template variable interpolation."""
    
    print("\nTemplate Variable Interpolation Demo")
    print("=" * 50)
    
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
    
    jwt_plugin = JwtPlugin()
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        print(f"  Template: {test_case['template']}")
        
        # Set context
        jwt_plugin.context = test_case['context']
        
        try:
            result = jwt_plugin._interpolate_template(test_case['template'])
            print(f"  Result: {result}")
            
            # Validate result
            if test_case['expected'] == "number":
                if isinstance(result, (int, str)) and str(result).isdigit():
                    print("  Valid number result")
                else:
                    print("  Expected number result")
            elif result == test_case['expected']:
                print("  Expected result")
            else:
                print(f"  Expected {test_case['expected']}, got {result}")
                
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    print("JWT Plugin Specification Demo")
    print("=" * 50)
    
    # Run the main specification demo
    success = demo_specification()
    
    if success:
        # Run template variable demo
        demo_template_variables()
    
    sys.exit(0 if success else 1)