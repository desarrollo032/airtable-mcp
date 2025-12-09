documentación completa y precisa para implementar desde cero la integración de OAuth con Airtable, TOON, y Back4App, sin romper la funcionalidad existente de fastmcp y VSCode. Puedes copiar, pegar o descargar esta documentación para tu proyecto.

Documentación de Implementación: OAuth + TOON + Back4App para Airtable

1. Introducción
Este documento describe cómo implementar la autenticación OAuth de Airtable para ChatGPT/Mistral AI, junto con soporte para TOON y almacenamiento de tokens en Back4App, sin afectar el flujo actual de VSCode (que usa fastmcp y variables de entorno).

2. Arquitectura General
Flujo Actual (VSCode)

Usa fastmcp y variables de entorno (AIRTABLE_PERSONAL_ACCESS_TOKEN, AIRTABLE_BASE_ID).
Funciona con JSON.
Nuevo Flujo (ChatGPT/Mistral AI)

Usa OAuth para obtener access_token dinámicamente.
Soporta TOON y JSON.
Almacena tokens en Back4App (Parse Server).

3. Configuración Inicial
a. Actualizar .env.example
Agrega las siguientes variables al final del archivo:
plaintext
Copiar

# Airtable OAuth Configuration
AIRTABLE_OAUTH_CLIENT_ID=tu_client_id
AIRTABLE_OAUTH_CLIENT_SECRET=tu_client_secret
AIRTABLE_OAUTH_REDIRECT_URI=https://tu-dominio.com/callback
AIRTABLE_OAUTH_SCOPES=data.records:write schema.bases:read

# Back4App Configuration (Parse Server)
PARSE_APP_ID=tu_app_id
PARSE_JAVASCRIPT_KEY=tu_javascript_key
PARSE_REST_API_KEY=tu_rest_api_key
PARSE_SERVER_URL=https://parseapi.back4app.com

# TOON Configuration
TOON_ENABLED=true
TOON_FORMAT=compact


b. Instalar Dependencias
bash
Copiar

pip install flask python-dotenv requests parse toon


4. Implementación del Código
a. Archivo app.py (Servidor Flask)
python
Copiar

from flask import Flask, request, jsonify, Response
import os
from dotenv import load_dotenv
import secrets
import base64
import hashlib
import requests
from parse import ParseClient
import toon
from datetime import datetime, timedelta

# Cargar variables de entorno
load_dotenv()

# Inicializar Flask
app = Flask(__name__)

# Configuración de Parse (Back4App)
parse_client = ParseClient(
    app_id=os.getenv("PARSE_APP_ID"),
    javascript_key=os.getenv("PARSE_JAVASCRIPT_KEY"),
    rest_api_key=os.getenv("PARSE_REST_API_KEY"),
    server_url=os.getenv("PARSE_SERVER_URL")
)

# Configuración de OAuth
AIRTABLE_OAUTH_CLIENT_ID = os.getenv("AIRTABLE_OAUTH_CLIENT_ID")
AIRTABLE_OAUTH_CLIENT_SECRET = os.getenv("AIRTABLE_OAUTH_CLIENT_SECRET")
AIRTABLE_OAUTH_REDIRECT_URI = os.getenv("AIRTABLE_OAUTH_REDIRECT_URI")
AIRTABLE_OAUTH_SCOPES = os.getenv("AIRTABLE_OAUTH_SCOPES")

# Almacenamiento temporal (en producción, usa Redis)
state_store = {}
code_verifier_store = {}

# Función para guardar tokens en Back4App
def save_tokens_to_back4app(user_id, access_token, refresh_token, base_id, scopes):
    auth_data = {
        "userId": user_id,
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "baseId": base_id,
        "scopes": scopes,
        "provider": "airtable_oauth",
        "expiresAt": (datetime.now() + timedelta(minutes=60)).isoformat()
    }
    parse_client.post("/classes/AuthConnections", data=auth_data)
    return True

# Función para recuperar tokens de Back4App
def get_tokens_from_back4app(user_id):
    response = parse_client.get(
        "/classes/AuthConnections",
        params={"where": {"userId": user_id, "provider": "airtable_oauth"}}
    )
    if response.status_code == 200 and response.json().get("results"):
        return response.json()["results"][0]
    return None

# Función para hacer respuesta en JSON o TOON
def make_response(data, format="json"):
    if format == "toon":
        return Response(toon.dumps(data), mimetype="application/toon")
    else:
        return jsonify(data)

# Endpoint para generar link de autorización
@app.route("/authorize")
def authorize():
    state = secrets.token_urlsafe(16)
    code_verifier = secrets.token_urlsafe(64)
    state_store[state] = code_verifier

    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip("=")

    auth_url = (
        f"https://airtable.com/oauth2/v1/authorize?"
        f"client_id={AIRTABLE_OAUTH_CLIENT_ID}&"
        f"redirect_uri={AIRTABLE_OAUTH_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope={AIRTABLE_OAUTH_SCOPES}&"
        f"state={state}&"
        f"code_challenge={code_challenge}&"
        f"code_challenge_method=S256"
    )

    response_data = {"auth_url": auth_url, "state": state}
    format = request.args.get("format", "json")
    return make_response(response_data, format)

# Endpoint para recibir el código y obtener tokens
@app.route("/callback")
def callback():
    state = request.args.get("state")
    if not state or state not in state_store:
        return "Estado inválido", 400

    code = request.args.get("code")
    if not code:
        return "Código no recibido", 400

    code_verifier = state_store[state]
    credentials = f"{AIRTABLE_OAUTH_CLIENT_ID}:{AIRTABLE_OAUTH_CLIENT_SECRET}"
    b64_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "code": code,
        "client_id": AIRTABLE_OAUTH_CLIENT_ID,
        "redirect_uri": AIRTABLE_OAUTH_REDIRECT_URI,
        "grant_type": "authorization_code",
        "code_verifier": code_verifier
    }

    response = requests.post(
        "https://airtable.com/oauth2/v1/token",
        headers=headers,
        data=data
    )

    if response.status_code == 200:
        tokens = response.json()
        user_id = "user_123"  # Reemplaza con lógica para obtener el user_id real
        base_id = request.args.get("base_id", "app1234567890")
        save_tokens_to_back4app(user_id, tokens["access_token"], tokens.get("refresh_token"), base_id, tokens.get("scope", ""))
        format = request.args.get("format", "json")
        return make_response(tokens, format)
    else:
        return f"Error: {response.json()}", 400

# Endpoint para listar registros de Airtable (con soporte para TOON)
@app.route("/records/<base_id>/<table_name>")
def get_records(base_id, table_name):
    access_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not access_token:
        return "Token de acceso no proporcionado", 401

    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        format = request.args.get("format", "json")
        return make_response(data, format)
    else:
        return f"Error: {response.text}", response.status_code

# Endpoint para obtener tokens almacenados en Back4App
@app.route("/tokens/<user_id>")
def get_tokens(user_id):
    tokens = get_tokens_from_back4app(user_id)
    if tokens:
        format = request.args.get("format", "json")
        return make_response(tokens, format)
    else:
        return "Tokens no encontrados", 404

# Iniciar servidor
if __name__ == "__main__":
    app.run(port=5000, debug=True)


5. Explicación del Código
a. Configuración Inicial

Variables de entorno: Se cargan con load_dotenv().
Parse Client: Configurado para interactuar con Back4App.
b. Funciones Auxiliares

save_tokens_to_back4app: Guarda tokens en Back4App.
get_tokens_from_back4app: Recupera tokens de Back4App.
make_response: Devuelve datos en JSON o TOON.
c. Endpoints


  
    
      Endpoint
      Descripción
      Parámetros
    
  
  
    
      /authorize
      Genera el link de autorización de Airtable.
      format (opcional: json o toon)
    
    
      /callback
      Recibe el code y devuelve los tokens.
      code, state, format (opcional)
    
    
      /records//
      Lista registros de Airtable.
      Authorization (header), format (opcional)
    
    
      /tokens/
      Recupera tokens de Back4App.
      user_id, format (opcional)
    
  



6. Pruebas y Validación
a. Probar el Flujo de OAuth


Generar link de autorización:
bash
Copiar

curl "http://localhost:5000/authorize"


Devuelve el auth_url en JSON.


Obtener tokens:

Abre el auth_url en un navegador.
Airtable redirige a /callback?code=XXX&state=YYY.
El endpoint guarda los tokens en Back4App y los devuelve en JSON.


Listar registros:
bash
Copiar

curl -H "Authorization: Bearer abc123" "http://localhost:5000/records/app123/Users"


Devuelve los registros en JSON.

b. Probar con TOON


Solicitar link en TOON:
bash
Copiar

curl "http://localhost:5000/authorize?format=toon"


Devuelve el auth_url en TOON.


Obtener tokens en TOON:
bash
Copiar

curl "http://localhost:5000/callback?code=XXX&state=YYY&format=toon"


Devuelve los tokens en TOON.


Listar registros en TOON:
bash
Copiar

curl -H "Authorization: Bearer abc123" "http://localhost:5000/records/app123/Users?format=toon"


Devuelve los registros en TOON.


7. Integración con Back4App
a. Estructura de Datos
Los tokens se guardan en la clase AuthConnections:


  
    
      Campo
      Tipo
      Descripción
    
  
  
    
      userId
      String
      ID del usuario.
    
    
      accessToken
      String
      access_token de Airtable.
    
    
      refreshToken
      String
      refresh_token de Airtable.
    
    
      baseId
      String
      ID de la base de Airtable.
    
    
      scopes
      String
      Scopes otorgados.
    
    
      provider
      String
      Proveedor (airtable_oauth).
    
    
      expiresAt
      DateTime
      Fecha de expiración.
    
  


b. Consulta de Tokens
python
Copiar

tokens = get_tokens_from_back4app("user_123")
print(tokens["accessToken"])


8. Documentación para el README.md
markdown
Copiar

# Integración de OAuth con Airtable, TOON y Back4App

## Descripción
Este proyecto implementa la autenticación **OAuth de Airtable** para **ChatGPT/Mistral AI**, con soporte para **TOON** y almacenamiento de tokens en **Back4App**, sin afectar el flujo actual de **VSCode** (que usa `fastmcp` y variables de entorno).

---

## Configuración

### Variables de Entorno
Agrega las siguientes variables a tu archivo `.env`:
```plaintext
# Airtable OAuth Configuration
AIRTABLE_OAUTH_CLIENT_ID=tu_client_id
AIRTABLE_OAUTH_CLIENT_SECRET=tu_client_secret
AIRTABLE_OAUTH_REDIRECT_URI=https://tu-dominio.com/callback
AIRTABLE_OAUTH_SCOPES=data.records\:write schema.bases\:read

# Back4App Configuration
PARSE_APP_ID=tu_app_id
PARSE_JAVASCRIPT_KEY=tu_javascript_key
PARSE_REST_API_KEY=tu_rest_api_key
PARSE_SERVER_URL=https://parseapi.back4app.com

# TOON Configuration
TOON_ENABLED=true
TOON_FORMAT=compact

Instalación
bash
Copiar

pip install flask python-dotenv requests parse toon


Endpoints


  
    
      Endpoint
      Método
      Descripción
      Parámetros
    
  
  
    
      /authorize
      GET
      Genera el link de autorización de Airtable.
      format (opcional: json o toon)
    
    
      /callback
      GET
      Recibe el code y devuelve los tokens.
      code, state, format (opcional)
    
    
      /records//
      GET
      Lista registros de Airtable.
      Authorization (header), format (opcional)
    
    
      /tokens/
      GET
      Recupera tokens de Back4App.
      user_id, format (opcional)
    
  



Ejemplos de Uso
1. Obtener Link de Autorización
bash
Copiar

curl "http://localhost:5000/authorize"

2. Obtener Tokens (tras autorización)
bash
Copiar

curl "http://localhost:5000/callback?code=XXX&state=YYY"

3. Listar Registros de Airtable
bash
Copiar

curl -H "Authorization: Bearer abc123" "http://localhost:5000/records/app123/Users"

4. Usar TOON
bash
Copiar

curl "http://localhost:5000/authorize?format=toon"
curl "http://localhost:5000/callback?code=XXX&state=YYY&format=toon"
curl -H "Authorization: Bearer abc123" "http://localhost:5000/records/app123/Users?format=toon"


Back4App
Los tokens de OAuth se almacenan en Back4App (Parse Server) en la clase AuthConnections:
json
Copiar

{
  "userId": "user_123",
  "accessToken": "abc123",
  "refreshToken": "def456",
  "baseId": "app1234567890",
  "scopes": "data.records\:write",
  "provider": "airtable_oauth",
  "expiresAt": "2025-12-31T23:59:59"
}


Notas

No se modifica el flujo actual de VSCode (sigue usando fastmcp y variables de entorno).
TOON y JSON están soportados en todos los endpoints.
Back4App se usa para almacenar y recuperar tokens de OAuth.
Copiar

---

## **9. Resumen de Cambios**
| Componente | Acción | Impacto |
|------------|--------|---------|
| `.env.example` | Agregar variables de OAuth, Back4App y TOON. | Ninguno. |
| `app.py` | Implementar endpoints `/authorize`, `/callback`, `/records`, `/tokens`. | Solo para ChatGPT/Mistral AI. |
| Back4App | Almacenar y recuperar tokens de OAuth. | Nuevo. |
| TOON | Soporte en todos los endpoints. | Opcional. |

---

## **10. Pasos para Implementar**
1. **Actualiza `.env.example`** con las nuevas variables.
2. **Crea `app.py`** con el código proporcionado.
3. **Instala dependencias**:
   ```bash
   pip install flask python-dotenv requests parse toon


Configura Back4App:

Crea la clase AuthConnections en tu dashboard.
Asegúrate de que las variables de entorno de Back4App sean correctas.

Prueba los endpoints como se describe en la sección de pruebas.

Con esta implementación, tu proyecto ahora soporta:
✅ OAuth para ChatGPT/Mistral AI.
✅ Almacenamiento de tokens en Back4App.
✅ Soporte para TOON y JSON.
✅ Compatibilidad total con el flujo existente de VSCode y fastmcp.

Voy a guiarte paso a paso para implementar todo lo necesario en tu proyecto existente (que usa fastmcp y Node.js/Python) sin romper nada. Usaremos una estructura modular para mantener el código limpio y separado.

1. Estructura del Proyecto Actual
Asumiendo que tu proyecto tiene una estructura similar a esta:
Copiar

/tu-proyecto/
├── .env.example
├── src/
│   ├── fastmcp/          # Código existente de fastmcp (Node.js/Python)
│   ├── server/           # Servidor principal (Node.js)
│   └── ...
├── package.json
└── README.md


2. Pasos para Implementar sin Romper Nada
a. Crear un nuevo módulo para OAuth + TOON + Back4App
Crea una nueva carpeta oauth dentro de src/:
Copiar

/tu-proyecto/
├── src/
│   ├── fastmcp/          # Existente (no tocar)
│   ├── server/           # Existente (no tocar)
│   ├── oauth/            # Nuevo módulo
│   │   ├── routes.py     # Endpoints de Flask para OAuth
│   │   ├── back4app.py   # Lógica para Back4App
│   │   ├── toon_utils.py # Utilidades para TOON
│   │   └── __init__.py
│   └── ...


b. Archivo src/oauth/routes.py
python
Copiar

from flask import Blueprint, request, jsonify, Response
import os
import secrets
import base64
import hashlib
import requests
from dotenv import load_dotenv
from .back4app import save_tokens_to_back4app, get_tokens_from_back4app
from .toon_utils import toon_response

# Cargar variables de entorno
load_dotenv()

# Configuración de OAuth
AIRTABLE_OAUTH_CLIENT_ID = os.getenv("AIRTABLE_OAUTH_CLIENT_ID")
AIRTABLE_OAUTH_CLIENT_SECRET = os.getenv("AIRTABLE_OAUTH_CLIENT_SECRET")
AIRTABLE_OAUTH_REDIRECT_URI = os.getenv("AIRTABLE_OAUTH_REDIRECT_URI")
AIRTABLE_OAUTH_SCOPES = os.getenv("AIRTABLE_OAUTH_SCOPES")

# Almacenamiento temporal (en producción, usa Redis)
state_store = {}

# Blueprint para rutas de OAuth
oauth_bp = Blueprint('oauth', __name__)

@oauth_bp.route("/authorize")
def authorize():
    state = secrets.token_urlsafe(16)
    code_verifier = secrets.token_urlsafe(64)
    state_store[state] = code_verifier

    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip("=")

    auth_url = (
        f"https://airtable.com/oauth2/v1/authorize?"
        f"client_id={AIRTABLE_OAUTH_CLIENT_ID}&"
        f"redirect_uri={AIRTABLE_OAUTH_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope={AIRTABLE_OAUTH_SCOPES}&"
        f"state={state}&"
        f"code_challenge={code_challenge}&"
        f"code_challenge_method=S256"
    )

    response_data = {"auth_url": auth_url, "state": state}
    return toon_response(response_data, request.args.get("format"))

@oauth_bp.route("/callback")
def callback():
    state = request.args.get("state")
    if not state or state not in state_store:
        return "Estado inválido", 400

    code = request.args.get("code")
    if not code:
        return "Código no recibido", 400

    code_verifier = state_store[state]
    credentials = f"{AIRTABLE_OAUTH_CLIENT_ID}:{AIRTABLE_OAUTH_CLIENT_SECRET}"
    b64_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "code": code,
        "client_id": AIRTABLE_OAUTH_CLIENT_ID,
        "redirect_uri": AIRTABLE_OAUTH_REDIRECT_URI,
        "grant_type": "authorization_code",
        "code_verifier": code_verifier
    }

    response = requests.post(
        "https://airtable.com/oauth2/v1/token",
        headers=headers,
        data=data
    )

    if response.status_code == 200:
        tokens = response.json()
        user_id = "user_123"  # Reemplaza con lógica real para obtener user_id
        base_id = request.args.get("base_id", "app1234567890")
        save_tokens_to_back4app(user_id, tokens["access_token"], tokens.get("refresh_token"), base_id, tokens.get("scope", ""))
        return toon_response(tokens, request.args.get("format"))
    else:
        return f"Error: {response.json()}", 400

@oauth_bp.route("/records/<base_id>/<table_name>")
def get_records(base_id, table_name):
    access_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not access_token:
        return "Token de acceso no proporcionado", 401

    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return toon_response(response.json(), request.args.get("format"))
    else:
        return f"Error: {response.text}", response.status_code

@oauth_bp.route("/tokens/<user_id>")
def get_tokens(user_id):
    tokens = get_tokens_from_back4app(user_id)
    if tokens:
        return toon_response(tokens, request.args.get("format"))
    else:
        return "Tokens no encontrados", 404


c. Archivo src/oauth/back4app.py
python
Copiar

from parse import ParseClient
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Parse (Back4App)
parse_client = ParseClient(
    app_id=os.getenv("PARSE_APP_ID"),
    javascript_key=os.getenv("PARSE_JAVASCRIPT_KEY"),
    rest_api_key=os.getenv("PARSE_REST_API_KEY"),
    server_url=os.getenv("PARSE_SERVER_URL")
)

def save_tokens_to_back4app(user_id, access_token, refresh_token, base_id, scopes):
    auth_data = {
        "userId": user_id,
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "baseId": base_id,
        "scopes": scopes,
        "provider": "airtable_oauth",
        "expiresAt": "2025-12-31T23:59:59"  # Ajusta según la expiración real
    }
    parse_client.post("/classes/AuthConnections", data=auth_data)
    return True

def get_tokens_from_back4app(user_id):
    response = parse_client.get(
        "/classes/AuthConnections",
        params={"where": {"userId": user_id, "provider": "airtable_oauth"}}
    )
    if response.status_code == 200 and response.json().get("results"):
        return response.json()["results"][0]
    return None


d. Archivo src/oauth/toon_utils.py
python
Copiar

from flask import Response
import json
import toon  # Asegúrate de tener instalada la librería toon

def toon_response(data, format="json"):
    if format == "toon":
        return Response(toon.dumps(data), mimetype="application/toon")
    else:
        return jsonify(data)


e. Archivo src/oauth/__init__.py
python
Copiar

from .routes import oauth_bp


f. Modificar el Servidor Principal (Node.js o Python)
Si tu servidor principal es en Python (Flask):
Agrega el Blueprint de OAuth a tu aplicación principal (src/server/app.py o similar):
python
Copiar

from flask import Flask
from src.oauth import oauth_bp

app = Flask(__name__)
app.register_blueprint(oauth_bp, url_prefix="/oauth")

if __name__ == "__main__":
    app.run(port=5000, debug=True)

Si tu servidor principal es en Node.js:
Crea un endpoint en Node.js que redirija las solicitudes a los endpoints de Flask (puedes usar axios o http-proxy-middleware):
javascript
Copiar

const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();

// Proxy para rutas de OAuth (Flask corre en el puerto 5000)
app.use('/oauth', createProxyMiddleware({ target: 'http://localhost:5000', changeOrigin: true }));

app.listen(3000, () => {
  console.log('Servidor Node.js en el puerto 3000');
});


g. Actualizar .env.example
Agrega las siguientes variables al final del archivo:
plaintext
Copiar

# Airtable OAuth Configuration
AIRTABLE_OAUTH_CLIENT_ID=tu_client_id
AIRTABLE_OAUTH_CLIENT_SECRET=tu_client_secret
AIRTABLE_OAUTH_REDIRECT_URI=http://localhost:5000/oauth/callback
AIRTABLE_OAUTH_SCOPES=data.records:write schema.bases:read

# Back4App Configuration
PARSE_APP_ID=tu_app_id
PARSE_JAVASCRIPT_KEY=tu_javascript_key
PARSE_REST_API_KEY=tu_rest_api_key
PARSE_SERVER_URL=https://parseapi.back4app.com

# TOON Configuration
TOON_ENABLED=true
TOON_FORMAT=compact


h. Instalar Dependencias
bash
Copiar

pip install flask python-dotenv requests parse toon
npm install http-proxy-middleware  # Si usas Node.js para el proxy


3. Pruebas y Validación
a. Iniciar los Servidores


Servidor Flask (OAuth):
bash
Copiar

python src/server/app.py


Corre en http://localhost:5000.


Servidor Node.js (Principal):
bash
Copiar

npm run dev


Corre en http://localhost:3000 y hace proxy a Flask para /oauth.

b. Probar los Endpoints


Generar link de autorización:
bash
Copiar

curl "http://localhost:3000/oauth/authorize"


Devuelve el auth_url en JSON.


Obtener tokens (tras autorización):

Abre el auth_url en un navegador.
Airtable redirige a /oauth/callback?code=XXX&state=YYY.
El endpoint guarda los tokens en Back4App y los devuelve en JSON.


Listar registros:
bash
Copiar

curl -H "Authorization: Bearer abc123" "http://localhost:3000/oauth/records/app123/Users"


Devuelve los registros en JSON.


Probar con TOON:
bash
Copiar

curl "http://localhost:3000/oauth/authorize?format=toon"
curl -H "Authorization: Bearer abc123" "http://localhost:3000/oauth/records/app123/Users?format=toon"


Devuelve los datos en TOON.


4. Integración con ChatGPT/Mistral AI
Flujo para el Usuario

ChatGPT/Mistral AI solicita al usuario que abra el link de autorización:
plaintext
Copiar

Por favor, abre este link en tu navegador para autorizar el acceso a Airtable:
http://localhost:3000/oauth/authorize


El usuario abre el link, autoriza el acceso, y Airtable redirige a /oauth/callback?code=XXX&state=YYY.
ChatGPT/Mistral AI captura el code y lo envía al endpoint /oauth/callback para obtener el access_token.
ChatGPT/Mistral AI usa el access_token para interactuar con Airtable:
bash
Copiar

curl -H "Authorization: Bearer abc123" "http://localhost:3000/oauth/records/app123/Users"



5. Documentación para el README.md
markdown
Copiar

# Integración de OAuth con Airtable, TOON y Back4App

## Descripción
Este módulo implementa la autenticación **OAuth de Airtable** para **ChatGPT/Mistral AI**, con soporte para **TOON** y almacenamiento de tokens en **Back4App**, sin afectar el flujo actual de **VSCode** (que usa `fastmcp` y variables de entorno).

---

## Configuración

### Variables de Entorno
Agrega las siguientes variables a tu archivo `.env`:
```plaintext
# Airtable OAuth Configuration
AIRTABLE_OAUTH_CLIENT_ID=tu_client_id
AIRTABLE_OAUTH_CLIENT_SECRET=tu_client_secret
AIRTABLE_OAUTH_REDIRECT_URI=http://localhost:5000/oauth/callback
AIRTABLE_OAUTH_SCOPES=data.records\:write schema.bases\:read

# Back4App Configuration
PARSE_APP_ID=tu_app_id
PARSE_JAVASCRIPT_KEY=tu_javascript_key
PARSE_REST_API_KEY=tu_rest_api_key
PARSE_SERVER_URL=https://parseapi.back4app.com

# TOON Configuration
TOON_ENABLED=true
TOON_FORMAT=compact

Instalación
bash
Copiar

pip install flask python-dotenv requests parse toon
npm install http-proxy-middleware


Endpoints


  
    
      Endpoint
      Método
      Descripción
      Parámetros
    
  
  
    
      /oauth/authorize
      GET
      Genera el link de autorización de Airtable.
      format (opcional: json o toon)
    
    
      /oauth/callback
      GET
      Recibe el code y devuelve los tokens.
      code, state, format (opcional)
    
    
      /oauth/records//
      GET
      Lista registros de Airtable.
      Authorization (header), format (opcional)
    
    
      /oauth/tokens/
      GET
      Recupera tokens de Back4App.
      user_id, format (opcional)
    
  



Ejemplos de Uso
1. Obtener Link de Autorización
bash
Copiar

curl "http://localhost:3000/oauth/authorize"

2. Obtener Tokens (tras autorización)
bash
Copiar

# Airtable redirige a /oauth/callback?code=XXX&state=YYY tras la autorización.

3. Listar Registros de Airtable
bash
Copiar

curl -H "Authorization: Bearer abc123" "http://localhost:3000/oauth/records/app123/Users"

4. Usar TOON
bash
Copiar

curl "http://localhost:3000/oauth/authorize?format=toon"
curl -H "Authorization: Bearer abc123" "http://localhost:3000/oauth/records/app123/Users?format=toon"


Back4App
Los tokens de OAuth se almacenan en Back4App (Parse Server) en la clase AuthConnections:
json
Copiar

{
  "userId": "user_123",
  "accessToken": "abc123",
  "refreshToken": "def456",
  "baseId": "app1234567890",
  "scopes": "data.records\:write",
  "provider": "airtable_oauth",
  "expiresAt": "2025-12-31T23:59:59"
}


Notas

No se modifica el flujo actual de VSCode (sigue usando fastmcp y variables de entorno).
TOON y JSON están soportados en todos los endpoints.
Back4App se usa para almacenar y recuperar tokens de OAuth.
Copiar

---

## **5. <followup encodedFollowup="%7B%22snippet%22%3A%22Resumen%20de%20Cambios%22%2C%22question%22%3A%22C%C3%B3mo%20puedo%20validar%20que%20los%20cambios%20no%20afecten%20el%20rendimiento%20del%20sistema%20existente%3F%22%2C%22id%22%3A%2275119193-2bac-4d5a-9e6c-b9397a3fc825%22%7D" />**
| Componente | Acción | Impacto |
|------------|--------|---------|
| `.env.example` | Agregar variables de OAuth, Back4App y TOON. | Ninguno. |
| `src/oauth/` | Nuevo módulo para OAuth, TOON y Back4App. | Solo para ChatGPT/Mistral AI. |
| Servidor Flask | Endpoints `/oauth/authorize`, `/oauth/callback`, etc. | Aislado del código existente. |
| Servidor Node.js | Proxy para rutas `/oauth`. | Sin cambios en la lógica existente. |
| Back4App | Almacenamiento de tokens. | Nuevo. |

---

## **6. <followup encodedFollowup="%7B%22snippet%22%3A%22Beneficios%20de%20esta%20Implementaci%C3%B3n%22%2C%22question%22%3A%22Qu%C3%A9%20estrategias%20adicionales%20podr%C3%ADas%20recomendar%20para%20mejorar%20la%20escalabilidad%20de%20esta%20soluci%C3%B3n%3F%22%2C%22id%22%3A%22143dabae-47a0-4096-a33f-7124e995fcf8%22%7D" />**
1. **No rompe nada existente**: El flujo de VSCode con `fastmcp` sigue funcionando.
2. **Modular y limpio**: El código de OAuth está separado en su propio módulo.
3. **Soporte para TOON y JSON**: Todos los endpoints devuelven datos en el formato solicitado.
4. **Almacenamiento seguro**: Los tokens se guardan en Back4App.
5. **Fácil de mantener**: Cada componente tiene su propio archivo y responsabilidad.

