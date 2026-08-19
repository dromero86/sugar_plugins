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
import re

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
            "create_dialog": self._create_dialog
        }
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """
        Execute a ncurses command.
        
        Args:
            command: The ncurses command to execute
            config: Configuration dictionary for the command
            
        Returns:
            Result of the ncurses operation
        """
        Output.Console(self.plugin_name, f"Executing ncurses command: {command}")
        
        if command not in self.commands:
            raise NcursesError(f"Comando no reconocido: {command}")
        
        try:
            # Interpolate variables in config
            interpolated_config = self.interpolate_variables(config)
            
            # Execute the command
            result = self.commands[command](interpolated_config)
            
            # Store result in context if specified
            result_key = config.get("result")
            if result_key and self.context:
                self.set_variable(result_key, result)
            
            return result
            
        except Exception as e:
            Output.Console(self.plugin_name, f"Error ejecutando {command}: {str(e)}")
            raise NcursesError(f"Error ejecutando {command}: {str(e)}")
    
    def get_available_commands(self) -> List[str]:
        """
        Return a list of available commands for this plugin.
        
        Returns:
            List of command names that this plugin supports
        """
        return list(self.commands.keys())
    
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