# FastMCP Deployment Guide

This guide covers the updated FastMCP deployment configuration for the Airtable MCP server, supporting both local development and Railway production deployment with HTTP/SSE transport.

## Overview

The Airtable MCP server now supports multiple deployment modes:
- **Local Development**: STDIO transport for development and testing
- **Railway Production**: HTTP transport with Server-Sent Events (SSE) support
- **Dual Transport**: TypeScript server supports both STDIO and HTTP simultaneously

## FastMCP Configuration

### fastmcp.json

The `fastmcp.json` file configures the FastMCP deployment:

```json
{
  "$schema": "https://gofastmcp.com/public/schemas/fastmcp.json/v1.json",
  "source": {
    "path": "src/python/inspector_server.py",
    "entrypoint": "mcp"
  },
  "deployment": {
    "transport": "http",
    "host": "0.0.0.0",
    "port": "$PORT",
    "log_level": "INFO"
  },
  "tools": {},
  "instructions": "Use describe/query tools for read flows. All mutations require diff review and idempotency keys."
}
```

**Key Settings:**
- `source.path`: Points to the Python server entry point
- `deployment.transport`: "http" enables HTTP/SSE transport
- `deployment.port`: "$PORT" uses Railway's assigned port
- `deployment.log_level`: Controls logging verbosity

## Deployment Options

### 1. Railway Deployment (Recommended)

#### railway.json Configuration

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "runtime": "V2",
    "numReplicas": 1,
    "startCommand": "fastmcp run",
    "preDeployCommand": [
      "python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt",
      "npm install"
    ],
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### Deployment Steps

1. **Push to GitHub**: Railway automatically detects the configuration
2. **Build Process**:
   - Uses Docker for consistent environment
   - Installs Python dependencies in virtual environment
   - Installs Node.js dependencies
3. **Start Command**: `fastmcp run` launches the server with HTTP transport

#### Production URL

Your MCP server will be available at:
```
https://your-project.railway.app/mcp
```

### 2. Local Development

#### Using FastMCP

```bash
# Install FastMCP CLI
pip install fastmcp

# Run with STDIO transport (default for local dev)
fastmcp run
```

#### Using Python Directly

```bash
# Activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Python server
python3 src/python/inspector_server.py
```

#### Using TypeScript Server

```bash
# Install Node dependencies
npm install

# Run with STDIO transport
npm start

# Run with HTTP transport
MCP_TRANSPORT=http MCP_USE_SSE=true npm start

# Run with dual transport (STDIO + HTTP)
MCP_TRANSPORT=http npm start
```

## Transport Modes

### STDIO Transport (Development)

- **Use Case**: Local development, testing, integration with Claude Desktop
- **Command**: `fastmcp run` (without MCP_TRANSPORT=http)
- **Protocol**: Standard input/output streams
- **Clients**: Claude Desktop, command-line tools

### HTTP Transport (Production)

- **Use Case**: Web applications, remote clients, Railway deployment
- **Command**: `fastmcp run` (with deployment.transport: "http")
- **Protocol**: HTTP with JSON-RPC 2.0
- **Features**: Server-Sent Events (SSE) support for real-time streaming

### Dual Transport (TypeScript Only)

The TypeScript server supports running both transports simultaneously:

```bash
# STDIO for local tools + HTTP for web clients
MCP_TRANSPORT=http npm start
```

## Server-Sent Events (SSE)

When using HTTP transport, the server automatically supports SSE for real-time streaming:

### Client Implementation

```javascript
// Connect to SSE endpoint
const evtSource = new EventSource('https://your-project.railway.app/mcp');

evtSource.onmessage = (event) => {
  console.log('Real-time event:', event.data);
};

evtSource.onerror = (err) => {
  console.error('SSE Error:', err);
};
```

### SSE Benefits

- **Real-time Updates**: Receive tool execution results as they happen
- **Streaming Responses**: ChatGPT-like streaming for long-running operations
- **Web Compatible**: Works with browsers and web applications
- **Bidirectional**: Can be extended to WebSocket for full duplex communication

## Docker Configuration

The `Dockerfile` is optimized for both Python and Node.js environments:

```dockerfile
FROM python:3.12-slim

# Install Node.js 22
RUN apt-get update && apt-get install -y curl build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Setup dependencies
COPY package.json package-lock.json requirements.txt ./
RUN python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
RUN npm install

# Copy project and run
COPY . .
EXPOSE 8000
CMD ["bash", "-c", ". .venv/bin/activate && fastmcp run"]
```

**Features:**
- Python 3.12 and Node.js 22
- Virtual environment for Python dependencies
- Layer caching for faster rebuilds
- Production environment variables

## Environment Variables

### Railway Environment

- `PORT`: Automatically set by Railway (used by FastMCP)
- `PYTHONUNBUFFERED=1`: Prevents Python output buffering
- `NODE_ENV=production`: Optimizes Node.js for production

### Custom Environment

- `MCP_TRANSPORT=http`: Enables HTTP transport (TypeScript only)
- `MCP_USE_SSE=true`: Enables SSE streaming (TypeScript only)

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Railway assigns `$PORT` automatically
   - Ensure no other services use port 8000 locally

2. **Import Errors**
   - Verify virtual environment is activated: `source .venv/bin/activate`
   - Check Python path: `python3 -c "import sys; print(sys.path)"`

3. **SSE Not Working**
   - Ensure `transport: "http"` in `fastmcp.json`
   - Check client EventSource implementation
   - Verify CORS settings if needed

4. **Build Failures**
   - Check Docker logs in Railway dashboard
   - Verify all dependencies are listed in `requirements.txt` and `package.json`

### Debug Commands

```bash
# Test FastMCP configuration
fastmcp run --help

# Check Python environment
python3 -c "import mcp; print('MCP import successful')"

# Test HTTP endpoint
curl -X POST https://your-project.railway.app/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}'
```

## Migration from Previous Versions

### From fastmcp serve

- Replace `fastmcp serve` with `fastmcp run`
- Update `fastmcp.json` schema to new format
- Use `railway.json` instead of manual Railway configuration

### From Direct Python Execution

- No changes needed for local development
- Railway deployment now uses Docker for consistency
- HTTP transport replaces custom server implementations

## Best Practices

1. **Environment Separation**: Use STDIO for development, HTTP for production
2. **Error Handling**: Implement proper error handling in MCP tools
3. **Logging**: Use appropriate log levels for different environments
4. **Security**: Validate inputs and implement rate limiting
5. **Monitoring**: Monitor Railway logs and performance metrics

## Support

For issues with FastMCP deployment:
- Check Railway deployment logs
- Verify `fastmcp.json` configuration
- Test locally with `fastmcp run`
- Review Docker build process

The updated configuration provides a robust, scalable deployment solution for the Airtable MCP server with modern FastMCP features and real-time capabilities.
