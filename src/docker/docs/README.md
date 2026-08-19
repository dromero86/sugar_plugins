# Docker Plugin para Sugar

## Descripción

El plugin Docker para Sugar proporciona funcionalidad completa de Docker Compose en el lenguaje declarativo de Sugar. Permite crear, gestionar y orquestar contenedores Docker, servicios, redes y volúmenes de manera declarativa y programática.

## Características

### 🐳 Gestión de Contenedores
- **Ejecutar contenedores** con configuración completa
- **Detener y reiniciar** contenedores
- **Inspeccionar** información detallada
- **Obtener logs** y estadísticas
- **Ejecutar comandos** dentro de contenedores

### 🏗️ Composición de Servicios
- **Crear composiciones** con múltiples servicios
- **Gestionar dependencias** entre servicios
- **Health checks** y monitoreo
- **Orquestación** automática de servicios

### 🌐 Gestión de Redes
- **Crear redes** personalizadas
- **Conectar/desconectar** contenedores
- **Configurar drivers** y opciones
- **Gestión de IPs** y aliases

### 💾 Gestión de Volúmenes
- **Crear volúmenes** persistentes
- **Backup y restore** de datos
- **Configurar drivers** de almacenamiento
- **Gestión de permisos** y etiquetas

### 🔄 Integración con Docker Compose
- **Exportar** composiciones a `docker-compose.yml`
- **Importar** archivos de Docker Compose
- **Validación** de configuraciones
- **Conversión** bidireccional

## Instalación

### Dependencias del Sistema
```bash
# Instalar Docker
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Verificar instalación
docker --version
docker-compose --version
```

### Dependencias de Python
```bash
pip install docker>=6.0.0 pyyaml>=6.0
```

## Uso Básico

### Crear una Composición Simple

```json
{
  "task": [
    {
      "docker": {
        "operator": "create_composition",
        "name": "mi_aplicacion",
        "version": "3.8",
        "services": {
          "web": {
            "image": "nginx:alpine",
            "ports": ["80:80"],
            "environment": {
              "NGINX_HOST": "localhost"
            },
            "volumes": ["./web:/usr/share/nginx/html"],
            "networks": ["app_network"],
            "restart": "unless-stopped"
          },
          "database": {
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
          "app_network": {
            "driver": "bridge"
          }
        },
        "volumes": {
          "postgres_data": {
            "driver": "local"
          }
        },
        "result": "composition_result"
      }
    }
  ]
}
```

### Gestionar la Composición

```json
{
  "task": [
    {
      "docker": {
        "operator": "start_composition",
        "name": "mi_aplicacion",
        "result": "start_result"
      }
    },
    {
      "docker": {
        "operator": "status_composition",
        "name": "mi_aplicacion",
        "result": "status_result"
      }
    },
    {
      "docker": {
        "operator": "health_check",
        "composition_name": "mi_aplicacion",
        "result": "health_result"
      }
    },
    {
      "docker": {
        "operator": "stop_composition",
        "name": "mi_aplicacion",
        "result": "stop_result"
      }
    }
  ]
}
```

## Comandos Disponibles

### Comandos de Composición

| Comando | Descripción | Parámetros |
|---------|-------------|------------|
| `create_composition` | Crear una nueva composición | `name`, `services`, `networks`, `volumes` |
| `start_composition` | Iniciar una composición | `name` |
| `stop_composition` | Detener una composición | `name` |
| `restart_composition` | Reiniciar una composición | `name` |
| `destroy_composition` | Destruir una composición | `name` |
| `status_composition` | Obtener estado de una composición | `name` |

### Comandos de Servicios

| Comando | Descripción | Parámetros |
|---------|-------------|------------|
| `create_service` | Crear un servicio | `name`, `image`, `ports`, `environment`, etc. |
| `start_service` | Iniciar un servicio | `name` |
| `stop_service` | Detener un servicio | `name` |
| `restart_service` | Reiniciar un servicio | `name` |
| `destroy_service` | Destruir un servicio | `name` |
| `status_service` | Obtener estado de un servicio | `name` |
| `logs_service` | Obtener logs de un servicio | `name` |
| `exec_service` | Ejecutar comando en un servicio | `name`, `command` |

### Comandos de Contenedores

| Comando | Descripción | Parámetros |
|---------|-------------|------------|
| `run_container` | Ejecutar un contenedor | `name`, `image`, `ports`, `environment`, etc. |
| `stop_container` | Detener un contenedor | `container_id` |
| `remove_container` | Eliminar un contenedor | `container_id` |
| `inspect_container` | Inspeccionar un contenedor | `container_id` |
| `logs_container` | Obtener logs de un contenedor | `container_id` |
| `exec_container` | Ejecutar comando en un contenedor | `container_id`, `command` |
| `stats_container` | Obtener estadísticas de un contenedor | `container_id` |

### Comandos de Redes

| Comando | Descripción | Parámetros |
|---------|-------------|------------|
| `create_network` | Crear una red | `name`, `driver`, `subnet`, `gateway` |
| `remove_network` | Eliminar una red | `name` |
| `list_networks` | Listar todas las redes | - |
| `inspect_network` | Inspeccionar una red | `name` |

### Comandos de Volúmenes

| Comando | Descripción | Parámetros |
|---------|-------------|------------|
| `create_volume` | Crear un volumen | `name`, `driver`, `labels` |
| `remove_volume` | Eliminar un volumen | `name` |
| `list_volumes` | Listar todos los volúmenes | - |
| `inspect_volume` | Inspeccionar un volumen | `name` |

### Comandos de Utilidad

| Comando | Descripción | Parámetros |
|---------|-------------|------------|
| `list_services` | Listar todos los servicios | - |
| `list_compositions` | Listar todas las composiciones | - |
| `health_check` | Verificar salud de servicios | `composition_name` o `service_name` |
| `cleanup` | Limpiar recursos no utilizados | `remove_containers`, `remove_networks`, `remove_volumes` |
| `export_compose` | Exportar a docker-compose.yml | `name`, `output_file` |
| `import_compose` | Importar desde docker-compose.yml | `input_file`, `name` |
| `validate_composition` | Validar una composición | `name` |

## Configuración de Servicios

### Parámetros Básicos

```json
{
  "name": "mi_servicio",
  "image": "nginx:alpine",
  "ports": ["80:80", "443:443"],
  "environment": {
    "NGINX_HOST": "localhost",
    "NGINX_PORT": "80"
  },
  "volumes": [
    "./web:/usr/share/nginx/html",
    "./nginx.conf:/etc/nginx/nginx.conf"
  ],
  "networks": ["app_network"],
  "restart": "unless-stopped",
  "command": ["nginx", "-g", "daemon off;"],
  "working_dir": "/app",
  "user": "nginx",
  "labels": {
    "app": "web",
    "environment": "production"
  }
}
```

### Health Checks

```json
{
  "healthcheck": {
    "test": ["CMD", "curl", "-f", "http://localhost/health"],
    "interval": "30s",
    "timeout": "10s",
    "retries": 3,
    "start_period": "40s"
  }
}
```

### Dependencias

```json
{
  "depends_on": ["database", "redis"]
}
```

## Configuración de Redes

### Red Básica

```json
{
  "name": "app_network",
  "driver": "bridge",
  "labels": {
    "app": "myapp"
  }
}
```

### Red con Configuración Avanzada

```json
{
  "name": "custom_network",
  "driver": "bridge",
  "subnet": "172.20.0.0/16",
  "gateway": "172.20.0.1",
  "ip_range": "172.20.0.0/24",
  "labels": {
    "app": "myapp",
    "environment": "production"
  }
}
```

## Configuración de Volúmenes

### Volumen Básico

```json
{
  "name": "app_data",
  "driver": "local",
  "labels": {
    "app": "myapp"
  }
}
```

### Volumen con Opciones

```json
{
  "name": "shared_data",
  "driver": "nfs",
  "options": {
    "type": "nfs",
    "o": "addr=192.168.1.100,rw",
    "device": ":/path/to/share"
  },
  "labels": {
    "app": "myapp",
    "type": "shared"
  }
}
```

## Ejemplos Avanzados

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
            "depends_on": ["api_service", "auth_service"],
            "networks": ["app_network"]
          },
          "api_service": {
            "image": "node:16-alpine",
            "ports": ["3000:3000"],
            "depends_on": ["database", "redis"],
            "networks": ["app_network"],
            "environment": {
              "DB_HOST": "database",
              "REDIS_HOST": "redis"
            }
          },
          "auth_service": {
            "image": "node:16-alpine",
            "ports": ["3001:3001"],
            "depends_on": ["database"],
            "networks": ["app_network"]
          },
          "database": {
            "image": "postgres:13-alpine",
            "volumes": ["postgres_data:/var/lib/postgresql/data"],
            "networks": ["app_network"]
          },
          "redis": {
            "image": "redis:alpine",
            "volumes": ["redis_data:/data"],
            "networks": ["app_network"]
          }
        },
        "networks": {
          "app_network": {"driver": "bridge"}
        },
        "volumes": {
          "postgres_data": {"driver": "local"},
          "redis_data": {"driver": "local"}
        }
      }
    }
  ]
}
```

### Exportar e Importar

```json
{
  "task": [
    {
      "docker": {
        "operator": "export_compose",
        "name": "mi_aplicacion",
        "output_file": "./docker-compose.yml"
      }
    },
    {
      "docker": {
        "operator": "import_compose",
        "input_file": "./docker-compose.yml",
        "name": "aplicacion_importada"
      }
    }
  ]
}
```

## Monitoreo y Health Checks

### Verificar Salud de Composición

```json
{
  "task": [
    {
      "docker": {
        "operator": "health_check",
        "composition_name": "mi_aplicacion",
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
        },
        "else": {
          "task": [
            {
              "print": {
                "text": "❌ Algunos servicios no están saludables: {{health_result.services_health}}"
              }
            }
          ]
        }
      }
    }
  ]
}
```

## Limpieza y Mantenimiento

### Limpiar Recursos No Utilizados

```json
{
  "task": [
    {
      "docker": {
        "operator": "cleanup",
        "remove_containers": true,
        "remove_networks": true,
        "remove_volumes": false,
        "result": "cleanup_result"
      }
    },
    {
      "print": {
        "text": "Limpieza completada: {{cleanup_result}}"
      }
    }
  ]
}
```

## Variables y Interpolación

El plugin soporta interpolación de variables de Sugar:

```json
{
  "String::db_password": "mi_password_secreta",
  "String::app_version": "1.0.0",
  "task": [
    {
      "docker": {
        "operator": "create_composition",
        "name": "app_con_variables",
        "services": {
          "database": {
            "image": "postgres:13-alpine",
            "environment": {
              "POSTGRES_PASSWORD": "{{db_password}}",
              "APP_VERSION": "{{app_version}}"
            }
          }
        }
      }
    }
  ]
}
```

## Manejo de Errores

### Ejemplo con Try-Catch

```json
{
  "task": [
    {
      "try": {
        "task": [
          {
            "docker": {
              "operator": "start_composition",
              "name": "mi_aplicacion"
            }
          }
        ]
      },
      "catch": {
        "task": [
          {
            "print": {
              "text": "Error al iniciar la aplicación: {{error}}"
            }
          },
          {
            "docker": {
              "operator": "cleanup",
              "remove_containers": true
            }
          }
        ]
      }
    }
  ]
}
```

## Mejores Prácticas

### 1. Nomenclatura Consistente
- Usa nombres descriptivos para composiciones y servicios
- Mantén consistencia en las etiquetas
- Usa prefijos para diferentes entornos

### 2. Gestión de Dependencias
- Define claramente las dependencias entre servicios
- Usa health checks para servicios críticos
- Considera el orden de inicio

### 3. Configuración de Redes
- Usa redes personalizadas para aislamiento
- Configura subnets cuando sea necesario
- Etiqueta las redes apropiadamente

### 4. Gestión de Volúmenes
- Usa volúmenes nombrados para persistencia
- Configura backups para datos críticos
- Considera el rendimiento del almacenamiento

### 5. Monitoreo
- Implementa health checks en todos los servicios
- Monitorea logs y estadísticas
- Configura alertas para servicios críticos

### 6. Seguridad
- No expongas puertos innecesarios
- Usa variables de entorno para secretos
- Configura usuarios no-root cuando sea posible

## Troubleshooting

### Problemas Comunes

#### 1. Contenedor no inicia
- Verifica que la imagen existe
- Revisa los logs del contenedor
- Confirma que los puertos no están en uso

#### 2. Servicios no se comunican
- Verifica que están en la misma red
- Confirma que los nombres de servicio son correctos
- Revisa la configuración de DNS

#### 3. Volúmenes no montan
- Verifica permisos del host
- Confirma que las rutas existen
- Revisa la configuración del driver

#### 4. Dependencias no se resuelven
- Verifica el orden de dependencias
- Confirma que los servicios están saludables
- Revisa los timeouts de health checks

### Comandos de Debug

```json
{
  "task": [
    {
      "docker": {
        "operator": "logs_service",
        "name": "mi_servicio",
        "result": "logs"
      }
    },
    {
      "docker": {
        "operator": "inspect_container",
        "container_id": "{{container_id}}",
        "result": "inspect"
      }
    },
    {
      "docker": {
        "operator": "exec_service",
        "name": "mi_servicio",
        "command": "ps aux",
        "result": "processes"
      }
    }
  ]
}
```

## Referencias

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Sugar Language Documentation](/docs/language/README.md)
- [Plugins Documentation](/plugins/README.md)

## Licencia

MIT License - Ver archivo LICENSE para más detalles.