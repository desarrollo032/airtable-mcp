#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Leer README.md para long_description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Leer dependencias desde requirements.txt
requirements_file = "requirements.txt"
if os.path.exists(requirements_file):
    with open(requirements_file, "r", encoding="utf-8") as req_file:
        requirements = [line.strip() for line in req_file if line.strip()]
else:
    requirements = []

setup(
    name="airtable-mcp",
    version="3.2.5",  # Coincide con tu package.json
    author="Rashid Azarang",
    author_email="rashidazarang@gmail.com",
    description="Airtable MCP for AI tools - updated to work with MCP SDK 1.4.1+",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rashidazarang/airtable-mcp",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.10",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            # Permite ejecutar el servidor desde la terminal
            "airtable-mcp=src.python.inspector_server:main",
        ],
    },
)
