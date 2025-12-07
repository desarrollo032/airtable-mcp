# Guía de Inicio Rápido para Usuarios de Claude

Esta guía proporciona instrucciones simples para poner en funcionamiento Airtable MCP con Claude.

## Paso 1: Clonar el repositorio

```bash
git clone https://github.com/rashidazarang/airtable-mcp.git
cd airtable-mcp
```

## Paso 2: Instalar dependencias

```bash
npm install
pip install mcp
```

## Paso 3: Configurar Claude

En la configuración de Claude, agregue un nuevo servidor MCP con esta configuración (ajuste las rutas según sea necesario):

```json
{
  "mcpServers": {
    "airtable": {
      "command": "python3",
      "args": [
        "/ruta/a/airtable-mcp/inspector_server.py",
        "--token",
        "SU_TOKEN_AIRTABLE",
        "--base",
        "SU_ID_BASE"
      ]
    }
  }
}
```

Reemplace:
- `/ruta/a/airtable-mcp/` con la ruta real donde clonó el repositorio
- `SU_TOKEN_AIRTABLE` con su Token de Acceso Personal de Airtable
- `SU_ID_BASE` con su ID de Base de Airtable

## Paso 4: Reiniciar Claude

Después de configurar, reinicie Claude e intente estos comandos:

1. "Listar las tablas en mi base Airtable"
2. "Mostrarme registros de [nombre de tabla]"

## Solución de Problemas

Si encuentra problemas:

1. Verifique los registros de Claude (haga clic en el mensaje de error)
2. Verifique que su token de Airtable e ID de base sean correctos
3. Asegúrese de haber especificado la ruta correcta a `inspector_server.py`

Esta versión incluye manejo mejorado de errores para formatear correctamente las respuestas JSON
