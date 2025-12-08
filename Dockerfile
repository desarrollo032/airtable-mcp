# Imagen base con Python 3.12‑slim
FROM python:3.12-slim

WORKDIR /app

# Instalar Node.js 22 + utilidades básicas
RUN apt-get update && \
    apt-get install -y curl gnupg build-essential && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiar package de Node para caching, instalar dependencias JS
COPY package.json package-lock.json /app/
RUN npm install --production --ignore-scripts

# Copiar requirements & crear entorno virtual Python
COPY requirements.txt /app/
RUN python3 -m venv .venv && \
    . .venv/bin/activate && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar todo el código fuente (incluyendo scripts .py, .js, carpetas, etc.)
COPY . /app/

# Variables de entorno útiles
ENV NODE_ENV=production
ENV PYTHONUNBUFFERED=1

# Si deseas usar transporte por defecto (stdio) o HTTP según variable
ENV FASTMCP_TRANSPORT=stdio
# Puedes definir PORT en el entorno al ejecutar, por ejemplo con docker run -e PORT=8000

EXPOSE 8000

# Comando de inicio: usa fastmcp run si instalaste fastmcp en el entorno
CMD [ "bash", "-c", "\
  . .venv/bin/activate && \
  if [ \"$FASTMCP_TRANSPORT\" = \"http\" ]; then \
    fastmcp run server.py:mcp --transport http --host 0.0.0.0 --port ${PORT:-8000}; \
  else \
    fastmcp run server.py:mcp; \
  fi" ]
