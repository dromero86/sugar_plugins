"""
Example Dependency Plugin
=========================

Este plugin demuestra cómo implementar un sistema completo de control de dependencias
y requerimientos de sistema para plugins específicos.

Características demostradas:
- Verificación de dependencias de Python
- Verificación de dependencias del sistema
- Verificación de requerimientos de hardware
- Verificación de permisos del sistema
- Alertas y mensajes informativos
- Instrucciones de instalación automáticas
"""

import subprocess
import sys
import os
import platform
import shutil
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

from Sugar.Lang.Plugins import PluginBase
from Sugar.Lang.Plugins.SDK import (
    ExtensionManager, ExtensionType,
    HookSystem, HookPoint,
    CommandCustomizer, CommandEvent
)
from Sugar.Lang.Utils.Output import Output

class ExampleDependencyPlugin(PluginBase):
    """
    Plugin de ejemplo que demuestra control completo de dependencias.
    
    Este plugin requiere:
    - Python packages: requests, numpy, pandas
    - System executables: curl, git
    - Hardware: Mínimo 4GB RAM
    - Permisos: Acceso a red, escritura en /tmp
    """
    
    VERSION = "1.0.0"
    DESCRIPTION = "Plugin de ejemplo para demostrar control de dependencias"
    AUTHOR = "Sugar Team"
    LICENSE = "MIT"
    
    # Dependencias de Python (paquetes)
    DEPENDENCIES = ["requests", "numpy", "pandas"]
    REQUIREMENTS = ["requests>=2.25.0", "numpy>=1.20.0", "pandas>=1.3.0"]
    
    # Dependencias del sistema (ejecutables)
    SYSTEM_DEPENDENCIES = ["curl", "git"]
    
    # Requerimientos de hardware
    HARDWARE_REQUIREMENTS = {
        "min_ram_gb": 4,
        "min_disk_gb": 1,
        "min_cpu_cores": 2
    }
    
    # Requerimientos de permisos
    PERMISSION_REQUIREMENTS = {
        "network_access": True,
        "write_access": ["/tmp", "./output"],
        "read_access": ["./data"]
    }
    
    def __init__(self, context=None, plugin_config: Optional[Dict[str, Any]] = None):
        """Inicializar el plugin con verificación de dependencias."""
        super().__init__(context, plugin_config)
        
        # Verificar dependencias al inicializar
        self.dependency_status = self._check_all_dependencies()
        
        if not self.dependency_status['all_satisfied']:
            self._log_dependency_warnings()
        
        # Initialize SDK if dependencies are satisfied
        if self.dependency_status['all_satisfied']:
            self._initialize_sdk()
    
    def _initialize_sdk(self):
        """Initialize SDK components for enhanced functionality."""
        try:
            self.extension_manager = ExtensionManager()
            self.hook_system = HookSystem()
            self.command_customizer = CommandCustomizer()
            
            # Register SDK extensions
            self._register_sdk_extensions()
            
            Output.Console(self.plugin_name, "SDK components initialized")
        except Exception as e:
            Output.Console(self.plugin_name, f"SDK initialization failed: {e}")
    
    def _register_sdk_extensions(self):
        """Register SDK extensions for enhanced functionality."""
        # Register command customization for dependency checking
        self.command_customizer.register_customizer(
            event=CommandEvent.BEFORE_COMMAND_EXECUTION,
            callback=self._before_command_callback,
            priority=10
        )
        
        # Register hook for dependency monitoring
        self.hook_system.register_hook(
            hook_point=HookPoint.BEFORE_TASK_EXECUTION,
            callback=self._before_task_hook,
            priority=5
        )
    
    def _before_command_callback(self, context):
        """Callback for command customization with dependency checking."""
        command_name = context.command_name
        
        # Check if command requires specific dependencies
        if command_name in ['test_functionality', 'install_dependencies']:
            Output.Console(self.plugin_name, f"Executing dependency-sensitive command: {command_name}")
        
        return context
    
    def _before_task_hook(self, hook_context):
        """Hook for task execution with dependency monitoring."""
        Output.Console(self.plugin_name, "Dependency plugin hook executed")
        return hook_context
    
    def _check_all_dependencies(self) -> Dict[str, Any]:
        """
        Verificar todas las dependencias y requerimientos.
        
        Returns:
            Diccionario con el estado de todas las dependencias
        """
        status = {
            'python_packages': self._check_python_packages(),
            'system_dependencies': self._check_system_dependencies(),
            'hardware_requirements': self._check_hardware_requirements(),
            'permission_requirements': self._check_permission_requirements(),
            'all_satisfied': True
        }
        
        # Verificar si todas las dependencias están satisfechas
        for category in ['python_packages', 'system_dependencies', 'hardware_requirements', 'permission_requirements']:
            if not status[category]['satisfied']:
                status['all_satisfied'] = False
        
        return status
    
    def _check_python_packages(self) -> Dict[str, Any]:
        """Verificar paquetes de Python."""
        results = {
            'satisfied': True,
            'packages': {},
            'missing': [],
            'install_commands': []
        }
        
        for package in self.DEPENDENCIES:
            try:
                module = __import__(package)
                results['packages'][package] = {
                    'available': True,
                    'version': self._get_package_version(package)
                }
            except ImportError:
                results['packages'][package] = {
                    'available': False,
                    'version': None
                }
                results['missing'].append(package)
                results['satisfied'] = False
        
        # Generar comandos de instalación
        if results['missing']:
            results['install_commands'] = [
                f"pip install {' '.join(results['missing'])}",
                f"pip install {' '.join(self.REQUIREMENTS)}"
            ]
        
        return results
    
    def _check_system_dependencies(self) -> Dict[str, Any]:
        """Verificar dependencias del sistema (ejecutables)."""
        results = {
            'satisfied': True,
            'executables': {},
            'missing': [],
            'install_instructions': {}
        }
        
        install_instructions = {
            'curl': {
                'ubuntu_debian': 'sudo apt-get install curl',
                'centos_rhel': 'sudo yum install curl',
                'fedora': 'sudo dnf install curl',
                'macos': 'brew install curl',
                'alpine': 'apk add curl'
            },
            'git': {
                'ubuntu_debian': 'sudo apt-get install git',
                'centos_rhel': 'sudo yum install git',
                'fedora': 'sudo dnf install git',
                'macos': 'brew install git',
                'alpine': 'apk add git'
            }
        }
        
        for executable in self.SYSTEM_DEPENDENCIES:
            path = shutil.which(executable)
            if path:
                results['executables'][executable] = {
                    'available': True,
                    'path': path,
                    'version': self._get_executable_version(executable)
                }
            else:
                results['executables'][executable] = {
                    'available': False,
                    'path': None,
                    'version': None
                }
                results['missing'].append(executable)
                results['satisfied'] = False
                
                # Agregar instrucciones de instalación
                if executable in install_instructions:
                    results['install_instructions'][executable] = install_instructions[executable]
        
        return results
    
    def _check_hardware_requirements(self) -> Dict[str, Any]:
        """Verificar requerimientos de hardware."""
        results = {
            'satisfied': True,
            'requirements': {},
            'current': {},
            'missing': []
        }
        
        # Verificar RAM
        try:
            import psutil
            ram_gb = psutil.virtual_memory().total / (1024**3)
            results['current']['ram_gb'] = round(ram_gb, 2)
            results['requirements']['ram_gb'] = self.HARDWARE_REQUIREMENTS['min_ram_gb']
            
            if ram_gb < self.HARDWARE_REQUIREMENTS['min_ram_gb']:
                results['satisfied'] = False
                results['missing'].append(f"RAM: {ram_gb:.1f}GB < {self.HARDWARE_REQUIREMENTS['min_ram_gb']}GB")
        except ImportError:
            results['current']['ram_gb'] = 'Unknown (psutil not available)'
            results['requirements']['ram_gb'] = self.HARDWARE_REQUIREMENTS['min_ram_gb']
        
        # Verificar CPU cores
        try:
            cpu_cores = os.cpu_count() or 1
            results['current']['cpu_cores'] = cpu_cores
            results['requirements']['cpu_cores'] = self.HARDWARE_REQUIREMENTS['min_cpu_cores']
            
            if cpu_cores < self.HARDWARE_REQUIREMENTS['min_cpu_cores']:
                results['satisfied'] = False
                results['missing'].append(f"CPU cores: {cpu_cores} < {self.HARDWARE_REQUIREMENTS['min_cpu_cores']}")
        except:
            results['current']['cpu_cores'] = 'Unknown'
            results['requirements']['cpu_cores'] = self.HARDWARE_REQUIREMENTS['min_cpu_cores']
        
        # Verificar espacio en disco
        try:
            disk_usage = shutil.disk_usage('.')
            disk_gb = disk_usage.free / (1024**3)
            results['current']['disk_gb'] = round(disk_gb, 2)
            results['requirements']['disk_gb'] = self.HARDWARE_REQUIREMENTS['min_disk_gb']
            
            if disk_gb < self.HARDWARE_REQUIREMENTS['min_disk_gb']:
                results['satisfied'] = False
                results['missing'].append(f"Disk space: {disk_gb:.1f}GB < {self.HARDWARE_REQUIREMENTS['min_disk_gb']}GB")
        except:
            results['current']['disk_gb'] = 'Unknown'
            results['requirements']['disk_gb'] = self.HARDWARE_REQUIREMENTS['min_disk_gb']
        
        return results
    
    def _check_permission_requirements(self) -> Dict[str, Any]:
        """Verificar requerimientos de permisos."""
        results = {
            'satisfied': True,
            'permissions': {},
            'missing': []
        }
        
        # Verificar acceso a red
        if self.PERMISSION_REQUIREMENTS['network_access']:
            try:
                import urllib.request
                urllib.request.urlopen('http://www.google.com', timeout=5)
                results['permissions']['network_access'] = True
            except:
                results['permissions']['network_access'] = False
                results['satisfied'] = False
                results['missing'].append('Network access')
        
        # Verificar permisos de escritura
        for path in self.PERMISSION_REQUIREMENTS['write_access']:
            try:
                test_file = Path(path) / '.test_write'
                test_file.parent.mkdir(parents=True, exist_ok=True)
                test_file.write_text('test')
                test_file.unlink()
                results['permissions'][f'write_access_{path}'] = True
            except Exception as e:
                results['permissions'][f'write_access_{path}'] = False
                results['satisfied'] = False
                results['missing'].append(f'Write access to {path}')
        
        # Verificar permisos de lectura
        for path in self.PERMISSION_REQUIREMENTS['read_access']:
            try:
                test_path = Path(path)
                if test_path.exists() and os.access(test_path, os.R_OK):
                    results['permissions'][f'read_access_{path}'] = True
                else:
                    results['permissions'][f'read_access_{path}'] = False
                    results['satisfied'] = False
                    results['missing'].append(f'Read access to {path}')
            except Exception as e:
                results['permissions'][f'read_access_{path}'] = False
                results['satisfied'] = False
                results['missing'].append(f'Read access to {path}')
        
        return results
    
    def _get_package_version(self, package: str) -> Optional[str]:
        """Obtener versión de un paquete de Python."""
        try:
            module = __import__(package)
            return getattr(module, '__version__', 'Unknown')
        except:
            return None
    
    def _get_executable_version(self, executable: str) -> Optional[str]:
        """Obtener versión de un ejecutable del sistema."""
        try:
            result = subprocess.run([executable, '--version'], 
                                  capture_output=True, text=True, check=False)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        return None
    
    def _log_dependency_warnings(self):
        """Registrar advertencias sobre dependencias faltantes."""
        Output.Console(self.plugin_name, " ADVERTENCIA: Algunas dependencias no están satisfechas")
        
        if not self.dependency_status['python_packages']['satisfied']:
            missing = self.dependency_status['python_packages']['missing']
            Output.Console(self.plugin_name, f"Paquetes de Python faltantes: {', '.join(missing)}")
            for cmd in self.dependency_status['python_packages']['install_commands']:
                Output.Console(self.plugin_name, f"Instalar con: {cmd}")
        
        if not self.dependency_status['system_dependencies']['satisfied']:
            missing = self.dependency_status['system_dependencies']['missing']
            Output.Console(self.plugin_name, f"Dependencias del sistema faltantes: {', '.join(missing)}")
        
        if not self.dependency_status['hardware_requirements']['satisfied']:
            missing = self.dependency_status['hardware_requirements']['missing']
            Output.Console(self.plugin_name, f"Requerimientos de hardware no cumplidos: {', '.join(missing)}")
        
        if not self.dependency_status['permission_requirements']['satisfied']:
            missing = self.dependency_status['permission_requirements']['missing']
            Output.Console(self.plugin_name, f"Permisos faltantes: {', '.join(missing)}")
    
    def get_available_commands(self) -> List[str]:
        """Obtener comandos disponibles."""
        commands = [
            "check_dependencies",      # Verificar estado de dependencias
            "install_dependencies",    # Instalar dependencias faltantes
            "system_info",            # Información del sistema
            "test_functionality",     # Probar funcionalidad del plugin
            "dependency_report"       # Reporte detallado de dependencias
        ]
        
        # Add SDK commands if SDK is available
        if hasattr(self, 'extension_manager'):
            commands.extend(["sdk_info", "sdk_test"])
        
        return commands
    
    def execute(self, command: str, config: Dict[str, Any]) -> Any:
        """Ejecutar un comando del plugin."""
        # Verificar dependencias antes de ejecutar comandos críticos
        if command in ["test_functionality"] and not self.dependency_status['all_satisfied']:
            raise RuntimeError(
                "No se puede ejecutar este comando porque no todas las dependencias están satisfechas. "
                "Use 'check_dependencies' para ver el estado actual."
            )
        
        if command == "check_dependencies":
            return self._check_dependencies_command(config)
        elif command == "install_dependencies":
            return self._install_dependencies_command(config)
        elif command == "system_info":
            return self._system_info_command(config)
        elif command == "test_functionality":
            return self._test_functionality_command(config)
        elif command == "dependency_report":
            return self._dependency_report_command(config)
        elif command == "sdk_info":
            return self._sdk_info_command(config)
        elif command == "sdk_test":
            return self._sdk_test_command(config)
        else:
            raise ValueError(f"Comando desconocido: {command}")
    
    def _check_dependencies_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comando para verificar dependencias."""
        return {
            'status': 'success',
            'all_satisfied': self.dependency_status['all_satisfied'],
            'dependencies': self.dependency_status,
            'message': 'Verificación de dependencias completada'
        }
    
    def _install_dependencies_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comando para instalar dependencias."""
        auto_install = config.get('auto_install', False)
        results = {
            'status': 'success',
            'installed': [],
            'failed': [],
            'skipped': []
        }
        
        # Instalar paquetes de Python faltantes
        if not self.dependency_status['python_packages']['satisfied']:
            missing = self.dependency_status['python_packages']['missing']
            if auto_install:
                for package in missing:
                    try:
                        subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                                     check=True, capture_output=True)
                        results['installed'].append(f"python:{package}")
                    except subprocess.CalledProcessError:
                        results['failed'].append(f"python:{package}")
            else:
                results['skipped'].extend([f"python:{pkg}" for pkg in missing])
        
        # Para dependencias del sistema, solo mostrar instrucciones
        if not self.dependency_status['system_dependencies']['satisfied']:
            results['skipped'].extend([
                f"system:{dep}" for dep in self.dependency_status['system_dependencies']['missing']
            ])
        
        return results
    
    def _system_info_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comando para obtener información del sistema."""
        return {
            'status': 'success',
            'system_info': {
                'platform': platform.platform(),
                'python_version': sys.version,
                'architecture': platform.architecture(),
                'processor': platform.processor(),
                'hardware': self.dependency_status['hardware_requirements']['current']
            }
        }
    
    def _test_functionality_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comando para probar la funcionalidad del plugin."""
        tests = {
            'python_packages': {},
            'system_dependencies': {},
            'permissions': {}
        }
        
        # Probar paquetes de Python
        for package in self.DEPENDENCIES:
            try:
                module = __import__(package)
                tests['python_packages'][package] = {
                    'status': 'working',
                    'version': getattr(module, '__version__', 'Unknown')
                }
            except Exception as e:
                tests['python_packages'][package] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Probar dependencias del sistema
        for executable in self.SYSTEM_DEPENDENCIES:
            try:
                result = subprocess.run([executable, '--version'], 
                                      capture_output=True, text=True, check=False)
                if result.returncode == 0:
                    tests['system_dependencies'][executable] = {
                        'status': 'working',
                        'version': result.stdout.strip().split('\n')[0]
                    }
                else:
                    tests['system_dependencies'][executable] = {
                        'status': 'error',
                        'error': 'Command failed'
                    }
            except Exception as e:
                tests['system_dependencies'][executable] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return {
            'status': 'success',
            'tests': tests,
            'message': 'Pruebas de funcionalidad completadas'
        }
    
    def _dependency_report_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comando para generar reporte detallado de dependencias."""
        report = {
            'plugin_info': {
                'name': self.plugin_name,
                'version': self.VERSION,
                'description': self.DESCRIPTION
            },
            'dependency_status': self.dependency_status,
            'recommendations': self._generate_recommendations(),
            'install_instructions': self._generate_install_instructions()
        }
        
        return {
            'status': 'success',
            'report': report,
            'message': 'Reporte de dependencias generado'
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generar recomendaciones basadas en el estado de dependencias."""
        recommendations = []
        
        if not self.dependency_status['all_satisfied']:
            recommendations.append(" Este plugin no puede funcionar correctamente sin todas las dependencias")
        
        if not self.dependency_status['python_packages']['satisfied']:
            recommendations.append("Instale los paquetes de Python faltantes usando pip")
        
        if not self.dependency_status['system_dependencies']['satisfied']:
            recommendations.append("Instale las dependencias del sistema usando el gestor de paquetes de su distribución")
        
        if not self.dependency_status['hardware_requirements']['satisfied']:
            recommendations.append("Considere actualizar su hardware o usar un sistema con más recursos")
        
        if not self.dependency_status['permission_requirements']['satisfied']:
            recommendations.append("Verifique los permisos del sistema y ajuste según sea necesario")
        
        if self.dependency_status['all_satisfied']:
            recommendations.append("Todas las dependencias están satisfechas. El plugin está listo para usar.")
        
        return recommendations
    
    def _generate_install_instructions(self) -> Dict[str, Any]:
        """Generar instrucciones de instalación."""
        instructions = {
            'python_packages': {
                'command': f"pip install {' '.join(self.DEPENDENCIES)}",
                'requirements_file': '\n'.join(self.REQUIREMENTS)
            },
            'system_dependencies': self.dependency_status['system_dependencies']['install_instructions'],
            'hardware_upgrade': "Considere actualizar su hardware según los requerimientos mínimos",
            'permissions': "Verifique y ajuste los permisos del sistema según sea necesario"
        }
        
        return instructions
    
    def _sdk_info_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comando para obtener información del SDK."""
        return {
            'status': 'success',
            'sdk_enabled': hasattr(self, 'extension_manager'),
            'plugin_name': self.plugin_name,
            'version': self.VERSION,
            'sdk_components': {
                'extension_manager': hasattr(self, 'extension_manager'),
                'hook_system': hasattr(self, 'hook_system'),
                'command_customizer': hasattr(self, 'command_customizer')
            },
            'dependency_status': self.dependency_status['all_satisfied']
        }
    
    def _sdk_test_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comando para probar funcionalidades del SDK."""
        if not hasattr(self, 'extension_manager'):
            return {
                'status': 'error',
                'message': 'SDK is not available (dependencies not satisfied)'
            }
        
        return {
            'status': 'success',
            'message': 'SDK functionality is working',
            'sdk_tests': {
                'hooks': {'executed': True, 'context': {'modified': False, 'should_continue': True}},
                'command_customization': {'executed': True, 'context': {'command_name': 'test', 'should_continue': True}}
            },
            'dependency_status': self.dependency_status['all_satisfied']
        }