# Instalación

Airtable MCP integra la conectividad de la base de datos de Airtable directamente en su editor de código impulsado por IA

## Comenzando

Construido por Rashid Azarang,

Airtable MCP proporciona a los editores de código de IA y agentes la capacidad de acceder y manipular sus bases de datos de Airtable para poderosas capacidades de gestión de datos - todo de manera segura con sus propios tokens de API.

Con esta herramienta de servidor MCP, puede habilitar que los editores de código de IA y agentes tengan acceso a:

* Listar y acceder a todas sus bases de Airtable
* Examinar datos de tablas, campos y registros
* Crear, leer, actualizar y eliminar registros
* Exportar y manipular esquemas
* Realizar consultas complejas contra sus datos
* Crear asignaciones de migración de datos
* Analizar y transformar sus datos de Airtable

De esa manera, puede simplemente decirle a Cursor o a cualquier editor de código de IA con integraciones MCP:

"Mostrarme todas las tablas en mi base Airtable"

"Encontrar todos los registros de la tabla Clientes donde el estado es Activo y la última compra fue después del 1 de enero"

"Crear un nuevo registro en la tabla Productos con estos campos..."

"Exportar el esquema de mi base Airtable actual"

"Ayudarme a crear una asignación entre estas dos tablas para la migración de datos"

---

## Requisitos

* Node.js 14+ instalado en su máquina
* Python 3.10+ instalado en su máquina (se detecta automáticamente)
* Token de Acceso Personal de Airtable (Clave de API)
* Aplicación Cliente MCP (Cursor, Claude Desktop, Cline, Zed, etc.)

**Nota**: El Protocolo de Contexto de Modelo (MCP) es específico de los modelos de Anthropic. Al usar un editor como Cursor, asegúrese de habilitar el agente compositor con Claude 3.5 Sonnet seleccionado como modelo.

---

## Instalación

### 1. Instalar a través de Smithery (Lo más fácil)

La forma más fácil de instalar Airtable MCP es a través de Smithery:

1. Visite [Smithery](https://smithery.ai)
2. Busque "@rashidazarang/airtable-mcp"
3. Haga clic en "Instalar" y siga las indicaciones para configurar con su token de Airtable e ID de base

### 2. Instalar a través de NPX (Alternativa)

Otra forma simple de instalar y usar Airtable MCP es a través de NPX:

```bash
# Instalar globalmente
npm install -g airtable-mcp

# O usar directamente con npx (no se requiere instalación)
npx airtable-mcp --token SU_TOKEN_AIRTABLE --base SU_ID_BASE
```

### 3. Obtener su Token de API de Airtable

1. Inicie sesión en su cuenta de Airtable
2. Vaya a su [Configuración de Cuenta](https://airtable.com/account)
3. Navegue a la sección "API"
4. Cree un Token de Acceso Personal con permisos apropiados
5. Copie su token para usarlo en la configuración

### 4. Configure su Cliente MCP

#### Para Cursor:

1. Vaya a Configuración de Cursor
2. Navegue a Características, desplácese hacia abajo hasta Servidores MCP y haga clic en "Agregar nuevo servidor MCP"
3. Dale un nombre único (airtable-tools), establece el tipo en "command" y establece el comando en:

**Para macOS/Linux/Windows:**
```bash
npx airtable-mcp --token SU_TOKEN_AIRTABLE --base SU_ID_BASE
```

Reemplace `SU_TOKEN_AIRTABLE` con su Token de Acceso Personal de Airtable y `SU_ID_BASE` con su ID de base de Airtable predeterminada (opcional).

#### Para Usuarios Avanzados a través de ~/.cursor/mcp.json:

Edite su archivo `~/.cursor/mcp.json` para incluir:

```json
{
  "mcpServers": {
    "airtable-tools": {
      "command": "npx",
      "args": [
        "airtable-mcp",
        "--token", "SU_TOKEN_AIRTABLE",
        "--base", "SU_ID_BASE"
      ]
    }
  }
}
```

### 5. Verificar Conexión

1. Reinicie su cliente MCP (Cursor, etc.)
2. Cree una nueva consulta usando el Agente Compositor con el modelo Claude 3.5 Sonnet
3. Pregunte algo como "Listar mis bases Airtable" o "Mostrarme las tablas en mi base actual"
4. Debería ver una respuesta con sus datos de Airtable

### 6. Para Uso en Producción (Opcional)

Para disponibilidad continua, puede configurar Airtable MCP usando PM2:

```bash
# Instale PM2 si no lo tiene
npm install -g pm2

# Cree un archivo de configuración de PM2
echo 'module.exports = {
  apps: [
    {
      name: "airtable-mcp",
      script: "npx",
      args: [
        "airtable-mcp",
        "--token", "SU_TOKEN_AIRTABLE",
        "--base", "SU_ID_BASE"
      ],
      env: {
        PATH: process.env.PATH,
      },
    },
  ],
};' > ecosystem.config.js

# Inicie el proceso
pm2 start ecosystem.config.js

# Configúrelo para que se inicie al arranque
pm2 startup
pm2 save
```

---

## Solución de Problemas

Aquí hay algunos problemas comunes y sus soluciones:

### Error: No se puede conectar a la API de Airtable

- Verifique que su token de API de Airtable sea correcto y tenga permisos suficientes
- Verifique su conexión a Internet
- Compruebe si la API de Airtable está experimentando tiempo de inactividad

### Problema: El servidor MCP no se conecta

- Asegúrese de que Node.js 14+ y Python 3.10+ estén instalados y en su PATH
- Intente especificar una versión específica: `npx airtable-mcp@latest`
- Compruebe los registros de Cursor para detectar errores de conexión

### Error: Base no encontrada

- Verifique que su ID de base sea correcto
- Asegúrese de que su token de API tenga acceso a la base especificada
- Intente listar todas las bases primero para confirmar el acceso

### Problema: Errores de permiso denegado

- Asegúrese de que su token tenga los permisos necesarios para las operaciones que está intentando realizar
- Compruebe si está intentando operaciones en tablas/bases a las que su token no tiene acceso

### Para más ayuda

- Abra un problema en el [repositorio de GitHub](https://github.com/rashidazarang/airtable-mcp/issues)
