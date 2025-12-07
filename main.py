#!/usr/bin/env python3
"""
Airtable MCP Server - Alternative Entry Point
"""
import os
import sys

# Add src/python to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

# Run the inspector server
if __name__ == "__main__":
    from inspector_server import main
    main()
