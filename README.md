# Todo List API - Backend

Una API REST completa para gestión de tareas construida con Django REST Framework, implementando Clean Architecture y características avanzadas de seguridad.

## 🚀 Características Principales

- **Autenticación JWT**: Autenticación basada en tokens con registro y login
- **Seguridad Avanzada**: Bloqueo de cuentas, seguimiento de intentos fallidos, rate limiting y protección contra fuerza bruta
- **Gestión de Usuarios**: Crear y gestionar usuarios con verificación de email y validación mejorada
- **Gestión de Tareas**: Operaciones CRUD completas para tareas con prioridades y fechas de vencimiento
- **Filtrado Avanzado**: Filtrar tareas por estado de completado, prioridad, fecha de vencimiento y más
- **Funcionalidad de Búsqueda**: Buscar tareas por título, descripción o nombre de usuario
- **Estadísticas**: Obtener insights sobre tareas y usuarios
- **Operaciones en Lote**: Completar múltiples tareas a la vez
- **Documentación API**: Documentación automática Swagger/OpenAPI
- **Testing Completo**: Cobertura completa de tests para modelos, vistas y endpoints de API

## 🛠️ Stack Tecnológico

- **Backend**: Django 5.2.1, Django REST Framework 3.15.2
- **Autenticación**: JWT (Simple JWT), Django Axes para protección contra fuerza bruta
- **Base de Datos**: PostgreSQL
- **Documentación**: drf-spectacular (OpenAPI/Swagger)
- **Seguridad**: Headers CORS, rate limiting, validación de entrada
- **Testing**: Django TestCase, DRF APITestCase
- **Calidad de Código**: Logging completo, validación y manejo de errores

## 🏗️ Arquitectura Clean Architecture

El proyecto implementa Clean Architecture con las siguientes capas:

```
apps/
├── authentication/          # Módulo de autenticación
│   ├── domain/             # Entidades y reglas de negocio
│   ├── application/        # Casos de uso y DTOs
│   ├── infrastructure/     # Repositorios e implementaciones
│   └── presentation/       # Controladores y serializers
├── tasks/                  # Módulo de tareas
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── presentation/
├── users/                  # Módulo de usuarios
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── presentation/
└── shared/                 # Componentes compartidos
    ├── domain/
    ├── application/
    ├── infrastructure/
    └── presentation/
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd todolist
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and settings
   ```

5. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

## 📡 API Endpoints

### 🔐 Autenticación (`/api/v1/auth/` y `/api/v2/auth/`)
- `POST /register/` - Registrar un nuevo usuario
- `POST /login/` - Login de usuario (retorna tokens JWT)
- `POST /refresh/` - Refrescar token de acceso
- `POST /logout/` - Cerrar sesión
- `POST /validate-token/` - Validar token
- `POST /password-reset/` - Solicitar reset de contraseña
- `POST /password-reset-confirm/` - Confirmar reset de contraseña
- `GET /sessions/` - Obtener sesiones del usuario
- `GET /security-events/` - Obtener eventos de seguridad

### 📋 Tareas (`/api/v1/tasks/` y `/api/v2/tasks/`)
- `GET /` - Listar todas las tareas (con filtrado y búsqueda)
- `POST /` - Crear una nueva tarea
- `GET /{id}/` - Obtener una tarea específica
- `PUT /{id}/` - Actualizar una tarea
- `DELETE /{id}/` - Eliminar una tarea
- `POST /bulk-complete/` - Marcar múltiples tareas como completadas
- `GET /statistics/` - Obtener estadísticas de tareas
- `GET /productivity/` - Obtener métricas de productividad

### 👥 Usuarios (`/api/v1/users/` y `/api/v2/users/`)
- `GET /` - Listar todos los usuarios
- `POST /` - Crear un nuevo usuario
- `GET /{id}/` - Obtener un usuario específico
- `PUT /{id}/` - Actualizar un usuario
- `DELETE /{id}/` - Eliminar un usuario
- `GET /{id}/tasks/` - Obtener usuario con sus tareas
- `GET /statistics/` - Obtener estadísticas de usuarios

## Filtering and Search

### Task Filtering
- `?completed=true/false` - Filter by completion status
- `?priority=low/medium/high/urgent` - Filter by priority
- `?user={user_id}` - Filter by user
- `?overdue=true/false` - Filter overdue tasks
- `?due_date_from=YYYY-MM-DD` - Filter tasks due after date
- `?due_date_to=YYYY-MM-DD` - Filter tasks due before date

### Search
- `?search={query}` - Search in task title, description, or user name

### Ordering
- `?ordering=created_at` - Order by creation date
- `?ordering=-due_date` - Order by due date (descending)
- `?ordering=priority` - Order by priority

## Authentication

The API uses JWT (JSON Web Token) authentication. To access protected endpoints:

1. **Register a new user**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/register/ \
     -H "Content-Type: application/json" \
     -d '{"name": "John Doe", "email": "john@example.com", "password": "securepassword123"}'
   ```

2. **Login to get JWT tokens**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"email": "john@example.com", "password": "securepassword123"}'
   ```

3. **Use the access token in requests**:
   ```bash
   curl -X GET http://localhost:8000/api/v1/tasks/ \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

### Token Management
- **Access tokens** expire after 60 minutes
- **Refresh tokens** expire after 7 days
- Use refresh tokens to get new access tokens without re-authentication

### Security Features
- Account lockout after 5 failed login attempts (30-minute cooldown)
- Rate limiting on authentication endpoints
- IP address tracking for security monitoring

## API Documentation

Access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## Models

### User
- `id` (UUID): Unique identifier
- `name` (CharField): User's full name (min 2 characters)
- `email` (EmailField): Unique email address (used as username)
- `is_active` (BooleanField): Account status
- `is_email_verified` (BooleanField): Email verification status
- `last_login_ip` (GenericIPAddressField): IP address of last login
- `failed_login_attempts` (PositiveIntegerField): Failed login attempt counter
- `account_locked_until` (DateTimeField): Account lock expiration timestamp
- `created_at` (DateTimeField): Creation timestamp
- `updated_at` (DateTimeField): Last update timestamp

### Task
- `id` (UUID): Unique identifier
- `title` (CharField): Task title (min 3 characters)
- `description` (TextField): Detailed description
- `completed` (BooleanField): Completion status
- `priority` (CharField): Priority level (low/medium/high/urgent)
- `due_date` (DateTimeField): Optional due date
- `completed_at` (DateTimeField): Completion timestamp
- `user` (ForeignKey): Task owner
- `created_at` (DateTimeField): Creation timestamp
- `updated_at` (DateTimeField): Last update timestamp

## Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run specific test module
python manage.py test api.tests.TaskModelTest

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Admin Interface

Access the Django admin at http://localhost:8000/admin/ with enhanced features:

- **User Management**: View users with task counts and activity status
- **Task Management**: Advanced filtering, search, and bulk operations
- **Color-coded Priority**: Visual priority indicators
- **Overdue Detection**: Automatic overdue task highlighting
- **Bulk Actions**: Mark multiple tasks as completed/pending

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Database Configuration
DB_NAME=todo_database
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5434

# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Logging

The application includes comprehensive logging:

- **File Logging**: Logs are written to `logs/django.log`
- **Console Logging**: Development-friendly console output
- **API Logging**: Track API operations and errors

## Security Features

- **JWT Authentication**: Secure token-based authentication with refresh tokens
- **Account Security**: Automatic account locking after 5 failed login attempts
- **Rate Limiting**: API rate limiting (5 login attempts per minute, 3 registrations per minute)
- **Brute Force Protection**: Django Axes integration for advanced attack prevention
- **Input Validation**: Comprehensive validation and sanitization
- **CORS Configuration**: Secure cross-origin resource sharing setup
- **Environment-based Configuration**: Secure settings management
- **Password Security**: Django's built-in password validation
- **IP Tracking**: Login attempt tracking with IP address logging

## Performance Optimizations

- Database query optimization with `select_related` and `prefetch_related`
- Efficient filtering with database indexes
- Pagination for large datasets
- Optimized admin queries

## Troubleshooting

### Database Issues

If you encounter database-related errors:

1. **Missing columns error** (e.g., "column 'last_login' does not exist"):
   ```bash
   # Reset and reapply migrations
   python manage.py migrate api zero --fake
   python manage.py migrate api
   ```

2. **Migration conflicts**:
   ```bash
   # Check migration status
   python manage.py showmigrations
   
   # If needed, reset all migrations
   python manage.py migrate --fake-initial
   ```

### Configuration Warnings

If you see Django Axes or static files warnings:
- Ensure the `static` directory exists: `mkdir -p static`
- Check that `AUTHENTICATION_BACKENDS` includes `axes.backends.AxesStandaloneBackend`
- Verify Axes configuration uses modern settings (not deprecated ones)

### Authentication Issues

1. **Account locked**: Wait 30 minutes or reset failed attempts in Django admin
2. **Token expired**: Use refresh token to get new access token
3. **Rate limiting**: Wait for the rate limit window to reset

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License.