# Airtable Brain MCP

## Resumen

Servidor MCP para Airtable con implementaciones FastMCP en Python, MCP SDK en TypeScript y compatibilidad JavaScript/OAuth.

## Convenciones del proyecto

- La implementación FastMCP Python recomendada para desarrollo es `src/python/inspector_server.py`.
- `npm run dev` inicia el servidor Python recomendado.
- `npm start` ejecuta FastMCP en modo HTTP usando el puerto de `PORT`.
- La implementación TypeScript requiere `npm run build` antes de ejecutar sus entradas compiladas.
- Las credenciales y tokens deben permanecer en variables de entorno o secretos del workspace.
- Mantener el README sincronizado con las implementaciones reales; no documentar herramientas que no estén registradas en la variante descrita.

## Verificación rápida

```bash
npm run build
npm run test:types
npm run lint
npm run format:check
```