# MCP Server Plugin para Sugar Language

## Descripción

El plugin **MCP Server** implementa un servidor nativo del **Model Context Protocol (MCP)** para Sugar Language, permitiendo que Sugar actúe como un servidor MCP para asistentes de IA y herramientas.

## Características

### 🌐 Protocolos Soportados
- **WebSocket**: Servidor MCP sobre WebSocket
- **TCP**: Servidor MCP sobre TCP con mensajes JSON

### 🛠️ Herramientas Nativas
- **execute_sugar_script**: Ejecutar scripts de Sugar
- **read_file**: Leer contenido de archivos
- **write_file**: Escribir contenido a archivos
- **http_request**: Realizar peticiones HTTP

### 📚 Recursos Nativos
- **Documentación**: Acceso a la documentación de Sugar
- **Ejemplos**: Acceso a ejemplos y tutoriales

### 🔧 Funcionalidades Avanzadas
- **Registro dinámico**: Agregar herramientas y recursos en tiempo de ejecución
- **Gestión de clientes**: Manejo de múltiples conexiones simultáneas
- **Protocolo MCP completo**: Implementación completa del protocolo MCP v2024-11-05

## Instalación

### Dependencias
El plugin no requiere dependencias externas adicionales, utiliza las capacidades nativas de Sugar.

### Activación
El plugin se carga automáticamente cuando está disponible en `plugins/src/mcp_server/`.

## Uso

### Comandos Disponibles

#### 1. Iniciar Servidor MCP

**WebSocket Server:**
```json
{
    "mcp_server": {
        "operator": "start_server",
        "host": "0.0.0.0",
        "port": 3000,
        "protocol": "websocket",
        "result": "server_status"
    }
}
```

**TCP Server:**
```json
{
    "mcp_server": {
        "operator": "start_server",
        "host": "0.0.0.0",
        "port": 3000,
        "protocol": "tcp",
        "result": "server_status"
    }
}
```

#### 2. Detener Servidor
```json
{
    "mcp_server": {
        "operator": "stop_server",
        "result": "stop_status"
    }
}
```

#### 3. Registrar Herramienta Personalizada
```json
{
    "mcp_server": {
        "operator": "register_tool",
        "name": "mi_herramienta",
        "description": "Descripción de mi herramienta",
        "input_schema": {
            "type": "object",
            "properties": {
                "parametro": {
                    "type": "string",
                    "description": "Descripción del parámetro"
                }
            },
            "required": ["parametro"]
        },
        "handler": "mi_handler_function",
        "result": "registration_status"
    }
}
```

#### 4. Registrar Recurso Personalizado
```json
{
    "mcp_server": {
        "operator": "register_resource",
        "uri": "sugar://mi_recurso.txt",
        "name": "Mi Recurso",
        "description": "Descripción de mi recurso",
        "mime_type": "text/plain",
        "handler": "mi_resource_handler",
        "result": "registration_status"
    }
}
```

#### 5. Listar Herramientas
```json
{
    "mcp_server": {
        "operator": "list_tools",
        "result": "tools_list"
    }
}
```

#### 6. Listar Recursos
```json
{
    "mcp_server": {
        "operator": "list_resources",
        "result": "resources_list"
    }
}
```

#### 7. Obtener Estado del Servidor
```json
{
    "mcp_server": {
        "operator": "get_server_status",
        "result": "server_status"
    }
}
```

#### 8. Probar Conexión
```json
{
    "mcp_server": {
        "operator": "test_connection",
        "result": "connection_status"
    }
}
```

## Ejemplos Completos

### Ejemplo 1: Servidor MCP Básico

```json
{
    "name": "MCP Server Básico",
    "description": "Ejemplo básico de servidor MCP",
    "tasks": [
        {
            "mcp_server": {
                "operator": "start_server",
                "host": "localhost",
                "port": 3000,
                "protocol": "websocket",
                "result": "server_status"
            }
        },
        {
            "print": {
                "text": "Servidor MCP iniciado: {{server_status.message}}"
            }
        },
        {
            "mcp_server": {
                "operator": "get_server_status",
                "result": "status"
            }
        },
        {
            "print": {
                "text": "Estado del servidor: {{status}}"
            }
        }
    ]
}
```

### Ejemplo 2: Servidor con Herramientas Personalizadas

```json
{
    "name": "MCP Server con Herramientas",
    "description": "Servidor MCP con herramientas personalizadas",
    "tasks": [
        {
            "mcp_server": {
                "operator": "start_server",
                "host": "0.0.0.0",
                "port": 3000,
                "protocol": "tcp",
                "result": "server_status"
            }
        },
        {
            "mcp_server": {
                "operator": "register_tool",
                "name": "calcular_suma",
                "description": "Calcular la suma de dos números",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "Primer número"},
                        "b": {"type": "number", "description": "Segundo número"}
                    },
                    "required": ["a", "b"]
                },
                "handler": "suma_handler",
                "result": "tool_status"
            }
        },
        {
            "mcp_server": {
                "operator": "list_tools",
                "result": "tools"
            }
        },
        {
            "print": {
                "text": "Herramientas disponibles: {{tools.tools}}"
            }
        }
    ]
}
```

### Ejemplo 3: Servidor con Recursos

```json
{
    "name": "MCP Server con Recursos",
    "description": "Servidor MCP con recursos personalizados",
    "tasks": [
        {
            "mcp_server": {
                "operator": "start_server",
                "host": "localhost",
                "port": 3000,
                "protocol": "websocket",
                "result": "server_status"
            }
        },
        {
            "mcp_server": {
                "operator": "register_resource",
                "uri": "sugar://config.json",
                "name": "Configuración",
                "description": "Archivo de configuración del sistema",
                "mime_type": "application/json",
                "handler": "config_handler",
                "result": "resource_status"
            }
        },
        {
            "mcp_server": {
                "operator": "list_resources",
                "result": "resources"
            }
        },
        {
            "print": {
                "text": "Recursos disponibles: {{resources.resources}}"
            }
        }
    ]
}
```

## Protocolo MCP

### Mensajes Soportados

#### 1. Initialize
```json
{
    "id": "1",
    "type": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {"listChanged": true},
            "resources": {"listChanged": true}
        },
        "clientInfo": {
            "name": "Test Client",
            "version": "1.0.0"
        }
    }
}
```

#### 2. Tools/Call
```json
{
    "id": "2",
    "type": "tools/call",
    "params": {
        "name": "read_file",
        "arguments": {
            "file_path": "/tmp/test.txt",
            "encoding": "utf-8"
        }
    }
}
```

#### 3. Tools/List
```json
{
    "id": "3",
    "type": "tools/list"
}
```

#### 4. Resources/Read
```json
{
    "id": "4",
    "type": "resources/read",
    "params": {
        "uri": "sugar://docs/language/README.md"
    }
}
```

#### 5. Resources/List
```json
{
    "id": "5",
    "type": "resources/list"
}
```

## Integración con Clientes MCP

### Cliente WebSocket
```javascript
const ws = new WebSocket('ws://localhost:3000/mcp');

ws.onopen = () => {
    // Enviar mensaje de inicialización
    ws.send(JSON.stringify({
        id: "1",
        type: "initialize",
        params: {
            protocolVersion: "2024-11-05",
            capabilities: {
                tools: {listChanged: true},
                resources: {listChanged: true}
            },
            clientInfo: {
                name: "Test Client",
                version: "1.0.0"
            }
        }
    }));
};

ws.onmessage = (event) => {
    const response = JSON.parse(event.data);
    console.log('MCP Response:', response);
};
```

### Cliente TCP
```python
import socket
import json

# Conectar al servidor MCP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 3000))

# Enviar mensaje de inicialización
init_message = {
    "id": "1",
    "type": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {"listChanged": True},
            "resources": {"listChanged": True}
        },
        "clientInfo": {
            "name": "Python Client",
            "version": "1.0.0"
        }
    }
}

sock.send((json.dumps(init_message) + "\n").encode('utf-8'))

# Recibir respuesta
response = sock.recv(4096).decode('utf-8')
print('MCP Response:', json.loads(response))
```

## Configuración Avanzada

### Configuración de Seguridad
```json
{
    "mcp_server": {
        "operator": "start_server",
        "host": "0.0.0.0",
        "port": 3000,
        "protocol": "websocket",
        "security": {
            "authentication": {
                "type": "token",
                "required": true,
                "tokens": ["token1", "token2"]
            },
            "rate_limiting": {
                "enabled": true,
                "max_requests_per_minute": 100
            }
        },
        "result": "server_status"
    }
}
```

### Configuración de Logging
```json
{
    "mcp_server": {
        "operator": "start_server",
        "host": "localhost",
        "port": 3000,
        "protocol": "tcp",
        "logging": {
            "level": "DEBUG",
            "file": "/tmp/mcp_server.log",
            "format": "json"
        },
        "result": "server_status"
    }
}
```

## Troubleshooting

### Problemas Comunes

#### 1. Puerto en Uso
```
Error: Address already in use
```
**Solución**: Cambiar el puerto o detener el proceso que usa el puerto.

#### 2. Permisos de Red
```
Error: Permission denied
```
**Solución**: Verificar permisos de red y firewall.

#### 3. Cliente no Conecta
```
Error: Connection refused
```
**Solución**: Verificar que el servidor esté ejecutándose y el puerto sea correcto.

### Debug
```json
{
    "mcp_server": {
        "operator": "get_server_status",
        "result": "debug_info"
    }
}
```

## Compatibilidad

- **Protocolo MCP**: v2024-11-05
- **Sugar Language**: v2.0.0+
- **Python**: 3.8+
- **Sistemas Operativos**: Linux, Windows, macOS

## Licencia

MIT License - Ver archivo LICENSE para más detalles.

## Contribuir

1. Fork el repositorio
2. Crear una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Crear un Pull Request

## Soporte

Para soporte y preguntas:
- Crear un issue en el repositorio
- Consultar la documentación de Sugar Language
- Revisar los ejemplos en `/examples/`
