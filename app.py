#!/usr/bin/env python3
"""
Airtable MCP Server - Entry Point
Main entry point for deploying on Rail.app
"""
import os
import sys
import subprocess

# Add src/python to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

# Run the inspector server
if __name__ == "__main__":
    script_path = os.path.join(os.path.dirname(__file__), 'src', 'python', 'inspector_server.py')
    os.execvp(sys.executable, [sys.executable, script_path] + sys.argv[1:])
