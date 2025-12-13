# Plan de Integración Completa - Airtable MCP

## Información Recopilada

### Estado Actual del Proyecto:
- ✅ **Herramientas básicas**: list_bases, list_tables, list_records, create_records, update_records, set_base_id
- ✅ **Sistema OAuth**: Implementado con refresh tokens
- ✅ **Configuración**: Settings con variables de entorno
- ✅ **Service Layer**: AirtableService con métodos básicos
- ✅ **Storage**: Sistema de almacenamiento (memory/redis)
- ✅ **TypeScript avanzado**: Herramientas webhooks y más avanzadas ya implementadas

### Funcionalidades Requeridas por Alcances:
1. **data.records:read** - ✅ Ya implementado (list_records)
2. **data.records:write** - ✅ Ya implementado (create_records, update_records)
3. **data.recordComments:read** - ❌ Faltante
4. **data.recordComments:write** - ❌ Faltante  
5. **schema.bases:read** - ✅ Ya implementado (list_tables)
6. **schema.bases:write** - ❌ Faltante
7. **webhook:manage** - ⚠️ Parcialmente implementado
8. **block:manage** - ❌ Faltante
9. **user.email:read** - ❌ Faltante

## Plan de Implementación

### Paso 1: Extender AirtableService
**Archivos a modificar:**
- `/services/airtable_service.py`

**Nuevas funcionalidades:**
- `get_record_comments()` - Para comentarios de registros
- `create_record_comment()` - Crear comentarios
- `update_record_comment()` - Editar comentarios
- `delete_record_comment()` - Eliminar comentarios
- `get_user_info()` - Información del usuario (email)
- `update_base_schema()` - Modificar estructura de bases
- `create_field()` - Crear nuevos campos
- `update_field()` - Modificar campos existentes
- `delete_field()` - Eliminar campos
- `create_table()` - Crear nuevas tablas
- `update_table()` - Modificar tablas
- `delete_table()` - Eliminar tablas

### Paso 2: Crear Herramientas MCP Avanzadas
**Archivos a crear/modificar:**
- `/src/python/tools/comments.py` (nuevo)
- `/src/python/tools/schema.py` (nuevo)
- `/src/python/tools/webhooks_advanced.py` (nuevo)
- `/src/python/tools/user_info.py` (nuevo)
- `/src/python/tools/blocks.py` (nuevo)

**Herramientas a implementar:**
- `get_record_comments()` - Ver comentarios de registros
- `create_record_comment()` - Crear comentario
- `update_record_comment()` - Editar comentario
- `delete_record_comment()` - Eliminar comentario
- `get_base_schema()` - Ver esquema detallado
- `create_field()` - Crear campo
- `update_field()` - Modificar campo
- `delete_field()` - Eliminar campo
- `create_table()` - Crear tabla
- `update_table()` - Modificar tabla
- `delete_table()` - Eliminar tabla
- `list_webhooks()` - Listar webhooks
- `create_webhook()` - Crear webhook
- `delete_webhook()` - Eliminar webhook
- `get_webhook_payloads()` - Obtener payloads
- `get_user_info()` - Información del usuario
- `list_blocks()` - Listar extensiones Blocks
- `create_block()` - Crear Block
- `update_block()` - Actualizar Block

### Paso 3: Actualizar OAuth Scopes
**Archivo a modificar:**
- `/config/settings.py`

**Agregar scopes completos:**
```python
airtable_scopes: str = (
    "data.records:read "
    "data.records:write "
    "data.recordComments:read "
    "data.recordComments:write "
    "schema.bases:read "
    "schema.bases:write "
    "webhook:manage "
    "block:manage "
    "user.email:read"
)
```

### Paso 4: Actualizar Inspector Server
**Archivo a modificar:**
- `/src/python/inspector_server.py`

**Agregar importación de nuevas herramientas:**
- Importar todas las nuevas herramientas
- Registrar las nuevas herramientas MCP

### Paso 5: Actualizar Cliente Airtable
**Archivo a modificar:**
- `/airtable_client.py`

**Agregar métodos para nuevas funcionalidades:**
- Métodos para comentarios
- Métodos para schema management
- Métodos para webhooks avanzados
- Métodos para Blocks
- Métodos para información de usuario

### Paso 6: Crear Tests
**Archivos a crear:**
- `/tests/test_comments.py`
- `/tests/test_schema.py`
- `/tests/test_webhooks_advanced.py`
- `/tests/test_user_info.py`
- `/tests/test_blocks.py`

## Archivos Dependientes a Editar

### Archivos Core a Modificar:
1. `/services/airtable_service.py` - Extender servicio API
2. `/src/python/inspector_server.py` - Agregar nuevas herramientas
3. `/config/settings.py` - Actualizar scopes
4. `/airtable_client.py` - Extender cliente

### Archivos Nuevos a Crear:
1. `/src/python/tools/__init__.py` - Inicializar paquete tools
2. `/src/python/tools/comments.py` - Herramientas de comentarios
3. `/src/python/tools/schema.py` - Herramientas de schema
4. `/src/python/tools/webhooks_advanced.py` - Webhooks avanzados
5. `/src/python/tools/user_info.py` - Información de usuario
6. `/src/python/tools/blocks.py` - Manejo de Blocks

### Archivos de Configuración:
1. `/.env.example` - Ejemplo con todos los scopes
2. `/docs/scopes.md` - Documentación de scopes

## Pasos de Seguimiento

### Instalación y Configuración:
1. Instalar dependencias adicionales (si las hay)
2. Configurar variables de entorno con scopes completos
3. Actualizar documentación

### Testing:
1. Ejecutar tests de todas las nuevas funcionalidades
2. Probar integración OAuth con scopes completos
3. Validar permisos por scope

### Documentación:
1. Actualizar README.md con nuevas herramientas
2. Crear guía de scopes y permisos
3. Documentar ejemplos de uso

## Estimación de Tiempo
- **Paso 1-2**: ~2-3 horas
- **Paso 3-4**: ~1 hora  
- **Paso 5-6**: ~1-2 horas
- **Testing y documentación**: ~1 hora

**Total estimado**: 5-7 horas de desarrollo
