# Guía de Despliegue - Airtable MCP Server

Este documento explica cómo desplegar el Airtable MCP Server en diferentes plataformas.

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

### Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

CMD ["python", "app.py"]
```

### Construir y Ejecutar
```bash
docker build -t airtable-mcp:latest .
docker run -e AIRTABLE_TOKEN=your_token -p 8000:8000 airtable-mcp:latest
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

- **Procfile** - Configuración para Heroku y plataformas similares
- **railway.json** - Configuración específica para Railway.app
- **railway.toml** - Configuración alternativa para Railway
- **app.py** - Punto de entrada para Railpack/Nixpacks
- **main.py** - Punto de entrada alternativo

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

---

**Última Actualización**: 7 de Diciembre de 2025
**Versión**: 3.2.5
