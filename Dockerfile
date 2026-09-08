# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicación
COPY . .

# Crear directorio para templates
RUN mkdir -p templates

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["python", "src/python/inspector_server.py"]
