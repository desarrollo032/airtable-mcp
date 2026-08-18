# Changelog - Airtable MCP Server

## [3.2.7] - 2025-12-07

### 🎉 Major Release - Integración Completa OAuth + FastMCP

#### ✨ Added
- **34 herramientas MCP** implementadas con cobertura completa de scopes
- **OAuth 2.0 integration completa** con soporte para todos los scopes de Airtable
- **FastMCP moderno** con transporte HTTP/SSE para streaming en tiempo real
- **Back4App integration** para almacenamiento seguro de tokens OAuth
- **Sistema de comentarios completo** (get_record_comments, create_record_comment, update_record_comment, delete_record_comment)
- **Gestión avanzada de schema** (create_field, update_field, delete_field, create_table, update_table, delete_table)
- **Webhooks avanzados** con debugging y renovación automática
- **Gestión de Blocks** con validación de configuración e historial de versiones
- **Información de usuario** con verificación de permisos por base

#### 🔐 OAuth Scopes Support
- `data.records:read` - Lectura de registros ✅
- `data.records:write` - Escritura de registros ✅
- `data.recordComments:read` - Leer comentarios ✅
- `data.recordComments:write` - Escribir comentarios ✅
- `schema.bases:read` - Leer estructura de bases ✅
- `schema.bases:write` - Escribir estructura de bases ✅
- `webhook:manage` - Gestionar webhooks ✅
- `block:manage` - Gestionar Blocks ✅
- `user.email:read` - Información de usuario ✅

#### 🛠️ Herramientas MCP Nuevas (28 adicionales)
**Comentarios (4):**
- `get_record_comments_by_id` - Ver comentarios de un registro
- `create_record_comment_by_id` - Crear nuevo comentario
- `update_record_comment_by_id` - Actualizar comentario existente
- `delete_record_comment_by_id` - Eliminar comentario

**Schema Management (7):**
- `get_base_schema_detailed` - Ver estructura detallada de base
- `create_table_field` - Crear nuevo campo en tabla
- `update_table_field` - Modificar campo existente
- `delete_table_field` - Eliminar campo
- `create_new_table` - Crear nueva tabla
- `update_existing_table` - Modificar tabla existente
- `delete_existing_table` - Eliminar tabla

**Webhooks Avanzados (6):**
- `list_all_webhooks` - Listar todos los webhooks de una base
- `create_new_webhook` - Crear nuevo webhook
- `delete_webhook_by_id` - Eliminar webhook por ID
- `get_webhook_debug_payloads` - Obtener payloads para debugging
- `refresh_webhook_expiration` - Renovar expiración de webhook
- `get_webhook_detailed_info` - Información detallada de webhook

**User Information (4):**
- `get_current_user_info` - Información completa del usuario
- `get_user_email` - Obtener email del usuario
- `get_user_settings` - Configuraciones del usuario
- `check_base_permissions` - Verificar permisos por base

**Blocks Management (7):**
- `list_all_blocks` - Listar todas las extensiones Blocks
- `get_block_details` - Detalles de un Block específico
- `create_new_block` - Crear nuevo Block
- `update_existing_block` - Actualizar Block existente
- `delete_block_by_id` - Eliminar Block por ID
- `validate_block_configuration` - Validar configuración de Block
- `get_block_version_history` - Historial de versiones de Block

#### 🏗️ Architecture Improvements
- **Servicios Core Extendidos** - `/services/airtable_service.py` con 25+ nuevos métodos
- **Herramientas MCP Organizadas** - Modularización en `/src/python/tools/`
- **Configuración OAuth Completa** - `/config/settings.py` con scopes completos
- **Cliente API Extendido** - `/airtable_client.py` con nuevas funcionalidades
- **Servidor MCP Integrado** - `/src/python/inspector_server.py` con todas las herramientas registradas

#### ⚡ Performance & Security
- **FastMCP auto-detection** - STDIO para desarrollo, HTTP para producción
- **Security patches** - Protección contra XSS y command injection
- **Enhanced error handling** - Manejo robusto de errores con logging detallado
- **Memory optimization** - Gestión eficiente de memoria y conexiones
- **Token management** - Rotación automática y almacenamiento seguro

#### 🧪 Testing
- **Suite completa de tests** - Unit, integration, e2e tests
- **OAuth testing** - Validación de todos los scopes
- **API testing** - Tests para todas las 34 herramientas MCP
- **Security testing** - Validación de parches de seguridad

#### 📚 Documentation
- **FastMCP deployment guide** - Guía completa de despliegue
- **OAuth tutorial** - Tutorial paso a paso de OAuth integration
- **API reference** - Documentación completa de la API
- **Security guide** - Mejores prácticas de seguridad

---

## [3.2.6] - 2025-12-07

### 🔄 FastMCP Moderno y Despliegue Optimizado

#### ✨ Added
- **FastMCP integration completa** para transporte HTTP/SSE
- **Railway deployment optimizado** con Docker builder
- **Auto transport detection** - STDIO para desarrollo, HTTP para producción
- **Streaming en tiempo real** con Server-Sent Events
- **Enhanced TypeScript support** con compilación mejorada

#### 🐛 Fixed
- **TypeScript compilation issues** - Resolución completa de problemas de compilación
- **Memory leaks** - Solución de memory leaks en sesiones largas
- **Connection handling** - Mejora en el manejo de conexiones

#### 🔒 Security
- **XSS prevention** - Protección mejorada contra XSS
- **Input sanitization** - Validación completa de entradas de usuario

---

## [3.2.5] - 2025-12-07

### 📋 ID de Base Opcional y Soporte Múltiples Bases

#### ✨ Added
- **ID de Base Opcional** - AIRTABLE_BASE_ID ahora es opcional desde v3.2.5
- **Base discovery** - Herramienta `list_bases` para descubrir bases accesibles
- **Dynamic base switching** - Cambio dinámico de base durante la sesión
- **Enhanced multi-base support** - Soporte mejorado para múltiples bases

#### 🔧 Improved
- **Flexible configuration** - Configuración más flexible para desarrollo
- **Better error messages** - Mensajes de error más informativos
- **Documentation updates** - Documentación actualizada

---

## [3.2.4] - 2025-09-09

### 🔒 Security Release - Complete XSS Fix

#### 🔒 Security Fixed
- **XSS vulnerabilities** en OAuth2 endpoint - Alertas GitHub #10 & #11
- **Unicode escaping** para todos los caracteres especiales en JSON
- **textContent usage** en lugar de innerHTML para contenido dinámico
- **Multiple escape layers** para defensa en profundidad
- **Security headers** - CSP, X-XSS-Protection, X-Content-Type-Options

---

## [3.2.3] - 2025-09-09

### 🔒 Security Release - Command Injection Fix

#### 🔒 Security Fixed
- **Command injection** en Python test client - GitHub Alert #10 resuelto
- **BASE_ID validation** al inicio de la aplicación
- **String interpolation vulnerabilities** eliminadas
- **Path traversal protection** implementada
- **Token format validation** agregada

---

## [3.2.2] - 2025-09-09

### 🔒 Initial Security Patches

#### 🔒 Security Fixed
- **Initial command injection fixes** en test_client.py
- **Input validation** para endpoints de API
- **Unused subprocess import** removido
- **Basic endpoint sanitization** implementada

#### ⚠️ Note
- Parcial fix - Resolución completa en v3.2.3

---

## [3.2.1] - 2025-09-09

### 🏗️ Major Architecture Fix & Project Restructure

#### 🏗️ Architecture Fixed
- **TypeScript compilation issue** completamente resuelto
- **.d.ts files** ahora contienen solo tipos, no código runtime
- **Proper separation** de tipos e implementación

#### 📁 New Project Structure
```
airtable-mcp/
├── src/
│   ├── index.js           # Main entry point
│   ├── typescript/        # TypeScript implementation
│   ├── javascript/        # JavaScript implementation
│   └── python/           # Python implementation
├── dist/                 # Compiled output
├── docs/
│   ├── guides/          # User guides
│   └── releases/        # Release notes
├── tests/               # All test files
└── types/               # TypeScript definitions
```

#### ✨ Added
- **World-class project organization**
- **Proper build system** con npm scripts
- **ESLint and Prettier configurations**
- **Jest testing framework setup**
- **CI/CD pipeline structure**

---

## [3.0.0] - Previous Versions

### 🚀 Initial Release Features
- Basic Airtable integration
- Personal Access Token support
- Simple record operations
- Basic MCP server implementation

### 🔄 Evolution to v3.x
- Progressive security improvements
- Architecture enhancements
- TypeScript adoption
- FastMCP integration

---

**📊 Version Summary:**
- **v3.2.7**: 34 herramientas MCP, OAuth completo, FastMCP moderno
- **v3.2.6**: FastMCP integration, Railway deployment
- **v3.2.5**: ID base opcional, multi-base support
- **v3.2.4**: XSS security fixes
- **v3.2.3**: Command injection fixes
- **v3.2.2**: Initial security patches
- **v3.2.1**: TypeScript architecture fix
- **v3.0.0**: Initial release

**🔒 Security Status:**
- ✅ **v3.2.4+**: All security vulnerabilities patched
- ✅ **v3.2.3+**: Command injection protected
- ✅ **v3.2.4+**: XSS prevention implemented
- ✅ **Ongoing**: Continuous security monitoring

**📈 Feature Growth:**
- **v3.2.1**: 6 herramientas básicas
- **v3.2.5**: 6 herramientas (ID base opcional)
- **v3.2.7**: 34 herramientas MCP completas
