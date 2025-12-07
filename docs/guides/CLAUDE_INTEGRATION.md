# Guía de Integración con Claude Desktop

Esta guía proporciona instrucciones detalladas para configurar Airtable MCP con Claude Desktop.

## Requisitos Previos

- Node.js 14+ instalado
- Claude Desktop instalado
- Token de API de Airtable
- ID de base de Airtable

## Pasos de Configuración

1. **Localizar Archivo de Configuración**
   - Abra Finder
   - Presione `Cmd + Shift + G`
   - Ingrese `~/Library/Application Support/Claude`
   - Cree o abra `claude_desktop_config.json`

2. **Agregar Configuración**
   ```json
   {
     "mcpServers": {
       "airtable-mcp": {
         "command": "npx",
         "args": [
           "@smithery/cli",
           "run",
           "@rashidazarang/airtable-mcp",
           "--token",
           "SU_TOKEN_AIRTABLE",
           "--base",
           "SU_ID_BASE"
         ]
       }
     }
   }
   ```

3. **Reemplazar Credenciales**
   - Reemplace `SU_TOKEN_AIRTABLE` con su token de [Cuenta de Airtable](https://airtable.com/account)
   - Reemplace `SU_ID_BASE` con su ID de base (encontrado en la URL de su base de Airtable)

4. **Reiniciar Claude Desktop**
   - Cierre Claude Desktop completamente
   - Espere 5 segundos
   - Vuelva a abrir Claude Desktop
   - Espere 30 segundos para que se establezca la conexión

## Verificación

Pruebe la conexión preguntando a Claude:
- "Mostrarme todas mis bases Airtable"
- "¿Qué tablas hay en esta base?"
- "Mostrarme los primeros 5 registros de cualquier tabla"

## Solución de Problemas

### Problemas de Conexión
1. Verifique la instalación de Node.js:
   ```bash
   node -v  # Debería mostrar v14 o superior
   ```

2. Pruebe CLI de Smithery:
   ```bash
   npx @smithery/cli --version
   ```

3. Verifique registros:
   - Abra `~/Library/Logs/Claude/mcp-server-airtable-mcp.log`
   - Busque cualquier mensaje de error

### Errores Comunes

1. **"Comando no encontrado"**
   ```bash
   npm install -g npm@latest
   ```

2. **Errores de Análisis de JSON**
   - Elimine todas las barras invertidas adicionales
   - Use el formato exacto mostrado arriba
   - Asegúrese de no haber comas finales

3. **Tiempo de Conexión Agotado**
   - Espere los 30 segundos completos después del inicio
   - Verifique su conexión a Internet
   - Verifique que su token de API sea válido

## Soporte

Si encuentra algún problema:
1. Verifique [Problemas de GitHub](https://github.com/rashidazarang/airtable-mcp/issues)
2. Únase a nuestro [Discord](https://discord.gg/your-discord)
