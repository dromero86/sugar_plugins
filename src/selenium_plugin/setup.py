#!/usr/bin/env python3
"""
Setup script for Selenium Plugin v2.0
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'docs', 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Plugin Selenium para Sugar v2.0"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="sugar-selenium-plugin",
    version="2.0.0",
    description="Plugin Selenium para Sugar con sintaxis @selenium/",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Sugar Team",
    author_email="team@sugar-lang.org",
    url="https://github.com/sugar-lang/selenium-plugin",
    packages=find_packages(),
    install_requires=read_requirements(),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
    ],
    keywords="selenium automation web testing sugar plugin",
    project_urls={
        "Bug Reports": "https://github.com/sugar-lang/selenium-plugin/issues",
        "Source": "https://github.com/sugar-lang/selenium-plugin",
        "Documentation": "https://github.com/sugar-lang/selenium-plugin/docs",
    },
    include_package_data=True,
    zip_safe=False,
)
