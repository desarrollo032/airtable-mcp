#!/bin/bash
# Intelligent server startup script

set -e

echo "🚀 Starting Airtable MCP Server..."

# Check environment
if [ "$MCP_TRANSPORT" = "stdio" ]; then
    echo "📡 Running in STDIO mode (development)"
    python server.py
elif [ "$MCP_TRANSPORT" = "http" ] || [ "$MCP_TRANSPORT" = "sse" ]; then
    echo "🌐 Running in HTTP/SSE mode (production)"
    python server.py
else
    echo "🔍 Auto-detecting transport mode..."
    if [ -n "$PORT" ]; then
        echo "🌐 Railway detected, using HTTP mode"
        export MCP_TRANSPORT=http
        python server.py
    else
        echo "📡 No PORT detected, using STDIO mode"
        export MCP_TRANSPORT=stdio
        python server.py
    fi
fi
