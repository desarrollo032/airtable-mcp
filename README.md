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

El proyecto expone Airtable como herramientas MCP para que clientes como Claude, ChatGPT u otros agentes compatibles puedan:

- 🔎 Descubrir bases, tablas y registros.
- ✍️ Crear y actualizar datos desde lenguaje natural.
- 🧩 Consultar esquemas y metadatos.
- 🔐 Aplicar reglas de gobernanza, listas permitidas y políticas PII.
- 🌐 Ejecutar el servidor mediante STDIO o HTTP.
- 🔌 Integrar OAuth, webhooks y almacenamiento auxiliar cuando el flujo lo requiere.

> **Importante:** este repositorio no es una copia oficial de Airtable ni del protocolo MCP. Las implementaciones se mantienen aquí para mejorar, adaptar y probar funcionalidades sobre la base existente.

## ✨ Capacidades principales

| Área | Capacidades |
| --- | --- |
| 🧠 **MCP** | Herramientas, recursos, prompts y transporte HTTP/STDIO según la implementación elegida. |
| 🗂️ **Airtable** | Descubrimiento de bases, tablas, lectura de registros y operaciones de escritura. |
| 🛡️ **Gobernanza** | Allowlist de bases/tablas, operaciones permitidas, redacción de PII y errores controlados en TypeScript. |
| ⚡ **Rendimiento** | Cliente HTTP asíncrono con `httpx`, operaciones por lotes en la implementación TypeScript y límites de solicitudes. |
| 🔁 **Integraciones** | OAuth 2.0, ChatGPT, webhooks, Redis y almacenamiento Back4App/Mongo en módulos opcionales. |
| 🧰 **DX** | TypeScript tipado, Zod, ESLint, Prettier, Jest, CLI y ejemplos de configuración para clientes MCP. |
| 🚀 **Despliegue** | Replit, Docker Compose, Railway, ejecución local y proceso web compatible con `PORT`. |

## 🧱 Implementaciones disponibles

El repositorio contiene varias implementaciones que comparten el objetivo, pero no exponen exactamente las mismas herramientas.

### ✅ FastMCP Python — recomendada para el entorno actual

Entrada principal: `src/python/inspector_server.py`

Es la ruta usada por `npm run dev` y por el punto de entrada `app.py`. Utiliza FastMCP 2.x, `httpx` y transporte HTTP.

Herramientas disponibles:

| Herramienta | Función |
| --- | --- |
| `list_bases` | Lista las bases accesibles con el token configurado. |
| `list_tables` | Lista las tablas de una base. |
| `list_records` | Consulta registros, con límite y filtro por fórmula. |
| `create_records` | Crea uno o varios registros a partir de JSON. |
| `update_records` | Actualiza registros a partir de JSON o formato TOON. |
| `set_base_id` | Cambia la base activa durante la sesión. |

### 🔐 MCP Python extendido con recursos y prompts

Entrada: `src/python/auth/src/server.py`

Esta variante añade:

- `get_record` y `delete_records`.
- Recursos `airtable://base/{base_id}` y `airtable://base/{base_id}/table/{table_name}`.
- Roots MCP para exportaciones.
- Prompts guiados para análisis, diseño de esquemas y migraciones.
- Completions y parseo JSON/TOON.
- Middleware y puntos de integración para autenticación/OAuth.

### 🔷 TypeScript — gobernanza y operaciones estructuradas

Entrada: `src/typescript/airtable-mcp-server.ts`

Registra herramientas con esquemas Zod y respuestas estructuradas:

`list_bases` · `describe` · `query` · `list_governance` · `list_exceptions` · `create` · `update` · `upsert` · `list_webhooks` · `create_webhook` · `refresh_webhook`

Incluye:

- ✅ Validación estricta de entradas.
- ✅ `dryRun` para revisar cambios antes de escribir.
- ✅ Idempotency keys para operaciones de escritura.
- ✅ Chunking de registros según el límite de Airtable.
- ✅ Allowlist de bases y tablas.
- ✅ Políticas `mask`, `hash` y `drop` para campos sensibles.
- ✅ Rate limiting y registro de excepciones.
- ✅ Transporte STDIO y HTTP/SSE en el servidor TypeScript.

### 📦 JavaScript y OAuth — compatibilidad

- `src/javascript/airtable_simple_production.js`: servidor JavaScript con validación, rate limiting, webhooks y compatibilidad con el flujo HTTP histórico.
- `src/javascript/airtable_simple.js`: implementación JavaScript simple/legacy.
- `src/oauth_server.js`: servidor OAuth separado para el flujo de autorización de Airtable y clientes que necesitan callback.

Estas variantes se conservan para compatibilidad y migración. Para nuevos cambios, prioriza FastMCP Python o TypeScript.

## 🗺️ Arquitectura

```text
┌─────────────────────────────────────────────────────────────────┐
│ Cliente MCP                                                     │
│ Claude Desktop · ChatGPT · Cursor · Windsurf · Inspector        │
└───────────────────────────────┬─────────────────────────────────┘
                                │ MCP / STDIO / HTTP
┌───────────────────────────────▼─────────────────────────────────┐
│ Capa MCP                                                        │
│ FastMCP Python · MCP SDK TypeScript · JavaScript legacy          │
└───────────────────────────────┬─────────────────────────────────┘
                                │ Validación · gobernanza · auth
┌───────────────────────────────▼─────────────────────────────────┐
│ Integración Airtable                                            │
│ Metadata API · Records API · Webhooks · OAuth opcional            │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                         Airtable API
```

### 📁 Estructura relevante

```text
.
├── app.py                         # Entrada web para Railway/Nixpacks
├── main.py                        # Entrada Python alternativa
├── package.json                   # Scripts y dependencias Node/TypeScript
├── requirements.txt               # Dependencias Python/FastMCP
├── fastmcp.json                   # Configuración FastMCP
├── src/
│   ├── python/
│   │   ├── inspector_server.py    # Servidor FastMCP recomendado
│   │   ├── server.py              # Variante FastMCP base
│   │   └── auth/                  # Variante extendida con recursos/prompts
│   ├── typescript/                # Servidor tipado y gobernado
│   ├── javascript/                # Servidores JavaScript compatibles
│   └── oauth_server.js            # Servicio OAuth separado
├── routes/                        # Rutas HTTP auxiliares
├── services/                      # Airtable, auth y almacenamiento
├── middleware/                    # Seguridad y formato TOON
├── tests/                         # Smoke tests e integración
├── examples/                      # Configuraciones y ejemplos
├── docs/                          # Guías y documentación ampliada
├── docker/                        # Imágenes Docker alternativas
└── bin/                           # CLI de servidor y CRUD
```

## 🧰 Stack tecnológico

### Backend y protocolo

- **Python 3.10+** — runtime principal para FastMCP.
- **FastMCP 2.x** — registro de herramientas y transporte MCP.
- **MCP Python SDK** — variante extendida del protocolo.
- **Node.js 18+** — runtime para JavaScript/TypeScript y OAuth.
- **TypeScript 5.3** — implementación con tipos y respuestas estructuradas.
- **`@modelcontextprotocol/sdk`** — servidor MCP para Node.

### Integración y datos

- **Airtable Web API** — bases, esquema, registros y webhooks.
- **`httpx`** — cliente HTTP asíncrono.
- **`requests` / `aiohttp`** — soporte de módulos Python heredados.
- **Redis** — almacenamiento/cache opcional para despliegues multiusuario.
- **Back4App/Parse** — almacenamiento opcional para OAuth y credenciales asociadas.

### Calidad y operación

- **Zod** — validación de entradas/salidas TypeScript.
- **Jest + ts-jest** — pruebas JavaScript/TypeScript.
- **ESLint + Prettier** — calidad y formato.
- **Docker / Docker Compose** — ejecución reproducible.
- **Railway / Replit** — despliegue y ejecución web.

## 🚀 Inicio rápido

### 1. Requisitos

- Python `3.10` o superior.
- Node.js `18` o superior.
- Una cuenta de Airtable.
- Un Personal Access Token de Airtable con los permisos mínimos:
  - `data.records:read`
  - `data.records:write`
  - `schema.bases:read`
  - `webhook:manage` si usarás webhooks.

### 2. Instalar dependencias

```bash
git clone <URL_DEL_REPOSITORIO>
cd airtable-mcp

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

npm ci
```

En Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
npm ci
```

### 3. Configurar el entorno

```bash
cp .env.example .env
```

Configuración mínima para FastMCP Python:

```env
AIRTABLE_PERSONAL_ACCESS_TOKEN=patXXXXXXXXXXXXXX
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO
```

`AIRTABLE_BASE_ID` puede omitirse para comenzar con `list_bases`; las operaciones sobre tablas y registros necesitarán una base activa. También se aceptan los alias `AIRTABLE_PAT`, `AIRTABLE_TOKEN` y `AIRTABLE_API_TOKEN` en las variantes que los implementan.

> 🔒 Nunca guardes tokens en Git. Usa secretos del entorno en Replit, Railway o tu proveedor de despliegue.

### 4. Ejecutar

#### Desarrollo recomendado

```bash
npm run dev
```

Equivale a ejecutar:

```bash
python3 src/python/inspector_server.py
```

#### FastMCP mediante configuración

```bash
source .venv/bin/activate
fastmcp run
```

La configuración se encuentra en `fastmcp.json`. Para producción, el script `npm start` configura HTTP, `0.0.0.0` y el puerto proporcionado por `PORT`.

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

Si el cliente usa un servidor remoto, despliega la variante HTTP y configura la URL MCP que te entregue FastMCP o tu plataforma. No expongas un endpoint de producción sin autenticación o sin una allowlist de bases/tablas.

## 💬 Ejemplos de interacción

Una vez conectado el servidor, puedes pedir:

```text
Lista mis bases de Airtable accesibles.
```

```text
Muéstrame las tablas de la base appXXXXXXXXXXXXXX.
```

```text
Consulta los registros activos de la tabla Projects usando una fórmula de Airtable.
```

```text
Prepara una actualización de estado para estos registros y muéstrame primero el dry run.
```

```text
Describe el esquema de la base y aplica la política de privacidad definida.
```

## ⚙️ Variables de entorno

| Variable | Requerida | Uso |
| --- | :---: | --- |
| `AIRTABLE_PERSONAL_ACCESS_TOKEN` | ✅* | Token PAT preferido por FastMCP Python. |
| `AIRTABLE_PAT` / `AIRTABLE_TOKEN` | ✅* | Alias aceptados por algunas implementaciones. |
| `AIRTABLE_BASE_ID` | ❌ | Base predeterminada; puede configurarse durante la sesión. |
| `AIRTABLE_DEFAULT_BASE` | ❌ | Base predeterminada para TypeScript. |
| `AIRTABLE_ALLOWED_BASES` | ❌ | Lista de bases permitidas separadas por comas. |
| `AIRTABLE_ALLOWED_TABLES` | ❌ | Allowlist TypeScript con formato `baseId:tableName`. |
| `PORT` | ❌ | Puerto HTTP; por defecto `8000` en FastMCP. |
| `HOST` | ❌ | Host local; por defecto `0.0.0.0` en FastMCP. |
| `LOG_LEVEL` | ❌ | `DEBUG`, `INFO`, `WARNING` o `ERROR`. |
| `FASTMCP_TRANSPORT` | ❌ | Transporte de despliegue, normalmente `http`. |
| `FASTMCP_MASK_ERROR_DETAILS` | ❌ | Oculta detalles sensibles en errores TypeScript. |
| `FASTMCP_STRICT_INPUT_VALIDATION` | ❌ | Activa validación estricta; está activa por defecto. |
| `FASTMCP_SERVER_AUTH` | ❌ | Configuración de auth del servidor TypeScript. |
| `REDIS_URL` | ❌ | Redis opcional para almacenamiento/cache. |
| `DATABASE_URL` | ❌ | Base opcional para integraciones TypeScript. |

Consulta [.env.example](./.env.example) para OAuth, Back4App/Parse, TOON y el resto de variables opcionales.

## 🛡️ Seguridad y buenas prácticas

1. **Usa secretos del entorno**, nunca tokens en argumentos, commits o ejemplos reales.
2. **Limita bases y tablas** con `AIRTABLE_ALLOWED_BASES` y `AIRTABLE_ALLOWED_TABLES`.
3. **Activa `dryRun`** antes de crear o actualizar datos desde la implementación TypeScript.
4. **Usa idempotency keys** cuando un cliente pueda repetir una operación de escritura.
5. **Separa desarrollo y producción** con tokens y bases diferentes.
6. **No expongas HTTP directamente** sin autenticación, proxy o una red privada.
7. **Revisa permisos Airtable** y otorga solo los scopes necesarios.
8. **Configura políticas PII** si procesas información sensible.

## 🧪 Calidad y pruebas

Comandos disponibles:

```bash
# Construir TypeScript
npm run build

# Verificación de tipos
npm run test:types

# Linter
npm run lint

# Formato
npm run format:check

# Suite Jest
npm test
```

Las pruebas de integración de `tests/` esperan un servidor disponible y, en varios casos, acceso real a Airtable. Configura las variables de entorno antes de ejecutarlas y evita usar una base con datos críticos.

```bash
# Ejemplos de smoke/integración
node tests/test_mcp_comprehensive.js
bash tests/test_all_features.sh
```

## 🐳 Docker

### Docker Compose

```bash
cp .env.example .env
# completa las variables necesarias
docker compose up --build
```

### Imagen de producción

```bash
docker build -t airtable-brain-mcp:latest .

docker run --rm \
  --env-file .env \
  -p 8000:8000 \
  airtable-brain-mcp:latest
```

Los Dockerfiles específicos se encuentran en `docker/`. Comprueba el `Dockerfile` activo y las variables del proveedor antes de publicar.

## 🚂 Railway y Replit

### Railway

El repositorio incluye `railway.json`, `railway.toml` y `Procfile`. La configuración de Railway usa `python3 app.py` y respeta `PORT`.

Variables mínimas:

```text
AIRTABLE_PERSONAL_ACCESS_TOKEN
AIRTABLE_BASE_ID       # opcional para descubrimiento inicial
LOG_LEVEL=INFO
```

### Replit

El workflow configurado es `Iniciar` y combina:

```text
Fastmcp run
npm run dev
```

Para una ejecución local simple, utiliza `npm run dev`. En caso de probar dos servidores HTTP simultáneamente, asigna puertos distintos para evitar colisiones.

## 📚 Documentación del repositorio

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

Las mejoras son bienvenidas. Antes de abrir un cambio:

1. Revisa la implementación que vas a modificar.
2. Mantén compatibles las rutas y variables existentes cuando sea posible.
3. Añade o actualiza pruebas para nuevas herramientas.
4. Ejecuta build, tipos, lint y formato.
5. Documenta cambios de protocolo, seguridad o configuración.

Consulta [CONTRIBUTING.md](./CONTRIBUTING.md) para conocer el flujo completo.

## 📄 Licencia y atribución

Este proyecto se distribuye bajo la [licencia MIT](./LICENSE). Se apoya en:

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP](https://gofastmcp.com/)
- [Airtable Web API](https://airtable.com/developers/web/api/introduction)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)

---

<p align="center">
  <strong>Construido para explorar, automatizar y mejorar la conexión entre agentes de IA y Airtable.</strong><br>
  <sub>Versión del paquete Node: 3.2.5 · Licencia MIT</sub>
</p>