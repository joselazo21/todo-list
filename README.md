# 🚀 Todo List Application - Full Stack

Una aplicación completa de lista de tareas con frontend en React y backend en Django, implementando arquitectura limpia y completamente dockerizada para fácil despliegue.

## 📥 Clonar el Proyecto

Para obtener una copia local del proyecto, puede clonarlo usando Git:

### 🔗 **Usando HTTPS (Recomendado)**
```bash
git clone https://github.com/tu-usuario/PruebaTecnica.git
cd PruebaTecnica
```

### 🔑 **Usando SSH**
```bash
git clone git@github.com:tu-usuario/PruebaTecnica.git
cd PruebaTecnica
```

### 📦 **Descargar ZIP**
También puede descargar el proyecto como archivo ZIP desde GitHub:
1. Vaya al repositorio en GitHub
2. Haga clic en el botón verde "Code"
3. Seleccione "Download ZIP"
4. Extraiga el archivo y navegue a la carpeta

### ✅ **Verificar la Clonación**
Una vez clonado, verifique que tienes todos los archivos:
```bash
ls -la
# Deberia ver: backend/, frontend/, docker-compose.yml, README.md, etc.
```

## ⚡ Inicio Rápido

### 📋 Prerrequisitos
- Docker
- Docker Compose

### 🚀 Ejecutar la Aplicación

#### Método Recomendado (Con información visual):

**En Linux/macOS:**
```bash
./start-app.sh
```

**En Windows:**
```cmd
start-app.bat
```

#### Método Manual (Docker Compose tradicional):
```bash
# Levantar todos los servicios
docker compose up --build

# En segundo plano
docker compose up --build -d
```

### 🛑 Detener la Aplicación
```bash
docker compose down
```

### 🔄 Reiniciar desde Cero
```bash
docker compose down -v
docker compose up --build
```

## 🌐 URLs de Acceso

Una vez iniciada la aplicación:

### 🎯 **Aplicación Principal**
- **URL Principal**: http://localhost:8080

### 🔧 **Servicios Individuales**
- **Frontend (React)**: http://localhost:5173
- **Backend API**: http://localhost:8080/api/
- **Admin Django**: http://localhost:8080/admin/
- **API Documentation**: http://localhost:8080/api/schema/swagger-ui/

### 🗄️ **Base de Datos**
- **PostgreSQL**: localhost:5432
- **Database**: todo_database
- **User**: postgres
- **Password**: postgres

## 🏗️ Arquitectura Completa

### 📦 **Servicios Dockerizados**

La aplicación está completamente empaquetada en 4 contenedores:

1. **🗄️ PostgreSQL Database** (puerto 5432)
   - Base de datos principal
   - Datos persistentes en volumen Docker
   - Configuración automática

2. **🐍 Django Backend** (puerto 8000)
   - API REST con Django REST Framework
   - Autenticación JWT
   - Arquitectura limpia con DDD
   - Instalación automática de dependencias

3. **⚛️ React Frontend** (puerto 5173)
   - Interfaz de usuario con React + TypeScript
   - Vite como bundler
   - TailwindCSS para estilos
   - Instalación automática de dependencias

4. **🌐 Nginx Reverse Proxy** (puerto 8080)
   - Proxy reverso que unifica frontend y backend
   - Manejo de archivos estáticos
   - Punto de entrada único

### 🎯 **Empaquetado Completo**

✅ **No necesitas instalar nada más que Docker**
- No requiere Node.js, Python, PostgreSQL local
- Todas las dependencias se instalan automáticamente
- Base de datos se configura automáticamente
- Migraciones se ejecutan automáticamente

## 📊 Funcionalidades

### 🐍 **Backend (Django API)**
- ✅ **Autenticación JWT**: Login, registro, refresh tokens
- ✅ **Seguridad avanzada**: Rate limiting, protección contra fuerza bruta
- ✅ **CRUD completo de tareas**: Crear, leer, actualizar, eliminar
- ✅ **Filtrado avanzado**: Por estado, prioridad, fecha
- ✅ **Búsqueda**: En título y descripción
- ✅ **Prioridades**: Baja, media, alta, urgente
- ✅ **Fechas de vencimiento**: Con detección de tareas vencidas
- ✅ **Estadísticas**: Métricas de productividad
- ✅ **Documentación automática**: Swagger/OpenAPI
- ✅ **Admin mejorado**: Interfaz administrativa completa

### ⚛️ **Frontend (React)**
- ✅ **Interfaz moderna**: Tailwind CSS con diseño responsive
- ✅ **React 19**: Última versión con TypeScript
- ✅ **Gestión de estado**: Context API optimizada
- ✅ **Autenticación**: Manejo automático de tokens
- ✅ **Componentes reutilizables**: Arquitectura modular
- ✅ **Estadísticas visuales**: Panel de métricas
- ✅ **Optimización**: Hooks optimizados para rendimiento

## 📁 Estructura del Proyecto

```
PruebaTecnica/
├── backend/                 # Django API
│   ├── apps/               # Aplicaciones Django
│   │   ├── authentication/ # Autenticación JWT
│   │   ├── tasks/          # Gestión de tareas
│   │   ├── users/          # Gestión de usuarios
│   │   └── shared/         # Componentes compartidos
│   ├── config/             # Configuración Django
│   ├── Dockerfile          # Docker para backend
│   ├── requirements.txt    # Dependencias Python
│   └── manage.py
├── frontend/               # React App
│   ├── src/               # Código fuente React
│   │   ├── components/    # Componentes React
│   │   ├── contexts/      # Context API
│   │   ├── hooks/         # Custom hooks
│   │   ├── services/      # Servicios API
│   │   └── types/         # Tipos TypeScript
│   ├── Dockerfile         # Docker para frontend
│   ├── package.json       # Dependencias Node.js
│   └── vite.config.ts     # Configuración Vite
├── scripts/               # Scripts de utilidad
├── docker-compose.yml     # Orquestación de servicios
├── nginx.conf            # Configuración Nginx
├── start-app.sh          # Script de inicio (Linux/macOS)
├── start-app.bat         # Script de inicio (Windows)
└── README.md             # Este archivo
```

## 🛠️ Comandos Útiles

### 📊 **Monitoreo**
```bash
# Ver estado de contenedores
docker compose ps

# Ver logs en tiempo real
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs frontend
docker compose logs backend
docker compose logs nginx
docker compose logs db
```

### 🔧 **Desarrollo**
```bash
# Reconstruir servicios
docker compose up --build

# Ejecutar comandos en el backend
docker compose exec backend python manage.py shell
docker compose exec backend python manage.py createsuperuser

# Acceder a la base de datos
docker compose exec db psql -U postgres -d todo_database

# Ejecutar tests del backend
docker compose exec backend python manage.py test
```

### 🧹 **Limpieza**
```bash
# Detener y eliminar contenedores
docker compose down

# Eliminar también volúmenes (datos de BD)
docker compose down -v

# Limpiar imágenes no utilizadas
docker system prune
```

## 🔧 Configuración Avanzada

### 🔀 **Cambiar Puertos**

Si algún puerto está ocupado, edita `docker-compose.yml`:

```yaml
nginx:
  ports:
    - "8081:80"  # Cambiar 8080 por 8081

frontend:
  ports:
    - "5174:5173"  # Cambiar 5173 por 5174
```

### 🔒 **Variables de Entorno**

Todas las configuraciones están en `docker-compose.yml`. Para producción, cambia:

- `SECRET_KEY`: Usar una clave secreta segura
- `DEBUG`: Cambiar a `False`
- `ALLOWED_HOSTS`: Configurar hosts permitidos
- Credenciales de base de datos

### 🚀 **Modo Producción**

Para producción, crea un `docker-compose.prod.yml`:

```yaml
services:
  backend:
    environment:
      - DEBUG=False
      - SECRET_KEY=tu-clave-secreta-segura
      - ALLOWED_HOSTS=tu-dominio.com
```

## 🐛 Solución de Problemas

### ❌ **Los contenedores no inician**
```bash
# Verificar logs
docker compose logs

# Reconstruir desde cero
docker compose down -v
docker compose up --build
```

### ❌ **Puerto ocupado**
```
Error: bind: address already in use
```
**Solución**: Cambiar puertos en `docker-compose.yml` o detener el servicio que usa el puerto.

### ❌ **Error de permisos (Linux/macOS)**
```bash
chmod +x start-app.sh
```

### ❌ **Frontend no carga**
- Verificar que nginx esté funcionando: `docker compose logs nginx`
- Verificar que frontend esté funcionando: `docker compose logs frontend`
- Probar acceso directo: http://localhost:5173

### ❌ **Backend no responde**
- Verificar logs: `docker compose logs backend`
- Verificar base de datos: `docker compose logs db`
- Probar acceso directo: http://localhost:8000

### ❌ **Base de datos no conecta**
```bash
# Verificar estado de la BD
docker compose exec db pg_isready -U postgres

# Recrear volumen de BD
docker compose down -v
docker compose up --build
```

## 🎯 Características Técnicas

### 🔒 **Seguridad**
- Autenticación JWT con refresh tokens
- Rate limiting en endpoints críticos
- Protección CORS configurada
- Validación de entrada completa
- Sanitización de datos

### 📈 **Performance**
- Nginx como proxy reverso
- Archivos estáticos optimizados
- Queries de base de datos optimizadas
- Frontend con lazy loading
- Caché de dependencias en Docker

### 🧪 **Testing**
- Tests unitarios en backend
- Cobertura de API endpoints
- Validación de modelos
- Tests de autenticación

### 📚 **Documentación**
- API documentada con Swagger
- Código comentado
- README completo
- Arquitectura documentada

## 🚀 Despliegue

### 🐳 **Docker Hub**
```bash
# Construir y subir imágenes
docker build -t tu-usuario/todolist-backend ./backend
docker build -t tu-usuario/todolist-frontend ./frontend
docker push tu-usuario/todolist-backend
docker push tu-usuario/todolist-frontend
```

### ☁️ **Cloud Deployment**
El proyecto está listo para desplegar en:
- AWS (ECS, EC2)
- Google Cloud (Cloud Run, GKE)
- Azure (Container Instances, AKS)
- DigitalOcean (App Platform)
- Heroku
- Railway

## 📝 Licencia

MIT License - Puedes usar este proyecto libremente.

---

## 🎉 ¡Listo para Usar!

Con un solo comando tienes una aplicación completa funcionando:

```bash
./start-app.sh
```

**¡Abre tu navegador en http://localhost:8080 y disfruta! 🚀**