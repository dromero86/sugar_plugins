# Documentación Técnica - Plugin RAR

## Arquitectura del Plugin

### Estructura de Clases

```python
class RarPlugin(PluginBase):
    """
    Plugin RAR que utiliza el SDK para manejar compresión y descompresión
    de archivos RAR con múltiples opciones y funcionalidades avanzadas.
    """
```

### Herencia y Dependencias

- **Clase Base**: `PluginBase` de Sugar
- **SDK Components**: ExtensionManager, HookSystem, InterpolationInterceptor, etc.
- **Dependencias Python**: `rarfile>=4.0`, `psutil>=5.8.0`
- **Dependencias Sistema**: `unrar`, `rar`

### Configuración del Plugin

```python
VERSION = "1.0.0"
DESCRIPTION = "Plugin para compresión y descompresión de archivos RAR usando el SDK"
AUTHOR = "Sugar Team"
LICENSE = "MIT"

# Dependencias
DEPENDENCIES = ["rarfile"]
REQUIREMENTS = ["rarfile>=4.0"]
SYSTEM_DEPENDENCIES = ["unrar", "rar"]

# Requerimientos de hardware
HARDWARE_REQUIREMENTS = {
    "min_ram_gb": 2,
    "min_disk_gb": 1,
    "min_cpu_cores": 1
}

# Requerimientos de permisos
PERMISSION_REQUIREMENTS = {
    "network_access": False,
    "write_access": ["/tmp", "./output"],
    "read_access": ["./data"]
}
```

## SDK Integration

### Componentes del SDK Utilizados

1. **ExtensionManager**: Gestión centralizada de extensiones
2. **HookSystem**: Sistema de hooks para interceptar eventos
3. **InterpolationInterceptor**: Interceptar interpolaciones de variables
4. **ASTModifier**: Modificar el árbol de sintaxis abstracta
5. **FlowController**: Controlar el flujo de ejecución
6. **CommandCustomizer**: Personalizar comandos existentes

### Hooks Registrados

```python
# Before Command Hook
self.sdk['hook_system'].register_hook(
    hook_point=HookPoint.BEFORE_COMMAND,
    callback=self._before_rar_command_hook,
    priority=10
)

# After Command Hook
self.sdk['hook_system'].register_hook(
    hook_point=HookPoint.AFTER_COMMAND,
    callback=self._after_rar_command_hook,
    priority=10
)
```

### Interceptores de Interpolación

```python
self.sdk['interpolation_interceptor'].register_interceptor(
    event=InterpolationEvent.BEFORE_INTERPOLATION,
    callback=self._interpolate_paths_callback,
    priority=5
)
```

### Customizadores de Comandos

```python
self.sdk['command_customizer'].register_customizer(
    event=CommandEvent.BEFORE_COMMAND_EXECUTION,
    callback=self._customize_rar_command,
    priority=8
)

# Alias de comandos
self.sdk['command_customizer'].add_command_alias("compress", "rar_compress")
self.sdk['command_customizer'].add_command_alias("extract", "rar_extract")
```

## Comandos Implementados

### 1. rar_compress

**Propósito**: Comprimir archivos o directorios en formato RAR

**Parámetros**:
- `source`: Archivo o directorio a comprimir
- `destination`: Archivo RAR de salida
- `compression_level`: Nivel de compresión (0-5, por defecto 3)
- `password`: Contraseña para el archivo (opcional)
- `include_hidden`: Incluir archivos ocultos (por defecto false)

**Retorno**:
```python
{
    'status': 'success',
    'source': source,
    'destination': destination,
    'format': 'rar',
    'compression_level': compression_level,
    'original_size': original_size,
    'compressed_size': compressed_size,
    'compression_ratio': ratio,
    'processing_time': time,
    'files_count': count
}
```

### 2. rar_extract

**Propósito**: Extraer archivos RAR

**Parámetros**:
- `source`: Archivo RAR a extraer
- `destination`: Directorio de destino
- `password`: Contraseña del archivo (si está protegido)
- `overwrite`: Sobrescribir archivos existentes (por defecto false)

**Retorno**:
```python
{
    'status': 'success',
    'source': source,
    'destination': destination,
    'format': 'rar',
    'compressed_size': compressed_size,
    'extracted_size': extracted_size,
    'extracted_files': count,
    'processing_time': time
}
```

### 3. rar_info

**Propósito**: Obtener información detallada de archivo RAR

**Parámetros**:
- `source`: Archivo RAR a inspeccionar

**Retorno**:
```python
{
    'status': 'success',
    'file': source,
    'format': 'rar',
    'size': file_size,
    'size_human': formatted_size,
    'files_count': count,
    'files': file_list,
    'is_encrypted': boolean,
    'comment': comment,
    'file_details': details_list
}
```

### 4. rar_list

**Propósito**: Listar contenido de archivo RAR

**Parámetros**:
- `source`: Archivo RAR
- `password`: Contraseña (si está protegido)

**Retorno**:
```python
{
    'status': 'success',
    'file': source,
    'format': 'rar',
    'files_count': count,
    'files': file_list
}
```

### 5. rar_test

**Propósito**: Probar integridad de archivo RAR

**Parámetros**:
- `source`: Archivo RAR a probar
- `password`: Contraseña (si está protegido)

**Retorno**:
```python
{
    'status': 'success',
    'file': source,
    'format': 'rar',
    'is_valid': boolean,
    'files_tested': count
}
```

## Manejo de Errores

### Estructura de Error

```python
{
    'status': 'error',
    'error': str(e),
    'source': source,
    'destination': destination,
    'format': 'rar'
}
```

### Tipos de Errores Comunes

1. **FileNotFoundError**: Archivo fuente no encontrado
2. **rarfile.BadRarFile**: Archivo RAR corrupto o inválido
3. **rarfile.BadRarFile: File is password protected**: Archivo protegido sin contraseña
4. **PermissionError**: Permisos insuficientes
5. **OSError**: Errores del sistema operativo

### Validación de Parámetros

```python
def _validate_rar_params(self, command):
    """Validar parámetros de comandos rar"""
    try:
        if command.get('name') == 'rar_compress':
            required = ['source', 'destination']
        elif command.get('name') == 'rar_extract':
            required = ['source', 'destination']
        else:
            return True
        
        for param in required:
            if param not in command:
                Output.Console(self.plugin_name, f"❌ Missing required parameter: {param}")
                return False
        
        # Validar que el archivo fuente existe
        source = command.get('source')
        if not os.path.exists(source):
            Output.Console(self.plugin_name, f"❌ Source file does not exist: {source}")
            return False
        
        return True
        
    except Exception as e:
        Output.Console(self.plugin_name, f"❌ Validation error: {e}")
        return False
```

## Configuración de rarfile

### Auto-detección de Herramientas

```python
def _configure_rarfile(self):
    """Configurar rarfile para el sistema"""
    try:
        # Configurar rutas de unrar/rar
        if os.name == 'nt':  # Windows
            rarfile.UNRAR_TOOL = "C:\\Program Files\\WinRAR\\UnRAR.exe"
        else:  # Linux/Unix
            # Buscar unrar en PATH
            import shutil
            unrar_path = shutil.which("unrar")
            if unrar_path:
                rarfile.UNRAR_TOOL = unrar_path
            else:
                # Intentar con rar
                rar_path = shutil.which("rar")
                if rar_path:
                    rarfile.UNRAR_TOOL = rar_path
        
        Output.Console(self.plugin_name, f"RAR tool configured: {rarfile.UNRAR_TOOL}")
    except Exception as e:
        Output.Console(self.plugin_name, f"Warning: Could not configure RAR tool: {e}")
```

### Configuración Manual

```python
import rarfile

# Configurar manualmente la ruta de unrar
rarfile.UNRAR_TOOL = "/usr/local/bin/unrar"
```

## Sistema de Dependencias

### Verificación de Dependencias

```python
def _check_all_dependencies(self):
    """Verificar todas las dependencias del plugin"""
    return {
        'python_dependencies': self._check_python_dependencies(),
        'system_dependencies': self._check_system_dependencies(),
        'hardware_requirements': self._check_hardware_requirements(),
        'permission_requirements': self._check_permission_requirements(),
        'all_satisfied': True  # Se actualiza basado en las verificaciones
    }
```

### Dependencias de Python

```python
def _check_python_dependencies(self):
    """Verificar dependencias de Python"""
    dependencies = []
    
    # Verificar rarfile
    try:
        import rarfile
        dependencies.append({
            'name': 'rarfile',
            'status': 'installed',
            'version': rarfile.__version__
        })
    except ImportError:
        dependencies.append({
            'name': 'rarfile',
            'status': 'missing',
            'version': None
        })
    
    # Verificar psutil
    try:
        import psutil
        dependencies.append({
            'name': 'psutil',
            'status': 'installed',
            'version': psutil.__version__
        })
    except ImportError:
        dependencies.append({
            'name': 'psutil',
            'status': 'missing',
            'version': None
        })
    
    return dependencies
```

### Dependencias del Sistema

```python
def _check_system_dependencies(self):
    """Verificar dependencias del sistema"""
    dependencies = []
    
    # Verificar unrar
    unrar_path = shutil.which("unrar")
    dependencies.append({
        'name': 'unrar',
        'status': 'installed' if unrar_path else 'missing',
        'path': unrar_path
    })
    
    # Verificar rar
    rar_path = shutil.which("rar")
    dependencies.append({
        'name': 'rar',
        'status': 'installed' if rar_path else 'missing',
        'path': rar_path
    })
    
    return dependencies
```

## Utilidades

### Cálculo de Tamaños

```python
def _get_size(self, path):
    """Obtener tamaño total de archivo o directorio"""
    if os.path.isfile(path):
        return os.path.getsize(path)
    elif os.path.isdir(path):
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total += os.path.getsize(filepath)
        return total
    return 0

def _format_size(self, size_bytes):
    """Formatear tamaño en bytes a formato legible"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"
```

### Conteo de Archivos

```python
def _count_files(self, path):
    """Contar archivos en directorio"""
    if os.path.isfile(path):
        return 1
    elif os.path.isdir(path):
        count = 0
        for root, dirs, files in os.walk(path):
            count += len(files)
        return count
    return 0
```

## Testing

### Comandos de Testing

1. **test_functionality**: Prueba completa de funcionalidad
2. **test_sdk**: Prueba de componentes del SDK
3. **check_dependencies**: Verificación de dependencias
4. **system_info**: Información del sistema

### Estructura de Tests

```python
def _test_functionality_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
    """Probar funcionalidad del plugin"""
    test_results = {}
    
    # Crear archivo de prueba
    test_file = self.temp_dir / "test_file.txt"
    test_file.write_text("This is a test file for RAR plugin functionality testing.")
    
    # Crear archivo RAR de prueba
    test_rar = self.temp_dir / "test.rar"
    
    try:
        # Probar compresión
        compress_result = self._compress_command({
            'source': str(test_file),
            'destination': str(test_rar)
        })
        test_results['compression'] = compress_result.get('status') == 'success'
        
        # Probar extracción
        extract_dir = self.temp_dir / "extract_test"
        extract_dir.mkdir(exist_ok=True)
        
        extract_result = self._extract_command({
            'source': str(test_rar),
            'destination': str(extract_dir)
        })
        test_results['extraction'] = extract_result.get('status') == 'success'
        
        # Probar información
        info_result = self._info_command({
            'source': str(test_rar)
        })
        test_results['info'] = info_result.get('status') == 'success'
        
        # Probar listado
        list_result = self._list_command({
            'source': str(test_rar)
        })
        test_results['listing'] = list_result.get('status') == 'success'
        
        # Limpiar
        test_file.unlink(missing_ok=True)
        test_rar.unlink(missing_ok=True)
        shutil.rmtree(extract_dir, ignore_errors=True)
        
        all_tests_passed = all(test_results.values())
        
        return {
            'status': 'success' if all_tests_passed else 'partial_success',
            'tests': test_results,
            'all_tests_passed': all_tests_passed,
            'message': 'RAR plugin functionality tested successfully' if all_tests_passed else 'Some tests failed'
        }
        
    except Exception as e:
        # Limpiar en caso de error
        test_file.unlink(missing_ok=True)
        test_rar.unlink(missing_ok=True)
        shutil.rmtree(extract_dir, ignore_errors=True)
        
        return {
            'status': 'error',
            'error': str(e),
            'tests': test_results
        }
```

## Cleanup y Recursos

### Limpieza de Recursos

```python
def cleanup(self):
    """Limpiar recursos del plugin"""
    Output.Console(self.plugin_name, "Cleaning up RAR Plugin...")
    
    # Limpiar extensiones del SDK
    if hasattr(self, 'sdk'):
        self.sdk['extension_manager'].unregister_all_plugin_extensions(self.plugin_name)
    
    # Limpiar directorio temporal
    if self.temp_dir.exists():
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    Output.Console(self.plugin_name, "RAR Plugin cleanup completed")
```

### Gestión de Archivos Temporales

```python
# Configuración del directorio temporal
self.temp_dir = Path(tempfile.gettempdir()) / "sugar_rar_plugin"
self.temp_dir.mkdir(exist_ok=True)
```

## Limitaciones y Consideraciones

### Limitaciones Conocidas

1. **Solo lectura**: rarfile solo permite extracción, no creación de archivos RAR
2. **Dependencias del sistema**: Requiere herramientas externas (unrar/rar)
3. **Formato RAR**: Solo soporta archivos RAR, no otros formatos
4. **Permisos**: Requiere permisos de lectura/escritura en directorios de trabajo

### Consideraciones de Rendimiento

1. **Memoria**: Archivos grandes pueden consumir mucha memoria
2. **Tiempo**: La compresión/descompresión puede ser lenta para archivos grandes
3. **CPU**: Operaciones intensivas en CPU durante la compresión

### Seguridad

1. **Contraseñas**: Las contraseñas se pasan como texto plano
2. **Archivos temporales**: Los archivos temporales pueden contener datos sensibles
3. **Permisos**: Verificar permisos antes de operaciones de archivo

## Extensibilidad

### Agregar Nuevos Comandos

```python
def execute(self, command: str, config: Dict[str, Any]) -> Any:
    """Ejecutar un comando del plugin"""
    if command == "nuevo_comando":
        return self._nuevo_comando(config)
    # ... otros comandos
    else:
        raise ValueError(f"Comando desconocido: {command}")

def _nuevo_comando(self, config: Dict[str, Any]) -> Dict[str, Any]:
    """Implementación del nuevo comando"""
    # Implementación aquí
    pass
```

### Extender el SDK

```python
def _register_sdk_extensions(self):
    """Registrar todas las extensiones del SDK"""
    # ... extensiones existentes
    
    # Agregar nueva extensión
    self.sdk['extension_manager'].register_extension(
        plugin_name=self.plugin_name,
        extension_type=ExtensionType.CUSTOM,
        callback=self._nueva_extension_callback,
        priority=5,
        metadata={'type': 'nueva_funcionalidad'}
    )
```
