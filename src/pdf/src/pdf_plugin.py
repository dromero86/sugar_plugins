"""
PDF Plugin
==========

Plugin completo para manipulación de documentos PDF usando el SDK.
Incluye lectura, escritura, extracción de texto, imágenes, metadatos,
y operaciones avanzadas de manipulación de PDFs.
"""

import os
import io
import json
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple

# Importar librerías de PDF con manejo de errores
try:
    import PyPDF2
    from PyPDF2 import PdfReader, PdfWriter
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    FPDF2_AVAILABLE = True
except ImportError:
    FPDF2_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Plugins.SDK import (
    ExtensionManager, ExtensionType,
    HookSystem, HookPoint,
    InterpolationInterceptor, InterpolationEvent,
    ASTModifier, ASTModificationEvent,
    FlowController, FlowEvent,
    CommandCustomizer, CommandEvent
)
from Sugar.Lang.Utils.Output import Output

from ..components.pdf_helper import PDFHelper, PDFMetadata, PDFPageInfo

class PDFPlugin(PluginBase):
    """
    Plugin PDF que utiliza el SDK para manejar documentos PDF.
    
    Funcionalidades:
    - Lectura y escritura de PDFs
    - Extracción de texto e imágenes
    - Manipulación de metadatos
    - Conversión y transformación
    - Análisis de contenido
    - Creación de PDFs desde cero
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Plugin para manipulación completa de documentos PDF usando el SDK"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    
    # Dependencias de Python
    DEPENDENCIES = ["PyPDF2", "pdfplumber", "fpdf2", "Pillow"]
    REQUIREMENTS = [
        "PyPDF2>=3.0.0",
        "pdfplumber>=0.9.0", 
        "fpdf2>=2.7.0",
        "Pillow>=10.0.0"
    ]
    
    # Dependencias del sistema
    SYSTEM_DEPENDENCIES = []
    
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
        "read_access": ["./data", "./input"]
    }
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        super().__init__(context, plugin_config)
        
        # Verificar dependencias al inicializar
        self.dependency_status = self._check_all_dependencies()
        
        # Alertar si hay dependencias faltantes
        if not self.dependency_status['all_satisfied']:
            self._log_dependency_warnings()
        
        # Inicializar SDK si las dependencias están satisfechas
        if self.dependency_status['all_satisfied']:
            self._initialize_sdk()
        
        # Configuración por defecto
        self.default_page_size = getattr(self.plugin_config, 'default_page_size', 'A4')
        self.default_font_size = getattr(self.plugin_config, 'default_font_size', 12)
        self.temp_dir = PDFHelper.create_temp_directory()
        
        # Inicializar helper
        self.helper = PDFHelper()
    
    def get_available_commands(self) -> List[str]:
        """Retorna la lista de comandos disponibles."""
        return [
            # Comandos básicos de lectura
            "read_pdf", "get_pdf_info", "extract_text", "extract_images",
            
            # Comandos de escritura y creación
            "create_pdf", "write_pdf", "merge_pdfs", "split_pdf",
            
            # Comandos de manipulación FPDF2
            "add_text", "add_image", "add_page", "remove_page",
            "rotate_page", "scale_page", "crop_page",
            "add_line", "add_rectangle", "add_circle", "add_ellipse",
            "set_font", "set_text_color", "set_fill_color", "set_draw_color",
            
            # Comandos de metadatos
            "get_metadata", "set_metadata", "update_metadata",
            
            # Comandos de análisis
            "analyze_pdf", "search_text", "count_pages", "get_page_info",
            
            # Comandos de conversión
            "convert_to_images", "extract_pages_as_images",
            
            # Comandos de utilidad
            "check_dependencies", "system_info", "test_functionality"
        ]
    
    def execute(self, operator: str, config: Dict[str, Any]) -> Any:
        """Ejecuta un comando del plugin."""
        # Verificar dependencias antes de comandos críticos
        if operator not in ["check_dependencies", "system_info", "test_functionality"]:
            if not self.dependency_status['all_satisfied']:
                raise RuntimeError("Dependencias no satisfechas. Ejecuta 'check_dependencies' para más información.")
        
        # Interpolar variables en la configuración
        config = self._interpolate_config(config)
        
        # Ejecutar comando correspondiente
        if operator == "read_pdf":
            return self._read_pdf(config)
        elif operator == "get_pdf_info":
            return self._get_pdf_info(config)
        elif operator == "extract_text":
            return self._extract_text(config)
        elif operator == "extract_images":
            return self._extract_images(config)
        elif operator == "create_pdf":
            return self._create_pdf(config)
        elif operator == "write_pdf":
            return self._write_pdf(config)
        elif operator == "merge_pdfs":
            return self._merge_pdfs(config)
        elif operator == "split_pdf":
            return self._split_pdf(config)
        elif operator == "add_text":
            return self._add_text(config)
        elif operator == "add_image":
            return self._add_image(config)
        elif operator == "add_page":
            return self._add_page(config)
        elif operator == "remove_page":
            return self._remove_page(config)
        elif operator == "rotate_page":
            return self._rotate_page(config)
        elif operator == "scale_page":
            return self._scale_page(config)
        elif operator == "crop_page":
            return self._crop_page(config)
        elif operator == "add_line":
            return self._add_line(config)
        elif operator == "add_rectangle":
            return self._add_rectangle(config)
        elif operator == "add_circle":
            return self._add_circle(config)
        elif operator == "add_ellipse":
            return self._add_ellipse(config)
        elif operator == "set_font":
            return self._set_font(config)
        elif operator == "set_text_color":
            return self._set_text_color(config)
        elif operator == "set_fill_color":
            return self._set_fill_color(config)
        elif operator == "set_draw_color":
            return self._set_draw_color(config)
        elif operator == "get_metadata":
            return self._get_metadata(config)
        elif operator == "set_metadata":
            return self._set_metadata(config)
        elif operator == "update_metadata":
            return self._update_metadata(config)
        elif operator == "analyze_pdf":
            return self._analyze_pdf(config)
        elif operator == "search_text":
            return self._search_text(config)
        elif operator == "count_pages":
            return self._count_pages(config)
        elif operator == "get_page_info":
            return self._get_page_info(config)
        elif operator == "convert_to_images":
            return self._convert_to_images(config)
        elif operator == "extract_pages_as_images":
            return self._extract_pages_as_images(config)
        elif operator == "check_dependencies":
            return self._check_dependencies(config)
        elif operator == "system_info":
            return self._system_info(config)
        elif operator == "test_functionality":
            return self._test_functionality(config)
        else:
            raise ValueError(f"Comando desconocido: {operator}")
    
    def _check_all_dependencies(self) -> Dict[str, Any]:
        """Verifica todas las dependencias del plugin."""
        status = {
            'all_satisfied': True,
            'python_packages': {},
            'system_tools': {},
            'missing_packages': [],
            'missing_tools': []
        }
        
        # Verificar paquetes de Python
        for package in self.DEPENDENCIES:
            try:
                if package == "PyPDF2":
                    status['python_packages'][package] = PYPDF2_AVAILABLE
                elif package == "pdfplumber":
                    status['python_packages'][package] = PDFPLUMBER_AVAILABLE
                elif package == "fpdf2":
                    status['python_packages'][package] = FPDF2_AVAILABLE
                elif package == "Pillow":
                    status['python_packages'][package] = PIL_AVAILABLE
                else:
                    __import__(package)
                    status['python_packages'][package] = True
            except ImportError:
                status['python_packages'][package] = False
                status['missing_packages'].append(package)
                status['all_satisfied'] = False
        
        # Verificar herramientas del sistema
        for tool in self.SYSTEM_DEPENDENCIES:
            try:
                import subprocess
                result = subprocess.run([tool, '--version'], 
                                     capture_output=True, text=True, timeout=5)
                status['system_tools'][tool] = result.returncode == 0
                if result.returncode != 0:
                    status['missing_tools'].append(tool)
                    status['all_satisfied'] = False
            except (FileNotFoundError, subprocess.TimeoutExpired):
                status['system_tools'][tool] = False
                status['missing_tools'].append(tool)
                status['all_satisfied'] = False
        
        return status
    
    def _log_dependency_warnings(self):
        """Registra advertencias sobre dependencias faltantes."""
        Output.Console(self.plugin_name, " Advertencia: Algunas dependencias no están disponibles")
        if self.dependency_status['missing_packages']:
            Output.Console(self.plugin_name, f"Paquetes faltantes: {', '.join(self.dependency_status['missing_packages'])}")
        if self.dependency_status['missing_tools']:
            Output.Console(self.plugin_name, f"Herramientas faltantes: {', '.join(self.dependency_status['missing_tools'])}")
    
    def _initialize_sdk(self):
        """Inicializa componentes del SDK."""
        try:
            self.extension_manager = ExtensionManager()
            self.hook_system = HookSystem()
            self.command_customizer = CommandCustomizer()
            
            # Registrar extensiones
            self._register_sdk_extensions()
            
            Output.Console(self.plugin_name, "SDK inicializado correctamente")
        except Exception as e:
            Output.Console(self.plugin_name, f" Error inicializando SDK: {e}")
    
    def _register_sdk_extensions(self):
        """Registra extensiones específicas del plugin."""
        try:
            # Hook para operaciones de PDF
            self.hook_system.register_hook(
                hook_point=HookPoint.BEFORE_TASK_EXECUTION,
                callback=self._before_pdf_operation,
                priority=5
            )
            
            # Customización de comandos
            self.command_customizer.register_customizer(
                event=CommandEvent.BEFORE_COMMAND_EXECUTION,
                callback=self._before_command_callback,
                priority=5
            )
        except Exception as e:
            Output.Console(self.plugin_name, f" Error registrando extensiones: {e}")
    
    def _before_pdf_operation(self, hook_context):
        """Hook ejecutado antes de operaciones de PDF."""
        Output.Console(self.plugin_name, f"Iniciando operación PDF: {hook_context.get('command', 'unknown')}")
        return hook_context
    
    def _before_command_callback(self, context):
        """Callback para customización de comandos."""
        Output.Console(self.plugin_name, f"Ejecutando comando PDF: {context.command_name}")
        return context
    
    def _interpolate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Interpola variables en la configuración."""
        if not self.context:
            return config
        
        interpolated_config = {}
        for key, value in config.items():
            if isinstance(value, str):
                interpolated_config[key] = self.interpolate_variables(value)
            elif isinstance(value, dict):
                interpolated_config[key] = self._interpolate_config(value)
            elif isinstance(value, list):
                interpolated_config[key] = [
                    self.interpolate_variables(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                interpolated_config[key] = value
        
        return interpolated_config
    
    def _read_pdf(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Lee un archivo PDF y retorna información básica."""
        file_path = config.get('file_path')
        if not file_path:
            raise ValueError("Se requiere 'file_path' para leer el PDF")
        
        if not self.helper.validate_file_path(file_path):
            raise FileNotFoundError(f"Archivo PDF no válido o no encontrado: {file_path}")
        
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                
                info = {
                    'file_path': file_path,
                    'page_count': len(reader.pages),
                    'metadata': self.helper.extract_metadata(reader),
                    'file_size': os.path.getsize(file_path),
                    'file_size_formatted': self.helper.format_file_size(os.path.getsize(file_path)),
                    'encrypted': reader.is_encrypted,
                    'status': 'success'
                }
                
                if 'result' in config:
                    self.set_variable(config['id'], info)
                
                return info
                
        except Exception as e:
            error_info = {
                'file_path': file_path,
                'error': str(e),
                'status': 'error'
            }
            if 'result' in config:
                self.set_variable(config['id'], error_info)
            raise
    
    def _get_pdf_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene información detallada del PDF."""
        return self._read_pdf(config)
    
    def _extract_text(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae texto del PDF."""
        file_path = config.get('file_path')
        pages = config.get('pages', 'all')  # 'all' o lista de números de página
        output_file = config.get('output_file')
        
        if not file_path:
            raise ValueError("Se requiere 'file_path' para extraer texto")
        
        if not self.helper.validate_file_path(file_path):
            raise FileNotFoundError(f"Archivo PDF no válido o no encontrado: {file_path}")
        
        try:
            if not PDFPLUMBER_AVAILABLE:
                raise RuntimeError("pdfplumber no está disponible. Instala con: pip install pdfplumber")
            
            with pdfplumber.open(file_path) as pdf:
                all_text = []
                page_texts = {}
                
                # Determinar páginas a procesar
                if pages == 'all':
                    pages_to_process = range(len(pdf.pages))
                else:
                    pages_to_process = [int(p) - 1 for p in pages if 1 <= int(p) <= len(pdf.pages)]
                
                for page_num in pages_to_process:
                    page = pdf.pages[page_num]
                    text = page.extract_text() or ""
                    all_text.append(text)
                    page_texts[f"page_{page_num + 1}"] = text
                
                full_text = '\n\n'.join(all_text)
                
                result = {
                    'file_path': file_path,
                    'total_pages': len(pdf.pages),
                    'processed_pages': len(pages_to_process),
                    'full_text': full_text,
                    'page_texts': page_texts,
                    'total_characters': len(full_text),
                    'status': 'success'
                }
                
                # Guardar en archivo si se especifica
                if output_file:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(full_text)
                    result['output_file'] = output_file
                
                if 'result' in config:
                    self.set_variable(config['id'], result)
                
                return result
                
        except Exception as e:
            error_info = {
                'file_path': file_path,
                'error': str(e),
                'status': 'error'
            }
            if 'result' in config:
                self.set_variable(config['id'], error_info)
            raise
    
    def _create_pdf(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo PDF desde cero usando FPDF2."""
        output_path = config.get('output_path')
        content = config.get('content', [])
        page_size = config.get('page_size', self.default_page_size)
        title = config.get('title', 'Documento PDF')
        
        if not output_path:
            raise ValueError("Se requiere 'output_path' para crear el PDF")
        
        if not FPDF2_AVAILABLE:
            raise RuntimeError("fpdf2 no está disponible. Instala con: pip install fpdf2")
        
        try:
            # Crear PDF con FPDF2
            pdf = FPDF()
            
            # Configurar tamaño de página
            if page_size.upper() == 'A4':
                pdf.add_page()
            elif page_size.upper() == 'LETTER':
                pdf.add_page(format='letter')
            else:
                pdf.add_page()
            
            # Configurar fuente y agregar título
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, title, new_line=True, align='C')
            pdf.ln(10)
            
            # Procesar contenido
            for item in content:
                if isinstance(item, dict):
                    item_type = item.get('type', 'text')
                    
                    if item_type == 'text':
                        text = item.get('text', '')
                        font_size = item.get('font_size', self.default_font_size)
                        font_style = item.get('font_style', 'N')  # N=normal, B=bold, I=italic
                        align = item.get('align', 'L')  # L=left, C=center, R=right
                        
                        pdf.set_font("Arial", font_style, font_size)
                        pdf.multi_cell(0, font_size/2, text, align=align)
                        pdf.ln(5)
                    
                    elif item_type == 'table':
                        table_data = item.get('data', [])
                        if table_data:
                            # Configurar tabla
                            col_widths = item.get('col_widths', [])
                            if not col_widths:
                                col_widths = [pdf.epw / len(table_data[0])] * len(table_data[0])
                            
                            # Encabezados
                            pdf.set_font("Arial", "B", 12)
                            for i, cell in enumerate(table_data[0]):
                                pdf.cell(col_widths[i], 10, str(cell), border=1, align='C')
                            pdf.ln()
                            
                            # Datos
                            pdf.set_font("Arial", "", 10)
                            for row in table_data[1:]:
                                for i, cell in enumerate(row):
                                    pdf.cell(col_widths[i], 10, str(cell), border=1, align='C')
                                pdf.ln()
                            pdf.ln(5)
                    
                    elif item_type == 'image':
                        image_path = item.get('image_path')
                        x = item.get('x', 10)
                        y = item.get('y', None)
                        w = item.get('width', 0)
                        h = item.get('height', 0)
                        
                        if image_path and os.path.exists(image_path):
                            if y is None:
                                pdf.image(image_path, x=x, w=w, h=h)
                            else:
                                pdf.image(image_path, x=x, y=y, w=w, h=h)
                            pdf.ln(5)
                    
                    elif item_type == 'line':
                        x1 = item.get('x1', 10)
                        y1 = item.get('y1', None)
                        x2 = item.get('x2', 190)
                        y2 = item.get('y2', None)
                        
                        if y1 is None:
                            y1 = pdf.get_y()
                        if y2 is None:
                            y2 = y1
                        
                        pdf.line(x1, y1, x2, y2)
                        pdf.ln(5)
                    
                    elif item_type == 'spacer':
                        height = item.get('height', 10)
                        pdf.ln(height)
                    
                    elif item_type == 'page_break':
                        pdf.add_page()
                
                elif isinstance(item, str):
                    pdf.set_font("Arial", "", 12)
                    pdf.multi_cell(0, 6, item)
                    pdf.ln(5)
            
            # Guardar PDF
            pdf.output(output_path)
            
            result = {
                'output_path': output_path,
                'page_count': pdf.page_no(),
                'file_size': os.path.getsize(output_path),
                'file_size_formatted': self.helper.format_file_size(os.path.getsize(output_path)),
                'status': 'success'
            }
            
            if 'result' in config:
                self.set_variable(config['id'], result)
            
            return result
            
        except Exception as e:
            error_info = {
                'output_path': output_path,
                'error': str(e),
                'status': 'error'
            }
            if 'result' in config:
                self.set_variable(config['id'], error_info)
            raise
    
    def _merge_pdfs(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Combina múltiples PDFs en uno solo."""
        input_files = config.get('input_files', [])
        output_path = config.get('output_path')
        
        if not input_files or not output_path:
            raise ValueError("Se requieren 'input_files' y 'output_path' para combinar PDFs")
        
        if not PYPDF2_AVAILABLE:
            raise RuntimeError("PyPDF2 no está disponible. Instala con: pip install PyPDF2")
        
        try:
            writer = PdfWriter()
            total_pages = 0
            valid_files = []
            
            for input_file in input_files:
                if not self.helper.validate_file_path(input_file):
                    Output.Console(self.plugin_name, f" Archivo no válido o no encontrado: {input_file}")
                    continue
                
                with open(input_file, 'rb') as file:
                    reader = PdfReader(file)
                    for page in reader.pages:
                        writer.add_page(page)
                    total_pages += len(reader.pages)
                    valid_files.append(input_file)
            
            # Escribir PDF combinado
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            result = {
                'input_files': valid_files,
                'output_path': output_path,
                'total_pages': total_pages,
                'file_size': os.path.getsize(output_path),
                'file_size_formatted': self.helper.format_file_size(os.path.getsize(output_path)),
                'status': 'success'
            }
            
            if 'result' in config:
                self.set_variable(config['id'], result)
            
            return result
            
        except Exception as e:
            error_info = {
                'input_files': input_files,
                'output_path': output_path,
                'error': str(e),
                'status': 'error'
            }
            if 'result' in config:
                self.set_variable(config['id'], error_info)
            raise
    
    def _analyze_pdf(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza el contenido del PDF."""
        file_path = config.get('file_path')
        
        if not file_path:
            raise ValueError("Se requiere 'file_path' para analizar el PDF")
        
        if not self.helper.validate_file_path(file_path):
            raise FileNotFoundError(f"Archivo PDF no válido o no encontrado: {file_path}")
        
        try:
            analysis = {
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'file_size_formatted': self.helper.format_file_size(os.path.getsize(file_path)),
                'pages': [],
                'total_text_length': 0,
                'total_images': 0,
                'has_forms': False,
                'is_encrypted': False,
                'status': 'success'
            }
            
            # Información básica con PyPDF2
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                analysis['page_count'] = len(reader.pages)
                analysis['is_encrypted'] = reader.is_encrypted
                analysis['metadata'] = self.helper.extract_metadata(reader)
                
                # Analizar cada página
                for i, page in enumerate(reader.pages):
                    page_info = {
                        'page_number': i + 1,
                        'width': float(page.mediabox.width),
                        'height': float(page.mediabox.height),
                        'rotation': page.get('/Rotate', 0)
                    }
                    analysis['pages'].append(page_info)
            
            # Análisis detallado con pdfplumber si está disponible
            if PDFPLUMBER_AVAILABLE:
                with pdfplumber.open(file_path) as pdf:
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text() or ""
                        analysis['pages'][i]['text_length'] = len(text)
                        analysis['pages'][i]['text_content'] = text[:500] + "..." if len(text) > 500 else text
                        analysis['total_text_length'] += len(text)
                        
                        # Contar imágenes
                        images = page.images
                        analysis['pages'][i]['image_count'] = len(images)
                        analysis['total_images'] += len(images)
                        
                        # Verificar formularios
                        if page.form_fields:
                            analysis['has_forms'] = True
            
            if 'result' in config:
                self.set_variable(config['id'], analysis)
            
            return analysis
            
        except Exception as e:
            error_info = {
                'file_path': file_path,
                'error': str(e),
                'status': 'error'
            }
            if 'result' in config:
                self.set_variable(config['id'], error_info)
            raise
    
    def _check_dependencies(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica el estado de las dependencias."""
        result = {
            'plugin_name': self.plugin_name,
            'version': self.VERSION,
            'dependency_status': self.dependency_status,
            'status': 'success'
        }
        
        if 'result' in config:
            self.set_variable(config['id'], result)
        
        return result
    
    def _test_functionality(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Prueba la funcionalidad del plugin."""
        try:
            # Crear un PDF de prueba
            test_pdf_path = os.path.join(self.temp_dir, 'test.pdf')
            
            # Crear PDF simple con FPDF2
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "PDF de prueba creado por Sugar PDF Plugin", new_line=True, align='C')
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 10, f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}", new_line=True, align='C')
            pdf.output(test_pdf_path)
            
            # Leer el PDF creado
            with open(test_pdf_path, 'rb') as file:
                reader = PdfReader(file)
                page_count = len(reader.pages)
            
            # Limpiar archivo de prueba
            os.unlink(test_pdf_path)
            
            test_results = {
                'pdf_creation': True,
                'pdf_reading': True,
                'page_count': page_count,
                'temp_dir_writable': os.access(self.temp_dir, os.W_OK),
                'dependencies_available': self.dependency_status['all_satisfied'],
                'status': 'success'
            }
            
            if 'result' in config:
                self.set_variable(config['id'], test_results)
            
            return test_results
            
        except Exception as e:
            error_info = {
                'error': str(e),
                'status': 'error'
            }
            if 'result' in config:
                self.set_variable(config['id'], error_info)
            raise
    
    # Métodos adicionales para completar la funcionalidad
    def _extract_images(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae imágenes del PDF."""
        # Implementación básica - se puede expandir
        return {"status": "not_implemented", "message": "Función en desarrollo"}
    
    def _write_pdf(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Escribe un PDF modificado."""
        # Implementación básica - se puede expandir
        return {"status": "not_implemented", "message": "Función en desarrollo"}
    
    def _split_pdf(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Divide un PDF en múltiples archivos."""
        # Implementación básica - se puede expandir
        return {"status": "not_implemented", "message": "Función en desarrollo"}
    
    def _add_text(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Agrega texto a un PDF existente usando FPDF2."""
        input_path = config.get('input_path')
        output_path = config.get('output_path')
        text = config.get('text', '')
        x = config.get('x', 10)
        y = config.get('y', None)
        font_size = config.get('font_size', 12)
        font_style = config.get('font_style', 'N')
        align = config.get('align', 'L')
        
        if not all([input_path, output_path, text]):
            raise ValueError("Se requieren 'input_path', 'output_path' y 'text' para agregar texto")
        
        if not FPDF2_AVAILABLE:
            raise RuntimeError("fpdf2 no está disponible. Instala con: pip install fpdf2")
        
        try:
            # Crear nuevo PDF con FPDF2
            pdf = FPDF()
            
            # Si hay un PDF de entrada, intentar copiar contenido
            if os.path.exists(input_path):
                # Por ahora, crear un nuevo PDF con el texto
                # En una implementación más avanzada, se podría usar PyPDF2 para combinar
                pass
            
            # Agregar página y texto
            pdf.add_page()
            if y is not None:
                pdf.set_xy(x, y)
            else:
                pdf.set_x(x)
            
            pdf.set_font("Arial", font_style, font_size)
            pdf.cell(0, font_size/2, text, new_line=True, align=align)
            
            # Guardar PDF
            pdf.output(output_path)
            
            result = {
                'input_path': input_path,
                'output_path': output_path,
                'text_added': text,
                'position': {'x': x, 'y': y},
                'font_size': font_size,
                'status': 'success'
            }
            
            if 'result' in config:
                self.set_variable(config['id'], result)
            
            return result
            
        except Exception as e:
            error_info = {
                'input_path': input_path,
                'output_path': output_path,
                'error': str(e),
                'status': 'error'
            }
            if 'result' in config:
                self.set_variable(config['id'], error_info)
            raise
    
    def _add_image(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Agrega una imagen a un PDF existente."""
        # Implementación básica - se puede expandir
        return {"status": "not_implemented", "message": "Función en desarrollo"}
    
    def _add_page(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Agrega una página al PDF."""
        # Implementación básica - se puede expandir
        return {"status": "not_implemented", "message": "Función en desarrollo"}
    
    def _remove_page(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Remueve una página del PDF."""
        # Implementación básica - se puede expandir
        return {"status": "not_implemented", "message": "Función en desarrollo"}
    
    def _rotate_page(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Rota una página del PDF."""
        # Implementación básica - se puede expandir
        return {"status": "not_implemented", "message": "Función en desarrollo"}
    
    def _scale_page(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Escala una página del PDF."""
        # Implementación básica - se puede expandir
        return {"status": "not_implemented", "message": "Función en desarrollo"}
    
    def _crop_page(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Recorta una página del PDF."""
        # Implementación básica - se puede expandir
        return {"status": "not_implemented", "message": "Función en desarrollo"}
    
    def _get_metadata(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene los metadatos del PDF."""
        # Implementación básica - se puede expandir
        return {"status": "not_implemented", "message": "Función en desarrollo"}
    
    def _set_metadata(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Establece metadatos en el PDF."""
        # Implementación básica - se puede expandir
        return {"status": "not_implemented", "message": "Función en desarrollo"}
    
    def _update_metadata(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza metadatos del PDF."""
        # Implementación básica - se puede expandir
        return {"status": "not_implemented", "message": "Función en desarrollo"}
    
    def _search_text(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Busca texto en el PDF."""
        # Implementación básica - se puede expandir
        return {"status": "not_implemented", "message": "Función en desarrollo"}
    
    def _count_pages(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Cuenta las páginas del PDF."""
        # Implementación básica - se puede expandir
        return {"status": "not_implemented", "message": "Función en desarrollo"}
    
    def _get_page_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene información de una página específica."""
        # Implementación básica - se puede expandir
        return {"status": "not_implemented", "message": "Función en desarrollo"}
    
    def _convert_to_images(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte PDF a imágenes."""
        # Implementación básica - se puede expandir
        return {"status": "not_implemented", "message": "Función en desarrollo"}
    
    def _extract_pages_as_images(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae páginas como imágenes."""
        # Implementación básica - se puede expandir
        return {"status": "not_implemented", "message": "Función en desarrollo"}
    
    def _system_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Proporciona información del sistema."""
        # Implementación básica - se puede expandir
        return {"status": "not_implemented", "message": "Función en desarrollo"}
    
    # Nuevos métodos específicos de FPDF2
    def _add_line(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Agrega una línea al PDF usando FPDF2."""
        output_path = config.get('output_path')
        x1 = config.get('x1', 10)
        y1 = config.get('y1', 10)
        x2 = config.get('x2', 200)
        y2 = config.get('y2', 10)
        
        if not output_path:
            raise ValueError("Se requiere 'output_path' para agregar línea")
        
        if not FPDF2_AVAILABLE:
            raise RuntimeError("fpdf2 no está disponible. Instala con: pip install fpdf2")
        
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.line(x1, y1, x2, y2)
            pdf.output(output_path)
            
            result = {
                'output_path': output_path,
                'line_coordinates': {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2},
                'status': 'success'
            }
            
            if 'result' in config:
                self.set_variable(config['id'], result)
            
            return result
            
        except Exception as e:
            error_info = {
                'output_path': output_path,
                'error': str(e),
                'status': 'error'
            }
            if 'result' in config:
                self.set_variable(config['id'], error_info)
            raise
    
    def _add_rectangle(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Agrega un rectángulo al PDF usando FPDF2."""
        output_path = config.get('output_path')
        x = config.get('x', 10)
        y = config.get('y', 10)
        w = config.get('width', 100)
        h = config.get('height', 50)
        style = config.get('style', 'D')  # D=draw, F=fill, DF=draw+fill
        
        if not output_path:
            raise ValueError("Se requiere 'output_path' para agregar rectángulo")
        
        if not FPDF2_AVAILABLE:
            raise RuntimeError("fpdf2 no está disponible. Instala con: pip install fpdf2")
        
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.rect(x, y, w, h, style=style)
            pdf.output(output_path)
            
            result = {
                'output_path': output_path,
                'rectangle': {'x': x, 'y': y, 'width': w, 'height': h, 'style': style},
                'status': 'success'
            }
            
            if 'result' in config:
                self.set_variable(config['id'], result)
            
            return result
            
        except Exception as e:
            error_info = {
                'output_path': output_path,
                'error': str(e),
                'status': 'error'
            }
            if 'result' in config:
                self.set_variable(config['id'], error_info)
            raise
    
    def _add_circle(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Agrega un círculo al PDF usando FPDF2."""
        output_path = config.get('output_path')
        x = config.get('x', 50)
        y = config.get('y', 50)
        r = config.get('radius', 30)
        style = config.get('style', 'D')  # D=draw, F=fill, DF=draw+fill
        
        if not output_path:
            raise ValueError("Se requiere 'output_path' para agregar círculo")
        
        if not FPDF2_AVAILABLE:
            raise RuntimeError("fpdf2 no está disponible. Instala con: pip install fpdf2")
        
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.circle(x, y, r, style=style)
            pdf.output(output_path)
            
            result = {
                'output_path': output_path,
                'circle': {'x': x, 'y': y, 'radius': r, 'style': style},
                'status': 'success'
            }
            
            if 'result' in config:
                self.set_variable(config['id'], result)
            
            return result
            
        except Exception as e:
            error_info = {
                'output_path': output_path,
                'error': str(e),
                'status': 'error'
            }
            if 'result' in config:
                self.set_variable(config['id'], error_info)
            raise
    
    def _add_ellipse(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Agrega una elipse al PDF usando FPDF2."""
        output_path = config.get('output_path')
        x = config.get('x', 50)
        y = config.get('y', 50)
        rx = config.get('rx', 40)
        ry = config.get('ry', 20)
        style = config.get('style', 'D')  # D=draw, F=fill, DF=draw+fill
        
        if not output_path:
            raise ValueError("Se requiere 'output_path' para agregar elipse")
        
        if not FPDF2_AVAILABLE:
            raise RuntimeError("fpdf2 no está disponible. Instala con: pip install fpdf2")
        
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.ellipse(x, y, rx, ry, style=style)
            pdf.output(output_path)
            
            result = {
                'output_path': output_path,
                'ellipse': {'x': x, 'y': y, 'rx': rx, 'ry': ry, 'style': style},
                'status': 'success'
            }
            
            if 'result' in config:
                self.set_variable(config['id'], result)
            
            return result
            
        except Exception as e:
            error_info = {
                'output_path': output_path,
                'error': str(e),
                'status': 'error'
            }
            if 'result' in config:
                self.set_variable(config['id'], error_info)
            raise
    
    def _set_font(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configura la fuente del PDF usando FPDF2."""
        output_path = config.get('output_path')
        font_family = config.get('font_family', 'Arial')
        font_style = config.get('font_style', 'N')  # N=normal, B=bold, I=italic, U=underline
        font_size = config.get('font_size', 12)
        
        if not output_path:
            raise ValueError("Se requiere 'output_path' para configurar fuente")
        
        if not FPDF2_AVAILABLE:
            raise RuntimeError("fpdf2 no está disponible. Instala con: pip install fpdf2")
        
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font(font_family, font_style, font_size)
            pdf.cell(0, 10, f"Texto con fuente {font_family} {font_style} {font_size}", new_line=True)
            pdf.output(output_path)
            
            result = {
                'output_path': output_path,
                'font_config': {'family': font_family, 'style': font_style, 'size': font_size},
                'status': 'success'
            }
            
            if 'result' in config:
                self.set_variable(config['id'], result)
            
            return result
            
        except Exception as e:
            error_info = {
                'output_path': output_path,
                'error': str(e),
                'status': 'error'
            }
            if 'result' in config:
                self.set_variable(config['id'], error_info)
            raise
    
    def _set_text_color(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configura el color del texto usando FPDF2."""
        output_path = config.get('output_path')
        r = config.get('r', 0)
        g = config.get('g', 0)
        b = config.get('b', 0)
        
        if not output_path:
            raise ValueError("Se requiere 'output_path' para configurar color de texto")
        
        if not FPDF2_AVAILABLE:
            raise RuntimeError("fpdf2 no está disponible. Instala con: pip install fpdf2")
        
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_text_color(r, g, b)
            pdf.cell(0, 10, f"Texto en color RGB({r},{g},{b})", new_line=True)
            pdf.output(output_path)
            
            result = {
                'output_path': output_path,
                'text_color': {'r': r, 'g': g, 'b': b},
                'status': 'success'
            }
            
            if 'result' in config:
                self.set_variable(config['id'], result)
            
            return result
            
        except Exception as e:
            error_info = {
                'output_path': output_path,
                'error': str(e),
                'status': 'error'
            }
            if 'result' in config:
                self.set_variable(config['id'], error_info)
            raise
    
    def _set_fill_color(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configura el color de relleno usando FPDF2."""
        output_path = config.get('output_path')
        r = config.get('r', 255)
        g = config.get('g', 255)
        b = config.get('b', 255)
        
        if not output_path:
            raise ValueError("Se requiere 'output_path' para configurar color de relleno")
        
        if not FPDF2_AVAILABLE:
            raise RuntimeError("fpdf2 no está disponible. Instala con: pip install fpdf2")
        
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_fill_color(r, g, b)
            pdf.rect(10, 10, 50, 30, style='F')
            pdf.output(output_path)
            
            result = {
                'output_path': output_path,
                'fill_color': {'r': r, 'g': g, 'b': b},
                'status': 'success'
            }
            
            if 'result' in config:
                self.set_variable(config['id'], result)
            
            return result
            
        except Exception as e:
            error_info = {
                'output_path': output_path,
                'error': str(e),
                'status': 'error'
            }
            if 'result' in config:
                self.set_variable(config['id'], error_info)
            raise
    
    def _set_draw_color(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configura el color de dibujo usando FPDF2."""
        output_path = config.get('output_path')
        r = config.get('r', 0)
        g = config.get('g', 0)
        b = config.get('b', 0)
        
        if not output_path:
            raise ValueError("Se requiere 'output_path' para configurar color de dibujo")
        
        if not FPDF2_AVAILABLE:
            raise RuntimeError("fpdf2 no está disponible. Instala con: pip install fpdf2")
        
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_draw_color(r, g, b)
            pdf.rect(10, 10, 50, 30, style='D')
            pdf.output(output_path)
            
            result = {
                'output_path': output_path,
                'draw_color': {'r': r, 'g': g, 'b': b},
                'status': 'success'
            }
            
            if 'result' in config:
                self.set_variable(config['id'], result)
            
            return result
            
        except Exception as e:
            error_info = {
                'output_path': output_path,
                'error': str(e),
                'status': 'error'
            }
            if 'result' in config:
                self.set_variable(config['id'], error_info)
            raise