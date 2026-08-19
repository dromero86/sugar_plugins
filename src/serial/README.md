# Plugin Serial para Sugar

## Descripción

El Plugin Serial es una extensión universal para Sugar que proporciona comunicación serie completa en múltiples plataformas. Soporta Windows COM, Linux TTY y macOS cu.*, con funcionalidades avanzadas para todos los casos de uso de comunicación serie.

## Características

- **Multiplataforma**: Soporte completo para Windows, Linux y macOS
- **Sistema de Sesiones**: Múltiples conexiones simultáneas con nombres descriptivos
- **Sistema Meta**: Configuración previa y auto-conexión de sesiones
- **Comunicación Avanzada**: Lectura/escritura con múltiples codificaciones
- **Control de Líneas**: Control completo de líneas DTR, RTS, CTS, DSR, RI, CD
- **Monitoreo**: Sistema de monitoreo en tiempo real con logging
- **Protocolos**: Soporte para Modbus RTU, NMEA, ESC/POS, comandos AT
- **Robustez**: Reconexión automática y manejo de errores

## Instalación

### Dependencias

```bash
pip install pyserial>=3.5
```

### Configuración

El plugin se instala automáticamente con Sugar. Para verificar la instalación:

```bash
virtual/bin/python3 Sugar/Service/SugarConsole.py -p
```

## Uso Básico

### Sintaxis General

```json
{
  "serial": {
    "operator": "comando",
    "parametro1": "valor1",
    "parametro2": "valor2",
    "result": "variable_resultado"
  }
}
```

### Conexión Básica

```json
{
  "serial": {
    "operator": "connect",
    "port": "COM3",
    "baudrate": 115200,
    "session": "mi_dispositivo",
    "result": "connection_status"
  }
}
```

### Comunicación

```json
{
  "serial": {
    "operator": "write",
    "session": "mi_dispositivo",
    "data": "HOLA\\r\\n",
    "result": "write_result"
  }
}
```

## Comandos Disponibles

### Comandos de Conexión

#### connect
Establece conexión con un puerto serie.

**Parámetros:**
- `port` (string, requerido): Puerto serie
- `baudrate` (int, opcional): Velocidad en baudios (default: 9600)
- `timeout` (float, opcional): Timeout en segundos (default: 1.0)
- `parity` (string, opcional): Paridad ("NONE", "EVEN", "ODD", "MARK", "SPACE")
- `stopbits` (int, opcional): Bits de parada (1 o 2)
- `bytesize` (int, opcional): Tamaño de bytes (5, 6, 7, 8)
- `session` (string, opcional): Nombre de sesión
- `auto_reconnect` (boolean, opcional): Reconexión automática

#### disconnect
Cierra la conexión serie.

**Parámetros:**
- `session` (string, opcional): Nombre de sesión a desconectar
- `force` (boolean, opcional): Forzar desconexión

#### list_ports
Lista todos los puertos serie disponibles.

**Parámetros:**
- `include_info` (boolean, opcional): Incluir información detallada
- `filter` (string, opcional): Filtrar por tipo ("USB", "Bluetooth", "Virtual")

#### test_connection
Prueba conectividad a un puerto.

**Parámetros:**
- `port` (string, requerido): Puerto a probar
- `baudrate` (int, opcional): Velocidad para la prueba

### Comandos de Comunicación

#### write
Envía datos al puerto serie.

**Parámetros:**
- `data` (string/bytes, requerido): Datos a enviar
- `session` (string, opcional): Sesión a usar
- `encoding` (string, opcional): Codificación ("utf-8", "ascii", "hex", "binary")
- `add_newline` (boolean, opcional): Agregar salto de línea

#### read
Lee datos del puerto serie.

**Parámetros:**
- `session` (string, opcional): Sesión a usar
- `size` (int, opcional): Número de bytes a leer
- `timeout` (float, opcional): Timeout específico
- `encoding` (string, opcional): Codificación para decodificar

#### read_line
Lee una línea completa del puerto serie.

**Parámetros:**
- `session` (string, opcional): Sesión a usar
- `eol` (string, opcional): Caracteres de fin de línea
- `timeout` (float, opcional): Timeout para la lectura

#### read_until
Lee datos hasta encontrar un delimitador.

**Parámetros:**
- `session` (string, opcional): Sesión a usar
- `terminator` (string, requerido): Delimitador de terminación
- `timeout` (float, opcional): Timeout

#### read_bytes
Lee un número específico de bytes.

**Parámetros:**
- `session` (string, opcional): Sesión a usar
- `size` (int, requerido): Número de bytes a leer
- `timeout` (float, opcional): Timeout

#### flush
Limpia los buffers de entrada y salida.

**Parámetros:**
- `session` (string, opcional): Sesión a usar

### Comandos de Configuración

#### configure
Configura parámetros del puerto serie.

**Parámetros:**
- `session` (string, opcional): Sesión a configurar
- `baudrate` (int, opcional): Nueva velocidad
- `parity` (string, opcional): Nueva paridad
- `stopbits` (int, opcional): Nuevos bits de parada
- `bytesize` (int, opcional): Nuevo tamaño de bytes
- `timeout` (float, opcional): Nuevo timeout
- `xonxoff` (boolean, opcional): Control de flujo XON/XOFF
- `rtscts` (boolean, opcional): Control de flujo RTS/CTS
- `dsrdtr` (boolean, opcional): Control de flujo DSR/DTR

#### get_config
Obtiene configuración actual del puerto.

**Parámetros:**
- `session` (string, opcional): Sesión a consultar

### Comandos de Control de Líneas

#### set_dtr
Controla la línea DTR (Data Terminal Ready).

**Parámetros:**
- `session` (string, opcional): Sesión a controlar
- `state` (boolean, requerido): Estado de DTR

#### set_rts
Controla la línea RTS (Request To Send).

**Parámetros:**
- `session` (string, opcional): Sesión a controlar
- `state` (boolean, requerido): Estado de RTS

#### get_cts
Lee el estado de la línea CTS (Clear To Send).

**Parámetros:**
- `session` (string, opcional): Sesión a consultar

#### get_dsr
Lee el estado de la línea DSR (Data Set Ready).

**Parámetros:**
- `session` (string, opcional): Sesión a consultar

#### get_ri
Lee el estado de la línea RI (Ring Indicator).

**Parámetros:**
- `session` (string, opcional): Sesión a consultar

#### get_cd
Lee el estado de la línea CD (Carrier Detect).

**Parámetros:**
- `session` (string, opcional): Sesión a consultar

### Comandos de Monitoreo

#### get_status
Obtiene estado del puerto o todas las sesiones.

**Parámetros:**
- `session` (string, opcional): Sesión específica

#### get_info
Obtiene información detallada del puerto.

**Parámetros:**
- `session` (string, opcional): Sesión específica

#### monitor
Inicia monitoreo continuo del puerto serie.

**Parámetros:**
- `session` (string, opcional): Sesión a monitorear
- `duration` (float, opcional): Duración del monitoreo en segundos
- `log_file` (string, opcional): Archivo para guardar logs
- `filter` (string, opcional): Filtro de datos

#### log_activity
Obtiene logs de actividad del monitor.

**Parámetros:**
- `session` (string, opcional): Sesión a consultar

## Sistema Meta

### Configuración Meta

```json
{
  "meta": {
    "serial": {
      "options": {
        "dispositivo_1": {
          "port": "COM3",
          "baudrate": 115200,
          "timeout": 2.0,
          "parity": "NONE",
          "stopbits": 1,
          "bytesize": 8,
          "auto_connect": true,
          "auto_reconnect": true
        },
        "dispositivo_2": {
          "port": "/dev/ttyUSB0",
          "baudrate": 9600,
          "timeout": 1.0,
          "auto_connect": false
        }
      }
    }
  }
}
```

### Auto-conexión

Las sesiones con `auto_connect: true` se conectan automáticamente al inicializar el plugin.

## Ejemplos de Uso

### Comunicación Básica

```json
{
  "meta": {
    "serial": {
      "options": {
        "arduino": {
          "port": "COM3",
          "baudrate": 115200,
          "auto_connect": true
        }
      }
    }
  },
  "task": [
    {
      "serial": {
        "operator": "write",
        "session": "arduino",
        "data": "LED_ON\\n",
        "result": "write_result"
      }
    },
    {
      "serial": {
        "operator": "read_line",
        "session": "arduino",
        "timeout": 2.0,
        "result": "response"
      }
    },
    {
      "print": {
        "text": "Respuesta: {{response}}"
      }
    }
  ]
}
```

### Comunicación Industrial

```json
{
  "task": [
    {
      "serial": {
        "operator": "connect",
        "port": "/dev/ttyS0",
        "baudrate": 19200,
        "parity": "EVEN",
        "session": "plc"
      }
    },
    {
      "serial": {
        "operator": "write",
        "session": "plc",
        "data": "01 03 00 00 00 01 84 0A",
        "encoding": "hex"
      }
    },
    {
      "serial": {
        "operator": "read_bytes",
        "session": "plc",
        "size": 7,
        "encoding": "hex",
        "result": "plc_response"
      }
    }
  ]
}
```

### Monitoreo en Tiempo Real

```json
{
  "task": [
    {
      "serial": {
        "operator": "connect",
        "port": "COM6",
        "session": "sensor"
      }
    },
    {
      "serial": {
        "operator": "monitor",
        "session": "sensor",
        "duration": 60.0,
        "log_file": "sensor.log"
      }
    },
    {
      "loop": {
        "count": 10,
        "task": [
          {
            "serial": {
              "operator": "read_line",
              "session": "sensor",
              "result": "data"
            }
          },
          {
            "print": {
              "text": "Datos: {{data}}"
            }
          }
        ]
      }
    }
  ]
}
```

## Casos de Uso Específicos

### Dispositivos Industriales
- **PLCs**: Comunicación Modbus RTU
- **Sensores**: Lectura de datos en tiempo real
- **Actuadores**: Control de dispositivos

### Sistemas Embebidos
- **Microcontroladores**: Arduino, ESP32, ARM
- **Sistemas IoT**: Comunicación con dispositivos conectados
- **Prototipos**: Desarrollo y testing

### Dispositivos GPS
- **Receptores GPS**: Protocolo NMEA
- **Navegación**: Obtención de coordenadas
- **Tracking**: Monitoreo de posición

### Impresoras
- **Térmicas**: Comandos ESC/POS
- **Etiquetas**: Impresión de códigos de barras
- **Tickets**: Sistemas de punto de venta

### Módems
- **Serie**: Comandos AT
- **Comunicación**: Envío de SMS
- **Datos**: Transmisión de datos

## Compatibilidad

### Plataformas Soportadas

- **Windows**: Puertos COM (COM1-COM256)
- **Linux**: Dispositivos TTY (/dev/ttyUSB*, /dev/ttyACM*, /dev/ttyS*)
- **macOS**: Dispositivos cu.* (/dev/cu.usbserial*, /dev/cu.usbmodem*)

### Velocidades de Baudios Soportadas

50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 500000, 576000, 921600, 1000000, 1152000, 1500000, 2000000, 2500000, 3000000, 3500000, 4000000

### Paridades Soportadas

- **NONE**: Sin paridad
- **EVEN**: Paridad par
- **ODD**: Paridad impar
- **MARK**: Bit de marca siempre 1
- **SPACE**: Bit de espacio siempre 0

## Troubleshooting

### Problemas Comunes

#### Puerto no encontrado
- Verificar que el dispositivo esté conectado
- Usar `list_ports` para ver puertos disponibles
- Verificar permisos en sistemas Unix

#### Error de conexión
- Verificar velocidad de baudios
- Comprobar configuración de paridad
- Verificar que el puerto no esté en uso

#### Datos no recibidos
- Verificar timeout
- Comprobar terminadores de línea
- Verificar configuración de codificación

#### Permisos en Linux
```bash
sudo usermod -a -G dialout $USER
sudo chmod 666 /dev/ttyUSB0
```

### Debug

Habilitar logs detallados:

```json
{
  "serial": {
    "operator": "get_status",
    "result": "debug_info"
  }
}
```

## Contribución

Para contribuir al plugin:

1. Fork del repositorio
2. Crear rama de feature
3. Implementar cambios
4. Agregar tests
5. Crear pull request

## Licencia

MIT License - Ver archivo LICENSE para detalles.

## Soporte

Para soporte y preguntas:

- **Issues**: Crear issue en GitHub
- **Documentación**: Ver ejemplos en `/examples/`
- **Tests**: Ejecutar tests en `/tests/`