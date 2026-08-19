# Guía de Troubleshooting - Plugin Serial

## Problemas Comunes

### 1. Puerto No Encontrado

#### Síntomas
- Error: "Puerto no encontrado" o "Port not found"
- El dispositivo no aparece en `list_ports`

#### Soluciones

**Windows:**
```bash
# Verificar en Administrador de Dispositivos
# Buscar en "Puertos (COM y LPT)"
# Reinstalar drivers si es necesario
```

**Linux:**
```bash
# Verificar dispositivos conectados
ls /dev/ttyUSB* /dev/ttyACM*

# Verificar permisos
ls -la /dev/ttyUSB0

# Agregar usuario al grupo dialout
sudo usermod -a -G dialout $USER

# Cambiar permisos temporalmente
sudo chmod 666 /dev/ttyUSB0
```

**macOS:**
```bash
# Verificar dispositivos
ls /dev/cu.*

# Verificar permisos
ls -la /dev/cu.usbserial*
```

#### Verificación
```json
{
  "serial": {
    "operator": "list_ports",
    "include_info": true,
    "result": "ports"
  }
}
```

### 2. Error de Conexión

#### Síntomas
- Error: "No se puede abrir el puerto"
- Timeout en conexión
- Dispositivo no responde

#### Soluciones

**Verificar Configuración:**
```json
{
  "serial": {
    "operator": "test_connection",
    "port": "COM3",
    "baudrate": 9600,
    "result": "test_result"
  }
}
```

**Verificar Velocidad de Baudios:**
- Probar velocidades comunes: 9600, 115200, 57600
- Verificar documentación del dispositivo

**Verificar Paridad:**
- Probar diferentes paridades: NONE, EVEN, ODD
- Verificar configuración del dispositivo

**Verificar Puerto en Uso:**
```bash
# Windows
netstat -an | findstr COM3

# Linux
lsof /dev/ttyUSB0

# macOS
lsof /dev/cu.usbserial*
```

### 3. Datos No Recibidos

#### Síntomas
- `read` retorna datos vacíos
- Timeout en lectura
- Datos incompletos

#### Soluciones

**Verificar Timeout:**
```json
{
  "serial": {
    "operator": "read_line",
    "session": "device",
    "timeout": 5.0,
    "result": "data"
  }
}
```

**Verificar Terminadores:**
```json
{
  "serial": {
    "operator": "read_until",
    "session": "device",
    "terminator": "\\r\\n",
    "result": "data"
  }
}
```

**Verificar Codificación:**
```json
{
  "serial": {
    "operator": "read",
    "session": "device",
    "encoding": "ascii",
    "result": "data"
  }
}
```

**Verificar Buffers:**
```json
{
  "serial": {
    "operator": "flush",
    "session": "device"
  }
}
```

### 4. Datos Corruptos

#### Síntomas
- Caracteres extraños en datos recibidos
- Datos incompletos
- Errores de decodificación

#### Soluciones

**Verificar Velocidad de Baudios:**
- Asegurar que coincida con el dispositivo
- Probar velocidades cercanas

**Verificar Paridad:**
- Verificar configuración de paridad
- Probar sin paridad (NONE)

**Verificar Bits de Parada:**
- Verificar configuración de stop bits
- Probar con 1 o 2 bits

**Verificar Codificación:**
```json
{
  "serial": {
    "operator": "read",
    "session": "device",
    "encoding": "latin1",
    "result": "data"
  }
}
```

### 5. Problemas de Permisos

#### Síntomas
- Error: "Permission denied"
- No se puede acceder al puerto
- Error de permisos en Linux/macOS

#### Soluciones

**Linux:**
```bash
# Agregar usuario al grupo dialout
sudo usermod -a -G dialout $USER

# Cambiar permisos del dispositivo
sudo chmod 666 /dev/ttyUSB0

# Crear regla udev permanente
sudo nano /etc/udev/rules.d/99-serial.rules
# Agregar: SUBSYSTEM=="tty", ATTRS{idVendor}=="1234", ATTRS{idProduct}=="5678", MODE="0666"
sudo udevadm control --reload-rules
```

**macOS:**
```bash
# Verificar permisos
ls -la /dev/cu.usbserial*

# Cambiar permisos si es necesario
sudo chmod 666 /dev/cu.usbserial*
```

### 6. Problemas de Drivers

#### Síntomas
- Dispositivo no reconocido
- Puerto aparece como "Unknown Device"
- Error de driver

#### Soluciones

**Windows:**
1. Abrir Administrador de Dispositivos
2. Buscar dispositivo con error
3. Actualizar driver
4. Reinstalar driver del fabricante

**Linux:**
```bash
# Verificar drivers cargados
lsmod | grep usbserial

# Cargar driver si es necesario
sudo modprobe usbserial

# Verificar información del dispositivo
lsusb -v
```

**macOS:**
1. Verificar en Información del Sistema
2. Instalar driver del fabricante
3. Reiniciar sistema si es necesario

### 7. Problemas de Control de Flujo

#### Síntomas
- Datos se pierden
- Comunicación intermitente
- Timeouts frecuentes

#### Soluciones

**Habilitar Control de Flujo:**
```json
{
  "serial": {
    "operator": "configure",
    "session": "device",
    "rtscts": true,
    "result": "config_result"
  }
}
```

**Control Manual de Líneas:**
```json
{
  "serial": {
    "operator": "set_dtr",
    "session": "device",
    "state": true
  }
}
```

### 8. Problemas de Monitoreo

#### Síntomas
- Monitor no inicia
- No se reciben datos en monitor
- Logs vacíos

#### Soluciones

**Verificar Sesión:**
```json
{
  "serial": {
    "operator": "get_status",
    "session": "device",
    "result": "status"
  }
}
```

**Verificar Filtros:**
```json
{
  "serial": {
    "operator": "monitor",
    "session": "device",
    "filter": ".*",
    "result": "monitor_result"
  }
}
```

**Verificar Archivo de Log:**
```json
{
  "serial": {
    "operator": "monitor",
    "session": "device",
    "log_file": "/tmp/serial.log",
    "result": "monitor_result"
  }
}
```

## Herramientas de Diagnóstico

### 1. Listar Puertos Disponibles

```json
{
  "serial": {
    "operator": "list_ports",
    "include_info": true,
    "result": "ports"
  }
}
```

### 2. Probar Conexión

```json
{
  "serial": {
    "operator": "test_connection",
    "port": "COM3",
    "baudrate": 9600,
    "result": "test_result"
  }
}
```

### 3. Obtener Estado de Sesión

```json
{
  "serial": {
    "operator": "get_status",
    "session": "device",
    "result": "status"
  }
}
```

### 4. Obtener Información Detallada

```json
{
  "serial": {
    "operator": "get_info",
    "session": "device",
    "result": "info"
  }
}
```

### 5. Verificar Configuración

```json
{
  "serial": {
    "operator": "get_config",
    "session": "device",
    "result": "config"
  }
}
```

## Comandos de Sistema Útiles

### Windows

```cmd
# Ver puertos COM
mode

# Ver dispositivos USB
wmic path Win32_SerialPort get DeviceID,Description

# Ver procesos usando puerto
netstat -an | findstr COM3
```

### Linux

```bash
# Ver dispositivos serie
ls /dev/tty*

# Ver información USB
lsusb

# Ver procesos usando puerto
lsof /dev/ttyUSB0

# Ver logs del sistema
dmesg | grep tty
```

### macOS

```bash
# Ver dispositivos serie
ls /dev/cu.*

# Ver información USB
system_profiler SPUSBDataType

# Ver procesos usando puerto
lsof /dev/cu.usbserial*
```

## Logs y Debugging

### Habilitar Logs Detallados

```json
{
  "serial": {
    "operator": "get_status",
    "result": "debug_info"
  }
}
```

### Monitoreo con Logs

```json
{
  "serial": {
    "operator": "monitor",
    "session": "device",
    "log_file": "debug.log",
    "result": "monitor_result"
  }
}
```

### Verificar Logs de Actividad

```json
{
  "serial": {
    "operator": "log_activity",
    "session": "device",
    "result": "activity_log"
  }
}
```

## Casos Específicos por Dispositivo

### Arduino

**Configuración Típica:**
```json
{
  "port": "COM3",
  "baudrate": 115200,
  "parity": "NONE",
  "stopbits": 1,
  "bytesize": 8
}
```

**Problemas Comunes:**
- Velocidad incorrecta
- Puerto incorrecto después de reinicio
- Timeout en lectura

### PLC Industrial

**Configuración Típica:**
```json
{
  "port": "/dev/ttyS0",
  "baudrate": 19200,
  "parity": "EVEN",
  "stopbits": 1,
  "bytesize": 8,
  "rtscts": true
}
```

**Problemas Comunes:**
- Control de flujo requerido
- Paridad específica
- Timeouts largos

### GPS

**Configuración Típica:**
```json
{
  "port": "COM6",
  "baudrate": 4800,
  "parity": "NONE",
  "stopbits": 1,
  "bytesize": 8
}
```

**Problemas Comunes:**
- Velocidad baja
- Datos NMEA específicos
- Terminadores específicos

### Impresora Térmica

**Configuración Típica:**
```json
{
  "port": "COM7",
  "baudrate": 9600,
  "parity": "NONE",
  "stopbits": 1,
  "bytesize": 8
}
```

**Problemas Comunes:**
- Comandos ESC/POS específicos
- Codificación binaria
- Timeouts cortos

## Contacto y Soporte

Para problemas no resueltos:

1. **Verificar logs**: Revisar logs del sistema y del plugin
2. **Documentar problema**: Incluir configuración y mensajes de error
3. **Crear issue**: Reportar en el repositorio del proyecto
4. **Incluir información**:
   - Sistema operativo
   - Versión de Sugar
   - Configuración del dispositivo
   - Logs de error
   - Pasos para reproducir