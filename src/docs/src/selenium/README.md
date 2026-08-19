# Selenium Plugin

El plugin Selenium proporciona funcionalidades avanzadas de automatización web usando Selenium WebDriver para navegación, interacción y extracción de datos.

## Características

- **Automatización web**: Control completo del navegador
- **Navegación**: Navegar entre páginas y URLs
- **Interacción**: Hacer clic, escribir, seleccionar elementos
- **Espera inteligente**: Esperar elementos dinámicamente
- **Captura de pantalla**: Capturar imágenes de páginas
- **Gestión de cookies**: Manejar cookies del navegador
- **Múltiples navegadores**: Chrome, Firefox, Safari, Edge

## Instalación

```bash
pip install -r requirements.txt
```

### Dependencias
- `selenium>=4.0.0`
- `webdriver-manager>=3.8.0`
- `beautifulsoup4>=4.9.0`

## Uso

### 1. Iniciar Navegador

```json
{
  "selenium": {
    "action": "start_browser",
    "browser": "chrome",
    "headless": false,
    "options": [
      "--no-sandbox",
      "--disable-dev-shm-usage"
    ],
    "result": "browser_session"
  }
}
```

### 2. Navegar a URL

```json
{
  "selenium": {
    "action": "navigate",
    "url": "https://example.com",
    "wait_for": "body",
    "timeout": 10,
    "result": "navigation_status"
  }
}
```

### 3. Buscar Elemento

```json
{
  "selenium": {
    "action": "find_element",
    "selector": "#search-input",
    "selector_type": "css",
    "wait": true,
    "result": "search_input"
  }
}
```

### 4. Escribir Texto

```json
{
  "selenium": {
    "action": "send_keys",
    "element": "{{ search_input }}",
    "text": "{{ search_term }}",
    "clear_first": true,
    "result": "text_entered"
  }
}
```

### 5. Hacer Clic

```json
{
  "selenium": {
    "action": "click",
    "element": "#submit-button",
    "wait_for": "#results",
    "result": "click_performed"
  }
}
```

## Parámetros

### Configuración del Navegador
- `action` (string, requerido): Acción a realizar
- `browser` (string, opcional): Tipo de navegador (chrome, firefox, safari, edge)
- `headless` (boolean, opcional): Modo headless (default: false)
- `options` (array, opcional): Opciones del navegador
- `result` (string, opcional): Variable para almacenar el resultado

### Configuración de Navegación
- `url` (string, opcional): URL a navegar
- `wait_for` (string, opcional): Elemento a esperar
- `timeout` (integer, opcional): Timeout en segundos
- `wait_until` (string, opcional): Condición de espera (visible, clickable, present)

### Configuración de Elementos
- `selector` (string, opcional): Selector del elemento
- `selector_type` (string, opcional): Tipo de selector (css, xpath, id, name, class)
- `element` (string, opcional): Referencia al elemento
- `text` (string, opcional): Texto a escribir

## Operaciones Disponibles

### Gestión del Navegador
- **start_browser**: Iniciar navegador
- **close_browser**: Cerrar navegador
- **quit_browser**: Salir completamente
- **get_window_size**: Obtener tamaño de ventana
- **set_window_size**: Establecer tamaño de ventana

### Navegación
- **navigate**: Navegar a URL
- **back**: Volver atrás
- **forward**: Ir adelante
- **refresh**: Recargar página
- **get_current_url**: Obtener URL actual
- **get_page_title**: Obtener título de página

### Búsqueda de Elementos
- **find_element**: Buscar elemento único
- **find_elements**: Buscar múltiples elementos
- **wait_for_element**: Esperar elemento
- **is_element_present**: Verificar si elemento existe
- **is_element_visible**: Verificar si elemento es visible

### Interacción
- **click**: Hacer clic en elemento
- **double_click**: Doble clic
- **right_click**: Clic derecho
- **send_keys**: Escribir texto
- **clear**: Limpiar campo
- **submit**: Enviar formulario

### Gestión de Formularios
- **select_option**: Seleccionar opción
- **check_checkbox**: Marcar checkbox
- **uncheck_checkbox**: Desmarcar checkbox
- **upload_file**: Subir archivo

### Captura y Extracción
- **take_screenshot**: Capturar pantalla
- **get_text**: Obtener texto de elemento
- **get_attribute**: Obtener atributo
- **get_css_value**: Obtener valor CSS

## Ejemplos Avanzados

### Login Automático

```json
{
  "selenium": {
    "action": "login",
    "url": "https://example.com/login",
    "credentials": {
      "username_selector": "#username",
      "password_selector": "#password",
      "submit_selector": "#login-btn",
      "username": "{{ username }}",
      "password": "{{ password }}"
    },
    "wait_for": ".dashboard",
    "result": "login_status"
  }
}
```

### Extracción de Datos

```json
{
  "selenium": {
    "action": "extract_data",
    "selectors": {
      "title": "h1.title",
      "description": ".description",
      "price": ".price",
      "images": "img.product-image"
    },
    "wait_for": ".product-details",
    "result": "extracted_data"
  }
}
```

### Navegación con Scroll

```json
{
  "selenium": {
    "action": "scroll_page",
    "direction": "down",
    "pixels": 1000,
    "wait_for_load": true,
    "result": "scroll_completed"
  }
}
```

### Manejo de Ventanas

```json
{
  "selenium": {
    "action": "switch_window",
    "window_type": "new",
    "wait_for": "body",
    "result": "window_switched"
  }
}
```

### Gestión de Cookies

```json
{
  "selenium": {
    "action": "manage_cookies",
    "operation": "add",
    "cookies": [
      {
        "name": "session_id",
        "value": "{{ session_value }}",
        "domain": ".example.com"
      }
    ],
    "result": "cookies_updated"
  }
}
```

### Captura de Pantalla Completa

```json
{
  "selenium": {
    "action": "take_full_screenshot",
    "output_path": "/path/to/screenshot.png",
    "scroll_pause": 0.5,
    "result": "screenshot_taken"
  }
}
```

## Configuración de Navegador

### Opciones de Chrome
```json
{
  "selenium": {
    "action": "start_browser",
    "browser": "chrome",
    "options": [
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--disable-gpu",
      "--window-size=1920,1080",
      "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    ],
    "result": "chrome_browser"
  }
}
```

### Opciones de Firefox
```json
{
  "selenium": {
    "action": "start_browser",
    "browser": "firefox",
    "options": [
      "--headless",
      "--width=1920",
      "--height=1080"
    ],
    "preferences": {
      "dom.webdriver.enabled": false,
      "general.useragent.override": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
    },
    "result": "firefox_browser"
  }
}
```

## Manejo de Errores

### Configuración de Reintentos
```json
{
  "selenium": {
    "action": "click",
    "element": "#submit-button",
    "retry": {
      "max_attempts": 3,
      "delay": 2,
      "wait_for": "#submit-button:not([disabled])"
    },
    "result": "click_with_retry"
  }
}
```

### Manejo de Excepciones
```json
{
  "selenium": {
    "action": "find_element",
    "selector": "#dynamic-element",
    "error_handling": {
      "element_not_found": "continue",
      "timeout": "retry",
      "stale_element": "refresh_page"
    },
    "result": "robust_element_find"
  }
}
```

## Optimización

### Configuración de Rendimiento
```json
{
  "selenium": {
    "action": "start_browser",
    "browser": "chrome",
    "performance": {
      "page_load_strategy": "eager",
      "implicit_wait": 10,
      "explicit_wait": 30,
      "disable_images": true,
      "disable_css": false,
      "disable_javascript": false
    },
    "result": "optimized_browser"
  }
}
```

### Configuración de Memoria
```json
{
  "selenium": {
    "action": "start_browser",
    "browser": "chrome",
    "memory": {
      "max_memory": "2GB",
      "clear_cache_on_start": true,
      "disable_logs": true
    },
    "result": "memory_efficient_browser"
  }
}
```

## Configuración de Seguridad

### Configuración Segura
```json
{
  "selenium": {
    "action": "start_browser",
    "browser": "chrome",
    "security": {
      "disable_images": true,
      "disable_javascript": false,
      "disable_css": true,
      "user_agent": "Sugar Bot 1.0",
      "disable_plugins": true,
      "disable_extensions": true
    },
    "result": "secure_browser"
  }
}
```

## Recursos Adicionales

- [Documentación de Selenium](https://selenium-python.readthedocs.io/)
- [Guía de Automatización Web](../../../docs/development/web_automation.md) 