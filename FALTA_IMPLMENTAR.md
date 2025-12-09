# 📋 Documentación de Implementación: OAuth + TOON + Back4App para Airtable MCP

## 🎯 Resumen Ejecutivo

Esta documentación proporciona una implementación completa y modular de autenticación OAuth para Airtable, integrada con soporte TOON y almacenamiento seguro en Back4App. La solución está diseñada para **no romper la funcionalidad existente** de VSCode/fastmcp, manteniendo la compatibilidad total con el flujo actual.

## 🏗️ Arquitectura de la Solución

### Flujos de Autenticación

| **Flujo Actual (VSCode)** | **Nuevo Flujo (ChatGPT/Mistral AI)** |
|---------------------------|-------------------------------------|
| ✅ Variables de entorno | 🔄 OAuth dinámico |
| ✅ FastMCP + JSON | ✅ TOON + JSON |
| ✅ Personal Access Token | 🔄 Tokens almacenados en Back4App |

### Componentes Principales

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ChatGPT/      │    │   OAuth Server  │    │   Back4App      │
│   Mistral AI    │◄──►│   (Flask)       │◄──►│   (Parse)       │
│                 │    │                 │    │                 │
│ • Solicita auth │    │ • /authorize    │    │ • AuthConnections│
│ • Usa tokens    │    │ • /callback     │    │ • Tokens seguros │
└─────────────────┘    │ • /records      │    └─────────────────┘
                       │ • /tokens       │
                       └─────────────────┘
                              ▲
                              │
                       ┌─────────────────┐
                       │   Airtable API  │
                       │   (OAuth 2.0)   │
                       └─────────────────┘
```

## ⚙️ Configuración Inicial

### 1. Variables de Entorno

Agrega estas variables a tu archivo `.env`:

```bash
# Airtable OAuth Configuration
AIRTABLE_OAUTH_CLIENT_ID=tu_client_id_aqui
AIRTABLE_OAUTH_CLIENT_SECRET=tu_client_secret_aqui
AIRTABLE_OAUTH_REDIRECT_URI=https://tu-dominio.com/callback
AIRTABLE_OAUTH_SCOPES=data.records:write schema.bases:read

# Back4App Configuration (Parse Server)
PARSE_APP_ID=tu_app_id_aqui
PARSE_JAVASCRIPT_KEY=tu_javascript_key_aqui
PARSE_REST_API_KEY=tu_rest_api_key_aqui
PARSE_SERVER_URL=https://parseapi.back4app.com

# TOON Configuration
TOON_ENABLED=true
TOON_FORMAT=compact
```

### 2. Dependencias

```bash
pip install flask python-dotenv requests parse toon
```

## 🚀 Implementación por Pasos

### Paso 1: Estructura del Proyecto

Crea la siguiente estructura modular:

```
/tu-proyecto/
├── src/
│   ├── oauth/                    # 🆕 Nuevo módulo OAuth
│   │   ├── __init__.py          # Inicialización del módulo
│   │   ├── routes.py            # Endpoints Flask
│   │   ├── back4app.py          # Cliente Back4App
│   │   ├── toon_utils.py        # Utilidades TOON
│   │   └── oauth_service.py     # Lógica de negocio OAuth
│   └── ...
├── .env.example                 # ✅ Actualizar con nuevas variables
└── requirements.txt             # ✅ Agregar dependencias
```

### Paso 2: Implementación del Cliente Back4App

**Archivo: `src/oauth/back4app.py`**

```python
from parse import ParseClient
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class Back4AppClient:
    def __init__(self):
        self.client = ParseClient(
            app_id=os.getenv("PARSE_APP_ID"),
            javascript_key=os.getenv("PARSE_JAVASCRIPT_KEY"),
            rest_api_key=os.getenv("PARSE_REST_API_KEY"),
            server_url=os.getenv("PARSE_SERVER_URL")
        )

    def save_tokens(self, user_id: str, access_token: str,
                   refresh_token: Optional[str], base_id: str,
                   scopes: str) -> bool:
        """Guarda tokens OAuth en Back4App"""
        try:
            auth_data = {
                "userId": user_id,
                "accessToken": access_token,
                "refreshToken": refresh_token,
                "baseId": base_id,
                "scopes": scopes,
                "provider": "airtable_oauth",
                "expiresAt": (datetime.now() + timedelta(hours=1)).isoformat(),
                "createdAt": datetime.now().isoformat()
            }

