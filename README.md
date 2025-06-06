# Todo List API

A comprehensive Todo List API built with Django REST Framework, featuring user management, task prioritization, filtering, and comprehensive documentation.

## Features

- **User Management**: Create and manage users with validation
- **Task Management**: Full CRUD operations for tasks with priorities
- **Advanced Filtering**: Filter tasks by completion status, priority, due date, and more
- **Search Functionality**: Search tasks by title, description, or user name
- **Statistics**: Get insights about tasks and users
- **Bulk Operations**: Complete multiple tasks at once
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation
- **Comprehensive Testing**: Full test coverage for models, views, and API endpoints

## Technology Stack

- **Backend**: Django 5.2.1, Django REST Framework 3.15.2
- **Database**: PostgreSQL
- **Documentation**: drf-spectacular (OpenAPI/Swagger)
- **Testing**: Django TestCase, DRF APITestCase
- **Code Quality**: Comprehensive logging, validation, and error handling

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

## API Endpoints

### Tasks
- `GET /api/v1/tasks/` - List all tasks (with filtering and search)
- `POST /api/v1/tasks/` - Create a new task
- `GET /api/v1/tasks/{id}/` - Retrieve a specific task
- `PUT /api/v1/tasks/{id}/` - Update a task
- `DELETE /api/v1/tasks/{id}/` - Delete a task

### Users
- `GET /api/v1/users/` - List all users
- `POST /api/v1/users/` - Create a new user
- `GET /api/v1/users/{id}/` - Retrieve a specific user
- `PUT /api/v1/users/{id}/` - Update a user
- `DELETE /api/v1/users/{id}/` - Delete a user
- `GET /api/v1/users/{id}/tasks/` - Get user with their tasks

### Statistics
- `GET /api/v1/statistics/tasks/` - Get task statistics
- `GET /api/v1/statistics/users/` - Get user statistics

### Bulk Operations
- `POST /api/v1/tasks/bulk-complete/` - Mark multiple tasks as completed

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

## API Documentation

Access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## Models

### User
- `id` (UUID): Unique identifier
- `name` (CharField): User's full name (min 2 characters)
- `email` (EmailField): Unique email address
- `is_active` (BooleanField): Account status
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

- Environment-based configuration
- Input validation and sanitization
- CORS configuration for frontend integration
- Secure database connections
- Comprehensive error handling

## Performance Optimizations

- Database query optimization with `select_related` and `prefetch_related`
- Efficient filtering with database indexes
- Pagination for large datasets
- Optimized admin queries

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License.