# Servidor Airtable MCP

[![MCP](https://img.shields.io/badge/MCP-3.2.6-blue)](https://github.com/rashidazarang/airtable-mcp) [![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue)](https://www.typescriptlang.org/) [![AI Agent](https://img.shields.io/badge/AI_Agent-Enhanced-purple)](https://github.com/rashidazarang/airtable-mcp) [![Security](https://img.shields.io/badge/Security-Enterprise-green)](https://github.com/rashidazarang/airtable-mcp) [![Protocol](https://img.shields.io/badge/Protocol-2024--11--05-success)](https://modelcontextprotocol.io/) [![FastMCP](https://img.shields.io/badge/FastMCP-Modern-orange)](https://github.com/rashidazarang/airtable-mcp)

🤖 **Agente IA Revolucionario v3.2.6** - Servidor Airtable MCP avanzado impulsado por IA con **integración FastMCP moderna**, transporte HTTP/SSE para streaming en tiempo real, despliegue optimizado en Railway, y arquitectura multi-lenguaje con compatibilidad completa.

---

## 📑 Tabla de Contenidos

- [Últimas Versiones](#últimas-versiones)
- [Suite de Inteligencia IA](#-suite-de-inteligencia-ia)
- [Características Principales](#-características)
- [Requisitos Previos](#-requisitos-previos)
- [Inicio Rápido](#-inicio-rápido)
- [Ejemplos de Uso](#-ejemplos-de-uso)
- [Herramientas Disponibles](#-herramientas-disponibles-33-total)
- [Configuración Avanzada](#-configuración-avanzada)
- [Pruebas](#-pruebas)
- [Solución de Problemas](#-solución-de-problemas)
- [Documentación](#-documentación)

---

## Últimas Versiones

### 🚀 v3.2.6 - Integración FastMCP Moderna y Despliegue Optimizado

**Mejoras Principales** con compatibilidad completa con versiones anteriores:
- ⚡ **FastMCP Moderno** - Integración completa con FastMCP para transporte HTTP/SSE
- 🌐 **Transporte HTTP con SSE** - Streaming en tiempo real para aplicaciones de producción
- 🚂 **Despliegue Railway Optimizado** - Configuración Docker builder con manejo dinámico de puertos
- 🏗️ **Arquitectura Multi-Lenguaje** - Soporte completo para Python, Node.js y TypeScript
- 🔧 **Configuración Automática** - Auto-detección de STDIO/HTTP según entorno
- 📦 **Sin Compilación en GitHub Actions** - Ejecución directa sin pasos de build
- 🐳 **Docker Producción** - Imágenes optimizadas para Railway y entornos de producción
- 🔄 **Comandos Diferenciados** - `npm run dev` para desarrollo, `npm start` para producción

### 🚀 v3.2.5 - ID de Base Opcional y Soporte Mejorado para Múltiples Bases

**Mejoras Principales** con compatibilidad completa con versiones anteriores:
- �� **ID de Base Opcional** - Comience sin especificar una base, descúbralas usando la herramienta `list_bases`
- 🔍 **Descubrimiento de Base Mejorado** - Nueva herramienta `list_bases` completamente implementada en TypeScript
- 🎯 **Selección de Base Dinámica** - Especifique IDs de base por llamada de herramienta, sin requisito de inicio
- ✅ **Problema #9 Resuelto** - Resolvió la limitación "base requerida al inicio"
- 🔧 **Gobernanza Mejorada** - Manejo inteligente de lista blanca de base para flujos de trabajo multi-base
- 📦 **Soporte Completo de STDIO** - Compatibilidad confirmada con Claude Desktop/Code

### 📋 v3.2.4 - Corrección de Seguridad XSS y Protección Completa

**Mejoras Principales** con compatibilidad completa con versiones anteriores:
- 🔧 **Arquitectura TypeScript Reparada** - Se resolvieron problemas de compilación, separación adecuada de tipos y código en tiempo de ejecución
- 📁 **Organización de Clase Mundial** - Proyecto reestructurado con src/typescript, src/javascript, src/python
- 🔒 **Corrección de Seguridad Completa** - Vulnerabilidad de inyección de comandos completamente resuelta con validación integral
- 🔷 **Implementación de TypeScript** - Servidor completamente seguro de tipos con validación estricta
- 📘 **Definiciones de Tipo Integrales** - Todos los 33 herramientas y 10 mensajes de IA completamente tipificados
- 🛡️ **Seguridad en Tiempo de Compilación** - Detecte errores antes de la ejecución con verificación de tipos avanzada
- 🎯 **Experiencia del Desarrollador** - Soporte para IntelliSense, autocompletado y refactorización
- 🔄 **Distribución Dual** - Use con JavaScript o TypeScript, su elección

---

## 🤖 Suite de Inteligencia IA

**Inteligencia Completa Impulsada por IA** con capacidades empresariales:
- 🤖 **10 Plantillas de Mensajes IA** - Análisis avanzado, predicciones y automatización
- 🔮 **Análisis Predictivo** - Pronóstico y análisis de tendencias con intervalos de confianza
- 🗣️ **Procesamiento de Lenguaje Natural** - Consulte sus datos usando lenguaje humano
- �� **Inteligencia Empresarial** - Información automatizada y recomendaciones
- 🏗️ **Diseño de Esquema Inteligente** - Arquitectura de base de datos optimizada para IA
- ⚡ **Automatización de Flujos de Trabajo** - Optimización de procesos inteligente
- 🔍 **Auditoría de Calidad de Datos** - Evaluación de calidad integral y correcciones
- 📈 **Análisis Estadístico** - Análisis avanzado con pruebas de significancia

---

## ✨ Características

### 🔍 Datos y Consultas
- **Consultas de Lenguaje Natural** - Haga preguntas sobre sus datos en inglés simple
- **Operaciones CRUD Completas** - Crear, leer, actualizar y eliminar registros
- **Descubrimiento de Bases** - Explore todas las bases accesibles y sus esquemas

### 🏗️ Gestión de Estructura
- **Gestión Avanzada de Esquemas** - Crear tablas, campos y gestionar la estructura de base
- **Gestión de Campos** - Agregue, modifique y elimine campos programáticamente
- **Operaciones por Lotes** - Crear, actualizar, eliminar hasta 10 registros a la vez

### 🌐 Integración y Webhooks
- **Gestión de Webhooks** - Crear y gestionar webhooks para notificaciones en tiempo real
- **Gestión de Adjuntos** - Cargue archivos a través de URLs a campos de adjuntos
- **Herramientas de Colaboración** - Gestione colaboradores de base y vistas compartidas

### 🔐 Seguridad y Rendimiento
- **Autenticación Segura** - Utiliza variables de entorno para credenciales
- **Seguridad Empresarial** - OAuth2, limitación de velocidad, validación integral
- **Rápido y Confiable** - Construido con Node.js para rendimiento óptimo

### 🎯 Herramientas y APIs
- **33 Herramientas Potentes** - Cobertura completa de API Airtable con operaciones por lotes
- **Integración IA** - Mensajes y muestreo para operaciones de datos inteligentes
- **Configuración Fácil** - Múltiples opciones de instalación disponibles

---

## 📋 Requisitos Previos

- Node.js 14+ instalado en su sistema
- Una cuenta Airtable con Token de Acceso Personal
- Su ID de Base Airtable (opcional en v3.2.5+)

---

## 🚀 Inicio Rápido

### Paso 1: Obtenga sus Credenciales de Airtable

#### 1. Token de Acceso Personal
Visite [Cuenta de Airtable](https://airtable.com/account) → Cree un token con los siguientes ámbitos:
- `data.records:read` - Leer registros de tablas
- `data.records:write` - Crear, actualizar, eliminar registros
- `schema.bases:read` - Ver esquemas de tablas
- `schema.bases:write` - **Nuevo en v1.5.0** - Crear/modificar tablas y campos
- `webhook:manage` - (Opcional) Para características de webhook

#### 2. ID de Base
Abra su base Airtable y copie el ID de la URL:
```
https://airtable.com/[BASE_ID]/...
```

### Paso 2: Instalación

Elija uno de estos métodos de instalación:

#### 🚀 FastMCP (Recomendado - v3.2.x+)

**Nueva versión con FastMCP moderno:**
```bash
# Instalar FastMCP CLI
pip install fastmcp

# Ejecutar el servidor
fastmcp run

# Para desarrollo con auto-reload
npm run dev

# Para producción (Railway)
npm start
```

**Características de FastMCP:**
- ✅ Transporte HTTP con SSE para streaming en tiempo real
- ✅ Configuración automática de STDIO/HTTP según entorno
- ✅ Compatible con Railway, Docker y desarrollo local
- ✅ No requiere compilación en GitHub Actions

#### 🔷 TypeScript (Desarrollo Avanzado)

```bash
# Instalar con soporte de TypeScript
npm install -g @rashidazarang/airtable-mcp

# Para desarrollo con tipos
npm install --save-dev typescript @types/node
```

#### 📦 JavaScript (Legacy)

**Opción A: Instalar a través de NPM**
```bash
npm install -g @rashidazarang/airtable-mcp
```

**Opción B: Clonar desde GitHub**
```bash
git clone https://github.com/rashidazarang/airtable-mcp.git
cd airtable-mcp
npm install
```

### Paso 3: Configurar Variables de Entorno

Cree un archivo `.env` en su directorio de proyecto:

```env
AIRTABLE_TOKEN=su_token_de_acceso_personal_aqui
AIRTABLE_BASE_ID=su_id_de_base_aqui  # OPCIONAL - puede ser descubierto usando la herramienta list_bases
```

**Nuevo en v3.2.5**: ¡El `AIRTABLE_BASE_ID` ahora es **opcional**! Puede:
- Comenzar sin un ID de base y usar la herramienta `list_bases` para descubrir sus bases accesibles
- Especificar IDs de base dinámicamente en cada llamada de herramienta
- Establecer una base predeterminada por conveniencia (recomendado)

**Nota de Seguridad**: ¡Nunca confirme archivos `.env` al control de versiones!

### Paso 4: Configure su Cliente MCP

#### 🚀 FastMCP (Recomendado - v3.2.x+)

**Configuración moderna con FastMCP:**

```json
{
  "mcpServers": {
    "airtable-fastmcp": {
      "command": "fastmcp",
      "args": ["run"],
      "env": {
        "AIRTABLE_TOKEN": "SU_TOKEN_AIRTABLE",
        "AIRTABLE_BASE_ID": "SU_ID_DE_BASE"
      }
    }
  }
}
```

**Ventajas de FastMCP:**
- ✅ Auto-detección de transporte (STDIO para desarrollo, HTTP para producción)
- ✅ Soporte SSE para streaming en tiempo real
- ✅ Configuración simplificada
- ✅ Compatible con Railway y Docker

#### 🔷 TypeScript (Experiencia Mejorada del Desarrollador)

```json
{
  "mcpServers": {
    "airtable-typescript": {
      "command": "npx",
      "args": ["@rashidazarang/airtable-mcp"],
      "env": {
        "AIRTABLE_TOKEN": "SU_TOKEN_AIRTABLE",
        "AIRTABLE_BASE_ID": "SU_ID_DE_BASE",
        "NODE_ENV": "production",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### 📦 JavaScript (Legacy)

```json
{
  "mcpServers": {
    "airtable": {
      "command": "npx",
      "args": ["@rashidazarang/airtable-mcp"],
      "env": {
        "AIRTABLE_TOKEN": "SU_TOKEN_AIRTABLE",
        "AIRTABLE_BASE_ID": "SU_ID_DE_BASE"
      }
    }
  }
}
```

#### Sin ID de Base (¡Nuevo!)

Comience sin especificar una base y descúbralas dinámicamente:

```json
{
  "mcpServers": {
    "airtable": {
      "command": "fastmcp",
      "args": ["run"],
      "env": {
        "AIRTABLE_TOKEN": "SU_TOKEN_AIRTABLE"
      }
    }
  }
}
```

¡Luego use la herramienta `list_bases` para descubrir sus bases accesibles!

### Paso 5: Reinicie su Cliente MCP

Después de la configuración, reinicie Claude Desktop o su cliente MCP para cargar el servidor de Airtable.

---

## 🎯 Ejemplos de Uso

Una vez configurado, puede interactuar con sus datos de Airtable naturalmente:

### 🔷 Desarrollo con TypeScript

```typescript
import { 
  AirtableMCPServer, 
  ListRecordsInput, 
  AnalyzeDataPrompt 
} from '@rashidazarang/airtable-mcp/types';

const server = new AirtableMCPServer();

// Operaciones de datos seguras de tipos
const params: ListRecordsInput = {
  table: 'Tasks',
  maxRecords: 10,
  filterByFormula: "Status = 'Active'"
};

const records = await server.handleToolCall('list_records', params);

// Análisis IA seguro de tipos
const analysis: AnalyzeDataPrompt = {
  table: 'Sales',
  analysis_type: 'predictive',
  confidence_level: 0.95
};

const insights = await server.handlePromptGet('analyze_data', analysis);
```

### 📦 Interacciones en Lenguaje Natural

**Operaciones Básicas**
```
"Listar todas mis bases Airtable accesibles"
"Mostrarme todos los registros en la tabla Proyectos"
"Crear una nueva tarea con prioridad 'Alta' y fecha de vencimiento mañana"
"Actualizar el estado de la tarea ID rec123 a 'Completado'"
"Eliminar todos los registros donde el estado sea 'Archivado'"
"¿Qué tablas hay en mi base?"
"Buscar registros donde Estado sea igual a 'Activo'"
```

**Operaciones de Webhook (v1.4.0+)**
```
"Crear un webhook para mi tabla que notifique a https://mi-app.com/webhook"
"Listar todos los webhooks activos en mi base"
"Mostrarme los webhooks recientes"
"Eliminar webhook ach123xyz"
```

**Gestión de Esquemas (v1.5.0+)**
```
"Listar todas mis bases Airtable accesibles"
"Mostrarme el esquema completo para esta base"
"Describir la tabla Proyectos con todos los detalles de campo"
"Crear una nueva tabla llamada 'Tareas' con campos Nombre, Prioridad y Fecha de Vencimiento"
"Agregar un campo de Estado a la tabla Proyectos existente"
"¿Qué tipos de campos están disponibles en Airtable?"
```

**Operaciones por Lotes y Adjuntos (v1.6.0+)**
```
"Crear 5 registros nuevos a la vez en la tabla Tareas"
"Actualizar múltiples registros con nuevos valores de estado"
"Eliminar estos 3 registros en una operación"
"Adjuntar esta URL de imagen al campo de foto del registro"
"¿Quiénes son los colaboradores en esta base?"
"Mostrarme todas las vistas compartidas en esta base"
```

---

## 🛠️ Herramientas Disponibles (33 Total)

### 📊 Operaciones de Datos (7 herramientas)
| Herramienta | Descripción |
|---|---|
| `list_tables` | Obtener todas las tablas en su base con información de esquema |
| `list_records` | Consultar registros con filtrado y paginación opcional |
| `get_record` | Recuperar un registro único por ID |
| `create_record` | Agregar nuevos registros a cualquier tabla |
| `update_record` | Modificar campos de registros existentes |
| `delete_record` | Eliminar registros de una tabla |
| `search_records` | Búsqueda avanzada con fórmulas de Airtable y ordenamiento |

### 🪝 Gestión de Webhooks (5 herramientas)
| Herramienta | Descripción |
|---|---|
| `list_webhooks` | Ver todos los webhooks configurados para su base |
| `create_webhook` | Configurar notificaciones en tiempo real para cambios de datos |
| `delete_webhook` | Eliminar configuraciones de webhook |
| `get_webhook_payloads` | Recuperar historial de notificaciones de webhook |
| `refresh_webhook` | Extender tiempo de vencimiento de webhook |

### 🔍 Descubrimiento de Esquema (6 herramientas) - **Nuevo en v1.5.0**
| Herramienta | Descripción |
|---|---|
| `list_bases` | Listar todas las bases Airtable accesibles con permisos |
| `get_base_schema` | Obtener información de esquema completa para cualquier base |
| `describe_table` | Obtener información de tabla detallada incluyendo todas las especificaciones de campo |
| `list_field_types` | Guía de referencia para todos los tipos de campos de Airtable disponibles |
| `get_table_views` | Listar todas las vistas para una tabla específica con configuraciones |

### 🏗️ Gestión de Tablas (3 herramientas) - **Nuevo en v1.5.0**
| Herramienta | Descripción |
|---|---|
| `create_table` | Crear nuevas tablas con definiciones de campo personalizadas |
| `update_table` | Modificar nombres y descripciones de tablas |
| `delete_table` | Eliminar tablas (requiere confirmación de seguridad) |

### 🔧 Gestión de Campos (3 herramientas) - **Nuevo en v1.5.0**
| Herramienta | Descripción |
|---|---|
| `create_field` | Agregar nuevos campos a tablas existentes con todos los tipos de campo |
| `update_field` | Modificar propiedades de campo, nombres y opciones |
| `delete_field` | Eliminar campos (requiere confirmación de seguridad) |

### ⚡ Operaciones por Lotes (4 herramientas) - **Nuevo en v1.6.0**
| Herramienta | Descripción |
|---|---|
| `batch_create_records` | Crear hasta 10 registros a la vez para mejor rendimiento |
| `batch_update_records` | Actualizar hasta 10 registros simultáneamente |
| `batch_delete_records` | Eliminar hasta 10 registros en una sola operación |
| `batch_upsert_records` | Actualizar registros existentes o crear nuevos basados en campos clave |

### 📎 Gestión de Adjuntos (1 herramienta) - **Nuevo en v1.6.0**
| Herramienta | Descripción |
|---|---|
| `upload_attachment` | Adjuntar archivos desde URLs públicas a campos de adjuntos |

### 👁️ Vistas Avanzadas (2 herramientas) - **Nuevo en v1.6.0**
| Herramienta | Descripción |
|---|---|
| `create_view` | Crear nuevas vistas (cuadrícula, formulario, calendario, etc.) con configuraciones personalizadas |
| `get_view_metadata` | Obtener información de vista detallada incluyendo filtros y ordenamientos |

### 🏢 Gestión de Base (3 herramientas) - **Nuevo en v1.6.0**
| Herramienta | Descripción |
|---|---|
| `create_base` | Crear nuevas bases Airtable con estructuras de tabla iniciales |
| `list_collaborators` | Ver colaboradores de base y sus niveles de permiso |
| `list_shares` | Listar vistas compartidas y sus configuraciones públicas |

### 🤖 Suite de Inteligencia IA (10 prompts) - **Nuevo en v3.0.0**
| Prompt | Descripción | Características Empresariales |
|---|---|---|
| `analyze_data` | Análisis estadístico avanzado con información de ML | Intervalos de confianza, detección de anomalías |
| `create_report` | Generación inteligente de informes con recomendaciones | Personalización multi-interesado, análisis de ROI |
| `data_insights` | Inteligencia empresarial y descubrimiento de patrones | Correlaciones entre tablas, indicadores predictivos |
| `optimize_workflow` | Recomendaciones de automatización impulsadas por IA | Gestión de cambios, hojas de ruta de implementación |
| `smart_schema_design` | Optimización de base de datos con mejores prácticas | Cumplimiento de GDPR y HIPAA, planificación de escalabilidad |
| `data_quality_audit` | Evaluación de calidad integral y correcciones | Remediación automatizada, marcos de gobernanza |
| `predictive_analytics` | Pronóstico y predicción de tendencias | Múltiples algoritmos, cuantificación de incertidumbre |
| `natural_language_query` | Procesamiento inteligente de preguntas humanas | Conciencia de contexto, puntuación de confianza |
| `smart_data_transformation` | Procesamiento de datos asistido por IA | Reglas de calidad, pistas de auditoría, optimización |
| `automation_recommendations` | Sugerencias de optimización de flujos de trabajo | Viabilidad técnica, análisis de costo-beneficio |

---

## 🔧 Configuración Avanzada

### Usando con Smithery Cloud

Para servidores MCP alojados en la nube:

```json
{
  "mcpServers": {
    "airtable": {
      "command": "npx",
      "args": [
        "@smithery/cli",
        "run",
        "@rashidazarang/airtable-mcp",
        "--token",
        "SU_TOKEN",
        "--base",
        "SU_ID_DE_BASE"
      ]
    }
  }
}
```

### Ejecución Directa de Node.js

Si clonó el repositorio:

```json
{
  "mcpServers": {
    "airtable": {
      "command": "node",
      "args": [
        "/ruta/a/airtable-mcp/airtable_simple.js",
        "--token",
        "SU_TOKEN",
        "--base",
        "SU_ID_DE_BASE"
      ]
    }
  }
}
```

---

## 🧪 Pruebas

### 🔷 TypeScript

Ejecute el conjunto de pruebas integral de TypeScript:

```bash
# Instale las dependencias primero
npm install

# Ejecutar verificación de tipos de TypeScript
npm run test:types

# Ejecutar conjunto de pruebas completo de TypeScript
npm run test:ts

# Construir y probar servidor de TypeScript
npm run build
npm run start:ts
```

**El conjunto de pruebas valida:**
- Seguridad de Tipos - Validación en tiempo de compilación de todas las interfaces
- Pruebas Empresariales - 33 herramientas con verificación de tipos estricta
- Validación de Prompts IA - Todos los 10 templates de IA con tipificación adecuada
- Manejo de Errores - Gestión de errores segura de tipos
- Rendimiento - Operaciones concurrentes con seguridad de tipos
- Integración - Cumplimiento completo del protocolo MCP

### 📦 JavaScript

Ejecute el conjunto de pruebas integral para verificar todas las 33 herramientas:

```bash
# Establecer variables de entorno primero
export AIRTABLE_TOKEN=su_token
export AIRTABLE_BASE_ID=su_id_de_base

# Iniciar el servidor
node airtable_simple.js &

# Ejecutar pruebas integrales (v1.6.0+)
./test_v1.6.0_comprehensive.sh
```

**El conjunto de pruebas valida:**
- Todas las 33 herramientas con llamadas reales a API
- Operaciones CRUD completas
- Gestión avanzada de esquemas
- Operaciones por lotes (crear/actualizar/eliminar múltiples registros)
- Gestión de adjuntos a través de URLs
- Creación de vistas avanzadas y metadatos
- Herramientas de gestión de base y colaboración
- Gestión de webhooks
- Manejo de errores y casos límite
- Verificación de seguridad
- Cobertura de pruebas del 100%

---

## 🐛 Solución de Problemas

### Error "Conexión Rechazada"
- Asegúrese de que el servidor MCP esté funcionando
- Compruebe que el puerto 8010 no esté bloqueado
- Reinicie su cliente MCP

### Error "Token Inválido"
- Verifique que su Token de Acceso Personal sea correcto
- Compruebe que el token tenga los ámbitos requeridos
- Asegúrese de que no haya espacios adicionales en sus credenciales

### Error "Base No Encontrada"
- Confirme que su ID de Base sea correcto
- Compruebe que su token tenga acceso a la base

### Conflictos de Puerto
Si el puerto 8010 está en uso:
```bash
lsof -ti:8010 | xargs kill -9
```

---

## 📚 Documentación

### 🔷 Documentación de TypeScript
- 📘 [Ejemplos de TypeScript](./examples/typescript/) - Ejemplos de uso completo seguro de tipos
- 🏗️ [Definiciones de Tipo](./types/) - Definiciones de tipo integrales para todas las características
- 🧪 [Pruebas de TypeScript](./src/test-suite.ts) - Marco de pruebas de nivel empresarial

### 📦 Documentación General  
- 🎆 [Notas de la Versión v3.1.0](./RELEASE_NOTES_v3.1.0.md) - **Último lanzamiento de TypeScript**
- [Notas de la Versión v1.6.0](./RELEASE_NOTES_v1.6.0.md) - Lanzamiento de características principales
- [Notas de la Versión v1.5.0](./RELEASE_NOTES_v1.5.0.md)
- [Notas de la Versión v1.4.0](./RELEASE_NOTES_v1.4.0.md)
- [Guía de Configuración Detallada](./CLAUDE_INTEGRATION.md)
- [Guía de Desarrollo](./DEVELOPMENT.md)
- [Aviso de Seguridad](./SECURITY_NOTICE.md)

---

## 📦 Historial de Versiones

| Versión | Fecha | Descripción |
|---------|-------|-------------|
| **v3.1.0** | 2025-08-16 | �� Soporte de TypeScript: Seguridad de tipos de nivel empresarial, distribución dual JS/TS |
| **v3.0.0** | 2025-08-16 | 🤖 Agente IA Revolucionario: 10 prompts inteligentes, análisis predictivo |
| **v2.2.3** | 2025-08-16 | 🔒 Lanzamiento de seguridad: Correcciones XSS y validación mejorada |
| **v2.2.0** | 2025-08-16 | 🏆 Implementación completa del protocolo MCP 2024-11-05 |
| **v1.6.0** | 2025-08-15 | 🎆 Operaciones por lotes y gestión de adjuntos (33 herramientas) |
| **v1.5.0** | 2025-08-15 | Gestión integral de esquemas (23 herramientas) |
| **v1.4.0** | 2025-08-14 | Soporte de webhook y operaciones CRUD mejoradas (12 herramientas) |
| **v1.2.4** | 2025-08-12 | Correcciones de seguridad y mejoras de estabilidad |
| **v1.2.3** | 2025-08-11 | Correcciones de errores y manejo de errores |
| **v1.2.2** | 2025-08-10 | Lanzamiento estable inicial |

---

## 📂 Estructura del Proyecto

```
airtable-mcp/
├── src/                    # Código fuente
│   ├── index.js           # Punto de entrada principal
│   ├── typescript/        # Implementación de TypeScript
│   ├── javascript/        # Implementación de JavaScript
│   └── python/            # Implementación de Python
├── dist/                  # Salida de TypeScript compilada
├── docs/                  # Documentación
│   ├── guides/           # Guías de usuario
│   └── releases/         # Notas de lanzamiento
├── tests/                # Archivos de prueba
├── examples/             # Ejemplos de uso
└── types/                # Definiciones de tipo de TypeScript
```

---

## 🤝 Contribuyendo

¡Las contribuciones son bienvenidas! Siéntase libre de enviar una Solicitud de Extracción. Para cambios principales, abra un problema primero para discutir lo que le gustaría cambiar.

Para más detalles, consulte [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## 📄 Licencia

Licencia MIT - vea el archivo [LICENSE](./LICENSE) para más detalles

---

## 🙏 Agradecimientos

- Construido para el [Protocolo de Contexto de Modelo](https://modelcontextprotocol.io/)
- Impulsado por [API de Airtable](https://airtable.com/developers/web/api/introduction)
- Compatible con [Claude Desktop](https://claude.ai/) y otros clientes MCP

---

## �� Soporte

- **Problemas**: [Problemas de GitHub](https://github.com/rashidazarang/airtable-mcp/issues)
- **Discusiones**: [Discusiones de GitHub](https://github.com/rashidazarang/airtable-mcp/discussions)

---

**Versión**: 3.2.5 | **Estado**: 🔷 TypeScript Estable + 🤖 Agente IA | **Protocolo MCP**: 2024-11-05 Completo | **Seguridad de Tipos**: Nivel Empresarial | **Inteligencia**: 10 Prompts de IA | **Seguridad**: Completamente Parcheada | **Última Actualización**: 7 de Diciembre de 2025
