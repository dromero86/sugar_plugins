# Documentación de Plugins

Esta carpeta contiene toda la documentación relacionada con los plugins del sistema Sugar.

## Estructura

```
docs/
├── README.md                    # Este archivo - Información general
├── user_guide/                  # Guía para desarrollar plugins
│   └── README.md               # Convenciones y sintaxis
└── src/                        # Listado de plugins
    ├── README.md               # Lista de plugins en desarrollo
    ├── plugin1/                # Documentación del plugin específico
    │   ├── README.md
    │   ├── docs/
    │   ├── examples/
    │   └── tests/
    └── plugin2/
        └── ...
```

## Propósito

Esta documentación está organizada para:

1. **Desarrolladores de plugins**: Guías completas sobre cómo crear y mantener plugins
2. **Usuarios de plugins**: Documentación específica de cada plugin con ejemplos
3. **Mantenimiento**: Estructura clara para facilitar la actualización de documentación

## Plugins Disponibles

Los plugins están organizados en la carpeta `src/` con la siguiente estructura:

- **curl**: Operaciones cURL avanzadas
- **database**: Operaciones con base de datos
- **environment**: Gestión de variables de entorno
- **jwt**: Manejo de tokens JWT
- **request**: Peticiones HTTP nativas
- **selenium**: Automatización web con Selenium
- **ssh**: Operaciones SSH
- **webserver**: Servidor web integrado
- **zip**: Operaciones de compresión
- **extract_table_selenium**: Extracción de tablas HTML
- **jinja2**: Plantillas Jinja2
- **openssl**: Operaciones criptográficas
- **compiler**: Compilación de código
- **driver**: Drivers de sistema
- **ftp**: Operaciones FTP
- **meta**: Operaciones meta-programación

## Convenciones

- Cada plugin debe tener su propia carpeta en `src/`
- La documentación debe incluir ejemplos prácticos
- Mantener consistencia en el formato y estructura
- Incluir información de instalación y dependencias
