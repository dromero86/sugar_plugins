"""
Setup script for SQLite Plugin
"""

from setuptools import setup, find_packages

setup(
    name="sugar-sqlite-plugin",
    version="1.0.0",
    description="Plugin SQLite para Sugar - Operaciones de base de datos SQLite",
    author="Sugar Team",
    author_email="team@sugar-lang.org",
    packages=find_packages(),
    install_requires=[
        # No se requieren dependencias externas
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="sugar, plugin, sqlite, database",
    project_urls={
        "Bug Reports": "https://github.com/sugar-lang/sugar/issues",
        "Source": "https://github.com/sugar-lang/sugar",
        "Documentation": "https://sugar-lang.org/docs/plugins/sqlite",
    },
)