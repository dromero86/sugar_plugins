#!/usr/bin/env python3
"""
Setup script para el plugin RAR de Sugar
"""

from setuptools import setup, find_packages
import os

# Leer el README
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Plugin RAR para Sugar - Compresión y descompresión de archivos RAR"

# Leer requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="sugar-rar-plugin",
    version="1.0.0",
    description="Plugin RAR para Sugar - Compresión y descompresión de archivos RAR",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Sugar Team",
    author_email="team@sugar-lang.org",
    url="https://github.com/sugar-lang/sugar-rar-plugin",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving :: Compression",
    ],
    keywords="sugar plugin rar compression archive",
    project_urls={
        "Bug Reports": "https://github.com/sugar-lang/sugar-rar-plugin/issues",
        "Source": "https://github.com/sugar-lang/sugar-rar-plugin",
        "Documentation": "https://sugar-lang.org/plugins/rar",
    },
    entry_points={
        "sugar.plugins": [
            "rar = src.rar_plugin:RarPlugin",
        ],
    },
)
