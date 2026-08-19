"""
Setup script for GnuPG Plugin
=============================

Installation script for the GnuPG plugin for Sugar Language.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "GnuPG Plugin for Sugar Language"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="sugar-gnupg-plugin",
    version="1.0.0",
    description="GnuPG cryptographic operations plugin for Sugar Language",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Sugar Team",
    author_email="team@sugar-lang.org",
    license="MIT",
    url="https://github.com/sugar-lang/plugins",
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
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="sugar language plugin gnupg cryptography encryption signing",
    project_urls={
        "Bug Reports": "https://github.com/sugar-lang/plugins/issues",
        "Source": "https://github.com/sugar-lang/plugins",
        "Documentation": "https://docs.sugar-lang.org/plugins/gnupg",
    },
    entry_points={
        "sugar.plugins": [
            "gnupg = src.GnuPGPlugin:GnuPGPlugin",
        ],
    },
)