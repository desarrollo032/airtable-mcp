# Estructura del Proyecto

## 📁 Diseño de Directorios

```
airtable-mcp/
├── src/                    # Código fuente
│   ├── index.js           # Punto de entrada principal
│   ├── typescript/        # Implementación de TypeScript
│   ├── javascript/        # Implementación de JavaScript
│   └── python/            # Implementación de Python
├── dist/                  # Salida compilada de TypeScript
├── docs/                  # Documentación
│   ├── api/              # Documentación de API
│   ├── guides/           # Guías de usuario
│   └── releases/         # Notas de lanzamiento
├── tests/                 # Archivos de prueba
│   ├── unit/            # Pruebas unitarias
│   ├── integration/     # Pruebas de integración
│   └── e2e/             # Pruebas de extremo a extremo
├── examples/             # Ejemplos de uso
├── bin/                  # Ejecutables de CLI
├── scripts/              # Secuencias de construcción y utilidades
├── config/               # Archivos de configuración
├── docker/               # Configuraciones de Docker
└── types/                # Definiciones de tipo de TypeScript
```

## 🚀 Inicio Rápido

```bash
# Instalar dependencias
npm install

# Construir TypeScript
npm run build

# Ejecutar el servidor
npm start

# Modo de desarrollo
npm run dev

# Ejecutar pruebas
npm test
```

## 📦 Scripts Disponibles

- `npm run build` - Compilar TypeScript a JavaScript
- `npm start` - Iniciar el servidor de producción
- `npm run dev` - Iniciar servidor de desarrollo con recarga en caliente
- `npm test` - Ejecutar todas las pruebas
- `npm run lint` - Verificar la calidad del código
- `npm run format` - Dar formato al código con Prettier

## 🔧 Implementaciones

### TypeScript (Primaria)
- Ubicación: `src/typescript/`
- Salida: `dist/`
- Entrada: `airtable-mcp-server.ts`

### JavaScript
- Ubicación: `src/javascript/`
- Entrada: `airtable_simple_production.js`

### Python
- Ubicación: `src/python/`
- Entrada: `inspector_server.py`

## 📝 Archivos de Configuración

- `package.json` - Dependencias y scripts de Node.js
- `tsconfig.json` - Configuración del compilador de TypeScript
- `.eslintrc.js` - Reglas de ESLint
- `.prettierrc` - Reglas de formato de Prettier
- `jest.config.js` - Configuración de pruebas de Jest
- `.nvmrc` - Especificación de versión de Node.js

## 🧪 Pruebas

Las pruebas están organizadas por tipo:
- Pruebas unitarias: `tests/unit/`
- Pruebas de integración: `tests/integration/`
- Pruebas de extremo a extremo: `tests/e2e/`

Ejecutar suites de pruebas específicas:
```bash
npm run test:unit
npm run test:integration
npm run test:e2e
```

## 📚 Documentación

- Documentación de API: `docs/api/`
- Guías de usuario: `docs/guides/`
- Notas de lanzamiento: `docs/releases/`
- Registro de cambios: `CHANGELOG.md`

## 🐳 Soporte de Docker

Las configuraciones de Docker están en el directorio `docker/`:
- `Dockerfile` - Implementación de Python
- `Dockerfile.node` - Implementación de Node.js

## 🤝 Contribuyendo

Para obtener información sobre cómo contribuir, consulte `CONTRIBUTING.md`
