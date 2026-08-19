"""
JWT Plugin Example
=================

This example demonstrates how to use the JWT plugin with the provided specification.
"""

# Example usage of the JWT plugin

# 1. Encode JWT with template variables
encode_config = {
    "jwt": {
        "operator": "encode",
        "payload": {
            "sub": "1234567890",
            "name": "{{ nombre|default('Usuario Anónimo') }}",
            "iat": "{{ timestamp }}",
            "exp": "{{ timestamp + 3600 }}"
        },
        "key": "{{ secret_key }}",
        "algorithm": "HS256",
        "result": "encoded_jwt"
    }
}

# 2. Decode JWT with verification
decode_config = {
    "jwt": {
        "operator": "decode",
        "token": "{{ encoded_jwt }}",
        "key": "{{ secret_key }}",
        "algorithms": ["HS256"],
        "verify": True,
        "result": "decoded_payload"
    }
}

# 3. Verify JWT with RS256
verify_config = {
    "jwt": {
        "operator": "verify",
        "token": "{{ token_input }}",
        "key": "{{ public_key }}",
        "algorithms": ["RS256"],
        "result": "is_valid"
    }
}

# 4. Decode JWT without verification
decode_unverified_config = {
    "jwt": {
        "operator": "decode",
        "token": "{{ token_input }}",
        "options": {
            "verify_signature": False
        },
        "result": "payload_unverified"
    }
}

# Example context with variables
example_context = {
    "nombre": "Juan Pérez",
    "secret_key": "my-secret-key-123",
    "public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
    "token_input": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# Example usage in Sugar:
"""
# Initialize the plugin
jwt_plugin = JwtPlugin(context=example_context)

# Encode a JWT
encoded_token = jwt_plugin.execute("encode", encode_config["jwt"])

# Decode and verify the JWT
decoded_payload = jwt_plugin.execute("decode", decode_config["jwt"])

# Verify a JWT
is_valid = jwt_plugin.execute("verify", verify_config["jwt"])

# Decode without verification
unverified_payload = jwt_plugin.execute("decode", decode_unverified_config["jwt"])
"""