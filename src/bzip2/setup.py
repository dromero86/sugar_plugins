#!/usr/bin/env python3
"""
Setup script para el plugin bzip2 de Sugar.
"""

from setuptools import setup, find_packages
import os

# Leer el README
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Plugin bzip2 para Sugar - Compresión y descompresión con bzip2"

# Leer requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="sugar-bzip2-plugin",
    version="1.0.0",
    description="Plugin bzip2 para Sugar - Compresión y descompresión con bzip2",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Sugar Team",
    author_email="team@sugar-lang.org",
    url="https://github.com/sugar-lang/plugins",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving :: Compression",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "sugar-bzip2=sugar_bzip2_plugin.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
