# Contribuyendo a Airtable MCP

¡Gracias por tu interés en contribuir a Airtable MCP! Esta guía te ayudará a 
comenzar con las contribuciones a este proyecto.

## Configuración del Desarrollo

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/rashidazarang/airtable-mcp.git
   cd airtable-mcp
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuración del entorno**:
   Cree un archivo `.env` en el directorio raíz con su token de API de Airtable:
   ```
   AIRTABLE_PERSONAL_ACCESS_TOKEN=su_token_aqui
   AIRTABLE_BASE_ID=id_base_predeterminada_opcional
   ```

## Ejecutar el Servidor

Puede ejecutar el servidor directamente con Python:

```bash
python3.10 inspector_server.py --token "su_token" --base "su_id_de_base"
```

O a través del wrapper de Node.js:

```bash
node index.js --token "su_token" --base "su_id_de_base"
```

## Pruebas

Ejecute el cliente de prueba para verificar su acceso a la API de Airtable:

```bash
python3.10 test_client.py
```

## Proceso de Solicitud de Extracción

1. **Bifurque el Repositorio** en GitHub.

2. **Cree una Rama** para su característica o corrección de errores.

3. **Realice Cambios** de acuerdo con las directrices de estilo del proyecto.

4. **Pruebe Completamente** para asegurarse de que sus cambios funcionen como se 
espera.

5. **Documente Cambios** en el README.md si es necesario.

6. **Envíe una Solicitud de Extracción** al repositorio principal.

## Directrices de Codificación

- Siga las directrices de estilo PEP 8 de Python
- Escriba cadenas de documentación para todas las funciones, clases y módulos
- Incluya sugerencias de tipo para parámetros de función y valores de retorno
- Escriba mensajes de confirmación claros

## Agregar Nuevas Herramientas

Cuando agregue nuevas herramientas de API de Airtable:

1. Agregue la función de herramienta a `inspector_server.py` utilizando el decorador `@app.tool()`
2. Defina tipos claros de parámetros y retorno
3. Proporcione una cadena de documentación descriptiva para la herramienta
4. Actualice el archivo `inspector.py` para incluir la nueva herramienta en el esquema JSON
5. Agregue manejo de errores para solicitudes de API
6. Actualice el README.md para documentar la nueva herramienta

## Licencia

Al contribuir a este proyecto, acepta que sus contribuciones se licenciarán bajo 
la misma licencia que el proyecto (MIT License).
