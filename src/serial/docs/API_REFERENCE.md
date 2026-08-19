# Referencia de API - Plugin Serial

## Clase SerialPlugin

### Constructor

```python
SerialPlugin(context=None, plugin_config=None)
```

**Parámetros:**
- `context`: Contexto de Sugar (opcional)
- `plugin_config`: Configuración del plugin (opcional)

### Métodos Principales

#### get_available_commands()
Retorna lista de comandos disponibles.

**Retorna:** `List[str]`

#### execute(command, config)
Ejecuta un comando del plugin.

**Parámetros:**
- `command` (str): Comando a ejecutar
- `config` (Dict[str, Any]): Configuración del comando

**Retorna:** `Any`

#### meta_hook(config)
Configura el plugin a través del sistema meta.

**Parámetros:**
- `config` (Dict[str, Any]): Configuración meta

**Retorna:** `Dict[str, Any]`

## Clase SerialConnection

### Constructor

```python
SerialConnection(port, **kwargs)
```

**Parámetros:**
- `port` (str): Puerto serie
- `**kwargs`: Parámetros de configuración

### Métodos

#### connect()
Establece la conexión serie.

**Retorna:** `bool`

#### disconnect()
Cierra la conexión serie.

**Retorna:** `bool`

#### write(data, encoding="utf-8")
Envía datos al puerto serie.

**Parámetros:**
- `data` (str): Datos a enviar
- `encoding` (str): Codificación

**Retorna:** `bool`

#### read(size=1, timeout=None)
Lee datos del puerto serie.

**Parámetros:**
- `size` (int): Número de bytes a leer
- `timeout` (float): Timeout específico

**Retorna:** `str`

#### read_line(eol="\\n", timeout=None)
Lee una línea del puerto serie.

**Parámetros:**
- `eol` (str): Caracteres de fin de línea
- `timeout` (float): Timeout específico

**Retorna:** `str`

#### read_until(terminator, timeout=None)
Lee datos hasta encontrar un terminador.

**Parámetros:**
- `terminator` (str): Terminador a buscar
- `timeout` (float): Timeout específico

**Retorna:** `str`

#### read_bytes(size, timeout=None)
Lee un número específico de bytes.

**Parámetros:**
- `size` (int): Número de bytes a leer
- `timeout` (float): Timeout específico

**Retorna:** `bytes`

#### flush()
Limpia los buffers.

**Retorna:** `bool`

#### configure(**kwargs)
Configura parámetros del puerto.

**Parámetros:**
- `**kwargs`: Parámetros a configurar

**Retorna:** `bool`

#### set_dtr(state)
Controla la línea DTR.

**Parámetros:**
- `state` (bool): Estado de DTR

**Retorna:** `bool`

#### set_rts(state)
Controla la línea RTS.

**Parámetros:**
- `state` (bool): Estado de RTS

**Retorna:** `bool`

#### get_cts()
Lee el estado de CTS.

**Retorna:** `bool`

#### get_dsr()
Lee el estado de DSR.

**Retorna:** `bool`

#### get_ri()
Lee el estado de RI.

**Retorna:** `bool`

#### get_cd()
Lee el estado de CD.

**Retorna:** `bool`

#### get_status()
Obtiene el estado de la conexión.

**Retorna:** `Dict[str, Any]`

#### get_info()
Obtiene información del puerto.

**Retorna:** `Dict[str, Any]`

## Clase SerialSession

### Constructor

```python
SerialSession(name, port, **kwargs)
```

**Parámetros:**
- `name` (str): Nombre de la sesión
- `port` (str): Puerto serie
- `**kwargs`: Parámetros de configuración

### Métodos

#### add_callback(event, callback)
Agrega un callback para un evento.

**Parámetros:**
- `event` (str): Tipo de evento
- `callback` (Callable): Función callback

#### remove_callback(event, callback)
Remueve un callback para un evento.

**Parámetros:**
- `event` (str): Tipo de evento
- `callback` (Callable): Función callback

#### connect()
Establece la conexión de la sesión.

**Retorna:** `bool`

#### disconnect()
Cierra la conexión de la sesión.

**Retorna:** `bool`

#### write(data, encoding="utf-8")
Envía datos a través de la sesión.

**Parámetros:**
- `data` (str): Datos a enviar
- `encoding` (str): Codificación

**Retorna:** `bool`

#### read(size=1, timeout=None)
Lee datos de la sesión.

**Parámetros:**
- `size` (int): Número de bytes a leer
- `timeout` (float): Timeout específico

**Retorna:** `str`

#### read_line(eol="\\n", timeout=None)
Lee una línea de la sesión.

**Parámetros:**
- `eol` (str): Caracteres de fin de línea
- `timeout` (float): Timeout específico

**Retorna:** `str`

#### read_until(terminator, timeout=None)
Lee datos hasta encontrar un terminador.

**Parámetros:**
- `terminator` (str): Terminador a buscar
- `timeout` (float): Timeout específico

**Retorna:** `str`

#### read_bytes(size, timeout=None)
Lee bytes de la sesión.

**Parámetros:**
- `size` (int): Número de bytes a leer
- `timeout` (float): Timeout específico

**Retorna:** `bytes`

#### flush()
Limpia los buffers de la sesión.

**Retorna:** `bool`

#### configure(**kwargs)
Configura la sesión.

**Parámetros:**
- `**kwargs`: Parámetros a configurar

**Retorna:** `bool`

#### set_dtr(state)
Controla DTR de la sesión.

**Parámetros:**
- `state` (bool): Estado de DTR

**Retorna:** `bool`

#### set_rts(state)
Controla RTS de la sesión.

**Parámetros:**
- `state` (bool): Estado de RTS

**Retorna:** `bool`

#### get_cts()
Lee CTS de la sesión.

**Retorna:** `bool`

#### get_dsr()
Lee DSR de la sesión.

**Retorna:** `bool`

#### get_ri()
Lee RI de la sesión.

**Retorna:** `bool`

#### get_cd()
Lee CD de la sesión.

**Retorna:** `bool`

#### get_status()
Obtiene el estado de la sesión.

**Retorna:** `Dict[str, Any]`

#### get_info()
Obtiene información de la sesión.

**Retorna:** `Dict[str, Any]`

#### is_connected()
Verifica si la sesión está conectada.

**Retorna:** `bool`

#### cleanup()
Limpia recursos de la sesión.

## Clase SerialMonitor

### Constructor

```python
SerialMonitor(session)
```

**Parámetros:**
- `session` (SerialSession): Sesión a monitorear

### Métodos

#### add_callback(event, callback)
Agrega un callback para un evento.

**Parámetros:**
- `event` (str): Tipo de evento
- `callback` (Callable): Función callback

#### remove_callback(event, callback)
Remueve un callback para un evento.

**Parámetros:**
- `event` (str): Tipo de evento
- `callback` (Callable): Función callback

#### start_monitoring(duration=None, log_file=None, filter_pattern=None)
Inicia el monitoreo.

**Parámetros:**
- `duration` (float): Duración del monitoreo
- `log_file` (str): Archivo para logs
- `filter_pattern` (str): Patrón de filtro

**Retorna:** `bool`

#### stop_monitoring()
Detiene el monitoreo.

**Retorna:** `bool`

#### get_buffer()
Obtiene el buffer de datos.

**Retorna:** `List[Dict[str, Any]]`

#### clear_buffer()
Limpia el buffer de datos.

#### get_status()
Obtiene el estado del monitor.

**Retorna:** `Dict[str, Any]`

#### cleanup()
Limpia recursos del monitor.

## Clase SerialUtils

### Métodos Estáticos

#### detect_platform()
Detecta el sistema operativo actual.

**Retorna:** `str`

#### normalize_port_name(port)
Normaliza el nombre del puerto según la plataforma.

**Parámetros:**
- `port` (str): Puerto a normalizar

**Retorna:** `str`

#### validate_baudrate(baudrate)
Valida que la velocidad de baudios sea válida.

**Parámetros:**
- `baudrate` (int): Velocidad a validar

**Retorna:** `bool`

#### validate_parity(parity)
Valida que la paridad sea válida.

**Parámetros:**
- `parity` (str): Paridad a validar

**Retorna:** `bool`

#### validate_stopbits(stopbits)
Valida que los bits de parada sean válidos.

**Parámetros:**
- `stopbits` (int): Bits de parada a validar

**Retorna:** `bool`

#### validate_bytesize(bytesize)
Valida que el tamaño de bytes sea válido.

**Parámetros:**
- `bytesize` (int): Tamaño de bytes a validar

**Retorna:** `bool`

#### parse_encoding(encoding)
Parsea y valida la codificación.

**Parámetros:**
- `encoding` (str): Codificación a parsear

**Retorna:** `str`

#### encode_data(data, encoding)
Codifica datos según la codificación especificada.

**Parámetros:**
- `data` (str): Datos a codificar
- `encoding` (str): Codificación

**Retorna:** `bytes`

#### decode_data(data, encoding)
Decodifica datos según la codificación especificada.

**Parámetros:**
- `data` (bytes): Datos a decodificar
- `encoding` (str): Codificación

**Retorna:** `str`

#### parse_eol(eol)
Parsea caracteres de fin de línea.

**Parámetros:**
- `eol` (str): Caracteres de fin de línea

**Retorna:** `bytes`

#### get_port_info(port)
Obtiene información detallada de un puerto.

**Parámetros:**
- `port` (str): Puerto a consultar

**Retorna:** `Dict[str, Any]`

#### list_available_ports()
Lista todos los puertos serie disponibles.

**Retorna:** `List[Dict[str, Any]]`

#### filter_ports(ports, filter_type=None)
Filtra puertos por tipo.

**Parámetros:**
- `ports` (List[Dict[str, Any]]): Lista de puertos
- `filter_type` (str): Tipo de filtro

**Retorna:** `List[Dict[str, Any]]`

## Eventos y Callbacks

### Eventos de Sesión

- `on_connect`: Cuando se establece conexión
- `on_disconnect`: Cuando se cierra conexión
- `on_error`: Cuando ocurre un error
- `on_data_received`: Cuando se reciben datos
- `on_data_sent`: Cuando se envían datos

### Eventos de Monitor

- `on_data`: Cuando se reciben datos durante monitoreo
- `on_error`: Cuando ocurre un error en monitoreo
- `on_start`: Cuando inicia el monitoreo
- `on_stop`: Cuando detiene el monitoreo

## Códigos de Error

### Errores de Conexión

- `SerialException`: Error general de comunicación serie
- `PortNotOpenError`: Puerto no abierto
- `SerialTimeoutException`: Timeout en operación
- `SerialException`: Error de configuración

### Errores de Validación

- `ValueError`: Parámetro inválido
- `TypeError`: Tipo de dato incorrecto
- `AttributeError`: Atributo no encontrado

## Ejemplos de Uso de API

### Crear Conexión Directa

```python
from components.SerialConnection import SerialConnection

connection = SerialConnection("COM3", baudrate=115200)
if connection.connect():
    connection.write("Hello")
    data = connection.read(10)
    connection.disconnect()
```

### Usar Sesión con Callbacks

```python
from components.SerialSession import SerialSession

def on_data_received(session, data):
    print(f"Received: {data}")

session = SerialSession("test", "COM3")
session.add_callback('on_data_received', on_data_received)
session.connect()
session.write("Test")
```

### Monitoreo con Callbacks

```python
from components.SerialMonitor import SerialMonitor

def on_monitor_data(monitor, data):
    print(f"Monitor data: {data}")

monitor = SerialMonitor(session)
monitor.add_callback('on_data', on_monitor_data)
monitor.start_monitoring(duration=60.0)
```