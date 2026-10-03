"""
Plugin Ncurses para Sugar Language
==================================

Proporciona capacidades completas de interfaz de terminal (TUI) utilizando ncurses.
Implementado como plugin siguiendo la arquitectura de plugins de Sugar.
"""

import curses
import curses.ascii
import threading
import time
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import locale
import unicodedata
from collections import defaultdict

from Sugar.Lang.Plugins.PluginBase import PluginBase
from Sugar.Lang.Utils.Output import Output

class NcursesError(Exception):
    """Excepción personalizada para errores de ncurses"""
    pass

class ColorTheme(Enum):
    """Temas de color disponibles"""
    DEFAULT = "default"
    DARK = "dark"
    LIGHT = "light"
    MONOCHROME = "monochrome"

class WidgetType(Enum):
    """Tipos de widgets disponibles"""
    BUTTON = "button"
    TEXT_FIELD = "text_field"
    LIST = "list"
    MENU = "menu"
    PROGRESS_BAR = "progress_bar"
    TABLE = "table"
    FORM = "form"

@dataclass
class Window:
    """Representa una ventana de ncurses"""
    name: str
    window: curses.window
    x: int
    y: int
    width: int
    height: int
    title: Optional[str] = None
    border: bool = True
    scrollable: bool = False

@dataclass
class Widget:
    """Representa un widget de la interfaz"""
    name: str
    widget_type: WidgetType
    x: int
    y: int
    width: int
    height: int
    data: Dict[str, Any] = field(default_factory=dict)
    callback: Optional[Callable] = None

@dataclass
class Event:
    """Representa un evento de la interfaz"""
    type: str
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)

class NcursesManager:
    """Gestor principal de ncurses"""
    
    def __init__(self):
        self.initialized = False
        self.windows: Dict[str, Window] = {}
        self.widgets: Dict[str, Widget] = {}
        self.active_window: Optional[str] = None
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.color_pairs: Dict[int, Tuple[int, int]] = {}
        self.themes: Dict[str, Dict[str, Any]] = {}
        self.screen_saved = False
        self.original_screen = None
        self._setup_themes()
    
    def _setup_themes(self):
        """Configura los temas de color predefinidos"""
        self.themes = {
            ColorTheme.DEFAULT.value: {
                "background": curses.COLOR_BLACK,
                "foreground": curses.COLOR_WHITE,
                "accent": curses.COLOR_CYAN,
                "error": curses.COLOR_RED,
                "success": curses.COLOR_GREEN,
                "warning": curses.COLOR_YELLOW
            },
            ColorTheme.DARK.value: {
                "background": curses.COLOR_BLACK,
                "foreground": curses.COLOR_WHITE,
                "accent": curses.COLOR_BLUE,
                "error": curses.COLOR_RED,
                "success": curses.COLOR_GREEN,
                "warning": curses.COLOR_YELLOW
            },
            ColorTheme.LIGHT.value: {
                "background": curses.COLOR_WHITE,
                "foreground": curses.COLOR_BLACK,
                "accent": curses.COLOR_BLUE,
                "error": curses.COLOR_RED,
                "success": curses.COLOR_GREEN,
                "warning": curses.COLOR_YELLOW
            },
            ColorTheme.MONOCHROME.value: {
                "background": curses.COLOR_WHITE,
                "foreground": curses.COLOR_BLACK,
                "accent": curses.COLOR_WHITE,
                "error": curses.COLOR_WHITE,
                "success": curses.COLOR_WHITE,
                "warning": curses.COLOR_WHITE
            }
        }

class NcursesPlugin(PluginBase):
    """
    Plugin Ncurses para Sugar Language.
    
    Proporciona capacidades completas de interfaz de terminal (TUI) utilizando ncurses.
    Permite crear aplicaciones de terminal interactivas, dashboards, formularios y
    interfaces de usuario avanzadas directamente desde Sugar Language.
    """
    
    # Plugin metadata
    VERSION = "1.0.0"
    DESCRIPTION = "Plugin Ncurses para Sugar - Interfaces de terminal interactivas (TUI)"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    DEPENDENCIES = []
    REQUIREMENTS = []
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """Initialize the ncurses plugin"""
        super().__init__(context, plugin_config)
        self.manager = NcursesManager()
        self._setup_commands()
    
    def _setup_commands(self):
        """Configura el mapeo de comandos"""
        self.commands = {
            # Gestión de terminal
            "init": self._init_ncurses,
            "end": self._end_ncurses,
            "refresh": self._refresh_screen,
            "clear": self._clear_screen,
            "get_size": self._get_terminal_size,
            
            # Gestión de ventanas
            "create_window": self._create_window,
            "delete_window": self._delete_window,
            "resize_window": self._resize_window,
            "move_window": self._move_window,
            "set_active_window": self._set_active_window,
            
            # Dibujo y texto
            "print": self._print_text,
            "draw_box": self._draw_box,
            "draw_line": self._draw_line,
            "fill_area": self._fill_area,
            "clear_area": self._clear_area,
            
            # Colores y estilos
            "init_colors": self._init_colors,
            "set_color": self._set_color,
            "set_attributes": self._set_attributes,
            "create_color_pair": self._create_color_pair,
            "set_theme": self._set_theme,
            
            # Entrada de usuario
            "get_key": self._get_key,
            "get_string": self._get_string,
            "get_choice": self._get_choice,
            "enable_mouse": self._enable_mouse,
            "get_mouse_event": self._get_mouse_event,
            
            # Widgets
            "create_button": self._create_button,
            "create_text_field": self._create_text_field,
            "create_list": self._create_list,
            "create_menu": self._create_menu,
            "create_progress_bar": self._create_progress_bar,
            "create_table": self._create_table,
            "create_form": self._create_form,
            
            # Layouts
            "create_grid": self._create_grid,
            "create_flexbox": self._create_flexbox,
            "position_widget": self._position_widget,
            "center_widget": self._center_widget,
            "align_widgets": self._align_widgets,
            
            # Eventos
            "on_key_press": self._on_key_press,
            "on_mouse_click": self._on_mouse_click,
            "on_window_resize": self._on_window_resize,
            "trigger_event": self._trigger_event,
            "wait_for_event": self._wait_for_event,
            
            # Utilidades
            "save_screen": self._save_screen,
            "restore_screen": self._restore_screen,
            "create_overlay": self._create_overlay,
            "show_help": self._show_help,
            "create_dialog": self._create_dialog,

            # TUI de alto nivel
            "datatable": self._datatable
        }
    
    def execute(self, operator: str, config: Dict[str, Any]) -> Any:
        """
        Execute a ncurses operator.

        El core invoca al plugin como `{"ncurses": {"operator": "...", ...}}`,
        con el nombre del plugin como `operator` (igual que el plugin
        `database`), asi que el operador real se resuelve desde
        `config["operator"]`.

        Args:
            operator: Nombre con el que el core invoco al plugin
            config: Configuration dictionary for the operator

        Returns:
            Result of the ncurses operation
        """
        op = config.get("operator") or operator

        if op not in self.commands:
            raise NcursesError(f"Comando no reconocido: {op}")

        try:
            # Interpolate variables in config
            interpolated_config = self.interpolate_variables(config)

            # Execute the operator
            result = self.commands[op](interpolated_config)

            # Store result in context if specified
            result_key = config.get("id")
            if result_key and self.context:
                self.set_variable(result_key, result)

            return result

        except NcursesError:
            raise
        except Exception as e:
            Output.Console(self.plugin_name, f"Error ejecutando {op}: {str(e)}")
            raise NcursesError(f"Error ejecutando {op}: {str(e)}")
    
    def get_available_commands(self) -> List[str]:
        """
        Return a list of available commands for this plugin.

        Debe devolver el nombre del plugin (no los operadores): el core
        registra el nodo `{"ncurses": {...}}` a partir de esta lista. Es la
        misma correccion que necesito el plugin `database`.
        """
        return ["ncurses"]
    
    # ============================================================================
    # GESTIÓN DE TERMINAL
    # ============================================================================
    
    def _init_ncurses(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Inicializa ncurses"""
        if self.manager.initialized:
            return {"status": "already_initialized"}
        
        try:
            # Inicializar ncurses
            self.manager.original_screen = curses.initscr()
            curses.noecho()
            curses.cbreak()
            curses.start_color()
            
            # Configuraciones opcionales
            if config.get("enable_colors", True):
                curses.use_default_colors()
            
            if config.get("enable_mouse", False):
                curses.mousemask(curses.ALL_MOUSE_EVENTS)
            
            if config.get("enable_keypad", True):
                self.manager.original_screen.keypad(True)
            
            self.manager.initialized = True
            
            return {
                "status": "initialized",
                "terminal_size": self._get_terminal_size({})
            }
        except Exception as e:
            raise NcursesError(f"Error inicializando ncurses: {str(e)}")
    
    def _end_ncurses(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Finaliza ncurses"""
        if not self.manager.initialized:
            return {"status": "not_initialized"}
        
        try:
            # Restaurar terminal
            curses.nocbreak()
            curses.echo()
            curses.endwin()
            
            self.manager.initialized = False
            self.manager.windows.clear()
            self.manager.widgets.clear()
            
            return {"status": "ended"}
        except Exception as e:
            raise NcursesError(f"Error finalizando ncurses: {str(e)}")
    
    def _refresh_screen(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza la pantalla"""
        if not self.manager.initialized:
            raise NcursesError("ncurses no está inicializado")
        
        try:
            if self.manager.active_window and self.manager.active_window in self.manager.windows:
                self.manager.windows[self.manager.active_window].window.refresh()
            else:
                curses.refresh()
            
            return {"status": "refreshed"}
        except Exception as e:
            raise NcursesError(f"Error refrescando pantalla: {str(e)}")
    
    def _clear_screen(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Limpia la pantalla"""
        if not self.manager.initialized:
            raise NcursesError("ncurses no está inicializado")
        
        try:
            curses.clear()
            return {"status": "cleared"}
        except Exception as e:
            raise NcursesError(f"Error limpiando pantalla: {str(e)}")
    
    def _get_terminal_size(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene el tamaño de la terminal"""
        if not self.manager.initialized:
            raise NcursesError("ncurses no está inicializado")
        
        try:
            height, width = self.manager.original_screen.getmaxyx()
            return {
                "width": width,
                "height": height,
                "size": f"{width}x{height}"
            }
        except Exception as e:
            raise NcursesError(f"Error obteniendo tamaño de terminal: {str(e)}")
    
    # ============================================================================
    # GESTIÓN DE VENTANAS
    # ============================================================================
    
    def _create_window(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva ventana"""
        if not self.manager.initialized:
            raise NcursesError("ncurses no está inicializado")
        
        try:
            name = config["name"]
            x = config.get("x", 0)
            y = config.get("y", 0)
            width = config.get("width", 10)
            height = config.get("height", 10)
            title = config.get("title")
            border = config.get("border", True)
            
            # Crear ventana
            window = curses.newwin(height, width, y, x)
            
            # Configurar ventana
            if border:
                window.box()
            
            if title:
                # Centrar título en la parte superior
                title_x = max(1, (width - len(title)) // 2)
                window.addstr(0, title_x, f" {title} ")
            
            # Guardar ventana
            self.manager.windows[name] = Window(
                name=name,
                window=window,
                x=x,
                y=y,
                width=width,
                height=height,
                title=title,
                border=border
            )
            
            # Establecer como activa si es la primera
            if not self.manager.active_window:
                self.manager.active_window = name
            
            return {
                "status": "created",
                "window_name": name,
                "position": {"x": x, "y": y},
                "size": {"width": width, "height": height}
            }
        except Exception as e:
            raise NcursesError(f"Error creando ventana: {str(e)}")
    
    def _delete_window(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina una ventana"""
        name = config["name"]
        
        if name not in self.manager.windows:
            raise NcursesError(f"Ventana no encontrada: {name}")
        
        try:
            # Eliminar widgets asociados
            widgets_to_remove = [
                widget_name for widget_name, widget in self.manager.widgets.items()
                if widget.data.get("window") == name
            ]
            for widget_name in widgets_to_remove:
                del self.manager.widgets[widget_name]
            
            # Eliminar ventana
            del self.manager.windows[name]
            
            # Cambiar ventana activa si es necesario
            if self.manager.active_window == name:
                self.manager.active_window = list(self.manager.windows.keys())[0] if self.manager.windows else None
            
            return {"status": "deleted", "window_name": name}
        except Exception as e:
            raise NcursesError(f"Error eliminando ventana: {str(e)}")
    
    def _set_active_window(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Establece la ventana activa"""
        window_name = config["window"]
        
        if window_name not in self.manager.windows:
            raise NcursesError(f"Ventana no encontrada: {window_name}")
        
        self.manager.active_window = window_name
        return {"status": "active_window_changed", "window_name": window_name}
    
    # ============================================================================
    # DIBUJO Y TEXTO
    # ============================================================================
    
    def _print_text(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Imprime texto en la posición especificada"""
        if not self.manager.initialized:
            raise NcursesError("ncurses no está inicializado")
        
        try:
            text = config["text"]
            x = config.get("x", 0)
            y = config.get("y", 0)
            color = config.get("color", "white")
            attributes = config.get("attributes", [])
            
            # Obtener ventana activa
            if not self.manager.active_window:
                raise NcursesError("No hay ventana activa")
            
            window = self.manager.windows[self.manager.active_window].window
            
            # Aplicar color y atributos
            attr = 0
            if color in self.manager.color_pairs:
                attr |= curses.color_pair(self.manager.color_pairs[color])
            
            for attr_name in attributes:
                if hasattr(curses, f"A_{attr_name.upper()}"):
                    attr |= getattr(curses, f"A_{attr_name.upper()}")
            
            # Imprimir texto
            window.addstr(y, x, text, attr)
            
            return {"status": "printed", "text": text, "position": {"x": x, "y": y}}
        except Exception as e:
            raise NcursesError(f"Error imprimiendo texto: {str(e)}")
    
    def _draw_box(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Dibuja una caja/borde"""
        if not self.manager.initialized:
            raise NcursesError("ncurses no está inicializado")
        
        try:
            x = config.get("x", 0)
            y = config.get("y", 0)
            width = config.get("width", 10)
            height = config.get("height", 5)
            title = config.get("title")
            
            if not self.manager.active_window:
                raise NcursesError("No hay ventana activa")
            
            window = self.manager.windows[self.manager.active_window].window
            
            # Dibujar caja
            window.box()
            
            # Agregar título si se especifica
            if title:
                title_x = max(x + 1, (x + width - len(title)) // 2)
                window.addstr(y, title_x, f" {title} ")
            
            return {"status": "box_drawn", "position": {"x": x, "y": y}, "size": {"width": width, "height": height}}
        except Exception as e:
            raise NcursesError(f"Error dibujando caja: {str(e)}")
    
    # ============================================================================
    # COLORES Y ESTILOS
    # ============================================================================
    
    def _init_colors(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Inicializa el sistema de colores"""
        if not self.manager.initialized:
            raise NcursesError("ncurses no está inicializado")
        
        try:
            theme_name = config.get("theme", ColorTheme.DEFAULT.value)
            
            if theme_name not in self.manager.themes:
                raise NcursesError(f"Tema no encontrado: {theme_name}")
            
            theme = self.manager.themes[theme_name]
            
            # Crear pares de colores
            pair_id = 1
            for color_name, color_value in theme.items():
                curses.init_pair(pair_id, color_value, theme["background"])
                self.manager.color_pairs[color_name] = pair_id
                pair_id += 1
            
            return {"status": "colors_initialized", "theme": theme_name}
        except Exception as e:
            raise NcursesError(f"Error inicializando colores: {str(e)}")
    
    def _set_theme(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica un tema completo"""
        return self._init_colors(config)
    
    # ============================================================================
    # ENTRADA DE USUARIO
    # ============================================================================
    
    def _get_key(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Captura una tecla"""
        if not self.manager.initialized:
            raise NcursesError("ncurses no está inicializado")
        
        try:
            if not self.manager.active_window:
                raise NcursesError("No hay ventana activa")
            
            window = self.manager.windows[self.manager.active_window].window
            
            # Capturar tecla
            key = window.getch()
            
            # Convertir a representación legible
            key_name = self._key_to_name(key)
            
            return {
                "key_code": key,
                "key_name": key_name,
                "key_char": chr(key) if 32 <= key <= 126 else None
            }
        except Exception as e:
            raise NcursesError(f"Error capturando tecla: {str(e)}")
    
    def _key_to_name(self, key: int) -> str:
        """Convierte un código de tecla a nombre legible"""
        key_names = {
            curses.KEY_UP: "UP",
            curses.KEY_DOWN: "DOWN",
            curses.KEY_LEFT: "LEFT",
            curses.KEY_RIGHT: "RIGHT",
            curses.KEY_ENTER: "ENTER",
            curses.KEY_BACKSPACE: "BACKSPACE",
            curses.KEY_DC: "DELETE",
            curses.KEY_HOME: "HOME",
            curses.KEY_END: "END",
            curses.KEY_PPAGE: "PAGE_UP",
            curses.KEY_NPAGE: "PAGE_DOWN",
            curses.KEY_F1: "F1",
            curses.KEY_F2: "F2",
            curses.KEY_F3: "F3",
            curses.KEY_F4: "F4",
            curses.KEY_F5: "F5",
            curses.KEY_F6: "F6",
            curses.KEY_F7: "F7",
            curses.KEY_F8: "F8",
            curses.KEY_F9: "F9",
            curses.KEY_F10: "F10",
            curses.KEY_F11: "F11",
            curses.KEY_F12: "F12",
            27: "ESC",  # Escape
            9: "TAB",   # Tab
            10: "ENTER" # Enter
        }
        
        return key_names.get(key, f"KEY_{key}")
    
    def _get_string(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Captura una cadena de texto"""
        if not self.manager.initialized:
            raise NcursesError("ncurses no está inicializado")
        
        try:
            prompt = config.get("prompt", "")
            max_length = config.get("max_length", 50)
            x = config.get("x", 0)
            y = config.get("y", 0)
            
            if not self.manager.active_window:
                raise NcursesError("No hay ventana activa")
            
            window = self.manager.windows[self.manager.active_window].window
            
            # Mostrar prompt
            if prompt:
                window.addstr(y, x, prompt)
                x += len(prompt)
            
            # Capturar string
            curses.echo()
            string = window.getstr(y, x, max_length).decode('utf-8')
            curses.noecho()
            
            return {"string": string, "length": len(string)}
        except Exception as e:
            raise NcursesError(f"Error capturando string: {str(e)}")
    
    # ============================================================================
    # WIDGETS
    # ============================================================================
    
    def _create_button(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un botón interactivo"""
        try:
            name = config["name"]
            text = config["text"]
            x = config.get("x", 0)
            y = config.get("y", 0)
            width = config.get("width", len(text) + 2)
            action = config.get("action")
            
            # Crear widget
            widget = Widget(
                name=name,
                widget_type=WidgetType.BUTTON,
                x=x,
                y=y,
                width=width,
                height=1,
                data={
                    "text": text,
                    "action": action,
                    "window": self.manager.active_window
                }
            )
            
            self.manager.widgets[name] = widget
            
            # Dibujar botón
            if self.manager.active_window:
                window = self.manager.windows[self.manager.active_window].window
                window.addstr(y, x, f"[{text}]")
            
            return {"status": "created", "widget_name": name, "type": "button"}
        except Exception as e:
            raise NcursesError(f"Error creando botón: {str(e)}")
    
    def _create_list(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una lista seleccionable"""
        try:
            name = config["name"]
            items = config["items"]
            x = config.get("x", 0)
            y = config.get("y", 0)
            width = config.get("width", max(len(item) for item in items) + 2)
            height = config.get("height", len(items))
            
            # Crear widget
            widget = Widget(
                name=name,
                widget_type=WidgetType.LIST,
                x=x,
                y=y,
                width=width,
                height=height,
                data={
                    "items": items,
                    "selected_index": 0,
                    "window": self.manager.active_window
                }
            )
            
            self.manager.widgets[name] = widget
            
            # Dibujar lista
            if self.manager.active_window:
                window = self.manager.windows[self.manager.active_window].window
                for i, item in enumerate(items[:height]):
                    prefix = "> " if i == 0 else "  "
                    window.addstr(y + i, x, f"{prefix}{item}")
            
            return {"status": "created", "widget_name": name, "type": "list", "item_count": len(items)}
        except Exception as e:
            raise NcursesError(f"Error creando lista: {str(e)}")
    
    def _create_form(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un formulario completo"""
        try:
            name = config["name"]
            title = config.get("title", "Formulario")
            fields = config["fields"]
            buttons = config.get("buttons", [])
            
            # Calcular dimensiones del formulario
            max_label_length = max(len(field["label"]) for field in fields)
            max_field_width = max(field.get("max_length", 20) for field in fields)
            form_width = max_label_length + max_field_width + 5
            form_height = len(fields) + len(buttons) + 4
            
            # Crear ventana para el formulario
            term_height, term_width = self.manager.original_screen.getmaxyx()
            form_x = (term_width - form_width) // 2
            form_y = (term_height - form_height) // 2
            
            # Crear widget
            widget = Widget(
                name=name,
                widget_type=WidgetType.FORM,
                x=form_x,
                y=form_y,
                width=form_width,
                height=form_height,
                data={
                    "title": title,
                    "fields": fields,
                    "buttons": buttons,
                    "current_field": 0,
                    "values": {}
                }
            )
            
            self.manager.widgets[name] = widget
            
            # Dibujar formulario
            self._draw_form(widget)
            
            return {"status": "created", "widget_name": name, "type": "form"}
        except Exception as e:
            raise NcursesError(f"Error creando formulario: {str(e)}")
    
    def _draw_form(self, widget: Widget):
        """Dibuja un formulario"""
        try:
            # Crear ventana temporal para el formulario
            form_win = curses.newwin(widget.height, widget.width, widget.y, widget.x)
            form_win.box()
            
            # Título
            title = widget.data["title"]
            title_x = (widget.width - len(title)) // 2
            form_win.addstr(0, title_x, f" {title} ")
            
            # Campos
            fields = widget.data["fields"]
            for i, field in enumerate(fields):
                y_pos = i + 2
                label = field["label"]
                form_win.addstr(y_pos, 1, label)
                form_win.addstr(y_pos, len(label) + 1, ":" + "_" * field.get("max_length", 20))
            
            # Botones
            buttons = widget.data["buttons"]
            button_y = len(fields) + 3
            button_x = 1
            for button in buttons:
                form_win.addstr(button_y, button_x, f"[{button['text']}]")
                button_x += len(button['text']) + 4
            
            form_win.refresh()
        except Exception as e:
            raise NcursesError(f"Error dibujando formulario: {str(e)}")
    
    # ============================================================================
    # LAYOUTS
    # ============================================================================
    
    def _create_grid(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un layout de cuadrícula"""
        try:
            name = config["name"]
            rows = config["rows"]
            cols = config["cols"]
            gaps = config.get("gaps", [0, 0])
            
            # Calcular dimensiones de la terminal
            term_height, term_width = self.manager.original_screen.getmaxyx()
            
            # Calcular tamaño de cada celda
            cell_width = (term_width - (cols - 1) * gaps[0]) // cols
            cell_height = (term_height - (rows - 1) * gaps[1]) // rows
            
            # Crear grid
            grid_data = {
                "name": name,
                "rows": rows,
                "cols": cols,
                "cell_width": cell_width,
                "cell_height": cell_height,
                "gaps": gaps,
                "cells": {}
            }
            
            # Guardar grid en el manager
            if not hasattr(self.manager, 'grids'):
                self.manager.grids = {}
            self.manager.grids[name] = grid_data
            
            return {
                "status": "created",
                "grid_name": name,
                "dimensions": {"rows": rows, "cols": cols},
                "cell_size": {"width": cell_width, "height": cell_height}
            }
        except Exception as e:
            raise NcursesError(f"Error creando grid: {str(e)}")
    
    # ============================================================================
    # EVENTOS
    # ============================================================================
    
    def _on_key_press(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Registra un callback para teclas"""
        try:
            key = config["key"]
            action = config["action"]
            
            if "key_handlers" not in self.manager.event_handlers:
                self.manager.event_handlers["key_handlers"] = {}
            
            self.manager.event_handlers["key_handlers"][key] = action
            
            return {"status": "registered", "key": key}
        except Exception as e:
            raise NcursesError(f"Error registrando callback de tecla: {str(e)}")
    
    def _wait_for_event(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Espera un evento específico"""
        if not self.manager.initialized:
            raise NcursesError("ncurses no está inicializado")
        
        try:
            timeout = config.get("timeout", -1)
            event_type = config.get("event_type", "any")
            
            if not self.manager.active_window:
                raise NcursesError("No hay ventana activa")
            
            window = self.manager.windows[self.manager.active_window].window
            
            # Configurar timeout si se especifica
            if timeout > 0:
                window.timeout(timeout * 1000)  # Convertir a milisegundos
            
            # Esperar evento
            key = window.getch()
            
            # Restaurar timeout
            if timeout > 0:
                window.timeout(-1)
            
            # Procesar evento
            if key == -1:  # Timeout
                return {"event": "timeout", "key": None}
            
            # Verificar si hay un handler registrado
            if "key_handlers" in self.manager.event_handlers:
                key_name = self._key_to_name(key)
                if key_name in self.manager.event_handlers["key_handlers"]:
                    handler = self.manager.event_handlers["key_handlers"][key_name]
                    # Aquí se ejecutaría el handler (acción)
                    return {"event": "key_press", "key": key_name, "handler": handler}
            
            return {"event": "key_press", "key": self._key_to_name(key), "key_code": key}
        except Exception as e:
            raise NcursesError(f"Error esperando evento: {str(e)}")
    
    # ============================================================================
    # UTILIDADES
    # ============================================================================
    
    def _save_screen(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Guarda el estado actual de la pantalla"""
        if not self.manager.initialized:
            raise NcursesError("ncurses no está inicializado")
        
        try:
            if not self.manager.screen_saved:
                self.manager.original_screen = curses.initscr()
                self.manager.screen_saved = True
            
            return {"status": "saved"}
        except Exception as e:
            raise NcursesError(f"Error guardando pantalla: {str(e)}")
    
    def _restore_screen(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Restaura el estado de la pantalla"""
        if not self.manager.initialized:
            raise NcursesError("ncurses no está inicializado")
        
        try:
            if self.manager.screen_saved:
                curses.endwin()
                self.manager.original_screen = curses.initscr()
                self.manager.screen_saved = False
            
            return {"status": "restored"}
        except Exception as e:
            raise NcursesError(f"Error restaurando pantalla: {str(e)}")
    
    def _show_help(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Muestra ayuda contextual"""
        try:
            help_text = config.get("text", "Ayuda no disponible")
            title = config.get("title", "Ayuda")
            
            # Crear ventana de ayuda
            term_height, term_width = self.manager.original_screen.getmaxyx()
            help_width = min(80, term_width - 4)
            help_height = min(20, term_height - 4)
            
            help_x = (term_width - help_width) // 2
            help_y = (term_height - help_height) // 2
            
            help_win = curses.newwin(help_height, help_width, help_y, help_x)
            help_win.box()
            
            # Título
            title_x = (help_width - len(title)) // 2
            help_win.addstr(0, title_x, f" {title} ")
            
            # Contenido
            lines = help_text.split('\n')
            for i, line in enumerate(lines[:help_height-2]):
                help_win.addstr(i + 1, 1, line[:help_width-2])
            
            help_win.refresh()
            
            # Esperar tecla
            help_win.getch()
            
            return {"status": "help_shown"}
        except Exception as e:
            raise NcursesError(f"Error mostrando ayuda: {str(e)}")
    
    # ============================================================================
    # ============================================================================
    # TUI DE ALTO NIVEL: DATATABLE (config estilo Webix)
    # ============================================================================

    def _datatable(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Frontend generico estilo Webix DataTable.

        No accede a datos: recibe las filas por `source` (variable de Sugar) o
        `data` (lista inline, o nombre de variable) y solo muestra/filtra/ordena/
        selecciona en memoria. La config sigue la API de Webix DataTable
        (`columns` con `id`/`header`/`width`/`fillspace`/`sort`/`template`,
        `data`, `select`, ...), reemplazando `view: "datatable"` por
        `operator: "datatable"`.
        """
        items = self._source_items(config)
        state = self._datatable_state(config, items)
        title = config.get("title", "Tabla")
        return self._run_datatable(config, state, title)

    def _source_items(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        data = config.get("data")
        if isinstance(data, list):
            return data
        source = config.get("source") or (data if isinstance(data, str) else None)
        if not source:
            raise NcursesError("datatable: falta 'source' o 'data' (filas para mostrar)")
        handler = getattr(self.context, "memory_handler", None) if self.context else None
        if handler is None:
            raise NcursesError("datatable: no hay memory_handler para leer la variable de Sugar")
        value = handler.get_variable(source)
        if value is None:
            raise NcursesError(f"datatable: la variable '{source}' no existe o esta vacia")
        if isinstance(value, dict):
            return [value]
        if not isinstance(value, list):
            raise NcursesError(f"datatable: '{source}' no es una lista (es {type(value).__name__})")
        return value

    def _datatable_state(self, config: Dict[str, Any], items: List[Dict[str, Any]]) -> Dict[str, Any]:
        columns = self._normalize_columns(config.get("columns"), items)
        search_fields = config.get("search_fields") or self._default_search_fields(columns, items)
        detail_fields = self._normalize_detail_fields(
            config.get("detail") or config.get("detail_fields"), items
        )
        sort_id = config.get("sort") if isinstance(config.get("sort"), str) else None
        sort_index = 0
        if sort_id:
            sort_index = next((i for i, col in enumerate(columns) if col["id"] == sort_id), 0)
        filter_spec = self._normalize_filter(config.get("filter"))
        filter_value = 0.0
        if filter_spec:
            filter_value = float(config.get("filter_default", filter_spec.get("default", 0)) or 0)
        return {
            "items": items,
            "columns": columns,
            "search_fields": search_fields,
            "detail_fields": detail_fields,
            "filter_spec": filter_spec,
            "filter_value": filter_value,
            "query": config.get("initial_query", ""),
            "only_flags": False,
            "offset": 0,
            "cursor": 0,
            "total": 0,
            "rows": [],
            "search_mode": False,
            "show_header": bool(config.get("header", True)),
            "select_mode": config.get("select", "row"),
            "marked": {},
            "sort_index": sort_index % len(columns) if columns else 0,
            "sort_desc": bool(config.get("sort_desc", False)),
            "header_focus": False,
            "header_cursor": sort_index % len(columns) if columns else 0,
            "dirty": True,
        }

    @staticmethod
    def _normalize_columns(columns, items):
        if not columns:
            keys = list(items[0].keys()) if items else []
            return [
                {
                    "id": key, "header": key, "type": NcursesPlugin._guess_type(items, key),
                    "width": None, "fillspace": False, "template": None, "align": None,
                    "format": None, "sortable": True,
                }
                for key in keys
            ]
        normalized = []
        for column in columns:
            if isinstance(column, str):
                column = {"id": column}
            header = column.get("header", column["id"])
            if isinstance(header, list):
                header = header[0] if header else column["id"]
            normalized.append({
                "id": column["id"],
                "header": str(header),
                "type": NcursesPlugin._column_type(column),
                "width": column.get("width"),
                "fillspace": bool(column.get("fillspace", False)),
                "template": column.get("template"),
                "align": column.get("align"),
                "format": column.get("format"),
                "sortable": "sort" in column,
            })
        return normalized

    @staticmethod
    def _column_type(column):
        template = column.get("template")
        if isinstance(template, str) and "common.checkbox" in template:
            return "flag"
        sort = str(column.get("sort", "")).lower()
        if sort in ("int", "integer", "number", "float", "double", "decimal"):
            return "number"
        if sort in ("flag", "bool", "boolean", "checkbox"):
            return "flag"
        return "text"

    @staticmethod
    def _guess_type(items, field):
        for row in items[:20]:
            value = row.get(field)
            if value is None or value == "":
                continue
            return "number" if isinstance(value, (int, float)) and not isinstance(value, bool) else "text"
        return "text"

    @staticmethod
    def _default_search_fields(columns, items):
        fields = [col["id"] for col in columns if col["type"] == "text"]
        if fields:
            return fields
        if not items:
            return []
        return [key for key, value in items[0].items() if isinstance(value, str)]

    @staticmethod
    def _normalize_filter(filter_spec):
        if not filter_spec:
            return None
        field = filter_spec.get("id") or filter_spec.get("field")
        if not field:
            return None
        return {
            "id": field,
            "header": filter_spec.get("header") or filter_spec.get("label") or field,
            "steps": filter_spec.get("steps") or [0],
            "default": filter_spec.get("default", 0),
        }

    @staticmethod
    def _normalize_detail_fields(detail_fields, items):
        if not detail_fields:
            keys = list(items[0].keys()) if items else []
            return [{"id": key, "header": key} for key in keys]
        normalized = []
        for field in detail_fields:
            if isinstance(field, str):
                normalized.append({"id": field, "header": field})
            else:
                field_id = field.get("id") or field.get("field")
                normalized.append({
                    "id": field_id,
                    "header": field.get("header") or field.get("label") or field_id,
                })
        return normalized

    def _datatable_reload(self, state: Dict[str, Any], page_size: int):
        view = self._apply_view(state)
        state["view"] = view
        state["total"] = len(view)
        state["offset"] = min(state["offset"], max(0, state["total"] - 1))
        state["rows"] = view[state["offset"]:state["offset"] + page_size]
        state["cursor"] = min(state["cursor"], max(0, len(state["rows"]) - 1))
        state["dirty"] = False

    def _apply_view(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        query = self._normalize(state["query"])
        search_fields = state["search_fields"]
        filter_spec = state["filter_spec"]
        flag_fields = [col["id"] for col in state["columns"] if col["type"] == "flag"]
        view = []
        for row in state["items"]:
            if query and not self._row_matches(row, query, search_fields):
                continue
            if filter_spec and not self._passes_filter(row, filter_spec, state["filter_value"]):
                continue
            if state["only_flags"] and flag_fields and not any(self._truthy(row.get(f)) for f in flag_fields):
                continue
            view.append(row)
        return self._sort_rows(view, state)

    def _sort_rows(self, view, state):
        if not state["columns"]:
            return view
        column = state["columns"][state["sort_index"] % len(state["columns"])]
        field = column["id"]
        is_number = column["type"] == "number"

        def has_value(row):
            return self._truthy(row.get(field))

        present = [row for row in view if has_value(row)]
        missing = [row for row in view if not has_value(row)]

        def key(row):
            value = row.get(field)
            if is_number:
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return 0.0
            return self._normalize(value)

        present.sort(key=key, reverse=state["sort_desc"])
        return present + missing

    def _row_matches(self, row, query, search_fields):
        for field in search_fields:
            if query in self._normalize(row.get(field)):
                return True
        return False

    @staticmethod
    def _passes_filter(row, filter_spec, minimum):
        if not minimum:
            return True
        try:
            return float(row.get(filter_spec["id"])) >= float(minimum)
        except (TypeError, ValueError):
            return False

    @staticmethod
    def _truthy(value):
        return value is not None and value != "" and value != 0 and value is not False

    @staticmethod
    def _normalize(value):
        text = "" if value is None else str(value)
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        return text.lower()

    def _run_datatable(self, config, state, title):
        locale.setlocale(locale.LC_ALL, "")
        screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        screen.keypad(True)
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        curses.start_color()
        try:
            curses.use_default_colors()
        except curses.error:
            pass
        self._init_datatable_colors()
        self.manager.initialized = True
        self.manager.original_screen = screen
        try:
            return self._datatable_loop(state, title)
        finally:
            curses.nocbreak()
            screen.keypad(False)
            curses.echo()
            curses.endwin()
            self.manager.initialized = False

    def _datatable_loop(self, state, title):
        while True:
            height, width = self.manager.original_screen.getmaxyx()
            window = curses.newwin(height, width, 0, 0)
            window.keypad(True)
            page_size = max(1, height - 7 - (1 if state["show_header"] else 0))
            if state["dirty"]:
                self._datatable_reload(state, page_size)
            self._draw_datatable(window, state, title, page_size)
            key = window.getch()
            del window
            if key == curses.KEY_RESIZE:
                state["dirty"] = True
                continue
            action = self._datatable_handle_key(key, state, page_size)
            if action == "quit":
                break
            if action == "detail" and state["rows"]:
                self._open_detail(state, title)
            elif action == "reload":
                state["dirty"] = True
        return {"status": "ok", "selected": self._selected_rows(state), "query": state["query"]}

    def _selected_rows(self, state):
        if state.get("select_mode") == "multiselect":
            marked = state.get("marked", {})
            selected = [row for row in state.get("view", []) if self._row_key(row) in marked]
            if not selected and state["rows"]:
                selected = [state["rows"][state["cursor"]]]
            return selected
        return state["rows"][state["cursor"]] if state["rows"] else None

    def _datatable_handle_key(self, key, state, page_size):
        if state["search_mode"]:
            return self._datatable_search_key(key, state)
        if state.get("header_focus"):
            return self._datatable_header_key(key, state)
        if key in (ord("q"), ord("Q")):
            return "quit"
        if key in (ord("h"), ord("H")):
            self._datatable_enter_header(state)
            return None
        if key in (curses.KEY_UP, ord("k")):
            if key == curses.KEY_UP and state["cursor"] == 0 and state["offset"] == 0 and state["show_header"]:
                self._datatable_enter_header(state)
            else:
                self._datatable_move(state, -1)
        elif key in (curses.KEY_DOWN, ord("j")):
            self._datatable_move(state, 1)
        elif key == curses.KEY_PPAGE:
            self._datatable_page(state, -page_size)
        elif key == curses.KEY_NPAGE:
            self._datatable_page(state, page_size)
        elif key == curses.KEY_HOME:
            state["cursor"] = 0
        elif key == curses.KEY_END:
            state["cursor"] = max(0, len(state["rows"]) - 1)
        elif key in (10, 13, curses.KEY_ENTER):
            return "detail"
        elif key == ord("/"):
            state["search_mode"] = True
        elif key in (ord("f"), ord("F")):
            self._datatable_cycle_filter(state)
            return "reload"
        elif key in (ord("l"), ord("L")):
            state["only_flags"] = not state["only_flags"]
            state["offset"] = 0
            state["cursor"] = 0
            return "reload"
        elif key in (ord("s"), ord("S")):
            self._datatable_cycle_sort(state)
            return "reload"
        elif key in (ord("o"), ord("O")):
            self._datatable_toggle_sort(state)
            return "reload"
        elif key == ord(" "):
            self._datatable_toggle_mark(state)
        elif key in (ord("r"), ord("R")):
            return "reload"
        return None

    def _datatable_toggle_mark(self, state):
        if state.get("select_mode") != "multiselect" or not state["rows"]:
            return
        key = self._row_key(state["rows"][state["cursor"]])
        marked = state["marked"]
        if key in marked:
            del marked[key]
        else:
            marked[key] = True

    def _datatable_search_key(self, key, state):
        if key in (10, 13, curses.KEY_ENTER):
            state["search_mode"] = False
        elif key == 27:
            state["query"] = ""
            state["search_mode"] = False
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            state["query"] = state["query"][:-1]
        elif 32 <= key < 127:
            state["query"] += chr(key)
        else:
            return None
        state["offset"] = 0
        state["cursor"] = 0
        return "reload"

    @staticmethod
    def _datatable_move(state, delta):
        page = len(state["rows"])
        if page == 0:
            return
        target = state["cursor"] + delta
        if target < 0:
            if state["offset"] > 0:
                state["offset"] -= 1
                state["dirty"] = True
            state["cursor"] = 0
        elif target >= page:
            if state["offset"] + page < state["total"]:
                state["offset"] += 1
                state["dirty"] = True
            state["cursor"] = page - 1
        else:
            state["cursor"] = target

    @staticmethod
    def _datatable_page(state, delta):
        max_offset = max(0, state["total"] - 1)
        state["offset"] = max(0, min(state["offset"] + delta, max_offset))
        state["cursor"] = 0
        state["dirty"] = True

    @staticmethod
    def _datatable_cycle_filter(state):
        spec = state.get("filter_spec")
        if not spec:
            return
        steps = spec.get("steps") or [0]
        try:
            index = steps.index(state["filter_value"])
        except ValueError:
            index = 0
        state["filter_value"] = float(steps[(index + 1) % len(steps)])
        state["offset"] = 0
        state["cursor"] = 0

    @staticmethod
    def _sortable_indices(columns):
        return [i for i, col in enumerate(columns) if col.get("sortable") and col["type"] != "flag"]

    @staticmethod
    def _datatable_cycle_sort(state):
        columns = state["columns"]
        sortable = NcursesPlugin._sortable_indices(columns)
        if not sortable:
            return
        try:
            position = sortable.index(state["sort_index"])
        except ValueError:
            position = -1
        state["sort_index"] = sortable[(position + 1) % len(sortable)]
        state["sort_desc"] = columns[state["sort_index"]]["type"] == "number"
        state["offset"] = 0
        state["cursor"] = 0

    @staticmethod
    def _datatable_sort_by(state, index):
        if index == state["sort_index"]:
            state["sort_desc"] = not state["sort_desc"]
        else:
            state["sort_index"] = index
            state["sort_desc"] = state["columns"][index]["type"] == "number"
        state["offset"] = 0
        state["cursor"] = 0
        state["dirty"] = True

    def _datatable_enter_header(self, state):
        sortable = self._sortable_indices(state["columns"])
        if not state["show_header"] or not sortable:
            return
        state["header_focus"] = True
        if state["header_cursor"] not in sortable:
            state["header_cursor"] = sortable[0]

    def _datatable_header_key(self, key, state):
        sortable = self._sortable_indices(state["columns"])
        if not sortable:
            state["header_focus"] = False
            return None
        if key in (27, curses.KEY_DOWN):
            state["header_focus"] = False
            return None
        if key in (ord("q"), ord("Q")):
            return "quit"
        position = sortable.index(state["header_cursor"]) if state["header_cursor"] in sortable else 0
        if key in (curses.KEY_LEFT, ord("h")):
            state["header_cursor"] = sortable[(position - 1) % len(sortable)]
        elif key in (curses.KEY_RIGHT, ord("l")):
            state["header_cursor"] = sortable[(position + 1) % len(sortable)]
        elif key in (10, 13, curses.KEY_ENTER, ord(" ")):
            self._datatable_sort_by(state, state["header_cursor"])
        return None

    @staticmethod
    def _datatable_toggle_sort(state):
        state["sort_desc"] = not state["sort_desc"]
        state["offset"] = 0
        state["cursor"] = 0

    @staticmethod
    def _datatable_sort_label(state):
        if not state["columns"]:
            return "-"
        column = state["columns"][state["sort_index"] % len(state["columns"])]
        return f"{column['header']} {'v' if state['sort_desc'] else '^'}"

    def _draw_datatable(self, window, state, title, page_size):
        window.erase()
        height, width = window.getmaxyx()
        window.box()
        self._safe_addstr(window, 0, 2, f" {title} ", curses.color_pair(6), width - 4)
        self._draw_datatable_header(window, state, width)
        widths = self._column_widths(state, width - 2)
        first_row = 5 if state["show_header"] else 4
        if state["show_header"]:
            self._draw_column_header(window, state, widths)
        self._draw_datatable_rows(window, state, page_size, widths, first_row)
        self._draw_datatable_footer(window, state, height, width)
        window.refresh()

    def _draw_datatable_header(self, window, state, width):
        cursor = "_" if state["search_mode"] else ""
        search_attr = curses.color_pair(4) if state["search_mode"] else curses.color_pair(1)
        self._safe_addstr(window, 1, 1, f"Buscar: {state['query']}{cursor}", search_attr, width - 2)
        parts = []
        spec = state.get("filter_spec")
        if spec:
            parts.append(f"{spec.get('header', spec['id'])} >= {state['filter_value']:g}")
        if any(col["type"] == "flag" for col in state["columns"]):
            parts.append(f"Flags: {'si' if state['only_flags'] else 'no'}")
        parts.append(f"Orden: {self._datatable_sort_label(state)}")
        if state.get("select_mode") == "multiselect":
            parts.append(f"Marcados: {len(state.get('marked', {}))}")
        parts.append(f"{state['total']} filas")
        self._safe_addstr(window, 2, 1, "   ".join(parts), curses.color_pair(5), width - 2)
        self._safe_addstr(window, 3, 1, "-" * (width - 2), curses.color_pair(1), width - 2)

    def _column_widths(self, state, available):
        columns = state["columns"]
        if not columns:
            return []
        widths = []
        for column in columns:
            if column.get("width"):
                widths.append(int(column["width"]))
            elif column["type"] == "flag":
                widths.append(3)
            else:
                sample = max((len(self._cell_text(row, column)) for row in state["rows"][:50]), default=0)
                widths.append(max(len(column["header"]), min(sample, 40)))
        overhead = 2 + max(0, len(columns) - 1)
        budget = max(1, available - overhead)
        while sum(widths) > budget:
            index = max(
                range(len(columns)),
                key=lambda i: widths[i] if columns[i]["type"] != "flag" else -1,
            )
            if widths[index] <= 3:
                break
            widths[index] -= 1
        expandable = [i for i, column in enumerate(columns) if column.get("fillspace")]
        remaining = budget - sum(widths)
        if remaining > 0 and expandable:
            share = remaining // len(expandable)
            for index in expandable:
                widths[index] += share
            widths[expandable[0]] += remaining - share * len(expandable)
        return widths

    def _draw_column_header(self, window, state, widths):
        x = 3
        sort_index = state["sort_index"]
        focus = state.get("header_focus")
        header_cursor = state.get("header_cursor")
        for index, (column, width) in enumerate(zip(state["columns"], widths)):
            text = column["header"]
            if index == sort_index:
                text = f"{text} {'v' if state['sort_desc'] else '^'}"
            text = text[:width]
            text = text.rjust(width) if self._align_right(column) else text.ljust(width)
            attr = curses.color_pair(2) if (focus and index == header_cursor) else curses.color_pair(5)
            self._safe_addstr(window, 4, x, text, attr, width)
            x += width + 1

    def _draw_datatable_rows(self, window, state, page_size, widths, first_row):
        for index, row in enumerate(state["rows"][:page_size]):
            self._draw_datatable_row(window, state, row, first_row + index, widths, index == state["cursor"])

    def _draw_datatable_row(self, window, state, row, y, widths, selected):
        row_attr = curses.color_pair(2) if selected else curses.color_pair(1)
        marked = state.get("select_mode") == "multiselect" and self._row_key(row) in state.get("marked", {})
        marker = ">" if selected else ("+" if marked else " ")
        self._safe_addstr(window, y, 1, marker, row_attr, 1)
        x = 3
        for column, width in zip(state["columns"], widths):
            text = self._cell_text(row, column)[:width]
            text = text.rjust(width) if self._align_right(column) else text.ljust(width)
            if column["type"] == "flag":
                available = self._truthy(row.get(column["id"]))
                attr = row_attr if selected else (
                    curses.color_pair(3) if available else curses.color_pair(1)
                )
            else:
                attr = row_attr
            self._safe_addstr(window, y, x, text, attr, width)
            x += width + 1

    def _draw_datatable_footer(self, window, state, height, width):
        if state.get("header_focus"):
            keys = "Cabecera: flechas/h-l mover  Enter ordenar  Esc/abajo volver  q salir"
        else:
            keys = "Flechas/Enter detalle  /buscar  s orden  o dir"
            if state["show_header"] and self._sortable_indices(state["columns"]):
                keys += "  h cabecera"
            if state.get("filter_spec"):
                keys += "  f filtro"
            if any(column["type"] == "flag" for column in state["columns"]):
                keys += "  l flags"
            if state.get("select_mode") == "multiselect":
                keys += "  espacio marcar"
            keys += "  q salir"
        self._safe_addstr(window, height - 2, 1, keys, curses.color_pair(1), width - 2)

    def _cell_text(self, row, column):
        value = row.get(column["id"])
        if column["type"] == "flag":
            return "[X]" if self._truthy(value) else "[ ]"
        template = column.get("template")
        if template:
            return self._apply_template(template, row)
        if value is None:
            return ""
        if column["type"] == "number" and column.get("format"):
            try:
                return column["format"] % float(value)
            except (TypeError, ValueError):
                return str(value)
        return str(value)

    @staticmethod
    def _apply_template(template, row):
        values = {key: ("" if value is None else value) for key, value in row.items()}
        try:
            return template.format_map(defaultdict(str, values))
        except (KeyError, ValueError, IndexError):
            return template

    @staticmethod
    def _row_key(row):
        if isinstance(row, dict) and row.get("id") is not None:
            return row["id"]
        return id(row)

    @staticmethod
    def _align_right(column):
        if column.get("align"):
            return column["align"] == "right"
        return column["type"] == "number"

    def _open_detail(self, state, title):
        if not state["rows"]:
            return
        row = state["rows"][state["cursor"]]
        first = state["detail_fields"][0] if state["detail_fields"] else None
        heading = str(row.get(first["id"])) if first else title
        self._show_overlay(f" {heading} ", self._detail_lines(row, state["detail_fields"]))

    @staticmethod
    def _detail_lines(row, detail_fields):
        lines = []
        for field in detail_fields:
            value = row.get(field["id"])
            if value is None or value == "":
                continue
            chunks = str(value).splitlines() or [""]
            for i, chunk in enumerate(chunks):
                prefix = f"{field['header']}: " if i == 0 else " " * (len(field["header"]) + 2)
                lines.append(prefix + chunk)
        return lines

    @staticmethod
    def _wrap_lines(lines, width):
        if width <= 1:
            return lines
        wrapped = []
        for line in lines:
            if len(line) <= width:
                wrapped.append(line)
            else:
                wrapped.extend(line[i:i + width] for i in range(0, len(line), width))
        return wrapped

    def _show_overlay(self, title, lines):
        parent = self.manager.original_screen
        height, width = parent.getmaxyx()
        win_w = max(20, min(width - 2, 100))
        lines = self._wrap_lines(lines, win_w - 2)
        win_h = max(5, min(height - 2, len(lines) + 2))
        win_y = max(0, (height - win_h) // 2)
        win_x = max(0, (width - win_w) // 2)
        overlay = curses.newwin(win_h, win_w, win_y, win_x)
        overlay.keypad(True)
        top, body_h = 0, win_h - 2
        while True:
            self._draw_overlay(overlay, title, lines, top, win_h, win_w)
            key = overlay.getch()
            if key in (curses.KEY_UP, ord("k")):
                top = max(0, top - 1)
            elif key in (curses.KEY_DOWN, ord("j")):
                top = min(max(0, len(lines) - body_h), top + 1)
            elif key == curses.KEY_PPAGE:
                top = max(0, top - body_h)
            elif key == curses.KEY_NPAGE:
                top = min(max(0, len(lines) - body_h), top + body_h)
            else:
                break
        del overlay

    def _draw_overlay(self, overlay, title, lines, top, win_h, win_w):
        overlay.erase()
        overlay.box()
        self._safe_addstr(overlay, 0, 2, title, curses.color_pair(5), win_w - 4)
        body_h = win_h - 2
        for i in range(body_h):
            index = top + i
            if index >= len(lines):
                break
            self._safe_addstr(overlay, i + 1, 1, lines[index], curses.color_pair(1), win_w - 2)
        if len(lines) > body_h:
            pct = int(100 * (top + body_h) / len(lines))
            self._safe_addstr(overlay, win_h - 1, max(1, win_w - 6), f"{pct:3d}%", curses.color_pair(5), 5)
        overlay.refresh()

    @staticmethod
    def _init_datatable_colors():
        curses.init_pair(1, curses.COLOR_WHITE, -1)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(3, curses.COLOR_GREEN, -1)
        curses.init_pair(4, curses.COLOR_YELLOW, -1)
        curses.init_pair(5, curses.COLOR_CYAN, -1)
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)

    @staticmethod
    def _safe_addstr(window, y, x, text, attr=0, max_width=None):
        try:
            if max_width is not None:
                text = text[:max_width]
            window.addstr(y, x, text, attr)
        except curses.error:
            pass

    # Métodos auxiliares para comandos no implementados completamente
    def _resize_window(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "resize_window"}
    
    def _move_window(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "move_window"}
    
    def _draw_line(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "draw_line"}
    
    def _fill_area(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "fill_area"}
    
    def _clear_area(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "clear_area"}
    
    def _set_color(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "set_color"}
    
    def _set_attributes(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "set_attributes"}
    
    def _create_color_pair(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "create_color_pair"}
    
    def _get_choice(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "get_choice"}
    
    def _enable_mouse(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "enable_mouse"}
    
    def _get_mouse_event(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "get_mouse_event"}
    
    def _create_text_field(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "create_text_field"}
    
    def _create_menu(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "create_menu"}
    
    def _create_progress_bar(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "create_progress_bar"}
    
    def _create_table(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "create_table"}
    
    def _create_flexbox(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "create_flexbox"}
    
    def _position_widget(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "position_widget"}
    
    def _center_widget(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "center_widget"}
    
    def _align_widgets(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "align_widgets"}
    
    def _on_mouse_click(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "on_mouse_click"}
    
    def _on_window_resize(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "on_window_resize"}
    
    def _trigger_event(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "trigger_event"}
    
    def _create_overlay(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "create_overlay"}
    
    def _create_dialog(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "not_implemented", "command": "create_dialog"}