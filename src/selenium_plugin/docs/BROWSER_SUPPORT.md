# Soporte de Navegadores - Selenium Plugin v2.1

## 📋 Descripción General

El plugin Selenium v2.1 soporta **Chrome, Firefox y Edge**. Cada navegador tiene configuraciones específicas y limitaciones propias que se documentan en esta guía.

> Safari, Opera e Internet Explorer **no están implementados** (no figuran en `SUPPORTED_BROWSERS` dentro de `SeleniumPlugin.py`). Configurar `meta.browser` con cualquiera de esos valores falla con `"Navegador no soportado: <browser>"`.

---

## 🌐 Navegadores Soportados

### Tabla de Compatibilidad

| Navegador | Clave | Plataforma | Headless | Detach | Auto-Download | Estado |
|-----------|-------|------------|----------|--------|---------------|--------|
| **Chrome** | `chrome` | Multiplataforma | ✅ | ✅ | ✅ | Activo |
| **Firefox** | `firefox` | Multiplataforma | ✅ | ❌ | ✅ | Activo |
| **Edge** | `edge` | Multiplataforma | ✅ | ✅ | ✅ | Activo |

---

## 🔧 Configuración por Navegador

### 1. **Chrome** - Navegador Recomendado

**Características:**
- ✅ Modo headless estable
- ✅ Modo detach disponible
- ✅ Descarga automática de drivers

**Configuración:**
```json
{
  "meta": {
    "mode": "selenium",
    "browser": "chrome",
    "options": [
      "--disable-gpu",
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--window-size=1920,1080"
    ],
    "headless": true,
    "detach": false,
    "timeout": 10,
    "implicit_wait": 5
  }
}
```

**Opciones Recomendadas:**
- `--disable-gpu`: Deshabilita aceleración GPU
- `--no-sandbox`: Deshabilita sandbox (requerido en algunos sistemas, ej. contenedores)
- `--disable-dev-shm-usage`: Evita problemas de memoria compartida
- `--window-size=1920,1080`: Define tamaño de ventana

### 2. **Firefox** - Alternativa Robusta

**Características:**
- ✅ Modo headless estable
- ❌ Modo detach no soportado
- ✅ Descarga automática de drivers (GeckoDriver)

**Configuración:**
```json
{
  "meta": {
    "mode": "selenium",
    "browser": "firefox",
    "options": [
      "--width=1920",
      "--height=1080",
      "--no-sandbox"
    ],
    "headless": true,
    "timeout": 10,
    "implicit_wait": 5
  }
}
```

**Limitaciones:**
- No soporta modo `detach`
- Algunas opciones específicas de Chrome (`--disable-gpu`, `--disable-dev-shm-usage`) no aplican en Firefox del mismo modo

### 3. **Edge** - Basado en Chromium

**Características:**
- ✅ Modo headless estable
- ✅ Modo detach disponible
- ✅ Descarga automática de drivers

**Configuración:**
```json
{
  "meta": {
    "mode": "selenium",
    "browser": "edge",
    "options": [
      "--disable-gpu",
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--window-size=1920,1080"
    ],
    "headless": true,
    "detach": false,
    "timeout": 10,
    "implicit_wait": 5
  }
}
```

**Ventajas:**
- Basado en Chromium (mismo motor que Chrome), mismas opciones de línea de comandos
- Mejor integración con Windows

---

## 📥 Descarga Automática de Drivers

### Configuración Automática

El plugin descarga automáticamente el driver que corresponda al navegador configurado, vía `webdriver-manager`:

```json
{
  "meta": {
    "mode": "selenium",
    "browser": "chrome"
    // No es necesario especificar driver.bin
  }
}
```

### Configuración Manual

Para usar un driver ya descargado/instalado:

```json
{
  "meta": {
    "mode": "selenium",
    "browser": "chrome",
    "driver": {
      "bin": "./drivers/chromedriver"
    }
  }
}
```

### Drivers por Navegador

| Navegador | Driver | Descarga Automática | Ubicación |
|-----------|--------|-------------------|-----------|
| Chrome | ChromeDriver | ✅ | `~/.wdm/drivers/chromedriver/` |
| Firefox | GeckoDriver | ✅ | `~/.wdm/drivers/geckodriver/` |
| Edge | EdgeDriver | ✅ | `~/.wdm/drivers/edgedriver/` |

---

## ⚙️ Configuraciones Avanzadas

### Configuración para Testing (con UI)

```json
{
  "meta": {
    "mode": "selenium",
    "browser": "firefox",
    "options": ["--width=1280", "--height=720", "--no-sandbox"],
    "headless": false,
    "timeout": 15,
    "implicit_wait": 5
  }
}
```

### Configuración para Producción (headless)

```json
{
  "meta": {
    "mode": "selenium",
    "browser": "chrome",
    "options": [
      "--disable-gpu",
      "--no-sandbox",
      "--disable-dev-shm-usage"
    ],
    "headless": true,
    "timeout": 60,
    "implicit_wait": 10
  }
}
```

---

## 🚨 Problemas Comunes y Soluciones

### Chrome
**Problema:** "cannot find Chrome binary"
**Solución:** Instalar Chrome/Chromium en el sistema, o apuntar `driver.bin` a un binario válido

**Problema:** "Chrome crashed unexpectedly" / "DevToolsActivePort file doesn't exist"
**Solución:** Agregar `--disable-dev-shm-usage` y `--no-sandbox` a `meta.options`

### Firefox
**Problema:** "geckodriver executable needs to be in PATH"
**Solución:** Usar descarga automática, o especificar `driver.bin` con la ruta completa

**Problema:** "Firefox crashed"
**Solución:** Agregar `--no-sandbox` y verificar la versión de Firefox instalada

### Edge
**Problema:** "EdgeDriver executable needs to be in PATH"
**Solución:** Usar descarga automática, o especificar `driver.bin`

---

## 🎯 Recomendaciones por Caso de Uso

### Desarrollo y Testing (con UI visible)
```json
{ "meta": { "mode": "selenium", "browser": "chrome", "headless": false, "timeout": 10 } }
```

### CI/CD y Automatización (headless)
```json
{ "meta": { "mode": "selenium", "browser": "chrome", "headless": true, "timeout": 30 } }
```

### Web Scraping
```json
{ "meta": { "mode": "selenium", "browser": "firefox", "headless": true } }
```

---

## 📞 Soporte

Para problemas específicos de navegadores, verificar la versión del driver correspondiente (ChromeDriver/GeckoDriver/EdgeDriver) contra la versión del navegador instalado — es la causa más común de fallas al inicializar el driver.

**Recursos adicionales:**
- [ChromeDriver](https://chromedriver.chromium.org/)
- [GeckoDriver](https://github.com/mozilla/geckodriver)
- [EdgeDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)

---

**Versión:** 2.1.0
**Autor:** Sugar Team
