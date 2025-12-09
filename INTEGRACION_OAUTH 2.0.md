# Documentación: Integración de Autenticación OAuth 2.0 con Airtable y Back4App

## 📌 Introducción
Este documento describe la implementación de un sistema de **autenticación OAuth 2.0 para Airtable** integrado con **Back4App/Parse** como almacenamiento principal, diseñado para funcionar junto al servidor MCP existente **sin modificar su funcionalidad actual**.

---

## 🔧 Arquitectura del Sistema

### **Componentes Principales**
1. **Servidor MCP Existente** (`src/python/server.py`):
   - **No modificado**. Continúa funcionando con `fastmcp run`.
   - Maneja transporte HTTP/SSE y herramientas MCP existentes.

2. **Nuevos Módulos de Autenticación** (`src/python/auth/`):
   - `oauth.py`: Flujo OAuth 2.0 con Airtable.
   - `direct.py`: Autenticación directa con API Key (opcional).

3. **Almacenamiento en Back4App** (`src/python/storage/`):
   - `back4app.py`: Implementación del almacenamiento usando Parse SDK.
   - `base.py`: Interfaz base para almacenamiento.
   - `redis.py`: Almacenamiento en Redis (opcional para caché).

4. **Rutas de Autenticación** (`src/python/routes/`):
   - `auth.py`: Endpoints para OAuth (`/auth/authorize`, `/auth/callback`).
   - `mcp.py`: Extensión del endpoint MCP existente para manejar autenticación.

5. **Configuración Centralizada** (`src/python/config.py`):
   - Variables de entorno y configuración del sistema.

---

## 🔑 Flujo de Autenticación

### **Diagrama de Flujo**
Usuario solicita herramientas MCP → Servidor responde con necesidad de autenticación
Usuario es redirigido a Airtable para autorización (OAuth 2.0)
Airtable devuelve código de autorización al callback (/auth/callback)
Servidor intercambia código por tokens y almacena en Back4App
Servidor crea sesión MCP y devuelve cookie con session_id
Solicitudes posteriores usan session_id para autenticación


### **Métodos de Autenticación Soportados**
| Método          | Descripción                                  | Endpoint                     |
|-----------------|----------------------------------------------|------------------------------|
| **OAuth 2.0**   | Flujo estándar con Airtable (recomendado)    | `/auth/authorize`, `/auth/callback` |
| **API Key**     | Autenticación directa con API Key de Airtable | `/api/auth/direct`          |

---

## 🗃️ Almacenamiento en Back4App

### **Estructura de Datos**
Se crearon **3 clases en Back4App** para manejar el almacenamiento:

1. **`OAuthState`**:
   - `state` (String): Estado único para protección CSRF.
   - `data` (String): Datos serializados en JSON.
   - `expires_at` (DateTime): Expiración (15 minutos).

2. **`UserToken`**:
   - `user_id` (String): ID único del usuario.
   - `tokens` (String): Tokens cifrados (access/refresh).
   - `expires_at` (DateTime): Expiración del token.
   - `scope` (String): Scopes autorizados.

3. **`UserSession`**:
   - `session_id` (String): ID único de la sesión MCP.
   - `data` (String): Datos de la sesión en JSON.
   - `expires_at` (DateTime): Expiración (30 días).

### **Seguridad Implementada**
- **Cifrado de Tokens**: Todos los tokens se cifran con **Fernet** antes de almacenarse.
- **TTL Automático**: Back4App no soporta TTL nativo, pero se implementó un **Cloud Code Job** para limpieza periódica.
- **Permisos Restringidos**: Solo el `master key` puede escribir en las clases.

---

## 🛠️ Integración con el Servidor Existente

### **Cambios Mínimos Realizados**
1. **Nuevas rutas de autenticación** (`/auth/authorize`, `/auth/callback`).
2. **Middleware para manejar sesiones** en solicitudes MCP.
3. **Extensión del endpoint `/mcp`** para validar autenticación antes de procesar solicitudes.

### **Lo que NO se Modificó**
✅ **`src/python/server.py`**: El servidor MCP existente sigue intacto.
✅ **Funcionalidad de `fastmcp run`**: Sin cambios.
✅ **Transporte HTTP/SSE**: Continúa funcionando igual.
✅ **Herramientas MCP existentes**: Todas siguen operativas.

---

## 📝 Configuración

### **Variables de Entorno (`.env`)**
```env
# Autenticación Airtable
AIRTABLE_CLIENT_ID=tu_client_id
AIRTABLE_CLIENT_SECRET=tu_client_secret
AIRTABLE_REDIRECT_URI=http://localhost:8000/auth/callback

# Back4App/Parse
PARSE_APP_ID=QT4gSRCrOLfNT8fJt48ETdR5DuF9yL2hVC38AkVG
PARSE_REST_API_KEY=KGMsAqfUzyGquvQ3H0p0HjABmE9WDGtRA62GpWzT
PARSE_SERVER_URL=https://parseapi.back4app.com

# Almacenamiento
STORAGE_BACKEND=back4app  # back4app/redis/memory

# Seguridad
SECRET_KEY=tu_clave_fernet_32_bytes
ENCRYPTION_KEY=tu_clave_fernet_32_bytes

Aquí tienes la documentación completa en Markdown sobre la implementación realizada, enfocada en la integración segura de autenticación OAuth 2.0 y almacenamiento en Back4App sin modificar el servidor MCP existente:

markdown
Copiar

# Documentación: Integración de Autenticación OAuth 2.0 con Airtable y Back4App

## 📌 Introducción
Este documento describe la implementación de un sistema de **autenticación OAuth 2.0 para Airtable** integrado con **Back4App/Parse** como almacenamiento principal, diseñado para funcionar junto al servidor MCP existente **sin modificar su funcionalidad actual**.

---

## 🔧 Arquitectura del Sistema

### **Componentes Principales**
1. **Servidor MCP Existente** (`src/python/server.py`):
   - **No modificado**. Continúa funcionando con `fastmcp run`.
   - Maneja transporte HTTP/SSE y herramientas MCP existentes.

2. **Nuevos Módulos de Autenticación** (`src/python/auth/`):
   - `oauth.py`: Flujo OAuth 2.0 con Airtable.
   - `direct.py`: Autenticación directa con API Key (opcional).

3. **Almacenamiento en Back4App** (`src/python/storage/`):
   - `back4app.py`: Implementación del almacenamiento usando Parse SDK.
   - `base.py`: Interfaz base para almacenamiento.
   - `redis.py`: Almacenamiento en Redis (opcional para caché).

4. **Rutas de Autenticación** (`src/python/routes/`):
   - `auth.py`: Endpoints para OAuth (`/auth/authorize`, `/auth/callback`).
   - `mcp.py`: Extensión del endpoint MCP existente para manejar autenticación.

5. **Configuración Centralizada** (`src/python/config.py`):
   - Variables de entorno y configuración del sistema.

---

## 🔑 Flujo de Autenticación

### **Diagrama de Flujo**


Usuario solicita herramientas MCP → Servidor responde con necesidad de autenticación
Usuario es redirigido a Airtable para autorización (OAuth 2.0)
Airtable devuelve código de autorización al callback (/auth/callback)
Servidor intercambia código por tokens y almacena en Back4App
Servidor crea sesión MCP y devuelve cookie con session_id
Solicitudes posteriores usan session_id para autenticación
Copiar

### **Métodos de Autenticación Soportados**
| Método          | Descripción                                  | Endpoint                     |
|-----------------|----------------------------------------------|------------------------------|
| **OAuth 2.0**   | Flujo estándar con Airtable (recomendado)    | `/auth/authorize`, `/auth/callback` |
| **API Key**     | Autenticación directa con API Key de Airtable | `/api/auth/direct`          |

---

## 🗃️ Almacenamiento en Back4App

### **Estructura de Datos**
Se crearon **3 clases en Back4App** para manejar el almacenamiento:

1. **`OAuthState`**:
   - `state` (String): Estado único para protección CSRF.
   - `data` (String): Datos serializados en JSON.
   - `expires_at` (DateTime): Expiración (15 minutos).

2. **`UserToken`**:
   - `user_id` (String): ID único del usuario.
   - `tokens` (String): Tokens cifrados (access/refresh).
   - `expires_at` (DateTime): Expiración del token.
   - `scope` (String): Scopes autorizados.

3. **`UserSession`**:
   - `session_id` (String): ID único de la sesión MCP.
   - `data` (String): Datos de la sesión en JSON.
   - `expires_at` (DateTime): Expiración (30 días).

### **Seguridad Implementada**
- **Cifrado de Tokens**: Todos los tokens se cifran con **Fernet** antes de almacenarse.
- **TTL Automático**: Back4App no soporta TTL nativo, pero se implementó un **Cloud Code Job** para limpieza periódica.
- **Permisos Restringidos**: Solo el `master key` puede escribir en las clases.

---

## 🛠️ Integración con el Servidor Existente

### **Cambios Mínimos Realizados**
1. **Nuevas rutas de autenticación** (`/auth/authorize`, `/auth/callback`).
2. **Middleware para manejar sesiones** en solicitudes MCP.
3. **Extensión del endpoint `/mcp`** para validar autenticación antes de procesar solicitudes.

### **Lo que NO se Modificó**
✅ **`src/python/server.py`**: El servidor MCP existente sigue intacto.
✅ **Funcionalidad de `fastmcp run`**: Sin cambios.
✅ **Transporte HTTP/SSE**: Continúa funcionando igual.
✅ **Herramientas MCP existentes**: Todas siguen operativas.

---

## 📝 Configuración

### **Variables de Entorno (`.env`)**
```env
# Autenticación Airtable
AIRTABLE_CLIENT_ID=tu_client_id
AIRTABLE_CLIENT_SECRET=tu_client_secret
AIRTABLE_REDIRECT_URI=http://localhost:8000/auth/callback

# Back4App/Parse
PARSE_APP_ID=QT4gSRCrOLfNT8fJt48ETdR5DuF9yL2hVC38AkVG
PARSE_REST_API_KEY=KGMsAqfUzyGquvQ3H0p0HjABmE9WDGtRA62GpWzT
PARSE_SERVER_URL=https://parseapi.back4app.com

# Almacenamiento
STORAGE_BACKEND=back4app  # back4app/redis/memory

# Seguridad
SECRET_KEY=tu_clave_fernet_32_bytes
ENCRYPTION_KEY=tu_clave_fernet_32_bytes

Requisitos Previos


Registrar aplicación en Airtable:

Crear app en Airtable Developer Console.
Configurar redirect_uri y scopes (data.records:read, data.records:write, schema.bases:read).


Configurar Back4App:

Crear las clases OAuthState, UserToken, UserSession.
Configurar permisos para que solo el master key pueda escribir.


Generar clave Fernet:

python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

🚀 Endpoints Implementados
 Endpoint,Método,Descripción,Autenticación
/auth/authorize,GET,Inicia flujo OAuth 2.0 con Airtable.,Ninguna
/auth/callback,GET,Callback de Airtable después de autorización.,Ninguna
/api/auth/direct,POST,Autenticación directa con API Key.,Ninguna
/mcp,POST,Endpoint MCP extendido con autenticación.,Bearer Token

🔄 Cloud Code para Limpieza Automática
// En Back4App → Cloud Code → Jobs
Parse.Cloud.job("cleanupExpiredData", async (request) => {
  const { log } = request;

  // Limpiar OAuthStates expirados
  const OAuthState = Parse.Object.extend("OAuthState");
  const oauthQuery = new Parse.Query(OAuthState);
  oauthQuery.lessThan("expires_at", new Date());
  const expiredOAuthStates = await oauthQuery.find({ useMasterKey: true });
  for (const state of expiredOAuthStates) {
    await state.destroy({ useMasterKey: true });
  }

  // Limpiar UserTokens expirados
  const UserToken = Parse.Object.extend("UserToken");
  const tokenQuery = new Parse.Query(UserToken);
  tokenQuery.lessThan("expires_at", new Date());
  const expiredTokens = await tokenQuery.find({ useMasterKey: true });
  for (const token of expiredTokens) {
    await token.destroy({ useMasterKey: true });
  }

  // Limpiar UserSessions expiradas
  const UserSession = Parse.Object.extend("UserSession");
  const sessionQuery = new Parse.Query(UserSession);
  sessionQuery.lessThan("expires_at", new Date());
  const expiredSessions = await sessionQuery.find({ useMasterKey: true });
  for (const session of expiredSessions) {
    await session.destroy({ useMasterKey: true });
  }

  return `Limpieza completada: ${expiredOAuthStates.length + expiredTokens.length + expiredSessions.length} registros eliminados`;
});

Aquí tienes la documentación completa en Markdown sobre la implementación realizada, enfocada en la integración segura de autenticación OAuth 2.0 y almacenamiento en Back4App sin modificar el servidor MCP existente:

markdown
Copiar

# Documentación: Integración de Autenticación OAuth 2.0 con Airtable y Back4App

## 📌 Introducción
Este documento describe la implementación de un sistema de **autenticación OAuth 2.0 para Airtable** integrado con **Back4App/Parse** como almacenamiento principal, diseñado para funcionar junto al servidor MCP existente **sin modificar su funcionalidad actual**.

---

## 🔧 Arquitectura del Sistema

### **Componentes Principales**
1. **Servidor MCP Existente** (`src/python/server.py`):
   - **No modificado**. Continúa funcionando con `fastmcp run`.
   - Maneja transporte HTTP/SSE y herramientas MCP existentes.

2. **Nuevos Módulos de Autenticación** (`src/python/auth/`):
   - `oauth.py`: Flujo OAuth 2.0 con Airtable.
   - `direct.py`: Autenticación directa con API Key (opcional).

3. **Almacenamiento en Back4App** (`src/python/storage/`):
   - `back4app.py`: Implementación del almacenamiento usando Parse SDK.
   - `base.py`: Interfaz base para almacenamiento.
   - `redis.py`: Almacenamiento en Redis (opcional para caché).

4. **Rutas de Autenticación** (`src/python/routes/`):
   - `auth.py`: Endpoints para OAuth (`/auth/authorize`, `/auth/callback`).
   - `mcp.py`: Extensión del endpoint MCP existente para manejar autenticación.

5. **Configuración Centralizada** (`src/python/config.py`):
   - Variables de entorno y configuración del sistema.

---

## 🔑 Flujo de Autenticación

### **Diagrama de Flujo**


Usuario solicita herramientas MCP → Servidor responde con necesidad de autenticación
Usuario es redirigido a Airtable para autorización (OAuth 2.0)
Airtable devuelve código de autorización al callback (/auth/callback)
Servidor intercambia código por tokens y almacena en Back4App
Servidor crea sesión MCP y devuelve cookie con session_id
Solicitudes posteriores usan session_id para autenticación
Copiar

### **Métodos de Autenticación Soportados**
| Método          | Descripción                                  | Endpoint                     |
|-----------------|----------------------------------------------|------------------------------|
| **OAuth 2.0**   | Flujo estándar con Airtable (recomendado)    | `/auth/authorize`, `/auth/callback` |
| **API Key**     | Autenticación directa con API Key de Airtable | `/api/auth/direct`          |

---

## 🗃️ Almacenamiento en Back4App

### **Estructura de Datos**
Se crearon **3 clases en Back4App** para manejar el almacenamiento:

1. **`OAuthState`**:
   - `state` (String): Estado único para protección CSRF.
   - `data` (String): Datos serializados en JSON.
   - `expires_at` (DateTime): Expiración (15 minutos).

2. **`UserToken`**:
   - `user_id` (String): ID único del usuario.
   - `tokens` (String): Tokens cifrados (access/refresh).
   - `expires_at` (DateTime): Expiración del token.
   - `scope` (String): Scopes autorizados.

3. **`UserSession`**:
   - `session_id` (String): ID único de la sesión MCP.
   - `data` (String): Datos de la sesión en JSON.
   - `expires_at` (DateTime): Expiración (30 días).

### **Seguridad Implementada**
- **Cifrado de Tokens**: Todos los tokens se cifran con **Fernet** antes de almacenarse.
- **TTL Automático**: Back4App no soporta TTL nativo, pero se implementó un **Cloud Code Job** para limpieza periódica.
- **Permisos Restringidos**: Solo el `master key` puede escribir en las clases.

---

## 🛠️ Integración con el Servidor Existente

### **Cambios Mínimos Realizados**
1. **Nuevas rutas de autenticación** (`/auth/authorize`, `/auth/callback`).
2. **Middleware para manejar sesiones** en solicitudes MCP.
3. **Extensión del endpoint `/mcp`** para validar autenticación antes de procesar solicitudes.

### **Lo que NO se Modificó**
✅ **`src/python/server.py`**: El servidor MCP existente sigue intacto.
✅ **Funcionalidad de `fastmcp run`**: Sin cambios.
✅ **Transporte HTTP/SSE**: Continúa funcionando igual.
✅ **Herramientas MCP existentes**: Todas siguen operativas.

---

## 📝 Configuración

### **Variables de Entorno (`.env`)**
```env
# Autenticación Airtable
AIRTABLE_CLIENT_ID=tu_client_id
AIRTABLE_CLIENT_SECRET=tu_client_secret
AIRTABLE_REDIRECT_URI=http://localhost:8000/auth/callback

# Back4App/Parse
PARSE_APP_ID=QT4gSRCrOLfNT8fJt48ETdR5DuF9yL2hVC38AkVG
PARSE_REST_API_KEY=KGMsAqfUzyGquvQ3H0p0HjABmE9WDGtRA62GpWzT
PARSE_SERVER_URL=https://parseapi.back4app.com

# Almacenamiento
STORAGE_BACKEND=back4app  # back4app/redis/memory

# Seguridad
SECRET_KEY=tu_clave_fernet_32_bytes
ENCRYPTION_KEY=tu_clave_fernet_32_bytes

Requisitos Previos


Registrar aplicación en Airtable:

Crear app en Airtable Developer Console.
Configurar redirect_uri y scopes (data.records:read, data.records:write, schema.bases:read).


Configurar Back4App:

Crear las clases OAuthState, UserToken, UserSession.
Configurar permisos para que solo el master key pueda escribir.


Generar clave Fernet:
bash
Copiar

python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"



🚀 Endpoints Implementados


  
    
      Endpoint
      Método
      Descripción
      Autenticación
    
  
  
    
      /auth/authorize
      GET
      Inicia flujo OAuth 2.0 con Airtable.
      Ninguna
    
    
      /auth/callback
      GET
      Callback de Airtable después de autorización.
      Ninguna
    
    
      /api/auth/direct
      POST
      Autenticación directa con API Key.
      Ninguna
    
    
      /mcp
      POST
      Endpoint MCP extendido con autenticación.
      Bearer Token
    
  



🔄 Cloud Code para Limpieza Automática
javascript
Copiar

// En Back4App → Cloud Code → Jobs
Parse.Cloud.job("cleanupExpiredData", async (request) => {
  const { log } = request;

  // Limpiar OAuthStates expirados
  const OAuthState = Parse.Object.extend("OAuthState");
  const oauthQuery = new Parse.Query(OAuthState);
  oauthQuery.lessThan("expires_at", new Date());
  const expiredOAuthStates = await oauthQuery.find({ useMasterKey: true });
  for (const state of expiredOAuthStates) {
    await state.destroy({ useMasterKey: true });
  }

  // Limpiar UserTokens expirados
  const UserToken = Parse.Object.extend("UserToken");
  const tokenQuery = new Parse.Query(UserToken);
  tokenQuery.lessThan("expires_at", new Date());
  const expiredTokens = await tokenQuery.find({ useMasterKey: true });
  for (const token of expiredTokens) {
    await token.destroy({ useMasterKey: true });
  }

  // Limpiar UserSessions expiradas
  const UserSession = Parse.Object.extend("UserSession");
  const sessionQuery = new Parse.Query(UserSession);
  sessionQuery.lessThan("expires_at", new Date());
  const expiredSessions = await sessionQuery.find({ useMasterKey: true });
  for (const session of expiredSessions) {
    await session.destroy({ useMasterKey: true });
  }

  return `Limpieza completada: ${expiredOAuthStates.length + expiredTokens.length + expiredSessions.length} registros eliminados`;
});

Programar este job para ejecutarse diariamente (ej: 3 AM).

📋 Ejemplo de Uso
1. Flujo OAuth 2.0

Usuario accede a:
http://localhost:8000/auth/authorize?platform=chatgpt
Es redirigido a Airtable para autorizar.
Airtable redirige a:
Copiar

http://localhost:8000/auth/callback?code=XXX&state=YYY


Servidor almacena tokens en Back4App y crea sesión.
Solicitudes posteriores usan el session_id en el header Authorization: Bearer {session_id}.
2. Autenticación Directa con API Key
bash
Copiar

curl -X POST http://localhost:8000/api/auth/direct \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "api_key=tu_api_key&platform=chatgpt"

3. Solicitud MCP Autenticada
bash
Copiar

curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_SESSION_ID" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'


🔍 Solución de Problemas


  
    
      Problema
      Causa Posible
      Solución
    
  
  
    
      Error 401 en /mcp
      Sesión no válida o expirada
      Vuelve a autenticarte.
    
    
      "Invalid state" en callback
      Estado OAuth expirado
      Reintenta el flujo de autenticación.
    
    
      Error al conectar a Back4App
      Credenciales incorrectas
      Verifica PARSE_APP_ID y PARSE_REST_API_KEY.
    
    
      Tokens no se guardan
      Permisos insuficientes en Back4App
      Configura ACLs para master key.
    
    
      Error de cifrado
      Clave Fernet incorrecta
      Genera una nueva clave con Fernet.
    
  



📌 Resumen de Cambios

Nuevos archivos añadidos (sin modificar los existentes):

src/python/auth/
src/python/storage/
src/python/routes/
src/python/config.py

Nuevas dependencias:

parse==1.19.0 (SDK para Back4App).

Nuevas variables de entorno para Back4App y Airtable.
Cloud Code Job para limpieza automática.

🎯 Beneficios de esta Implementación
✅ Integración no invasiva: No se modificó el servidor MCP existente.
✅ Almacenamiento seguro: Tokens cifrados en Back4App.
✅ Doble método de autenticación: OAuth 2.0 + API Key directa.
✅ Compatibilidad total: Funciona con fastmcp run y transporte HTTP/SSE.
✅ Escalable: Back4App maneja miles de usuarios.
✅ Seguridad robusta: Cifrado, TTL, permisos restringidos.

Nota: Esta implementación extiende la funcionalidad existente sin romperla, permitiendo que el servidor MCP siga funcionando exactamente igual que antes, pero ahora con autenticación segura y almacenamiento en Back4App.





