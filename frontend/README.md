# Todo List Frontend

Una aplicación frontend moderna para gestión de tareas construida con React 19, TypeScript y Tailwind CSS, con integración completa a la API REST del backend.

## 🚀 Características Principales

- **React 19**: Última versión de React con hooks modernos y optimizaciones
- **TypeScript**: Type safety completo para mejor desarrollo y mantenimiento
- **Tailwind CSS 4.1.8**: Framework CSS moderno con diseño responsive
- **Vite**: Build tool rápido con Hot Module Replacement
- **React Router DOM**: Navegación SPA con routing avanzado
- **Axios**: Cliente HTTP con interceptors automáticos para JWT
- **Context API**: Gestión de estado global sin librerías externas
- **Hooks Personalizados**: Lógica reutilizable y optimizada
- **Componentes Modulares**: Arquitectura escalable y mantenible

## 🛠️ Stack Tecnológico

- **Framework**: React 19.1.0
- **Lenguaje**: TypeScript 5.8.3
- **Estilos**: Tailwind CSS 4.1.8
- **Build Tool**: Vite 6.3.5
- **Routing**: React Router DOM 7.6.2
- **HTTP Client**: Axios 1.9.0
- **Linting**: ESLint 9.25.0
- **Package Manager**: pnpm (recomendado)

## 📁 Estructura del Proyecto

```
src/
├── components/              # Componentes reutilizables
│   ├── ProductivityMetrics.tsx  # Métricas de productividad
│   ├── SignIn.tsx              # Formulario de login
│   ├── SignUp.tsx              # Formulario de registro
│   ├── StatisticsPanel.tsx     # Panel de estadísticas
│   ├── TaskStatistics.tsx      # Estadísticas de tareas
│   └── Todo.tsx                # Componente principal de tareas
├── contexts/               # Context providers
│   ├── AuthContext.tsx         # Contexto de autenticación
│   └── TodoContext.tsx         # Contexto de tareas
├── hooks/                  # Hooks personalizados
│   ├── useAuthService.ts       # Hook para autenticación
│   ├── useTodo.ts             # Hook básico para tareas
│   └── useTodoOptimized.ts    # Hook optimizado para tareas
├── services/               # Servicios de API
│   ├─�� api.ts                 # Configuración base de Axios
│   └── todoService.ts         # Servicios específicos de tareas
├── types/                  # Definiciones de tipos TypeScript
│   └── types.ts               # Tipos compartidos
├── assets/                 # Recursos estáticos
│   └── icons/                 # Iconos SVG personalizados
│       ├── CheckIcon.tsx
│       ├── DeleteIcon.tsx
│       ├── SaveIcon.tsx
│       └── index.ts
├── App.tsx                 # Componente principal
├── main.tsx               # Punto de entrada
└── routes.tsx             # Configuración de rutas
```

## 🚀 Instalación y Desarrollo

### Prerrequisitos
- Node.js 18+ 
- pnpm (recomendado) o npm

### Instalación

```bash
# Clonar el repositorio
git clone <repository-url>
cd PruebaTecnica/frontend

# Instalar dependencias con pnpm (recomendado)
pnpm install

# O con npm
npm install
```

### Desarrollo

```bash
# Iniciar servidor de desarrollo
pnpm dev

# O con npm
npm run dev
```

La aplicación estará disponible en http://localhost:5173

### Build para Producción

```bash
# Construir para producción
pnpm build

# Previsualizar build de producción
pnpm preview
```

### Linting

```bash
# Ejecutar ESLint
pnpm lint

# O con npm
npm run lint
```

## 🔧 Configuración

### Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto frontend:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=Todo List App
```

### Configuración de Vite

El proyecto usa Vite con las siguientes configuraciones principales:

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true
  }
})
```

## 🎨 Componentes Principales

### AuthContext
Maneja el estado global de autenticación:
- Login/logout automático
- Persistencia de tokens JWT
- Refresh automático de tokens
- Estado de carga

### TodoContext
Gestiona el estado de las tareas:
- CRUD de tareas
- Filtrado y búsqueda
- Estadísticas en tiempo real
- Optimizaciones de rendimiento

### Hooks Personalizados

#### useAuthService
```typescript
const { login, logout, register, isAuthenticated, user } = useAuthService();
```

#### useTodoOptimized
```typescript
const {
  tasks,
  loading,
  createTask,
  updateTask,
  deleteTask,
  toggleTask,
  bulkComplete
} = useTodoOptimized();
```

## 🎯 Funcionalidades

### Autenticación
- ✅ Login con email y contraseña
- ✅ Registro de nuevos usuarios
- ✅ Logout automático
- ✅ Manejo automático de tokens JWT
- ✅ Refresh automático de tokens
- ✅ Protección de rutas

### Gestión de Tareas
- ✅ Crear nuevas tareas
- ✅ Editar tareas existentes
- ✅ Marcar como completadas/pendientes
- ✅ Eliminar tareas
- ✅ Filtrar por estado y prioridad
- ✅ Búsqueda en tiempo real
- ✅ Operaciones en lote

### Interfaz de Usuario
- ✅ Diseño responsive (móvil y desktop)
- ✅ Tema moderno con Tailwind CSS
- ✅ Animaciones suaves
- ✅ Feedback visual inmediato
- ✅ Loading states
- ✅ Manejo de errores

### Estadísticas y Métricas
- ✅ Panel de estadísticas de tareas
- ✅ Métricas de productividad
- ✅ Gráficos visuales
- ✅ Progreso en tiempo real

## 🔒 Seguridad

### Autenticación JWT
- Tokens almacenados de forma segura
- Refresh automático antes de expiración
- Logout automático en caso de tokens inválidos
- Interceptors de Axios para manejo automático

### Validación
- Validación de formularios en tiempo real
- Sanitización de entrada de usuario
- Manejo seguro de errores de API

## 🚀 Optimizaciones de Rendimiento

### React Optimizations
- Uso de `useMemo` y `useCallback` para evitar re-renders
- Lazy loading de componentes
- Optimización de Context providers
- Debouncing en búsquedas

### Network Optimizations
- Interceptors de Axios para manejo automático de tokens
- Cache de respuestas cuando es apropiado
- Manejo optimizado de estados de carga
- Retry automático en caso de errores de red

## 🎨 Estilos y Diseño

### Tailwind CSS
El proyecto usa Tailwind CSS 4.1.8 con:
- Configuración personalizada
- Clases utilitarias modernas
- Diseño responsive
- Tema consistente

### Componentes de UI
- Botones con estados hover y active
- Formularios con validación visual
- Modales y overlays
- Iconos SVG personalizados

## 🧪 Testing

```bash
# Ejecutar tests (cuando estén configurados)
pnpm test

# Coverage
pnpm test:coverage
```

## 📱 Responsive Design

La aplicación está optimizada para:
- **Desktop**: Experiencia completa con sidebar y paneles
- **Tablet**: Layout adaptado con navegación optimizada
- **Mobile**: Interfaz simplificada y touch-friendly

## 🔧 Desarrollo

### Estructura de Commits
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bugs
- `docs:` Documentación
- `style:` Cambios de estilo
- `refactor:` Refactoring de código
- `test:` Tests

### Code Style
- ESLint configurado con reglas estrictas
- Prettier para formateo automático
- TypeScript strict mode
- Convenciones de naming consistentes

## 🚀 Deployment

### Docker
```bash
# Build imagen Docker
docker build -t todo-frontend .

# Ejecutar contenedor
docker run -p 5173:5173 todo-frontend
```

### Build Estático
```bash
# Build para producción
pnpm build

# Los archivos estáticos estarán en dist/
```

## 🐛 Troubleshooting

### Problemas Comunes

1. **Error de CORS**: Verificar configuración del backend
2. **Tokens expirados**: El refresh automático debería manejar esto
3. **Problemas de build**: Limpiar node_modules y reinstalar

### Debug
```bash
# Limpiar cache
pnpm store prune

# Reinstalar dependencias
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

## 📄 Licencia

MIT License

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para la feature (`git checkout -b feature/AmazingFeature`)
3. Commit los cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request