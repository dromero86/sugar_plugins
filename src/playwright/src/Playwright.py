"""
Playwright Component for Playwright Plugin
=========================================

Handles the main Playwright instance and provides utility functions.
"""

from typing import Any, Dict, Optional
from Sugar.Lang.Utils.Output import Output

class Playwright:
    """
    Main Playwright component for the plugin.
    """
    
    def __init__(self, plugin):
        """
        Initialize Playwright component.
        
        Args:
            plugin: Reference to the main plugin instance
        """
        self.plugin = plugin
        self.playwright = None
        
        Output.Console(self.plugin.plugin_name, "Playwright component initialized")
    
    def install_browsers(self):
        """
        Install Playwright browsers.
        """
        try:
            import subprocess
            import sys
            
            Output.Console(self.plugin.plugin_name, "Installing Playwright browsers...")
            
            # Run playwright install
            result = subprocess.run([
                sys.executable, "-m", "playwright", "install"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                Output.Console(self.plugin.plugin_name, "Playwright browsers installed successfully")
                return {"success": True, "message": "Browsers installed successfully"}
            else:
                Output.Console(self.plugin.plugin_name, f"Error installing browsers: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            Output.Console(self.plugin.plugin_name, f"Error installing browsers: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_browser_info(self):
        """
        Get information about available browsers.
        """
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browsers = []
                
                # Check Chromium
                try:
                    chromium = p.chromium.launch()
                    browsers.append({
                        "name": "chromium",
                        "version": chromium.version,
                        "available": True
                    })
                    chromium.close()
                except Exception:
                    browsers.append({
                        "name": "chromium",
                        "available": False
                    })
                
                # Check Firefox
                try:
                    firefox = p.firefox.launch()
                    browsers.append({
                        "name": "firefox",
                        "version": firefox.version,
                        "available": True
                    })
                    firefox.close()
                except Exception:
                    browsers.append({
                        "name": "firefox",
                        "available": False
                    })
                
                # Check WebKit
                try:
                    webkit = p.webkit.launch()
                    browsers.append({
                        "name": "webkit",
                        "version": webkit.version,
                        "available": True
                    })
                    webkit.close()
                except Exception:
                    browsers.append({
                        "name": "webkit",
                        "available": False
                    })
            
            return {
                "success": True,
                "browsers": browsers
            }
            
        except Exception as e:
            Output.Console(self.plugin.plugin_name, f"Error getting browser info: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def check_dependencies(self):
        """
        Check if Playwright dependencies are satisfied.
        """
        try:
            import playwright
            
            # Check if playwright is installed
            playwright_version = playwright.__version__
            
            # Check if browsers are installed
            browser_info = self.get_browser_info()
            
            result = {
                "success": True,
                "playwright_version": playwright_version,
                "browsers": browser_info.get("browsers", []),
                "all_browsers_available": all(b.get("available", False) for b in browser_info.get("browsers", []))
            }
            
            Output.Console(self.plugin.plugin_name, f"Playwright version: {playwright_version}")
            
            return result
            
        except ImportError:
            return {
                "success": False,
                "error": "Playwright not installed",
                "install_command": "pip install playwright"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
