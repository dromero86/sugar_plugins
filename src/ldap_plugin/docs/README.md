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

## Uso

### Conexión Básica

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

### Búsqueda en el Directorio

```json
{
  "ldap": {
    "operator": "search",
    "connection_name": "main_server",
    "base_dn": "dc=example,dc=com",
    "search_filter": "(objectClass=person)",
    "attributes": ["cn", "uid", "mail"],
    "result": "search_results"
  }
}
```

### Autenticación de Usuario

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

Ver el directorio `examples/` para ejemplos completos de uso.

## Configuración Avanzada

### Conexión SSL/TLS

```json
{
  "ldap": {
    "operator": "connect",
    "server": "ldap.example.com",
    "port": 636,
    "use_ssl": true,
    "username": "cn=admin,dc=example,dc=com",
    "password": "admin_password",
    "connection_name": "secure_server"
  }
}
```

### Conexión TLS

```json
{
  "ldap": {
    "operator": "connect",
    "server": "ldap.example.com",
    "port": 389,
    "use_tls": true,
    "username": "cn=admin,dc=example,dc=com",
    "password": "admin_password",
    "connection_name": "tls_server"
  }
}
```

### Búsqueda con Filtros Personalizados

```json
{
  "ldap": {
    "operator": "search_users",
    "connection_name": "main_server",
    "base_dn": "ou=users,dc=example,dc=com",
    "search_filter": "(&(objectClass=person)(uid=john*))",
    "attributes": ["cn", "uid", "mail", "sn", "givenName"],
    "result": "john_users"
  }
}
```

## Manejo de Errores

El plugin incluye manejo robusto de errores para:

- Errores de conexión
- Errores de autenticación
- Errores de búsqueda
- Errores de permisos
- Errores de dependencias

Todos los errores se registran en el sistema de logging de Sugar y se devuelven en el formato estándar:

```json
{
  "status": "error",
  "message": "Descripción del error"
}
```

## Mejores Prácticas

1. **Seguridad**: Usar conexiones SSL/TLS para datos sensibles
2. **Conexiones**: Cerrar conexiones cuando no se usen
3. **Filtros**: Usar filtros específicos para mejorar el rendimiento
4. **Atributos**: Solicitar solo los atributos necesarios
5. **Manejo de Errores**: Verificar siempre el status de las operaciones
6. **Variables**: Usar interpolación de variables para configuraciones reutilizables

## Troubleshooting

### Problemas Comunes

1. **Error de conexión**: Verificar servidor, puerto y credenciales
2. **Error de autenticación**: Verificar DN y contraseña del usuario
3. **Error de permisos**: Verificar permisos del usuario de conexión
4. **Error de dependencias**: Instalar python-ldap si no está disponible

### Debug

Habilitar logging detallado para debug:

```json
{
  "ldap": {
    "operator": "test_connection",
    "connection_name": "main_server",
    "result": "test_result"
  }
}
```

## Soporte

Para soporte técnico, consultar la documentación de Sugar o crear un issue en el repositorio del proyecto.