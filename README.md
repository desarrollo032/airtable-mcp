# 🧠 Airtable Brain MCP

> Servidor [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) para conectar asistentes de IA con Airtable de forma segura, extensible y orientada a automatización.

[![MCP](https://img.shields.io/badge/MCP-compatible-6f42c1?style=for-the-badge)](https://modelcontextprotocol.io/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.x-ff6b35?style=for-the-badge)](https://gofastmcp.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-339933?style=for-the-badge&logo=node.js&logoColor=white)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178c6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-22c55e?style=for-the-badge)](./LICENSE)

<p align="center">
  <strong>Datos de Airtable disponibles para tus agentes, con control de acceso, validación y varios transportes MCP.</strong>
</p>

---

## 📌 ¿Qué es este proyecto?

**Airtable Brain MCP** es una copia evolucionada y una base de experimentación del servidor `airtable-mcp`, adaptada para mejorar sus capacidades y facilitar su ejecución en entornos locales, Replit, Docker y Railway.

Expone Airtable como herramientas MCP para que clientes como Claude, ChatGPT, Cursor, Windsurf u otros agentes compatibles puedan:

- 🔎 Descubrir bases, tablas y registros.
- ✍️ Crear y actualizar datos desde lenguaje natural.
- 🧩 Consultar esquemas y metadatos.
- 🔐 Aplicar reglas de gobernanza, listas permitidas y políticas PII.
- 🌐 Ejecutar el servidor mediante STDIO o HTTP.
- 🔌 Integrar OAuth, webhooks y almacenamiento auxiliar.

> **Importante:** este repositorio no es una copia oficial de Airtable ni del protocolo MCP. Se mantiene como una base mejorada para adaptar, probar y ampliar funcionalidades sobre el proyecto MCP original.

## ✨ Capacidades principales

| Área | Capacidades |
| --- | --- |
| 🧠 **MCP** | Herramientas, recursos, prompts y transporte HTTP/STDIO según la implementación. |
| 🗂️ **Airtable** | Descubrimiento de bases, tablas, lectura y escritura de registros. |
| 🛡️ **Gobernanza** | Allowlist de bases/tablas, operaciones permitidas y redacción de PII en TypeScript. |
| ⚡ **Rendimiento** | Cliente asíncrono `httpx`, operaciones por lotes y límites de solicitudes. |
| 🔁 **Integraciones** | OAuth 2.0, ChatGPT, webhooks, Redis y Back4App/Mongo opcionales. |
| 🧰 **Calidad** | TypeScript, Zod, ESLint, Prettier, Jest, CLI y ejemplos para clientes MCP. |
| 🚀 **Despliegue** | Replit, Docker Compose, Railway y ejecución local con `PORT`. |

## 🧱 Implementaciones disponibles

Las variantes comparten el objetivo, pero no exponen exactamente las mismas herramientas.

### ✅ FastMCP Python — recomendada

Entrada principal: `src/python/inspector_server.py`

Es la ruta usada por `npm run dev` y por `app.py`. Utiliza FastMCP 2.x, `httpx` y transporte HTTP.

| Herramienta | Función |
| --- | --- |
| `list_bases` | Lista las bases accesibles con el token configurado. |
| `list_tables` | Lista las tablas de una base. |
| `list_records` | Consulta registros con límite y filtro por fórmula. |
| `create_records` | Crea uno o varios registros desde JSON. |
| `update_records` | Actualiza registros desde JSON o TOON. |
| `set_base_id` | Cambia la base activa durante la sesión. |

### 🔐 MCP Python extendido

Entrada: `src/python/auth/src/server.py`

Añade `get_record`, `delete_records`, recursos `airtable://`, roots MCP para exportaciones, prompts guiados, completions y parseo JSON/TOON. También contiene puntos de integración para autenticación y OAuth.

### 🔷 TypeScript — gobernanza y operaciones estructuradas

Entrada: `src/typescript/airtable-mcp-server.ts`

Herramientas registradas:

`list_bases` · `describe` · `query` · `list_governance` · `list_exceptions` · `create` · `update` · `upsert` · `list_webhooks` · `create_webhook` · `refresh_webhook`

Incluye:

- ✅ Validación estricta con Zod.
- ✅ `dryRun` para revisar cambios antes de escribir.
- ✅ Idempotency keys y chunking según límites de Airtable.
- ✅ Allowlist de bases y tablas.
- ✅ Políticas PII `mask`, `hash` y `drop`.
- ✅ Rate limiting y registro de excepciones.
- ✅ Transporte STDIO y HTTP/SSE.

### 📦 JavaScript y OAuth — compatibilidad

- `src/javascript/airtable_simple_production.js`: servidor JavaScript con validación, rate limiting y compatibilidad HTTP histórica.
- `src/javascript/airtable_simple.js`: implementación JavaScript simple/legacy.
- `src/oauth_server.js`: servidor OAuth separado para autorización y callbacks.

Estas variantes se conservan para compatibilidad y migración. Para nuevos cambios, prioriza FastMCP Python o TypeScript.

## 🗺️ Arquitectura

```text
┌─────────────────────────────────────────────────────────────────┐
│ Cliente MCP: Claude · ChatGPT · Cursor · Windsurf · Inspector   │
└───────────────────────────────┬─────────────────────────────────┘
                                │ MCP / STDIO / HTTP
┌───────────────────────────────▼─────────────────────────────────┐
│ FastMCP Python · MCP SDK TypeScript · JavaScript legacy          │
└───────────────────────────────┬─────────────────────────────────┘
                                │ Validación · gobernanza · auth
┌───────────────────────────────▼─────────────────────────────────┐
│ Airtable Metadata API · Records API · Webhooks · OAuth           │
└─────────────────────────────────────────────────────────────────┘
```

## 🧰 Stack tecnológico

### Backend y protocolo

- **Python 3.10+** y **FastMCP 2.x** para la ruta principal.
- **MCP Python SDK** para la variante extendida.
- **Node.js 18+** para JavaScript, TypeScript y OAuth.
- **TypeScript 5.3** con `@modelcontextprotocol/sdk`.
- **Zod** para validar entradas y salidas estructuradas.

### Integración y operación

- **Airtable Web API** para metadata, registros y webhooks.
- **`httpx`**, `requests` y `aiohttp` para comunicación HTTP.
- **Redis** y **Back4App/Parse** como almacenamiento opcional.
- **Jest**, **ts-jest**, **ESLint** y **Prettier**.
- **Docker**, **Docker Compose**, **Railway** y **Replit**.

## 📁 Estructura del proyecto

```text
.
├── app.py                         # Entrada web para Railway/Nixpacks
├── main.py                        # Entrada Python alternativa
├── package.json                   # Scripts y dependencias Node/TypeScript
├── requirements.txt               # Dependencias Python/FastMCP
├── fastmcp.json                   # Configuración FastMCP
├── src/
│   ├── python/
│   │   ├── inspector_server.py    # FastMCP recomendado
│   │   ├── server.py              # Variante FastMCP base
│   │   └── auth/                  # Recursos, prompts y OAuth
│   ├── typescript/                # Servidor tipado y gobernado
│   ├── javascript/                # Servidores JavaScript
│   └── oauth_server.js            # Servicio OAuth
├── routes/                        # Rutas HTTP auxiliares
├── services/                      # Airtable, auth y almacenamiento
├── middleware/                    # Seguridad y formato TOON
├── tests/                         # Smoke tests e integración
├── examples/                      # Configuraciones de clientes
├── docs/                          # Guías ampliadas
├── docker/                        # Dockerfiles alternativos
└── bin/                           # CLI de servidor y CRUD
```

## 🚀 Inicio rápido

### 1. Requisitos

- Python `3.10+`.
- Node.js `18+`.
- Cuenta de Airtable.
- Personal Access Token con `data.records:read`, `data.records:write` y `schema.bases:read`.
- `webhook:manage` si utilizarás webhooks.

### 2. Instalar dependencias

```bash
git clone <URL_DEL_REPOSITORIO>
cd airtable-mcp

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

npm install
```

En Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
npm install
```

### 3. Configurar el entorno

```bash
cp .env.example .env
```

Configuración mínima:

```env
AIRTABLE_PERSONAL_ACCESS_TOKEN=patXXXXXXXXXXXXXX
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO
```

`AIRTABLE_BASE_ID` puede omitirse para comenzar con `list_bases`; las operaciones sobre tablas y registros necesitarán una base activa. También se aceptan `AIRTABLE_PAT`, `AIRTABLE_TOKEN` y `AIRTABLE_API_TOKEN` en las variantes que los implementan.

> 🔒 Nunca guardes tokens en Git. Usa secretos del entorno en Replit, Railway o tu proveedor de despliegue.

### 4. Ejecutar

#### Desarrollo recomendado

```bash
npm run dev
```

Equivale a:

```bash
python3 src/python/inspector_server.py
```

#### FastMCP mediante configuración

```bash
source .venv/bin/activate
fastmcp run
```

La configuración se encuentra en `fastmcp.json`. Para producción, `npm start` configura HTTP, `0.0.0.0` y el puerto proporcionado por `PORT`.

#### TypeScript

```bash
npm run build
npm run start:http
```

#### JavaScript legacy

```bash
npm run start:js
```

## 🤖 Configurar un cliente MCP

Ejemplo genérico para Claude Desktop, Cursor u otro cliente que soporte comandos MCP:

```json
{
  "mcpServers": {
    "airtable-brain": {
      "command": "fastmcp",
      "args": ["run"],
      "env": {
        "AIRTABLE_PERSONAL_ACCESS_TOKEN": "TU_TOKEN",
        "AIRTABLE_BASE_ID": "appXXXXXXXXXXXXXX"
      }
    }
  }
}
```

Para un servidor remoto, despliega la variante HTTP y configura la URL MCP entregada por FastMCP o tu plataforma. No expongas producción sin autenticación, proxy o allowlist.

## 💬 Ejemplos de interacción

```text
Lista mis bases de Airtable accesibles.
Muéstrame las tablas de la base appXXXXXXXXXXXXXX.
Consulta los registros activos de Projects usando una fórmula de Airtable.
Prepara una actualización y muéstrame primero el dry run.
Describe el esquema de la base y aplica la política de privacidad definida.
```

## ⚙️ Variables de entorno

| Variable | Req. | Uso |
| --- | :---: | --- |
| `AIRTABLE_PERSONAL_ACCESS_TOKEN` | ✅* | Token PAT preferido por FastMCP Python. |
| `AIRTABLE_PAT` / `AIRTABLE_TOKEN` | ✅* | Alias aceptados por algunas implementaciones. |
| `AIRTABLE_BASE_ID` | ❌ | Base predeterminada; puede configurarse durante la sesión. |
| `AIRTABLE_DEFAULT_BASE` | ❌ | Base predeterminada para TypeScript. |
| `AIRTABLE_ALLOWED_BASES` | ❌ | Bases permitidas separadas por comas. |
| `AIRTABLE_ALLOWED_TABLES` | ❌ | Allowlist TypeScript: `baseId:tableName`. |
| `PORT` | ❌ | Puerto HTTP; por defecto `8000`. |
| `HOST` | ❌ | Host HTTP; por defecto `0.0.0.0`. |
| `LOG_LEVEL` | ❌ | Nivel `DEBUG`, `INFO`, `WARNING` o `ERROR`. |
| `FASTMCP_TRANSPORT` | ❌ | Transporte de despliegue, normalmente `http`. |
| `FASTMCP_MASK_ERROR_DETAILS` | ❌ | Oculta detalles sensibles en errores TypeScript. |
| `FASTMCP_STRICT_INPUT_VALIDATION` | ❌ | Validación estricta; activa por defecto. |
| `FASTMCP_SERVER_AUTH` | ❌ | Auth del servidor TypeScript. |
| `REDIS_URL` / `DATABASE_URL` | ❌ | Integraciones opcionales. |

Consulta [.env.example](./.env.example) para OAuth, Back4App/Parse, TOON y variables adicionales.

## 🛡️ Seguridad y buenas prácticas

1. Usa secretos del entorno, nunca tokens en código, commits o ejemplos reales.
2. Limita bases y tablas con `AIRTABLE_ALLOWED_BASES` y `AIRTABLE_ALLOWED_TABLES`.
3. Activa `dryRun` antes de escribir desde TypeScript.
4. Usa idempotency keys cuando una operación pueda repetirse.
5. Separa tokens y bases de desarrollo y producción.
6. No expongas HTTP sin autenticación, proxy o red privada.
7. Otorga solo los scopes Airtable necesarios.
8. Configura políticas PII si procesas información sensible.

## 🧪 Calidad y pruebas

```bash
npm run build
npm run test:types
npm run lint
npm run format:check
npm test
```

Las pruebas de integración en `tests/` pueden requerir un servidor disponible y acceso real a Airtable. No las ejecutes contra una base con datos críticos.

```bash
node tests/test_mcp_comprehensive.js
bash tests/test_all_features.sh
```

## 🐳 Docker

```bash
cp .env.example .env
docker compose up --build
```

O con la imagen principal:

```bash
docker build -t airtable-brain-mcp:latest .
docker run --rm --env-file .env -p 8000:8000 airtable-brain-mcp:latest
```

Los Dockerfiles específicos se encuentran en `docker/`.

## 🚂 Railway y Replit

### Railway

El repositorio incluye `railway.json`, `railway.toml` y `Procfile`. `railway.json` usa `python3 app.py` y respeta `PORT`.

Variables mínimas:

```text
AIRTABLE_PERSONAL_ACCESS_TOKEN
AIRTABLE_BASE_ID       # opcional para descubrimiento inicial
LOG_LEVEL=INFO
```

### Replit

El workflow configurado es `Iniciar` y combina `Fastmcp run` con `npm run dev`. Para una ejecución local simple utiliza `npm run dev`. Si ejecutas dos servidores HTTP a la vez, usa puertos distintos para evitar colisiones.

## 📚 Documentación relacionada

- [Guía de despliegue](./DEPLOYMENT.md)
- [Estructura del proyecto](./PROJECT_STRUCTURE.md)
- [Integración con Airtable](./docs/airtable_integration.md)
- [Guía de instalación](./docs/guides/INSTALLATION.md)
- [Inicio rápido](./docs/guides/QUICK_START.md)
- [Despliegue FastMCP](./docs/guides/FASTMCP_DEPLOYMENT.md)
- [Integración Claude](./docs/guides/CLAUDE_INTEGRATION.md)
- [Funciones mejoradas](./docs/guides/ENHANCED_FEATURES.md)
- [OAuth](./src/OAUTH_README.md)
- [Contribución](./CONTRIBUTING.md)
- [Aviso de seguridad](./SECURITY_NOTICE.md)
- [Changelog](./CHANGELOG.md)

## 🤝 Contribuir

1. Revisa la implementación que vas a modificar.
2. Mantén compatibles las rutas y variables existentes cuando sea posible.
3. Añade o actualiza pruebas para nuevas herramientas.
4. Ejecuta build, tipos, lint y formato.
5. Documenta cambios de protocolo, seguridad o configuración.

Consulta [CONTRIBUTING.md](./CONTRIBUTING.md) para el flujo completo.

## 📄 Licencia y atribución

Este proyecto se distribuye bajo la [licencia MIT](./LICENSE) y utiliza:

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP](https://gofastmcp.com/)
- [Airtable Web API](https://airtable.com/developers/web/api/introduction)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)

---

<p align="center">
  <strong>Construido para explorar, automatizar y mejorar la conexión entre agentes de IA y Airtable.</strong><br>
  <sub>Versión del paquete Node: 3.2.7 · Licencia MIT</sub>
</p>