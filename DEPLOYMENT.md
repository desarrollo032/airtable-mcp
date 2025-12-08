# Guía de Despliegue - Airtable MCP Server

Este documento explica cómo desplegar el Airtable MCP Server en diferentes plataformas, incluyendo información de versiones y compatibilidad.

## 📋 Información de Versiones

### Versión Actual: 3.2.5
- **Fecha de Lanzamiento**: Diciembre 2024
- **Compatibilidad**: Python 3.8+, Node.js 18+
- **Transportes Soportados**: STDIO, HTTP, SSE (Server-Sent Events)
- **Plataformas**: Railway, Heroku, Docker, Local

### Historial de Versiones Importantes

#### v3.2.x (Actual)
- ✅ Soporte completo para FastMCP moderno
- ✅ Transporte HTTP con SSE para streaming en tiempo real
- ✅ Despliegue dual (Python + TypeScript)
- ✅ Compatibilidad con Railway.app optimizada

#### v3.1.x - v3.0.x
- ✅ Soporte para TypeScript completo
- ✅ Herramientas avanzadas de Airtable
- ✅ Configuración mejorada de entornos

#### v1.x - v2.x
- ✅ Funcionalidad básica de MCP
- ✅ Integración con Airtable API
- ✅ Soporte para múltiples bases

### Compatibilidad

| Versión | Python | Node.js | FastMCP | Transporte |
|---------|--------|---------|---------|------------|
| 3.2.x   | 3.8+   | 18+     | ✅      | STDIO/HTTP/SSE |
| 3.1.x   | 3.8+   | 16+     | ❌      | STDIO       |
| 2.x     | 3.6+   | ❌      | ❌      | STDIO       |
| 1.x     | 3.6+   | ❌      | ❌      | STDIO       |

### Actualizaciones Recomendadas

#### De v3.1.x a v3.2.x
```bash
# Actualizar dependencias
pip install -r requirements.txt --upgrade
npm update

# Verificar configuración FastMCP
# Asegurarse de que fastmcp.json use el nuevo esquema
```

#### De v2.x/v1.x a v3.x
```bash
# Backup de configuración actual
cp .env .env.backup

# Actualizar completamente
git pull origin main
pip install -r requirements.txt
npm install

# Revisar variables de entorno (AIRTABLE_BASE_ID ahora opcional)
```

## ⚠️ Notas de Compatibilidad

- **FastMCP**: Las versiones 3.2.x requieren FastMCP moderno para despliegue HTTP
- **Variables de Entorno**: `AIRTABLE_BASE_ID` es opcional desde v3.2.5
- **Docker**: Imagen actualizada a Python 3.12 y Node.js 22
- **Railway**: Configuración optimizada para el nuevo sistema de despliegue

## 🚀 Despliegue en Railway.app

### Requisitos Previos
- Cuenta en [Railway.app](https://railway.app)
- Airtable API Token
- Repositorio Git de este proyecto

### Pasos para Desplegar

1. **Clonar el Repositorio**
   ```bash
   git clone https://github.com/desarrollo032/airtable-mcp.git
   cd airtable-mcp
   ```

2. **Crear Proyecto en Railway**
   ```bash
   railway init
   ```

3. **Configurar Variables de Entorno**
   En el dashboard de Railway, configura las siguientes variables:
   ```
   AIRTABLE_TOKEN=tu_token_aqui
   AIRTABLE_BASE_ID=tu_id_base_aqui (opcional)
   LOG_LEVEL=INFO
   ```

4. **Desplegar**
   ```bash
   railway up
   ```

### Variables de Entorno Soportadas

- `AIRTABLE_TOKEN` - Token de Acceso Personal de Airtable (requerido)
- `AIRTABLE_BASE_ID` - ID de base Airtable (opcional en v3.2.5+)
- `LOG_LEVEL` - Nivel de logs (DEBUG, INFO, WARNING, ERROR) - por defecto INFO
- `PORT` - Puerto en el que escucha el servidor (por defecto 8000)

## 🐳 Despliegue con Docker

### Dockerfile Multi-Lenguaje (v3.2.x)
```dockerfile
FROM python:3.12-slim

# Instalar Node.js 22
RUN apt-get update && apt-get install -y curl build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Configurar dependencias
COPY package.json package-lock.json requirements.txt ./
RUN python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
RUN npm install

# Copiar proyecto
COPY . .

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production
EXPOSE 8000

# Comando FastMCP
CMD ["bash", "-c", ". .venv/bin/activate && fastmcp run"]
```

### Construir y Ejecutar
```bash
# Construir imagen
docker build -t airtable-mcp:latest .

# Ejecutar con variables de entorno
docker run -e AIRTABLE_TOKEN=your_token \
           -e AIRTABLE_BASE_ID=your_base_id \
           -p 8000:8000 \
           airtable-mcp:latest
```

### Modos de Ejecución

#### Desarrollo Local (STDIO)
```bash
docker run --rm -it airtable-mcp:latest fastmcp run
```

#### Producción (HTTP + SSE)
```bash
docker run -e MCP_TRANSPORT=http -p 8000:8000 airtable-mcp:latest
```

## 🌍 Otros Proveedores de Hosting

### Heroku
1. Clonar el repositorio
2. Crear `Procfile` (ya incluido):
   ```
   web: python app.py
   ```
3. Desplegar:
   ```bash
   heroku login
   git push heroku main
   ```

### Google Cloud Run
```bash
gcloud run deploy airtable-mcp \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars AIRTABLE_TOKEN=your_token
```

### AWS Lambda
Requiere adaptación especial. Contactar para más detalles.

## 🔧 Archivos de Configuración

### v3.2.x (FastMCP Moderno)
- **fastmcp.json** - Configuración FastMCP con transporte HTTP/SSE
- **railway.json** - Configuración Railway con Docker builder
- **Dockerfile** - Imagen multi-lenguaje (Python + Node.js)
- **Procfile** - Configuración legacy para Heroku

### Versiones Anteriores
- **app.py** - Punto de entrada para Railpack/Nixpacks
- **main.py** - Punto de entrada alternativo
- **railway.toml** - Configuración alternativa para Railway

## ✅ Verificar que Funciona

1. Una vez desplegado, el servidor MCP estará disponible
2. Verificar logs en el dashboard de la plataforma
3. Para probar localmente:
   ```bash
   pip install -r requirements.txt
   python app.py
   ```

## 🐛 Solución de Problemas

### Error: "No start command was found"
- Asegúrate de que `app.py` o `main.py` existe en la raíz del proyecto
- O configura `Procfile` correctamente

### Error: "Module not found"
- Verifica que `requirements.txt` tiene todas las dependencias
- Asegúrate de que `pip install -r requirements.txt` se ejecutó

### Error: "AIRTABLE_TOKEN not found"
- Configura la variable de entorno en el dashboard de tu plataforma
- O crea un archivo `.env` localmente (nunca en producción)

## 📚 Más Información

- [Documentación de Railway](https://docs.railway.app/)
- [Airtable API Reference](https://airtable.com/developers/web/api/introduction)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## 📋 Comandos Útiles por Versión

### v3.2.x (FastMCP)
```bash
# Desarrollo local
fastmcp run

# Producción Railway
# Automático con railway.json

# Docker local
docker run airtable-mcp:latest

# Verificar configuración
fastmcp run --help
```

### v3.1.x - v3.0.x (TypeScript)
```bash
# Desarrollo
npm run dev

# Producción
npm start

# Build
npm run build
```

### v2.x - v1.x (Python Only)
```bash
# Desarrollo
python app.py

# Producción
python app.py
```

## 🔄 Migración entre Versiones

### Checklist de Migración a v3.2.x
- [ ] Backup de configuración actual (`.env`, variables Railway)
- [ ] Actualizar código: `git pull origin main`
- [ ] Instalar dependencias: `pip install -r requirements.txt && npm install`
- [ ] Verificar `fastmcp.json` con nuevo esquema
- [ ] Probar localmente: `fastmcp run`
- [ ] Desplegar en Railway con nueva configuración
- [ ] Verificar HTTP endpoint: `https://tu-app.railway.app/mcp`

---

**Última Actualización**: Diciembre 2024
**Versión**: 3.2.5
**FastMCP**: ✅ Compatible
**SSE Streaming**: ✅ Disponible
