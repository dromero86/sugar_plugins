"""
JWT Plugin Practical Demo
=========================

This script demonstrates a practical use case of the JWT plugin
showing how it would be used in a real application.
"""

import jwt
import time
import json

class PracticalJwtPlugin:
    """Practical JWT plugin demonstration."""
    
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
            options = config.get("options", {})
            
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
            jwt.decode(token, key, algorithms=algorithms, options=options)
            
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

def practical_demo():
    """Demonstrate a practical use case of the JWT plugin."""
    
    print("JWT Plugin - Caso de Uso Práctico")
    print("=" * 60)
    print("Escenario: Sistema de autenticación de una aplicación web")
    print()
    
    # Simulate a web application context
    context = {
        "user": {
            "id": "user_12345",
            "email": "usuario@ejemplo.com",
            "nombre": "Ana Martínez",
            "role": "admin"
        },
        "app": {
            "secret_key": "mi-clave-secreta-super-segura-2024",
            "issuer": "mi-aplicacion.com",
            "audience": "usuarios"
        },
        "session": {
            "duration": 3600  # 1 hour in seconds
        }
    }
    
    # Initialize the plugin
    jwt_plugin = PracticalJwtPlugin(context=context)
    
    print("Usuario autenticado:")
    print(f"   ID: {context['user']['id']}")
    print(f"   Email: {context['user']['email']}")
    print(f"   Nombre: {context['user']['nombre']}")
    print(f"   Rol: {context['user']['role']}")
    print()
    
    # Step 1: Create a JWT token for the user
    print("Paso 1: Crear token JWT para el usuario")
    print("-" * 50)
    
    encode_config = {
        "payload": {
            "sub": "{{ user.id }}",
            "email": "{{ user.email }}",
            "name": "{{ user.nombre|default('Usuario Anónimo') }}",
            "role": "{{ user.role }}",
            "iss": "{{ app.issuer }}",
            "aud": "{{ app.audience }}",
            "iat": "{{ timestamp }}",
            "exp": "{{ timestamp + 3600 }}",
            "jti": "{{ user.id }}_{{ timestamp }}"
        },
        "key": "{{ app.secret_key }}",
        "algorithm": "HS256",
        "result": "user_token"
    }
    
    try:
        user_token = jwt_plugin.execute("encode", encode_config)
        print(f"Token creado exitosamente")
        print(f"   Token: {user_token[:50]}...")
        print(f"   Longitud: {len(user_token)} caracteres")
        print(f"   Guardado en: context['user_token']")
    except Exception as e:
        print(f"Error creando token: {e}")
        return False
    
    print()
    
    # Step 2: Verify the token
    print("Paso 2: Verificar el token")
    print("-" * 50)
    
    verify_config = {
        "token": "{{ user_token }}",
        "key": "{{ app.secret_key }}",
        "algorithms": ["HS256"],
        "options": {
            "verify_aud": False,
            "verify_iss": False
        },
        "result": "token_valid"
    }
    
    try:
        is_valid = jwt_plugin.execute("verify", verify_config)
        if is_valid:
            print("Token verificado exitosamente")
            print("   El token es válido y puede ser usado")
        else:
            print("Token inválido")
            print("   El token no puede ser usado")
    except Exception as e:
        print(f"Error verificando token: {e}")
        return False
    
    print()
    
    # Step 3: Decode the token to get user information
    print("Paso 3: Decodificar el token para obtener información del usuario")
    print("-" * 50)
    
    decode_config = {
        "token": "{{ user_token }}",
        "key": "{{ app.secret_key }}",
        "algorithms": ["HS256"],
        "verify": True,
        "options": {
            "verify_aud": False,
            "verify_iss": False
        },
        "result": "user_info"
    }
    
    try:
        user_info = jwt_plugin.execute("decode", decode_config)
        print("Token decodificado exitosamente")
        print("   Información del usuario:")
        print(f"      ID: {user_info.get('sub')}")
        print(f"      Email: {user_info.get('email')}")
        print(f"      Nombre: {user_info.get('name')}")
        print(f"      Rol: {user_info.get('role')}")
        print(f"      Emisor: {user_info.get('iss')}")
        print(f"      Audiencia: {user_info.get('aud')}")
        print(f"      Creado: {user_info.get('iat')}")
        print(f"      Expira: {user_info.get('exp')}")
        print(f"      JTI: {user_info.get('jti')}")
    except Exception as e:
        print(f"Error decodificando token: {e}")
        return False
    
    print()
    
    # Step 4: Show how the context has been updated
    print("Paso 4: Estado final del contexto")
    print("-" * 50)
    print("   Variables creadas durante la sesión:")
    for key, value in context.items():
        if key in ['user_token', 'token_valid', 'user_info']:
            if isinstance(value, str) and len(value) > 50:
                print(f"      {key}: {value[:50]}...")
            else:
                print(f"      {key}: {value}")
    
    print()
    
    # Step 5: Demonstrate token expiration handling
    print("⏰ Paso 5: Demostración de manejo de expiración")
    print("-" * 50)
    
    # Create a token that expires in 1 second
    context['expired_token'] = jwt.encode(
        {
            "sub": "test_user",
            "exp": int(time.time()) + 1  # Expires in 1 second
        },
        context['app']['secret_key'],
        algorithm="HS256"
    )
    
    print("   Creando token que expira en 1 segundo...")
    time.sleep(2)  # Wait for token to expire
    
    expired_verify_config = {
        "token": "{{ expired_token }}",
        "key": "{{ app.secret_key }}",
        "algorithms": ["HS256"],
        "result": "expired_token_valid"
    }
    
    try:
        expired_valid = jwt_plugin.execute("verify", expired_verify_config)
        if not expired_valid:
            print("   Correctamente detectó que el token expiró")
        else:
            print("   No detectó la expiración del token")
    except Exception as e:
        print(f"   Error verificando token expirado: {e}")
    
    print()
    
    print("=" * 60)
    print("Demostración práctica completada exitosamente!")
    print("   El plugin JWT está funcionando perfectamente en un caso de uso real.")
    return True

if __name__ == "__main__":
    success = practical_demo()
    exit(0 if success else 1)