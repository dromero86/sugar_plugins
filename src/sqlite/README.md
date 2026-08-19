# Plugin SQLite para Sugar

## 📋 Descripción

El plugin SQLite para Sugar proporciona operaciones completas de base de datos SQLite, incluyendo gestión de conexiones, ejecución de consultas, manejo de transacciones, administración de bases de datos e importación/exportación de datos.

## ✨ Características

- ✅ **Gestión de conexiones**: Conexión y desconexión a bases de datos SQLite
- ✅ **Operaciones SQL**: Ejecución de consultas SQL personalizadas
- ✅ **Operaciones CRUD**: Insert, Update, Delete, Select simplificados
- ✅ **Gestión de transacciones**: Begin, Commit, Rollback, Savepoints
- ✅ **Administración de BD**: Backup, Restore, Vacuum, Analyze
- ✅ **Importación/Exportación**: CSV y JSON
- ✅ **Información de esquema**: Tablas, índices, triggers, vistas
- ✅ **Sin dependencias externas**: SQLite3 viene incluido en Python
- ✅ **Interpolación de variables**: Soporte para variables de Sugar
- ✅ **Manejo de errores robusto**: Sistema completo de manejo de excepciones

## 🚀 Instalación

No se requieren dependencias externas. SQLite3 viene incluido en Python por defecto.

```bash
# El plugin está listo para usar
```

## 📖 Documentación

- [Documentación completa](docs/README.md) - Guía detallada de todos los comandos
- [Ejemplos básicos](examples/basic_usage.json) - Ejemplos de uso básico
- [Ejemplos avanzados](examples/advanced_usage.json) - Ejemplos con transacciones y administración
- [Ejemplos de transacciones](examples/transaction_example.json) - Manejo de transacciones

## 🎯 Comandos Principales

### Gestión de Conexiones
- `connect` - Establecer conexión a base de datos
- `disconnect` - Cerrar conexión
- `test_connection` - Probar conexión

### Operaciones Básicas
- `execute` - Ejecutar SQL personalizado
- `query` - Consulta SELECT con parámetros
- `select` - Consulta simplificada

### Operaciones CRUD
- `create_table` - Crear tabla
- `insert` - Insertar datos
- `update` - Actualizar datos
- `delete` - Eliminar datos

### Transacciones
- `begin_transaction` - Iniciar transacción
- `commit` - Confirmar transacción
- `rollback` - Revertir transacción
- `savepoint` - Crear punto de guardado

### Administración
- `backup` - Crear copia de seguridad
- `restore` - Restaurar desde backup
- `vacuum` - Reclamar espacio
- `analyze` - Analizar para optimización

### Importación/Exportación
- `export_data` - Exportar a CSV/JSON
- `import_data` - Importar desde CSV/JSON

## 💡 Ejemplo Rápido

```json
{
  "task": [
    {
      "sqlite": {
        "operator": "connect",
        "database_path": "./data/mi_base.db"
      }
    },
    {
      "sqlite": {
        "operator": "create_table",
        "table_name": "usuarios",
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
            "name": "email",
            "type": "TEXT",
            "constraints": "UNIQUE"
          }
        ]
      }
    },
    {
      "sqlite": {
        "operator": "insert",
        "table": "usuarios",
        "data": {
          "nombre": "Juan Pérez",
          "email": "juan@ejemplo.com"
        }
      }
    },
    {
      "sqlite": {
        "operator": "select",
        "table": "usuarios",
        "result": "usuarios_data"
      }
    },
    {
      "print": { "text": "Usuarios: {{usuarios_data}}" }
    }
  ]
}
```

## 🔧 Ejecución

Para ejecutar ejemplos del plugin SQLite:

```bash
# Ejemplo básico
virtual/bin/python3 Sugar/Service/SugarConsole.py plugins/src/sqlite/examples/basic_usage.json

# Ejemplo avanzado
virtual/bin/python3 Sugar/Service/SugarConsole.py plugins/src/sqlite/examples/advanced_usage.json

# Ejemplo de transacciones
virtual/bin/python3 Sugar/Service/SugarConsole.py plugins/src/sqlite/examples/transaction_example.json
```

## 📁 Estructura del Plugin

```
sqlite/
├── __init__.py                 # Inicialización del plugin
├── plugin.json                 # Configuración del plugin
├── requirements.txt            # Dependencias (vacío - SQLite3 incluido)
├── setup.py                    # Script de instalación
├── README.md                   # Este archivo
├── src/
│   └── sqlite_plugin.py        # Implementación principal
├── docs/
│   └── README.md               # Documentación completa
└── examples/
    ├── basic_usage.json        # Ejemplo básico
    ├── advanced_usage.json     # Ejemplo avanzado
    └── transaction_example.json # Ejemplo de transacciones
```

## 🔗 Integración con Sugar

El plugin se integra perfectamente con el sistema de plugins de Sugar:

- **Hereda de PluginBase**: Implementa la interfaz estándar de Sugar
- **Sistema de variables**: Soporte completo para interpolación de variables
- **Manejo de errores**: Integrado con el sistema de logging de Sugar
- **Contexto**: Acceso completo al contexto de Sugar

## 🛡️ Características de Seguridad

- **Preparación de consultas**: Previene SQL injection
- **Validación de datos**: Verificación de tipos y restricciones
- **Transacciones seguras**: Rollback automático en caso de error
- **Manejo de conexiones**: Cierre automático de conexiones

## 📊 Rendimiento

- **Conexiones eficientes**: Reutilización de conexiones
- **Transacciones optimizadas**: Soporte para WAL mode
- **Consultas preparadas**: Mejora el rendimiento de consultas repetitivas
- **Índices automáticos**: Optimización de consultas

## 🔧 Configuración

El plugin soporta configuración avanzada:

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

## 🐛 Troubleshooting

### Problemas Comunes

1. **"No database connection"**
   - Asegúrate de usar `connect` antes de otras operaciones

2. **"Database is locked"**
   - Verifica que no haya otras conexiones activas
   - Usa `timeout` más alto en la configuración

3. **"Table already exists"**
   - Usa `CREATE TABLE IF NOT EXISTS` en lugar de `CREATE TABLE`

4. **"No such table"**
   - Verifica que la tabla existe con `list_tables`
   - Usa `create_table` para crear la tabla

## 📈 Roadmap

- [ ] Soporte para vistas materializadas
- [ ] Migración de esquemas
- [ ] Replicación de datos
- [ ] Encriptación de bases de datos
- [ ] Soporte para extensiones SQLite

## 🤝 Contribución

Para contribuir al plugin SQLite:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Implementa los cambios
4. Añade tests
5. Envía un pull request

## 📄 Licencia

MIT License - Ver [LICENSE](../../LICENSE) para más detalles.

## 👥 Autores

- **Sugar Team** - Desarrollo inicial

## 🔗 Enlaces Relacionados

- [Documentación de Sugar](https://sugar-lang.org/docs)
- [Sistema de Plugins](https://sugar-lang.org/docs/plugins)
- [SQLite Documentation](https://www.sqlite.org/docs.html)