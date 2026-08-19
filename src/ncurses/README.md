# Plugin Ncurses para Sugar

## 📋 Descripción

El plugin Ncurses para Sugar proporciona capacidades completas de interfaz de terminal (TUI - Text User Interface) utilizando la biblioteca ncurses. Permite crear aplicaciones de terminal interactivas, dashboards, formularios y interfaces de usuario avanzadas directamente desde Sugar Language.

## ✨ Características

- ✅ **Gestión de ventanas**: Creación y gestión de ventanas múltiples
- ✅ **Interfaz de usuario**: Formularios, menús, listas y controles interactivos
- ✅ **Colores y estilos**: Soporte completo para colores, atributos y estilos
- ✅ **Entrada de usuario**: Captura de teclas, mouse y eventos
- ✅ **Layouts avanzados**: Grid, flexbox y layouts personalizados
- ✅ **Widgets predefinidos**: Botones, campos de texto, listas, barras de progreso
- ✅ **Animaciones**: Efectos visuales y transiciones
- ✅ **Temas**: Sistema de temas personalizables
- ✅ **Responsive**: Adaptación automática al tamaño de terminal
- ✅ **Eventos**: Sistema de eventos y callbacks
- ✅ **Sin dependencias externas**: ncurses viene incluido en Python

## 🚀 Instalación

No se requieren dependencias externas. ncurses viene incluido en Python por defecto.

```bash
# El plugin está listo para usar
```

## 📖 Documentación

- [Documentación completa](docs/README.md) - Guía detallada de todos los comandos
- [Ejemplos básicos](examples/basic_usage.json) - Ejemplos de uso básico
- [Ejemplos avanzados](examples/advanced_usage.json) - Interfaces complejas
- [Ejemplos de widgets](examples/widgets_example.json) - Uso de widgets predefinidos

## 🎯 Comandos Principales

### Gestión de Terminal
- `init` - Inicializar ncurses
- `end` - Finalizar ncurses
- `refresh` - Actualizar pantalla
- `clear` - Limpiar pantalla
- `get_size` - Obtener tamaño de terminal

### Gestión de Ventanas
- `create_window` - Crear nueva ventana
- `delete_window` - Eliminar ventana
- `resize_window` - Redimensionar ventana
- `move_window` - Mover ventana
- `set_active_window` - Establecer ventana activa

### Dibujo y Texto
- `print` - Imprimir texto en posición específica
- `draw_box` - Dibujar caja/borde
- `draw_line` - Dibujar líneas
- `fill_area` - Rellenar área con carácter
- `clear_area` - Limpiar área específica

### Colores y Estilos
- `init_colors` - Inicializar sistema de colores
- `set_color` - Establecer color de texto/fondo
- `set_attributes` - Establecer atributos (bold, underline, etc.)
- `create_color_pair` - Crear par de colores personalizado
- `set_theme` - Aplicar tema completo

### Entrada de Usuario
- `get_key` - Capturar tecla
- `get_string` - Capturar string
- `get_choice` - Capturar selección de menú
- `enable_mouse` - Habilitar soporte de mouse
- `get_mouse_event` - Capturar evento de mouse

### Widgets Predefinidos
- `create_button` - Crear botón interactivo
- `create_text_field` - Crear campo de texto
- `create_list` - Crear lista seleccionable
- `create_menu` - Crear menú desplegable
- `create_progress_bar` - Crear barra de progreso
- `create_table` - Crear tabla de datos
- `create_form` - Crear formulario completo

### Layouts y Posicionamiento
- `create_grid` - Crear layout de cuadrícula
- `create_flexbox` - Crear layout flexible
- `position_widget` - Posicionar widget
- `center_widget` - Centrar widget
- `align_widgets` - Alinear múltiples widgets

### Eventos y Callbacks
- `on_key_press` - Registrar callback para teclas
- `on_mouse_click` - Registrar callback para clicks
- `on_window_resize` - Registrar callback para resize
- `trigger_event` - Disparar evento personalizado
- `wait_for_event` - Esperar evento específico

### Utilidades
- `save_screen` - Guardar estado de pantalla
- `restore_screen` - Restaurar estado de pantalla
- `create_overlay` - Crear overlay temporal
- `show_help` - Mostrar ayuda contextual
- `create_dialog` - Crear diálogo modal

## 💡 Ejemplo Rápido

```json
{
  "task": [
    {
      "ncurses": {
        "operator": "init",
        "enable_colors": true,
        "enable_mouse": true
      }
    },
    {
      "ncurses": {
        "operator": "init_colors",
        "theme": "default"
      }
    },
    {
      "ncurses": {
        "operator": "create_window",
        "name": "main_window",
        "x": 0,
        "y": 0,
        "width": "100%",
        "height": "100%",
        "title": "Mi Aplicación Sugar"
      }
    },
    {
      "ncurses": {
        "operator": "set_active_window",
        "window": "main_window"
      }
    },
    {
      "ncurses": {
        "operator": "print",
        "text": "¡Bienvenido a Sugar Language!",
        "x": 2,
        "y": 2,
        "color": "green",
        "attributes": ["bold"]
      }
    },
    {
      "ncurses": {
        "operator": "create_button",
        "name": "btn_salir",
        "text": "Salir",
        "x": 10,
        "y": 10,
        "width": 10,
        "action": "exit"
      }
    },
    {
      "ncurses": {
        "operator": "refresh"
      }
    },
    {
      "ncurses": {
        "operator": "wait_for_event",
        "timeout": -1
      }
    },
    {
      "ncurses": {
        "operator": "end"
      }
    }
  ]
}
```

## 💡 Ejemplo: Dashboard Interactivo

```json
{
  "task": [
    {
      "ncurses": {
        "operator": "init",
        "enable_colors": true
      }
    },
    {
      "ncurses": {
        "operator": "create_grid",
        "name": "dashboard",
        "rows": 3,
        "cols": 2,
        "gaps": [1, 1]
      }
    },
    {
      "ncurses": {
        "operator": "create_window",
        "name": "stats_panel",
        "grid": "dashboard",
        "row": 0,
        "col": 0,
        "title": "Estadísticas"
      }
    },
    {
      "ncurses": {
        "operator": "create_window",
        "name": "menu_panel",
        "grid": "dashboard",
        "row": 0,
        "col": 1,
        "title": "Menú Principal"
      }
    },
    {
      "ncurses": {
        "operator": "create_list",
        "window": "menu_panel",
        "items": [
          "Ver estadísticas",
          "Configuración",
          "Exportar datos",
          "Salir"
        ],
        "x": 2,
        "y": 2,
        "result": "selected_option"
      }
    },
    {
      "ncurses": {
        "operator": "refresh"
      }
    }
  ]
}
```

## 💡 Ejemplo: Formulario Completo

```json
{
  "task": [
    {
      "ncurses": {
        "operator": "create_form",
        "name": "user_form",
        "title": "Registro de Usuario",
        "fields": [
          {
            "name": "nombre",
            "label": "Nombre:",
            "type": "text",
            "required": true,
            "max_length": 50
          },
          {
            "name": "email",
            "label": "Email:",
            "type": "email",
            "required": true
          },
          {
            "name": "edad",
            "label": "Edad:",
            "type": "number",
            "min": 18,
            "max": 100
          },
          {
            "name": "genero",
            "label": "Género:",
            "type": "select",
            "options": ["Masculino", "Femenino", "Otro"]
          }
        ],
        "buttons": [
          {
            "text": "Guardar",
            "action": "submit"
          },
          {
            "text": "Cancelar",
            "action": "cancel"
          }
        ],
        "result": "form_data"
      }
    }
  ]
}
```

## 🎨 Temas Disponibles

### Tema Default
- Colores suaves y profesionales
- Alto contraste para legibilidad
- Compatible con la mayoría de terminales

### Tema Dark
- Fondo oscuro con texto claro
- Colores modernos y elegantes
- Ideal para uso nocturno

### Tema Light
- Fondo claro con texto oscuro
- Colores vibrantes
- Perfecto para entornos bien iluminados

### Tema Monochrome
- Solo blanco y negro
- Compatible con terminales antiguas
- Ideal para accesibilidad

## 🔧 Configuración Avanzada

### Personalización de Colores
```json
{
  "ncurses": {
    "operator": "create_color_pair",
    "pair_id": 1,
    "foreground": "white",
    "background": "blue"
  }
}
```

### Eventos Personalizados
```json
{
  "ncurses": {
    "operator": "on_key_press",
    "key": "q",
    "action": {
      "ncurses": {
        "operator": "end"
      }
    }
  }
}
```

### Layouts Responsivos
```json
{
  "ncurses": {
    "operator": "create_flexbox",
    "name": "responsive_layout",
    "direction": "vertical",
    "justify": "center",
    "align": "center",
    "wrap": true
  }
}
```

## 📚 Referencias

- [Documentación de ncurses](https://docs.python.org/3/library/curses.html)
- [Sistema de Plugins](https://sugar-lang.org/docs/plugins)
- [Guía de Widgets](docs/widgets.md)
- [Tutorial de Temas](docs/themes.md)

## 🤝 Contribuir

Para contribuir al plugin ncurses:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Implementa los cambios
4. Añade tests
5. Envía un pull request

## 📄 Licencia

Este plugin está bajo la licencia MIT. Ver [LICENSE](../../LICENSE) para más detalles.