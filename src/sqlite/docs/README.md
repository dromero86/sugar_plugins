# Plugin SQLite para Sugar

## Descripción

El plugin SQLite para Sugar proporciona operaciones completas de base de datos SQLite, incluyendo gestión de conexiones, ejecución de consultas, manejo de transacciones, administración de bases de datos e importación/exportación de datos.

## Características

- ✅ **Gestión de conexiones**: Conexión y desconexión a bases de datos SQLite
- ✅ **Operaciones SQL**: Ejecución de consultas SQL personalizadas
- ✅ **Operaciones CRUD**: Insert, Update, Delete, Select simplificados
- ✅ **Gestión de transacciones**: Begin, Commit, Rollback, Savepoints
- ✅ **Administración de BD**: Backup, Restore, Vacuum, Analyze
- ✅ **Importación/Exportación**: CSV y JSON
- ✅ **Información de esquema**: Tablas, índices, triggers, vistas
- ✅ **Sin dependencias externas**: SQLite3 viene incluido en Python

## Instalación

No se requieren dependencias externas. SQLite3 viene incluido en Python por defecto.

```bash
# El plugin está listo para usar
```

## Comandos Disponibles

### Gestión de Conexiones

#### `connect`
Establece conexión a una base de datos SQLite.

```json
{
  "sqlite": {
    "operator": "connect",
    "database_path": "./data/mi_base.db"
  }
}
```

**Parámetros:**
- `database_path` (requerido): Ruta al archivo de base de datos
- `timeout` (opcional): Timeout de conexión (default: 30.0)
- `check_same_thread` (opcional): Verificar mismo hilo (default: true)
- `isolation_level` (opcional): Nivel de aislamiento

#### `disconnect`
Cierra la conexión a la base de datos.

```json
{
  "sqlite": {
    "operator": "disconnect"
  }
}
```

#### `test_connection`
Prueba la conexión actual.

```json
{
  "sqlite": {
    "operator": "test_connection",
    "result": "connection_status"
  }
}
```

### Operaciones Básicas

#### `execute`
Ejecuta una consulta SQL personalizada.

```json
{
  "sqlite": {
    "operator": "execute",
    "sql": "CREATE TABLE usuarios (id INTEGER PRIMARY KEY, nombre TEXT, email TEXT)",
    "result": "create_result"
  }
}
```

#### `query`
Ejecuta una consulta SELECT y retorna datos.

```json
{
  "sqlite": {
    "operator": "query",
    "sql": "SELECT * FROM usuarios WHERE edad > ${edad_minima}",
    "params": [18],
    "result": "usuarios_data"
  }
}
```

#### `select`
Consulta simplificada con parámetros estructurados.

```json
{
  "sqlite": {
    "operator": "select",
    "table": "usuarios",
    "columns": "id, nombre, email",
    "where": "edad > 18",
    "order_by": "nombre ASC",
    "limit": 10,
    "result": "usuarios_filtrados"
  }
}
```

### Operaciones de Tablas

#### `create_table`
Crea una nueva tabla.

```json
{
  "sqlite": {
    "operator": "create_table",
    "table_name": "productos",
    "columns": [
      {
        "name": "id",
        "type": "INTEGER",
        "constraints": "PRIMARY KEY AUTOINCREMENT"
      },
      {
        "name": "nombre",
        "type": "TEXT",
        "constraints": "NOT NULL"
      },
      {
        "name": "precio",
        "type": "REAL",
        "constraints": "NOT NULL"
      },
      {
        "name": "fecha_creacion",
        "type": "DATETIME",
        "constraints": "DEFAULT CURRENT_TIMESTAMP"
      }
    ],
    "result": "table_creation"
  }
}
```

#### `insert`
Inserta datos en una tabla.

```json
{
  "sqlite": {
    "operator": "insert",
    "table": "usuarios",
    "data": {
      "nombre": "Juan Pérez",
      "email": "juan@ejemplo.com",
      "edad": 25
    },
    "result": "insert_result"
  }
}
```

**Inserción múltiple:**
```json
{
  "sqlite": {
    "operator": "insert",
    "table": "usuarios",
    "data": [
      {
        "nombre": "Ana García",
        "email": "ana@ejemplo.com",
        "edad": 30
      },
      {
        "nombre": "Carlos López",
        "email": "carlos@ejemplo.com",
        "edad": 28
      }
    ],
    "result": "bulk_insert_result"
  }
}
```

#### `update`
Actualiza datos en una tabla.

```json
{
  "sqlite": {
    "operator": "update",
    "table": "usuarios",
    "data": {
      "edad": 26,
      "email": "juan.nuevo@ejemplo.com"
    },
    "where": "id = 1",
    "result": "update_result"
  }
}
```

#### `delete`
Elimina datos de una tabla.

```json
{
  "sqlite": {
    "operator": "delete",
    "table": "usuarios",
    "where": "edad < 18",
    "result": "delete_result"
  }
}
```

### Información de Esquema

#### `list_tables`
Lista todas las tablas en la base de datos.

```json
{
  "sqlite": {
    "operator": "list_tables",
    "result": "tablas_disponibles"
  }
}
```

#### `describe_table`
Describe la estructura de una tabla.

```json
{
  "sqlite": {
    "operator": "describe_table",
    "table": "usuarios",
    "result": "estructura_tabla"
  }
}
```

#### `get_table_info`
Obtiene información detallada de una tabla.

```json
{
  "sqlite": {
    "operator": "get_table_info",
    "table": "usuarios",
    "result": "info_tabla"
  }
}
```

#### `get_indexes`
Obtiene los índices de una tabla.

```json
{
  "sqlite": {
    "operator": "get_indexes",
    "table": "usuarios",
    "result": "indices_tabla"
  }
}
```

#### `get_triggers`
Obtiene los triggers de una tabla.

```json
{
  "sqlite": {
    "operator": "get_triggers",
    "table": "usuarios",
    "result": "triggers_tabla"
  }
}
```

#### `get_views`
Obtiene todas las vistas en la base de datos.

```json
{
  "sqlite": {
    "operator": "get_views",
    "result": "vistas_disponibles"
  }
}
```

### Administración de Base de Datos

#### `backup`
Crea una copia de seguridad de la base de datos.

```json
{
  "sqlite": {
    "operator": "backup",
    "backup_path": "./backups/mi_base_backup.db",
    "result": "backup_result"
  }
}
```

#### `restore`
Restaura la base de datos desde una copia de seguridad.

```json
{
  "sqlite": {
    "operator": "restore",
    "backup_path": "./backups/mi_base_backup.db",
    "result": "restore_result"
  }
}
```

#### `vacuum`
Reclama espacio en la base de datos.

```json
{
  "sqlite": {
    "operator": "vacuum",
    "result": "vacuum_result"
  }
}
```

#### `analyze`
Analiza la base de datos para optimización de consultas.

```json
{
  "sqlite": {
    "operator": "analyze",
    "result": "analyze_result"
  }
}
```

#### `check_integrity`
Verifica la integridad de la base de datos.

```json
{
  "sqlite": {
    "operator": "check_integrity",
    "result": "integrity_check"
  }
}
```

### Importación y Exportación

#### `export_data`
Exporta datos de una tabla a archivo.

```json
{
  "sqlite": {
    "operator": "export_data",
    "table": "usuarios",
    "file_path": "./exports/usuarios.csv",
    "format": "csv",
    "result": "export_result"
  }
}
```

**Formatos soportados:**
- `csv`: Archivo CSV
- `json`: Archivo JSON

#### `import_data`
Importa datos desde archivo a una tabla.

```json
{
  "sqlite": {
    "operator": "import_data",
    "table": "usuarios",
    "file_path": "./imports/nuevos_usuarios.csv",
    "format": "csv",
    "result": "import_result"
  }
}
```

### Gestión de Transacciones

#### `begin_transaction`
Inicia una transacción.

```json
{
  "sqlite": {
    "operator": "begin_transaction",
    "result": "transaction_started"
  }
}
```

#### `commit`
Confirma la transacción actual.

```json
{
  "sqlite": {
    "operator": "commit",
    "result": "transaction_committed"
  }
}
```

#### `rollback`
Revierte la transacción actual.

```json
{
  "sqlite": {
    "operator": "rollback",
    "result": "transaction_rolled_back"
  }
}
```

#### `savepoint`
Crea un punto de guardado.

```json
{
  "sqlite": {
    "operator": "savepoint",
    "name": "mi_savepoint",
    "result": "savepoint_created"
  }
}
```

#### `rollback_to_savepoint`
Revierte a un punto de guardado específico.

```json
{
  "sqlite": {
    "operator": "rollback_to_savepoint",
    "name": "mi_savepoint",
    "result": "rolled_back_to_savepoint"
  }
}
```

#### `release_savepoint`
Libera un punto de guardado.

```json
{
  "sqlite": {
    "operator": "release_savepoint",
    "name": "mi_savepoint",
    "result": "savepoint_released"
  }
}
```

## Ejemplos de Uso

### Ejemplo 1: Crear Base de Datos y Tabla

```json
{
  "task": [
    {
      "sqlite": {
        "operator": "connect",
        "database_path": "./data/tienda.db"
      }
    },
    {
      "sqlite": {
        "operator": "create_table",
        "table_name": "productos",
        "columns": [
          {
            "name": "id",
            "type": "INTEGER",
            "constraints": "PRIMARY KEY AUTOINCREMENT"
          },
          {
            "name": "nombre",
            "type": "TEXT",
            "constraints": "NOT NULL"
          },
          {
            "name": "precio",
            "type": "REAL",
            "constraints": "NOT NULL"
          },
          {
            "name": "stock",
            "type": "INTEGER",
            "constraints": "DEFAULT 0"
          }
        ],
        "result": "tabla_creada"
      }
    },
    {
      "print": { "text": "Tabla productos creada: {{tabla_creada}}" }
    }
  ]
}
```

### Ejemplo 2: Insertar y Consultar Datos

```json
{
  "task": [
    {
      "sqlite": {
        "operator": "connect",
        "database_path": "./data/tienda.db"
      }
    },
    {
      "sqlite": {
        "operator": "insert",
        "table": "productos",
        "data": [
          {
            "nombre": "Laptop",
            "precio": 999.99,
            "stock": 10
          },
          {
            "nombre": "Mouse",
            "precio": 25.50,
            "stock": 50
          },
          {
            "nombre": "Teclado",
            "precio": 75.00,
            "stock": 30
          }
        ],
        "result": "productos_insertados"
      }
    },
    {
      "sqlite": {
        "operator": "select",
        "table": "productos",
        "where": "precio > 50",
        "order_by": "precio DESC",
        "result": "productos_caros"
      }
    },
    {
      "print": { "text": "Productos caros: {{productos_caros}}" }
    }
  ]
}
```

### Ejemplo 3: Transacciones y Backup

```json
{
  "task": [
    {
      "sqlite": {
        "operator": "connect",
        "database_path": "./data/tienda.db"
      }
    },
    {
      "sqlite": {
        "operator": "begin_transaction"
      }
    },
    {
      "sqlite": {
        "operator": "update",
        "table": "productos",
        "data": { "stock": 15 },
        "where": "nombre = 'Laptop'"
      }
    },
    {
      "sqlite": {
        "operator": "savepoint",
        "name": "antes_descuento"
      }
    },
    {
      "sqlite": {
        "operator": "update",
        "table": "productos",
        "data": { "precio": "precio * 0.9" },
        "where": "stock > 20"
      }
    },
    {
      "sqlite": {
        "operator": "commit"
      }
    },
    {
      "sqlite": {
        "operator": "backup",
        "backup_path": "./backups/tienda_backup.db"
      }
    }
  ]
}
```

### Ejemplo 4: Importación y Exportación

```json
{
  "task": [
    {
      "sqlite": {
        "operator": "connect",
        "database_path": "./data/tienda.db"
      }
    },
    {
      "sqlite": {
        "operator": "export_data",
        "table": "productos",
        "file_path": "./exports/productos.csv",
        "format": "csv",
        "result": "export_result"
      }
    },
    {
      "print": { "text": "Datos exportados: {{export_result}}" }
    },
    {
      "sqlite": {
        "operator": "import_data",
        "table": "productos_nuevos",
        "file_path": "./imports/nuevos_productos.json",
        "format": "json",
        "result": "import_result"
      }
    },
    {
      "print": { "text": "Datos importados: {{import_result}}" }
    }
  ]
}
```

### Ejemplo 5: Análisis y Mantenimiento

```json
{
  "task": [
    {
      "sqlite": {
        "operator": "connect",
        "database_path": "./data/tienda.db"
      }
    },
    {
      "sqlite": {
        "operator": "check_integrity",
        "result": "integrity_status"
      }
    },
    {
      "print": { "text": "Estado de integridad: {{integrity_status}}" }
    },
    {
      "sqlite": {
        "operator": "analyze",
        "result": "analyze_result"
      }
    },
    {
      "sqlite": {
        "operator": "vacuum",
        "result": "vacuum_result"
      }
    },
    {
      "print": { "text": "Mantenimiento completado" }
    }
  ]
}
```

## Variables de Entorno

Puedes usar variables de entorno para la ruta de la base de datos:

```json
{
  "sqlite": {
    "operator": "connect",
    "database_path": "env(DATABASE_PATH)"
  }
}
```

## Interpolación de Variables

Puedes usar variables de Sugar en las consultas SQL:

```json
{
  "String::edad_minima": "18",
  "task": [
    {
      "sqlite": {
        "operator": "query",
        "sql": "SELECT * FROM usuarios WHERE edad > ${edad_minima}",
        "result": "usuarios_mayores"
      }
    }
  ]
}
```

## Configuración del Plugin

Puedes configurar el plugin al inicializarlo:

```json
{
  "sqlite": {
    "operator": "connect",
    "database_path": "./data/mi_base.db",
    "timeout": 60.0,
    "check_same_thread": false,
    "isolation_level": "IMMEDIATE"
  }
}
```

## Manejo de Errores

El plugin maneja errores de manera robusta:

```json
{
  "task": [
    {
      "try": {
        "task": [
          {
            "sqlite": {
              "operator": "connect",
              "database_path": "/ruta/invalida/base.db"
            }
          }
        ]
      },
      "catch": {
        "task": [
          {
            "print": { "text": "Error de conexión: {{error}}" }
          }
        ]
      }
    }
  ]
}
```

## Mejores Prácticas

1. **Siempre desconecta**: Usa `disconnect` al finalizar operaciones
2. **Usa transacciones**: Para operaciones múltiples, usa transacciones
3. **Backup regular**: Haz copias de seguridad periódicas
4. **Validación de datos**: Valida los datos antes de insertar
5. **Índices**: Crea índices para consultas frecuentes
6. **Preparación de consultas**: Usa parámetros para evitar SQL injection

## Limitaciones

- Solo soporta SQLite
- No soporta conexiones remotas
- Limitado a un archivo por conexión
- No soporta usuarios y permisos

## Troubleshooting

### Error: "No database connection"
- Asegúrate de usar `connect` antes de otras operaciones

### Error: "Database is locked"
- Verifica que no haya otras conexiones activas
- Usa `timeout` más alto en la configuración

### Error: "Table already exists"
- Usa `CREATE TABLE IF NOT EXISTS` en lugar de `CREATE TABLE`

### Error: "No such table"
- Verifica que la tabla existe con `list_tables`
- Usa `create_table` para crear la tabla

## Compatibilidad

- **Python**: 3.7+
- **SQLite**: 3.x (incluido en Python)
- **Sistemas**: Windows, Linux, macOS
- **Sugar**: v2.0.0+