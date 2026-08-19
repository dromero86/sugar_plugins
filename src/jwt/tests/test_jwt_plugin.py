"""
Test JWT Plugin
==============

Test script to verify the JWT plugin functionality.
"""

import sys
import os
import time

# Add the parent directory to the path to import the plugin
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from plugins.jwt.jwt_plugin import JwtPlugin

def test_jwt_plugin():
    """Test the JWT plugin functionality."""
    
    # Test context with variables
    context = {
        "nombre": "Juan Pérez",
        "secret_key": "my-secret-key-123",
        "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----",
        "user": {
            "id": "12345",
            "email": "juan@example.com"
        }
    }
    
    # Initialize the plugin
    jwt_plugin = JwtPlugin(context=context)
    
    print("Testing JWT Plugin...")
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
        encoded_token = jwt_plugin.execute("encode", encode_config)
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
        decoded_payload = jwt_plugin.execute("decode", decode_config)
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
        unverified_payload = jwt_plugin.execute("decode", decode_unverified_config)
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
        is_valid = jwt_plugin.execute("verify", verify_config)
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
    
    jwt_plugin2 = JwtPlugin(context=context_without_nombre)
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
        encoded_token_default = jwt_plugin2.execute("encode", encode_config_default)
        decoded_default = jwt_plugin2.execute("decode", {
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
    success = test_jwt_plugin()
    sys.exit(0 if success else 1)