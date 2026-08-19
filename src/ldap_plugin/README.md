# LDAP Plugin para Sugar

Plugin de Lightweight Directory Access Protocol (LDAP) para Sugar que proporciona operaciones completas de servicios de directorio.

## Características

- **Gestión de Conexiones**: Conexión a servidores LDAP con soporte SSL/TLS
- **Autenticación**: Autenticación de usuarios contra directorios LDAP
- **Operaciones de Búsqueda**: Búsqueda de usuarios, grupos y otros objetos del directorio
- **Gestión de Usuarios**: Crear, modificar, eliminar y gestionar cuentas de usuario
- **Gestión de Grupos**: Crear, modificar, eliminar y gestionar grupos
- **Gestión de Esquemas**: Acceso a información del esquema LDAP
- **Manejo de Errores**: Manejo robusto de errores y logging

## Instalación

1. Instalar la dependencia requerida:
   ```bash
   pip install python-ldap
   ```

2. El plugin será cargado automáticamente por Sugar.

## Uso Básico

### Conexión a LDAP

```json
{
  "ldap": {
    "operator": "connect",
    "server": "ldap.example.com",
    "port": 389,
    "username": "cn=admin,dc=example,dc=com",
    "password": "admin_password",
    "connection_name": "main_server"
  }
}
```

### Búsqueda de Usuarios

```json
{
  "ldap": {
    "operator": "search_users",
    "connection_name": "main_server",
    "base_dn": "dc=example,dc=com",
    "result": "users"
  }
}
```

### Autenticación

```json
{
  "ldap": {
    "operator": "authenticate",
    "connection_name": "main_server",
    "username": "cn=john.doe,ou=users,dc=example,dc=com",
    "password": "user_password",
    "result": "auth_result"
  }
}
```

## Comandos Disponibles

### Gestión de Conexiones
- `connect`: Establecer conexión a servidor LDAP
- `disconnect`: Desconectar del servidor LDAP
- `test_connection`: Probar conexión LDAP
- `list_connections`: Listar conexiones activas

### Operaciones de Búsqueda
- `search`: Realizar búsqueda LDAP general
- `search_users`: Buscar usuarios
- `search_groups`: Buscar grupos
- `search_computers`: Buscar computadoras

### Autenticación
- `authenticate`: Autenticar usuario contra LDAP
- `bind`: Vincular con credenciales
- `unbind`: Desvincular de LDAP
- `verify_credentials`: Verificar credenciales de usuario

### Gestión de Usuarios
- `create_user`: Crear nuevo usuario
- `modify_user`: Modificar atributos de usuario
- `delete_user`: Eliminar usuario
- `enable_user`: Habilitar cuenta de usuario
- `disable_user`: Deshabilitar cuenta de usuario
- `reset_password`: Restablecer contraseña de usuario
- `unlock_user`: Desbloquear cuenta de usuario
- `get_user_info`: Obtener información de usuario
- `list_users`: Listar todos los usuarios

### Gestión de Grupos
- `create_group`: Crear nuevo grupo
- `modify_group`: Modificar atributos de grupo
- `delete_group`: Eliminar grupo
- `add_user_to_group`: Agregar usuario a grupo
- `remove_user_from_group`: Remover usuario de grupo
- `get_group_info`: Obtener información de grupo
- `list_groups`: Listar todos los grupos

### Esquema y Estructura
- `get_schema`: Obtener información del esquema LDAP
- `get_dn_info`: Obtener información sobre un DN
- `list_attributes`: Listar atributos disponibles
- `get_base_dn`: Obtener información del DN base

### Utilidades
- `check_dependencies`: Verificar dependencias del plugin
- `system_info`: Obtener información del sistema
- `test_functionality`: Probar funcionalidad del plugin

## Dependencias

- `python-ldap>=3.4.0`: Biblioteca Python para LDAP

## Ejemplos

Ver el directorio `examples/` para ejemplos completos de uso:

- `basic_connection.json`: Conexión básica y búsqueda
- `authentication.json`: Autenticación de usuarios
- `user_search.json`: Búsqueda avanzada de usuarios

## Documentación

Ver el directorio `docs/` para documentación detallada.

## Ejecución

Para ejecutar los ejemplos, usar uno de estos comandos desde la raíz del workspace:

```bash
# Recomendado
virtual/bin/python3 Sugar/Service/SugarConsole.py plugins/src/ldap/examples/basic_connection.json

# Alternativa
virtual/bin/python Sugar/Service/SugarConsole.py plugins/src/ldap/examples/basic_connection.json

# Si el entorno virtual está activado
python3 Sugar/Service/SugarConsole.py plugins/src/ldap/examples/basic_connection.json
```

## Estructura del Plugin

```
plugins/src/ldap/
├── __init__.py                 # Configuración del plugin
├── src/                        # Código fuente
│   ├── __init__.py            # Configuración de componentes
│   ├── LDAPPlugin.py          # Clase principal del plugin
│   ├── LDAPConnection.py      # Gestión de conexiones
│   ├── LDAPSearch.py          # Operaciones de búsqueda
│   ├── LDAPUserManagement.py  # Gestión de usuarios
│   └── LDAPGroupManagement.py # Gestión de grupos
├── docs/                       # Documentación
│   └── README.md              # Documentación detallada
├── examples/                   # Ejemplos de uso
│   ├── basic_connection.json  # Conexión básica
│   ├── authentication.json    # Autenticación
│   └── user_search.json       # Búsqueda de usuarios
├── tests/                      # Tests (pendiente)
├── requirements.txt            # Dependencias
└── README.md                   # Este archivo
```

## Licencia

MIT License - Ver archivo LICENSE para más detalles.