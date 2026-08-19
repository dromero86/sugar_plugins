# Docker Plugin para Sugar

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/sugar-lang/sugar)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

Un plugin completo para Sugar que proporciona funcionalidad de Docker Compose en el lenguaje declarativo de Sugar. Permite crear, gestionar y orquestar contenedores Docker, servicios, redes y volúmenes de manera declarativa.

## 🚀 Características Principales

- **🐳 Gestión Completa de Contenedores**: Ejecutar, detener, inspeccionar y gestionar contenedores Docker
- **🏗️ Composición de Servicios**: Crear y orquestar múltiples servicios con dependencias
- **🌐 Gestión de Redes**: Crear y configurar redes personalizadas
- **💾 Gestión de Volúmenes**: Manejar almacenamiento persistente y backups
- **🔄 Integración Docker Compose**: Exportar/importar archivos docker-compose.yml
- **🏥 Health Checks**: Monitoreo automático de servicios
- **🔧 Validación**: Validación completa de configuraciones
- **🧹 Limpieza**: Gestión automática de recursos no utilizados

## 📦 Instalación

### Dependencias del Sistema
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# CentOS/RHEL
sudo yum install docker docker-compose

# macOS
brew install docker docker-compose

# Verificar instalación
docker --version
docker-compose --version
```

### Dependencias de Python
```bash
pip install docker>=6.0.0 pyyaml>=6.0
```

## 🎯 Uso Rápido

### Ejemplo Básico: Aplicación Web + Base de Datos

```json
{
  "task": [
    {
      "docker": {
        "operator": "create_composition",
        "name": "mi_app",
        "services": {
          "web": {
            "image": "nginx:alpine",
            "ports": ["80:80"],
            "volumes": ["./web:/usr/share/nginx/html"],
            "networks": ["app_network"]
          },
          "db": {
            "image": "postgres:13-alpine",
            "ports": ["5432:5432"],
            "environment": {
              "POSTGRES_DB": "myapp",
              "POSTGRES_USER": "user",
              "POSTGRES_PASSWORD": "password"
            },
            "volumes": ["postgres_data:/var/lib/postgresql/data"],
            "networks": ["app_network"]
          }
        },
        "networks": {
          "app_network": {"driver": "bridge"}
        },
        "volumes": {
          "postgres_data": {"driver": "local"}
        }
      }
    },
    {
      "docker": {
        "operator": "start_composition",
        "name": "mi_app"
      }
    }
  ]
}
```

### Ejecutar desde Sugar

```bash
# Usando el entorno virtual de Sugar
virtual/bin/python3 Sugar/Service/SugarConsole.py mi_composicion.json

# O si el entorno virtual está activado
python3 Sugar/Service/SugarConsole.py mi_composicion.json
```

## 📚 Documentación Completa

Para documentación detallada, ejemplos avanzados y mejores prácticas, consulta:

- **[Documentación Completa](docs/README.md)** - Guía completa del plugin
- **[Ejemplos](examples/)** - Ejemplos prácticos de uso
- **[API Reference](docs/README.md#comandos-disponibles)** - Referencia de comandos

## 🔧 Comandos Principales

### Composición de Servicios
- `create_composition` - Crear una nueva composición
- `start_composition` - Iniciar una composición
- `stop_composition` - Detener una composición
- `restart_composition` - Reiniciar una composición
- `destroy_composition` - Destruir una composición
- `status_composition` - Obtener estado de una composición

### Gestión de Contenedores
- `run_container` - Ejecutar un contenedor
- `stop_container` - Detener un contenedor
- `inspect_container` - Inspeccionar un contenedor
- `logs_container` - Obtener logs de un contenedor
- `exec_container` - Ejecutar comando en un contenedor

### Utilidades
- `health_check` - Verificar salud de servicios
- `export_compose` - Exportar a docker-compose.yml
- `import_compose` - Importar desde docker-compose.yml
- `cleanup` - Limpiar recursos no utilizados

## 🎨 Ejemplos Avanzados

### Microservicios con Dependencias

```json
{
  "task": [
    {
      "docker": {
        "operator": "create_composition",
        "name": "microservices",
        "services": {
          "api_gateway": {
            "image": "nginx:alpine",
            "ports": ["8080:80"],
            "depends_on": ["api_service", "auth_service"]
          },
          "api_service": {
            "image": "node:16-alpine",
            "ports": ["3000:3000"],
            "depends_on": ["database", "redis"],
            "environment": {
              "DB_HOST": "database",
              "REDIS_HOST": "redis"
            }
          },
          "database": {
            "image": "postgres:13-alpine",
            "volumes": ["postgres_data:/var/lib/postgresql/data"]
          },
          "redis": {
            "image": "redis:alpine",
            "volumes": ["redis_data:/data"]
          }
        }
      }
    }
  ]
}
```

### Monitoreo y Health Checks

```json
{
  "task": [
    {
      "docker": {
        "operator": "health_check",
        "composition_name": "mi_app",
        "result": "health_result"
      }
    },
    {
      "if": {
        "condition": "${health_result.overall_healthy} == true",
        "then": {
          "task": [
            {
              "print": {
                "text": "✅ Todos los servicios están saludables"
              }
            }
          ]
        }
      }
    }
  ]
}
```

## 🛠️ Desarrollo

### Estructura del Plugin

```
docker/
├── src/
│   ├── DockerPlugin.py      # Plugin principal
│   ├── DockerContainer.py   # Gestión de contenedores
│   ├── DockerNetwork.py     # Gestión de redes
│   ├── DockerVolume.py      # Gestión de volúmenes
│   └── DockerCompose.py     # Integración Docker Compose
├── examples/                # Ejemplos de uso
├── docs/                    # Documentación
├── requirements.txt         # Dependencias
└── README.md               # Este archivo
```

### Ejecutar Tests

```bash
# Ejecutar tests del plugin
python -m pytest plugins/src/docker/tests/

# Ejecutar ejemplo básico
virtual/bin/python3 Sugar/Service/SugarConsole.py plugins/src/docker/examples/basic_composition.json
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- [Docker](https://www.docker.com/) - Por la tecnología de contenedores
- [Docker Compose](https://docs.docker.com/compose/) - Por la inspiración en la sintaxis
- [Sugar Language](https://github.com/sugar-lang/sugar) - Por el framework base

## 📞 Soporte

- **Documentación**: [docs/README.md](docs/README.md)
- **Issues**: [GitHub Issues](https://github.com/sugar-lang/sugar/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/sugar-lang/sugar/discussions)

---

**¿Te gusta este plugin? ¡Dale una ⭐ en GitHub!**