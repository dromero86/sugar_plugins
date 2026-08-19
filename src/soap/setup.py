"""
Setup script for SOAP Plugin
===========================

Installation script for the SOAP plugin for Sugar Language.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "SOAP Plugin for Sugar Language"

# Read plugin.json for metadata
def read_plugin_metadata():
    import json
    plugin_path = os.path.join(os.path.dirname(__file__), 'plugin.json')
    if os.path.exists(plugin_path):
        with open(plugin_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

# Get plugin metadata
plugin_metadata = read_plugin_metadata()

setup(
    name="sugar-soap-plugin",
    version=plugin_metadata.get('version', '1.0.0'),
    description=plugin_metadata.get('description', 'SOAP Plugin for Sugar Language'),
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author=plugin_metadata.get('author', 'Sugar Team'),
    author_email="team@sugar-lang.org",
    url="https://github.com/sugar-lang/plugins",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: HTTP Clients",
        "Topic :: Communications :: Web Services",
    ],
    keywords="soap, web services, xml, wsdl, sugar language, plugin",
    project_urls={
        "Bug Reports": "https://github.com/sugar-lang/plugins/issues",
        "Source": "https://github.com/sugar-lang/plugins",
        "Documentation": "https://docs.sugar-lang.org/plugins/soap",
    },
    entry_points={
        "sugar.plugins": [
            "soap = src.SOAPPlugin:SOAPPlugin",
        ],
    },
    zip_safe=False,
)