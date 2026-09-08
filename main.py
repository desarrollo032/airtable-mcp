#!/usr/bin/env python3
"""
Airtable MCP Server - Alternative Entry Point
"""
import os
import sys

# Keep this entry point aligned with app.py and the deployment commands.
if __name__ == "__main__":
    script_path = os.path.join(
        os.path.dirname(__file__), "src", "python", "inspector_server.py"
    )
    os.execv(sys.executable, [sys.executable, script_path, *sys.argv[1:]])
