# Instalación del Plugin Playwright

## Requisitos Previos

### Sistema Operativo
- **Linux**: Ubuntu 18.04+, CentOS 7+, Debian 9+
- **macOS**: 10.14+ (Mojave)
- **Windows**: Windows 10+

### Python
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Dependencias del Sistema

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    libwoff1 \
    libopus0 \
    libwebp6 \
    libwebpdemux2 \
    libenchant1c2a \
    libgudev-1.0-0 \
    libsecret-1-0 \
    libhyphen0 \
    libgdk-pixbuf2.0-0 \
    libegl1 \
    libnotify4 \
    libxslt1.1 \
    libevent-2.1-7 \
    libgles2 \
    libvpx6

# CentOS/RHEL
sudo yum install -y \
    libwoff \
    opus \
    libwebp \
    libwebp-devel \
    enchant \
    libgudev1 \
    libsecret \
    hyphen \
    gdk-pixbuf2 \
    libegl \
    libnotify \
    libxslt \
    libevent \
    mesa-libGLES \
    libvpx
```

#### macOS
```bash
# Instalar Homebrew si no está instalado
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar dependencias
brew install \
    libwoff \
    opus \
    webp \
    enchant \
    libsecret \
    hyphen \
    gdk-pixbuf \
    libnotify \
    libxslt \
    libevent \
    mesa \
    libvpx
```

#### Windows
- Las dependencias se instalan automáticamente con Playwright

## Instalación del Plugin

### 1. Instalar Playwright

```bash
# Instalar Playwright
pip install playwright

# Verificar instalación
python -c "import playwright; print(playwright.__version__)"
```

### 2. Instalar Navegadores

```bash
# Instalar todos los navegadores
playwright install

# O instalar navegadores específicos
playwright install chromium
playwright install firefox
playwright install webkit
```

### 3. Instalar el Plugin

#### Opción A: Instalación Local
```bash
# Navegar al directorio del plugin
cd plugins/src/playwright

# Instalar el plugin
pip install .

# Verificar instalación
python -c "from playwright import PlaywrightPlugin; print('Plugin instalado correctamente')"
```

#### Opción B: Instalación con Sugarize
```bash
# Usando el gestor de paquetes de Sugar
sugarize require playwright ^1.0.0

# O desde un repositorio Git
sugarize require https://github.com/user/playwright-plugin --branch main
```

### 4. Verificar Instalación

```bash
# Verificar que Playwright está disponible
python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    print('Playwright funcionando correctamente')
"

# Verificar navegadores instalados
playwright --version
```

## Configuración del Entorno

### Variables de Entorno (Opcional)

```bash
# Configurar directorio de descargas
export PLAYWRIGHT_DOWNLOADS_DIR="/path/to/downloads"

# Configurar directorio de cache
export PLAYWRIGHT_CACHE_DIR="/path/to/cache"

# Configurar proxy (si es necesario)
export PLAYWRIGHT_PROXY="http://proxy.example.com:8080"
```

### Configuración de Permisos

#### Linux
```bash
# Dar permisos de ejecución a los navegadores
chmod +x ~/.cache/ms-playwright/*/chrome-linux/chrome
chmod +x ~/.cache/ms-playwright/*/firefox/firefox
chmod +x ~/.cache/ms-playwright/*/webkit/webkit

# Si hay problemas de permisos
sudo chown -R $USER:$USER ~/.cache/ms-playwright
```

#### macOS
```bash
# Permitir ejecución de aplicaciones no firmadas
sudo spctl --master-disable

# O permitir específicamente los navegadores de Playwright
sudo xattr -d com.apple.quarantine ~/.cache/ms-playwright/*/chrome-mac/Chromium.app
sudo xattr -d com.apple.quarantine ~/.cache/ms-playwright/*/firefox/firefox
sudo xattr -d com.apple.quarantine ~/.cache/ms-playwright/*/webkit/webkit
```

## Verificación de la Instalación

### Test Básico

Crear un archivo de prueba `test_installation.json`:

```json
{
  "meta": {
    "playwright": {
      "browser_type": "chromium",
      "headless": true
    }
  },
  "task": [
    {
      "playwright": {
        "operator": "launch_browser",
        "result": "browser_status"
      }
    },
    {
      "print": {
        "text": "Navegador lanzado: {{browser_status.browser_type}}"
      }
    },
    {
      "playwright": {
        "operator": "new_context"
      }
    },
    {
      "playwright": {
        "operator": "new_page"
      }
    },
    {
      "playwright": {
        "operator": "goto",
        "url": "https://example.com"
      }
    },
    {
      "playwright": {
        "operator": "get_title",
        "result": "title"
      }
    },
    {
      "print": {
        "text": "Título: {{title.title}}"
      }
    },
    {
      "playwright": {
        "operator": "close_browser"
      }
    },
    {
      "print": {
        "text": "✅ Instalación verificada correctamente"
      }
    }
  ]
}
```

Ejecutar el test:

```bash
# Desde el entorno virtual de Sugar
virtual/bin/python3 Sugar/Service/SugarConsole.py test_installation.json
```

### Verificación de Navegadores

```bash
# Verificar navegadores disponibles
python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browsers = []
    for browser_type in ['chromium', 'firefox', 'webkit']:
        try:
            browser = getattr(p, browser_type).launch()
            browsers.append(f'{browser_type}: {browser.version}')
            browser.close()
        except Exception as e:
            browsers.append(f'{browser_type}: Error - {e}')
    print('Navegadores disponibles:')
    for browser in browsers:
        print(f'  - {browser}')
"
```

## Solución de Problemas

### Problemas Comunes

#### 1. Error: "playwright: command not found"
```bash
# Asegurar que Playwright está instalado
pip install playwright

# Verificar PATH
which playwright
```

#### 2. Error: "Browser not found"
```bash
# Reinstalar navegadores
playwright install --force

# O instalar navegadores específicos
playwright install chromium
```

#### 3. Error de Permisos en Linux
```bash
# Dar permisos de ejecución
chmod +x ~/.cache/ms-playwright/*/chrome-linux/chrome

# O reinstalar con permisos correctos
sudo playwright install
```

#### 4. Error de Sandbox en Docker
```bash
# Usar argumentos de navegador para Docker
{
  "playwright": {
    "operator": "launch_browser",
    "args": ["--no-sandbox", "--disable-dev-shm-usage"]
  }
}
```

#### 5. Error de Memoria
```bash
# Usar modo headless
{
  "playwright": {
    "operator": "launch_browser",
    "headless": true
  }
}
```

### Logs de Debug

```bash
# Habilitar logs detallados
export DEBUG=pw:api

# O en el código
import os
os.environ['DEBUG'] = 'pw:api'
```

### Verificación de Dependencias

```bash
# Verificar dependencias del sistema
playwright install-deps

# Verificar dependencias de Python
pip list | grep playwright
```

## Actualización

### Actualizar Playwright
```bash
# Actualizar Playwright
pip install --upgrade playwright

# Actualizar navegadores
playwright install
```

### Actualizar el Plugin
```bash
# Si instalado localmente
cd plugins/src/playwright
pip install --upgrade .

# Si instalado con sugarize
sugarize update playwright
```

## Desinstalación

### Desinstalar el Plugin
```bash
# Si instalado localmente
pip uninstall playwright

# Si instalado con sugarize
sugarize remove playwright
```

### Desinstalar Playwright
```bash
# Desinstalar Playwright
pip uninstall playwright

# Eliminar navegadores
rm -rf ~/.cache/ms-playwright
```

## Soporte

Para obtener ayuda con la instalación:

1. **Documentación oficial**: [Playwright Python](https://playwright.dev/python/)
2. **Issues del plugin**: Crear un issue en el repositorio del plugin
3. **Comunidad**: Foros y canales de la comunidad de Sugar

### Información del Sistema

Para reportar problemas, incluir:

```bash
# Información del sistema
python --version
pip --version
playwright --version
uname -a  # Linux/macOS
systeminfo  # Windows
```
