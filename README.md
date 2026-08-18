# 🚀 Airtable MCP Server

<div align="center">
  <img src="https://img.shields.io/badge/MCP-3.2.7-blue?style=for-the-badge&logo=airtable" alt="MCP Version" />
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/TypeScript-5.3-blue?style=for-the-badge&logo=typescript" alt="TypeScript" />
  <img src="https://img.shields.io/badge/FastMCP-Modern-orange?style=for-the-badge" alt="FastMCP" />
  <img src="https://img.shields.io/badge/Protocol-2024--11--05-success?style=for-the-badge" alt="Protocol" />
</div>

<br />

🤖 **Agente IA Revolucionario** - Servidor Airtable MCP avanzado impulsado por IA con integración de **FastMCP**, transporte HTTP/SSE para streaming en tiempo real, NLP, y compatibilidad con arquitecturas multi-lenguaje.

---

## 📑 Índice

- [Acerca del Proyecto](#-acerca-del-proyecto)
- [Stack Tecnológico](#-stack-tecnológico)
- [Características Principales](#-características-principales)
- [Suite de Inteligencia IA](#-suite-de-inteligencia-ia)
- [Requisitos Previos](#-requisitos-previos)
- [Inicio Rápido](#-inicio-rápido)
- [Herramientas Disponibles](#-herramientas-disponibles)
- [Documentación y Soporte](#-documentación-y-soporte)

---

## 🌟 Acerca del Proyecto

**Airtable MCP Server** (Model Context Protocol) es un servidor diseñado para integrar inteligencia artificial con operaciones de Airtable. Permite a los LLM (como Claude) y otros clientes MCP interactuar con tus bases de datos Airtable utilizando lenguaje natural, ejecutar operaciones complejas, analizar datos y automatizar flujos de trabajo.

---

## 🛠️ Stack Tecnológico

Este proyecto utiliza un stack moderno para garantizar alto rendimiento, escalabilidad y facilidad de integración:

*   **Lenguajes:** Python (Backend Principal) y Node.js/TypeScript.
*   **Framework de Servidor:** `FastMCP` para la integración del protocolo Model Context Protocol, proporcionando transporte eficiente HTTP/SSE.
*   **Networking:** `aiohttp` para operaciones asíncronas de red en Python.
*   **Configuración y Validación:** `pydantic_settings` (Python) y `zod` (TypeScript).
*   **Despliegue:** Optimizado para Docker y entornos en la nube como Railway.

---

## ✨ Características Principales

*   🗣️ **Lenguaje Natural a Airtable (NLP):** Parsea consultas en lenguaje natural para realizar operaciones de bases de datos.
*   🔄 **Operaciones CRUD Completas:** Crear, leer, actualizar y eliminar registros de manera programática.
*   🏗️ **Gestión de Esquemas:** Control total sobre bases, tablas, y campos.
*   ⚡ **Operaciones por Lotes:** Procesa múltiples registros de manera eficiente (hasta 10 a la vez).
*   🌐 **Integración de Webhooks:** Escucha y gestiona eventos en tiempo real.
*   🔐 **Seguridad Integrada:** Soporte OAuth 2.0 y validaciones estrictas.
*   🐳 **Docker-Ready:** Imágenes optimizadas y despliegue simple mediante `docker-compose`.

---

## 🧠 Suite de Inteligencia IA

Aprovecha al máximo el potencial de la IA con nuestras herramientas y prompts integrados:

*   📊 **Análisis Predictivo:** Pronóstico de tendencias de datos.
*   📈 **Inteligencia Empresarial (BI):** Descubrimiento de patrones y reportes de calidad.
*   📐 **Diseño de Esquemas Inteligente:** Recomendaciones automatizadas de estructura de base de datos.
*   🚀 **Optimización de Flujos:** Recomendaciones de automatización de tareas.

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener lo siguiente:

1.  **Node.js 18+** o **Python 3.10+**.
2.  Una cuenta de Airtable con un **Token de Acceso Personal**.
3.  Ámbitos requeridos para el Token:
    *   `data.records:read` & `data.records:write`
    *   `schema.bases:read` & `schema.bases:write`
    *   `webhook:manage`

---

## 🚀 Inicio Rápido

### 1️⃣ Configuración de Variables de Entorno

Crea un archivo `.env` en la raíz de tu proyecto:

```env
AIRTABLE_TOKEN=tu_token_de_acceso_personal
AIRTABLE_BASE_ID=tu_id_de_base_opcional
```

> **Nota:** En versiones modernas, el `AIRTABLE_BASE_ID` es opcional, ya que el servidor puede descubrir bases a las que tienes acceso de forma dinámica.

### 2️⃣ Instalación y Ejecución

**Vía NPM (Para Node/TypeScript):**
```bash
npm install
npm run dev
```

**Vía Python (Recomendado con FastMCP):**
```bash
pip install -r requirements.txt
python3 src/python/inspector_server.py
```

### 3️⃣ Integración con Claude Desktop

Agrega la configuración en tu cliente MCP (ej. Claude Desktop):

```json
{
  "mcpServers": {
    "airtable-fastmcp": {
      "command": "fastmcp",
      "args": ["run", "src/python/inspector_server.py:mcp"],
      "env": {
        "AIRTABLE_TOKEN": "TU_TOKEN_AIRTABLE"
      }
    }
  }
}
```

---

## 🛠️ Herramientas Disponibles

El servidor expone más de **30 herramientas** categorizadas para el LLM:

| Categoría | Herramientas Destacadas | Descripción |
| :--- | :--- | :--- |
| **🔍 Consultas** | `list_records`, `search_records` | Buscar y listar información. |
| **✍️ Edición** | `create_record`, `update_record` | Manipular registros. |
| **🏗️ Estructura** | `list_bases`, `describe_table` | Explorar la estructura de la BD. |
| **⚡ Lotes** | `batch_create_records` | Operaciones masivas. |
| **🪝 Webhooks**| `create_webhook`, `list_webhooks` | Integraciones en tiempo real. |

---

## 📖 Documentación y Soporte

*   **Problemas y Bugs:** [GitHub Issues](https://github.com/rashidazarang/airtable-mcp/issues)
*   **Guía de Contribución:** [CONTRIBUTING.md](./CONTRIBUTING.md)
*   **Licencia:** MIT - Ver [LICENSE](./LICENSE)

<br />
<div align="center">
  Hecho con ❤️ para la comunidad de desarrollo IA.
</div>
