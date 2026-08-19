"""
Extract Table Selenium Plugin
============================

A Sugar plugin for extracting data from HTML tables using Selenium WebDriver.
Provides advanced table extraction capabilities with support for dynamic content,
JavaScript-rendered tables, and complex table structures.
"""

from .src.extract_table_selenium import ExtractTableSeleniumPlugin

__version__ = "1.0.0"
__author__ = "Sugar Team"
__description__ = "Selenium-based HTML table extraction plugin"

__all__ = ["ExtractTableSeleniumPlugin"]