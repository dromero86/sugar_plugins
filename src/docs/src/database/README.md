# Database Plugin

El plugin Database proporciona funcionalidades para interactuar con bases de datos relacionales y NoSQL, incluyendo operaciones CRUD, consultas complejas y gestión de transacciones.

## Características

- **Múltiples bases de datos**: MySQL, PostgreSQL, SQLite, MongoDB, Redis
- **Operaciones CRUD**: Create, Read, Update, Delete
- **Consultas complejas**: JOINs, subconsultas, agregaciones
- **Transacciones**: Gestión de transacciones ACID
- **Connection pooling**: Pool de conexiones para mejor rendimiento
- **Migraciones**: Gestión de esquemas de base de datos
- **Backup y restore**: Operaciones de respaldo y restauración

## Instalación

```bash
pip install -r requirements.txt
```

### Dependencias
- `sqlalchemy>=1.4.0`
- `psycopg2-binary>=2.9.0` (PostgreSQL)
- `pymysql>=1.0.0` (MySQL)
- `pymongo>=4.0.0` (MongoDB)
- `redis>=4.0.0` (Redis)

## Uso

### 1. Conexión a Base de Datos

```json
{
  "database": {
    "action": "connect",
    "type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "username": "{{ db_user }}",
    "password": "{{ db_pass }}",
    "result": "db_connection"
  }
}
```

### 2. Consulta SELECT

```json
{
  "database": {
    "action": "query",
    "sql": "SELECT * FROM users WHERE status = 'active'",
    "params": {
      "status": "active"
    },
    "result": "active_users"
  }
}
```

### 3. Insertar Datos

```json
{
  "database": {
    "action": "insert",
    "table": "users",
    "data": {
      "name": "Juan Pérez",
      "email": "juan@example.com",
      "status": "active"
    },
    "result": "inserted_user"
  }
}
```

### 4. Actualizar Datos

```json
{
  "database": {
    "action": "update",
    "table": "users",
    "data": {
      "status": "inactive"
    },
    "where": {
      "email": "juan@example.com"
    },
    "result": "updated_user"
  }
}
```

### 5. Eliminar Datos

```json
{
  "database": {
    "action": "delete",
    "table": "users",
    "where": {
      "status": "inactive"
    },
    "result": "deleted_users"
  }
}
```

## Parámetros

### Configuración de Conexión
- `action` (string, requerido): Acción a realizar
- `type` (string, opcional): Tipo de base de datos (postgresql, mysql, sqlite, mongodb, redis)
- `host` (string, opcional): Host de la base de datos
- `port` (integer, opcional): Puerto de la base de datos
- `database` (string, opcional): Nombre de la base de datos
- `username` (string, opcional): Usuario de la base de datos
- `password` (string, opcional): Contraseña de la base de datos
- `result` (string, opcional): Variable para almacenar el resultado

### Configuración de Consultas
- `sql` (string, opcional): Consulta SQL
- `table` (string, opcional): Nombre de la tabla
- `data` (object, opcional): Datos a insertar/actualizar
- `where` (object, opcional): Condiciones WHERE
- `params` (object, opcional): Parámetros de la consulta

### Configuración Avanzada
- `transaction` (boolean, opcional): Usar transacción
- `timeout` (integer, opcional): Timeout en segundos
- `pool_size` (integer, opcional): Tamaño del pool de conexiones
- `ssl_mode` (string, opcional): Modo SSL

## Operaciones Disponibles

### Gestión de Conexiones
- **connect**: Conectar a base de datos
- **disconnect**: Desconectar de base de datos
- **test_connection**: Probar conexión
- **get_connection_info**: Obtener información de conexión

### Operaciones CRUD
- **query**: Ejecutar consulta SELECT
- **insert**: Insertar datos
- **update**: Actualizar datos
- **delete**: Eliminar datos
- **upsert**: Insertar o actualizar

### Gestión de Esquemas
- **create_table**: Crear tabla
- **drop_table**: Eliminar tabla
- **alter_table**: Modificar tabla
- **create_index**: Crear índice
- **drop_index**: Eliminar índice

### Transacciones
- **begin_transaction**: Iniciar transacción
- **commit**: Confirmar transacción
- **rollback**: Revertir transacción
- **savepoint**: Crear punto de guardado

### Utilidades
- **backup**: Crear respaldo
- **restore**: Restaurar respaldo
- **migrate**: Ejecutar migraciones
- **analyze**: Analizar rendimiento

## Ejemplos Avanzados

### Consulta con JOIN

```json
{
  "database": {
    "action": "query",
    "sql": "SELECT u.name, p.title FROM users u JOIN posts p ON u.id = p.user_id WHERE u.status = 'active'",
    "params": {
      "status": "active"
    },
    "result": "users_with_posts"
  }
}
```

### Transacción Completa

```json
{
  "database": {
    "action": "transaction",
    "operations": [
      {
        "action": "insert",
        "table": "orders",
        "data": {
          "user_id": "{{ user_id }}",
          "total": "{{ order_total }}"
        }
      },
      {
        "action": "update",
        "table": "users",
        "data": {
          "last_order_date": "{{ current_date }}"
        },
        "where": {
          "id": "{{ user_id }}"
        }
      }
    ],
    "result": "order_transaction"
  }
}
```

### Consulta con Agregaciones

```json
{
  "database": {
    "action": "query",
    "sql": "SELECT category, COUNT(*) as count, AVG(price) as avg_price FROM products GROUP BY category HAVING COUNT(*) > 10",
    "result": "product_stats"
  }
}
```

### Migración de Esquema

```json
{
  "database": {
    "action": "migrate",
    "migrations": [
      {
        "version": "001",
        "up": "ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE",
        "down": "ALTER TABLE users DROP COLUMN email_verified"
      }
    ],
    "result": "migration_status"
  }
}
```

### Backup Automático

```json
{
  "database": {
    "action": "backup",
    "backup_path": "/backups/db_$(date +%Y%m%d_%H%M).sql",
    "format": "sql",
    "compress": true,
    "include_schema": true,
    "result": "backup_status"
  }
}
```

### Consulta con Subconsulta

```json
{
  "database": {
    "action": "query",
    "sql": "SELECT * FROM products WHERE price > (SELECT AVG(price) FROM products)",
    "result": "expensive_products"
  }
}
```

## Configuración de Base de Datos

### PostgreSQL
```json
{
  "database": {
    "action": "connect",
    "type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "username": "{{ pg_user }}",
    "password": "{{ pg_pass }}",
    "ssl_mode": "require",
    "pool_size": 10,
    "result": "postgres_connection"
  }
}
```

### MySQL
```json
{
  "database": {
    "action": "connect",
    "type": "mysql",
    "host": "localhost",
    "port": 3306,
    "database": "mydb",
    "username": "{{ mysql_user }}",
    "password": "{{ mysql_pass }}",
    "charset": "utf8mb4",
    "result": "mysql_connection"
  }
}
```

### SQLite
```json
{
  "database": {
    "action": "connect",
    "type": "sqlite",
    "database": "/path/to/database.db",
    "timeout": 30,
    "result": "sqlite_connection"
  }
}
```

### MongoDB
```json
{
  "database": {
    "action": "connect",
    "type": "mongodb",
    "host": "localhost",
    "port": 27017,
    "database": "mydb",
    "username": "{{ mongo_user }}",
    "password": "{{ mongo_pass }}",
    "result": "mongo_connection"
  }
}
```

## Manejo de Errores

### Configuración de Reintentos
```json
{
  "database": {
    "action": "query",
    "sql": "SELECT * FROM large_table",
    "retry": {
      "max_attempts": 3,
      "backoff_factor": 2,
      "timeout": 60
    },
    "result": "robust_query"
  }
}
```

### Validación de Datos
```json
{
  "database": {
    "action": "insert",
    "table": "users",
    "data": {
      "name": "{{ user_name }}",
      "email": "{{ user_email }}"
    },
    "validation": {
      "required": ["name", "email"],
      "email_format": true,
      "unique_constraints": ["email"]
    },
    "result": "validated_insert"
  }
}
```

## Optimización

### Configuración de Rendimiento
```json
{
  "database": {
    "action": "connect",
    "type": "postgresql",
    "performance": {
      "pool_size": 20,
      "max_overflow": 30,
      "pool_timeout": 30,
      "pool_recycle": 3600
    },
    "result": "optimized_connection"
  }
}
```

### Configuración de Consultas
```json
{
  "database": {
    "action": "query",
    "sql": "SELECT * FROM large_table",
    "optimization": {
      "use_index": true,
      "limit": 1000,
      "offset": 0,
      "explain": true
    },
    "result": "optimized_query"
  }
}
```

## Configuración de Seguridad

### Configuración Segura
```json
{
  "database": {
    "action": "connect",
    "type": "postgresql",
    "security": {
      "ssl_mode": "require",
      "ssl_cert": "/path/to/cert.pem",
      "ssl_key": "/path/to/key.pem",
      "ssl_ca": "/path/to/ca.pem",
      "connection_timeout": 10
    },
    "result": "secure_connection"
  }
}
```

## Recursos Adicionales

- [Documentación de SQLAlchemy](https://docs.sqlalchemy.org/)
- [Guía de Bases de Datos](../../../docs/development/database_operations.md) 