# Compiler Plugin

El plugin Compiler proporciona funcionalidades para compilar código fuente en diferentes lenguajes de programación.

## Características

- **Compilación de código**: Compilar código fuente a ejecutables
- **Múltiples lenguajes**: Soporte para C, C++, Java, Go, Rust
- **Optimización**: Opciones de optimización configurables
- **Debugging**: Información de debug incluida
- **Cross-compilation**: Compilación para diferentes plataformas
- **Dependencias**: Gestión automática de dependencias

## Instalación

```bash
pip install -r requirements.txt
```

### Dependencias
- `subprocess` (incluido en Python estándar)
- `pathlib` (incluido en Python estándar)
- Compiladores específicos del lenguaje

## Uso

### 1. Compilación C Básica

```json
{
  "compiler": {
    "language": "c",
    "source": "/path/to/main.c",
    "output": "/path/to/program",
    "result": "compile_status"
  }
}
```

### 2. Compilación C++ con Opciones

```json
{
  "compiler": {
    "language": "cpp",
    "source": "/path/to/main.cpp",
    "output": "/path/to/program",
    "options": [
      "-std=c++17",
      "-O2",
      "-Wall",
      "-Wextra"
    ],
    "result": "cpp_compile"
  }
}
```

### 3. Compilación Java

```json
{
  "compiler": {
    "language": "java",
    "source": "/path/to/Main.java",
    "output": "/path/to/classes",
    "classpath": "/path/to/dependencies",
    "result": "java_compile"
  }
}
```

### 4. Compilación Go

```json
{
  "compiler": {
    "language": "go",
    "source": "/path/to/main.go",
    "output": "/path/to/program",
    "goos": "linux",
    "goarch": "amd64",
    "result": "go_compile"
  }
}
```

### 5. Compilación Rust

```json
{
  "compiler": {
    "language": "rust",
    "source": "/path/to/Cargo.toml",
    "output": "/path/to/target",
    "release": true,
    "result": "rust_compile"
  }
}
```

## Parámetros

### Configuración Básica
- `language` (string, requerido): Lenguaje de programación
  - `c`: C
  - `cpp`: C++
  - `java`: Java
  - `go`: Go
  - `rust`: Rust
- `source` (string, requerido): Archivo fuente o directorio
- `output` (string, opcional): Archivo de salida o directorio

### Opciones de Compilación
- `options` (array, opcional): Opciones del compilador
- `include_dirs` (array, opcional): Directorios de inclusión
- `library_dirs` (array, opcional): Directorios de librerías
- `libraries` (array, opcional): Librerías a enlazar

### Configuración Específica
- `classpath` (string, opcional): Classpath para Java
- `goos` (string, opcional): Sistema operativo objetivo para Go
- `goarch` (string, opcional): Arquitectura objetivo para Go
- `release` (boolean, opcional): Compilación de release para Rust

### Resultado
- `result` (string, opcional): Variable para almacenar el resultado

## Lenguajes Soportados

### C/C++
- **Compilador**: GCC/Clang
- **Extensiones**: .c, .cpp, .cc, .cxx
- **Opciones comunes**:
  - `-std=c11`: Estándar C11
  - `-std=c++17`: Estándar C++17
  - `-O2`: Optimización nivel 2
  - `-Wall`: Todas las advertencias
  - `-g`: Información de debug

### Java
- **Compilador**: javac
- **Extensiones**: .java
- **Opciones comunes**:
  - `-cp`: Classpath
  - `-d`: Directorio de salida
  - `-source`: Versión de fuente
  - `-target`: Versión objetivo

### Go
- **Compilador**: go build
- **Extensiones**: .go
- **Variables de entorno**:
  - `GOOS`: Sistema operativo objetivo
  - `GOARCH`: Arquitectura objetivo
  - `CGO_ENABLED`: Habilitar CGO

### Rust
- **Compilador**: cargo build
- **Archivos**: Cargo.toml
- **Opciones**:
  - `--release`: Compilación optimizada
  - `--target`: Target específico

## Ejemplos Avanzados

### Compilación con Librerías

```json
{
  "compiler": {
    "language": "cpp",
    "source": "/path/to/main.cpp",
    "output": "/path/to/program",
    "include_dirs": [
      "/usr/include/opencv4",
      "/usr/local/include"
    ],
    "library_dirs": [
      "/usr/lib/x86_64-linux-gnu",
      "/usr/local/lib"
    ],
    "libraries": [
      "opencv_core",
      "opencv_imgproc"
    ],
    "options": [
      "-std=c++17",
      "-O3",
      "-Wall"
    ],
    "result": "opencv_compile"
  }
}
```

### Cross-Compilation Go

```json
{
  "compiler": {
    "language": "go",
    "source": "/path/to/main.go",
    "output": "/path/to/program",
    "goos": "windows",
    "goarch": "amd64",
    "options": [
      "-ldflags=-s -w"
    ],
    "result": "windows_build"
  }
}
```

### Compilación Java con Dependencias

```json
{
  "compiler": {
    "language": "java",
    "source": "/path/to/src",
    "output": "/path/to/classes",
    "classpath": "/path/to/lib/*",
    "options": [
      "-source", "11",
      "-target", "11",
      "-encoding", "UTF-8"
    ],
    "result": "java_with_deps"
  }
}
```

### Compilación Rust Multi-Target

```json
{
  "compiler": {
    "language": "rust",
    "source": "/path/to/Cargo.toml",
    "output": "/path/to/target",
    "release": true,
    "options": [
      "--target", "x86_64-unknown-linux-gnu"
    ],
    "result": "rust_release"
  }
}
```

## Configuración de Entorno

### Variables de Entorno
- `CC`: Compilador C
- `CXX`: Compilador C++
- `JAVA_HOME`: Directorio de Java
- `GOROOT`: Directorio de Go
- `RUSTUP_HOME`: Directorio de Rust

### Configuración de Path
```json
{
  "compiler": {
    "language": "c",
    "source": "/path/to/main.c",
    "output": "/path/to/program",
    "env": {
      "PATH": "/usr/local/bin:/usr/bin:/bin",
      "CC": "gcc",
      "CFLAGS": "-O2 -Wall"
    },
    "result": "env_compile"
  }
}
```

## Manejo de Errores

El plugin maneja los siguientes tipos de errores:

- **Compilador no encontrado**: Compilador no instalado
- **Errores de sintaxis**: Errores en el código fuente
- **Dependencias faltantes**: Librerías no encontradas
- **Permisos insuficientes**: Falta de permisos de escritura
- **Espacio insuficiente**: Disco lleno

## Optimización

### Niveles de Optimización
- `-O0`: Sin optimización (debug)
- `-O1`: Optimización básica
- `-O2`: Optimización estándar
- `-O3`: Optimización agresiva

### Flags de Debug
- `-g`: Información de debug
- `-ggdb`: Información de debug para GDB
- `-g3`: Información de debug máxima

## Recursos Adicionales

- [Documentación de GCC](https://gcc.gnu.org/onlinedocs/)
- [Documentación de Java](https://docs.oracle.com/javase/)
- [Documentación de Go](https://golang.org/doc/)
- [Documentación de Rust](https://doc.rust-lang.org/)
