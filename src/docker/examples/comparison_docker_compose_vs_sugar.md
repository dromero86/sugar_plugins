# Comparación: Docker Compose vs Sugar Docker Plugin

Este documento muestra la equivalencia entre la sintaxis de Docker Compose y el plugin Docker de Sugar.

## Ejemplo Básico: Aplicación Web + Base de Datos

### Docker Compose (docker-compose.yml)

```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    environment:
      NGINX_HOST: localhost
      NGINX_PORT: 80
    volumes:
      - ./web:/usr/share/nginx/html
    networks:
      - app_network
    restart: unless-stopped
    labels:
      app: web
      environment: development

  database:
    image: postgres:13-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app_network
    restart: unless-stopped
    labels:
      app: database
      environment: development

networks:
  app_network:
    driver: bridge
    labels:
      app: myapp

volumes:
  postgres_data:
    driver: local
    labels:
      app: database
```

### Sugar Docker Plugin (script.json)

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
              "NGINX_HOST": "localhost",
              "NGINX_PORT": "80"
            },
            "volumes": ["./web:/usr/share/nginx/html"],
            "networks": ["app_network"],
            "restart": "unless-stopped",
            "labels": {
              "app": "web",
              "environment": "development"
            }
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
            "networks": ["app_network"],
            "restart": "unless-stopped",
            "labels": {
              "app": "database",
              "environment": "development"
            }
          }
        },
        "networks": {
          "app_network": {
            "driver": "bridge",
            "labels": {
              "app": "myapp"
            }
          }
        },
        "volumes": {
          "postgres_data": {
            "driver": "local",
            "labels": {
              "app": "database"
            }
          }
        }
      }
    },
    {
      "docker": {
        "operator": "start_composition",
        "name": "mi_aplicacion"
      }
    }
  ]
}
```

## Comandos Equivalentes

### Docker Compose CLI

```bash
# Crear y ejecutar
docker-compose up -d

# Ver estado
docker-compose ps

# Ver logs
docker-compose logs

# Detener
docker-compose down

# Reiniciar
docker-compose restart

# Escalar servicios
docker-compose up -d --scale web=3
```

### Sugar Docker Plugin

```json
{
  "task": [
    {
      "docker": {
        "operator": "start_composition",
        "name": "mi_aplicacion"
      }
    },
    {
      "docker": {
        "operator": "status_composition",
        "name": "mi_aplicacion"
      }
    },
    {
      "docker": {
        "operator": "logs_service",
        "name": "web"
      }
    },
    {
      "docker": {
        "operator": "stop_composition",
        "name": "mi_aplicacion"
      }
    },
    {
      "docker": {
        "operator": "restart_composition",
        "name": "mi_aplicacion"
      }
    }
  ]
}
```

## Ejemplo Avanzado: Microservicios

### Docker Compose (docker-compose.yml)

```yaml
version: '3.8'

services:
  api_gateway:
    image: nginx:alpine
    ports:
      - "8080:80"
    environment:
      UPSTREAM_API: http://api_service:3000
      UPSTREAM_AUTH: http://auth_service:3001
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    networks:
      - app_network
    depends_on:
      - api_service
      - auth_service
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    labels:
      app: api_gateway
      tier: frontend

  api_service:
    image: node:16-alpine
    ports:
      - "3000:3000"
    environment:
      NODE_ENV: production
      DB_HOST: database
      DB_PORT: 5432
      REDIS_HOST: redis
      REDIS_PORT: 6379
    volumes:
      - ./api:/app
      - /app/node_modules
    networks:
      - app_network
    depends_on:
      - database
      - redis
    working_dir: /app
    command: ["npm", "start"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    labels:
      app: api_service
      tier: backend

  auth_service:
    image: node:16-alpine
    ports:
      - "3001:3001"
    environment:
      NODE_ENV: production
      JWT_SECRET: your-secret-key
      DB_HOST: database
      DB_PORT: 5432
    volumes:
      - ./auth:/app
      - /app/node_modules
    networks:
      - app_network
    depends_on:
      - database
    working_dir: /app
    command: ["npm", "start"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    labels:
      app: auth_service
      tier: backend

  database:
    image: postgres:13-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: microservices
      POSTGRES_USER: app_user
      POSTGRES_PASSWORD: secure_password
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - app_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app_user -d microservices"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    labels:
      app: database
      tier: data

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      - ./redis.conf:/usr/local/etc/redis/redis.conf
    networks:
      - app_network
    command: ["redis-server", "/usr/local/etc/redis/redis.conf"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    labels:
      app: redis
      tier: cache

networks:
  app_network:
    driver: bridge
    labels:
      app: microservices_app

volumes:
  postgres_data:
    driver: local
    labels:
      app: database
  redis_data:
    driver: local
    labels:
      app: redis
```

### Sugar Docker Plugin (script.json)

```json
{
  "task": [
    {
      "docker": {
        "operator": "create_composition",
        "name": "microservices_app",
        "version": "3.8",
        "services": {
          "api_gateway": {
            "image": "nginx:alpine",
            "ports": ["8080:80"],
            "environment": {
              "UPSTREAM_API": "http://api_service:3000",
              "UPSTREAM_AUTH": "http://auth_service:3001"
            },
            "volumes": ["./nginx.conf:/etc/nginx/nginx.conf"],
            "networks": ["app_network"],
            "depends_on": ["api_service", "auth_service"],
            "healthcheck": {
              "test": ["CMD", "curl", "-f", "http://localhost/health"],
              "interval": "30s",
              "timeout": "10s",
              "retries": 3,
              "start_period": "40s"
            },
            "labels": {
              "app": "api_gateway",
              "tier": "frontend"
            }
          },
          "api_service": {
            "image": "node:16-alpine",
            "ports": ["3000:3000"],
            "environment": {
              "NODE_ENV": "production",
              "DB_HOST": "database",
              "DB_PORT": "5432",
              "REDIS_HOST": "redis",
              "REDIS_PORT": "6379"
            },
            "volumes": ["./api:/app", "/app/node_modules"],
            "networks": ["app_network"],
            "depends_on": ["database", "redis"],
            "working_dir": "/app",
            "command": ["npm", "start"],
            "healthcheck": {
              "test": ["CMD", "curl", "-f", "http://localhost:3000/health"],
              "interval": "30s",
              "timeout": "10s",
              "retries": 3
            },
            "labels": {
              "app": "api_service",
              "tier": "backend"
            }
          },
          "auth_service": {
            "image": "node:16-alpine",
            "ports": ["3001:3001"],
            "environment": {
              "NODE_ENV": "production",
              "JWT_SECRET": "your-secret-key",
              "DB_HOST": "database",
              "DB_PORT": "5432"
            },
            "volumes": ["./auth:/app", "/app/node_modules"],
            "networks": ["app_network"],
            "depends_on": ["database"],
            "working_dir": "/app",
            "command": ["npm", "start"],
            "healthcheck": {
              "test": ["CMD", "curl", "-f", "http://localhost:3001/health"],
              "interval": "30s",
              "timeout": "10s",
              "retries": 3
            },
            "labels": {
              "app": "auth_service",
              "tier": "backend"
            }
          },
          "database": {
            "image": "postgres:13-alpine",
            "ports": ["5432:5432"],
            "environment": {
              "POSTGRES_DB": "microservices",
              "POSTGRES_USER": "app_user",
              "POSTGRES_PASSWORD": "secure_password",
              "POSTGRES_INITDB_ARGS": "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
            },
            "volumes": ["postgres_data:/var/lib/postgresql/data", "./init.sql:/docker-entrypoint-initdb.d/init.sql"],
            "networks": ["app_network"],
            "healthcheck": {
              "test": ["CMD-SHELL", "pg_isready -U app_user -d microservices"],
              "interval": "30s",
              "timeout": "10s",
              "retries": 5,
              "start_period": "30s"
            },
            "labels": {
              "app": "database",
              "tier": "data"
            }
          },
          "redis": {
            "image": "redis:6-alpine",
            "ports": ["6379:6379"],
            "volumes": ["redis_data:/data", "./redis.conf:/usr/local/etc/redis/redis.conf"],
            "networks": ["app_network"],
            "command": ["redis-server", "/usr/local/etc/redis/redis.conf"],
            "healthcheck": {
              "test": ["CMD", "redis-cli", "ping"],
              "interval": "30s",
              "timeout": "10s",
              "retries": 3
            },
            "labels": {
              "app": "redis",
              "tier": "cache"
            }
          }
        },
        "networks": {
          "app_network": {
            "driver": "bridge",
            "labels": {
              "app": "microservices_app"
            }
          }
        },
        "volumes": {
          "postgres_data": {
            "driver": "local",
            "labels": {
              "app": "database"
            }
          },
          "redis_data": {
            "driver": "local",
            "labels": {
              "app": "redis"
            }
          }
        }
      }
    },
    {
      "docker": {
        "operator": "start_composition",
        "name": "microservices_app"
      }
    },
    {
      "docker": {
        "operator": "health_check",
        "composition_name": "microservices_app"
      }
    }
  ]
}
```

## Ventajas de Sugar sobre Docker Compose

### 1. **Programabilidad**
- **Docker Compose**: Estático, solo configuración
- **Sugar**: Dinámico, lógica condicional, loops, variables

### 2. **Integración con Variables**
```json
{
  "String::db_password": "mi_password_secreta",
  "String::app_version": "1.0.0",
  "task": [
    {
      "docker": {
        "operator": "create_composition",
        "services": {
          "database": {
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

### 3. **Lógica Condicional**
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
                "text": "✅ Aplicación saludable"
              }
            }
          ]
        },
        "else": {
          "task": [
            {
              "docker": {
                "operator": "restart_composition",
                "name": "mi_app"
              }
            }
          ]
        }
      }
    }
  ]
}
```

### 4. **Manejo de Errores**
```json
{
  "task": [
    {
      "try": {
        "task": [
          {
            "docker": {
              "operator": "start_composition",
              "name": "mi_app"
            }
          }
        ]
      },
      "catch": {
        "task": [
          {
            "print": {
              "text": "Error: {{error}}"
            }
          },
          {
            "docker": {
              "operator": "cleanup"
            }
          }
        ]
      }
    }
  ]
}
```

### 5. **Integración con Otros Plugins**
```json
{
  "task": [
    {
      "docker": {
        "operator": "start_composition",
        "name": "mi_app"
      }
    },
    {
      "request": {
        "operator": "get",
        "url": "http://localhost:8080/health",
        "result": "health_response"
      }
    },
    {
      "if": {
        "condition": "${health_response.status_code} == 200",
        "then": {
          "task": [
            {
              "print": {
                "text": "Aplicación iniciada correctamente"
              }
            }
          ]
        }
      }
    }
  ]
}
```

## Conversión Bidireccional

### Exportar Sugar a Docker Compose
```json
{
  "task": [
    {
      "docker": {
        "operator": "export_compose",
        "name": "mi_aplicacion",
        "output_file": "./docker-compose.yml"
      }
    }
  ]
}
```

### Importar Docker Compose a Sugar
```json
{
  "task": [
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

## Conclusión

El plugin Docker de Sugar proporciona toda la funcionalidad de Docker Compose con ventajas adicionales:

- **✅ Compatibilidad total** con Docker Compose
- **✅ Programabilidad** y lógica condicional
- **✅ Integración** con variables y otros plugins
- **✅ Manejo de errores** robusto
- **✅ Conversión bidireccional** automática
- **✅ Sintaxis declarativa** familiar

Esto hace que Sugar sea ideal para casos de uso que requieren más que solo configuración estática, como CI/CD, orquestación compleja, y automatización de infraestructura.