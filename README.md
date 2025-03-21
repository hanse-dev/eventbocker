# Event Management System

A Flask-based event management system for creating and managing events.

## Project Structure
```
./
├── app/               # Application package
│   ├── models/        # Database models
│   ├── routes/        # Route handlers
│   ├── static/        # Static files (CSS, JS, images)
│   ├── templates/     # HTML templates
│   ├── app.py        # Application factory
│   ├── config.py     # Configuration
│   └── extensions.py # Flask extensions
├── docker/           # Docker configuration
│   ├── Dockerfile    # Multi-stage build for both dev and prod
│   └── docker-entrypoint.sh  # Unified entrypoint script
├── instance/         # SQLite database (gitignored)
├── requirements.txt  # Python dependencies
├── init_migrations.py # Database migration manager
├── docker-compose.yml      # Production deployment
├── docker-compose.dev.yml  # Development setup
└── example.env      # Environment variables template
```

## Quick Start

### Using Docker (Recommended)

1. Copy the environment file:
   ```bash
   cp example.env .env
   ```

2. Build and start the containers:
   ```bash
   # For development (includes hot-reload and debugging)
   docker compose -f docker-compose.dev.yml up --build

   # For production
   docker compose up --build
   ```

The application will be available at:
- Development: http://localhost:5001 (with hot-reload and debugging on port 5678)
- Production: http://localhost:5001 (with Gunicorn server)

### Docker Development Features

Our Docker setup includes several developer-friendly features:

1. **Hot Reload**: Code changes are automatically detected and reloaded
2. **Remote Debugging**: Available on port 5678 (use VS Code or PyCharm)
3. **Pip Cache**: Dependencies are cached between builds
4. **Database Migrations**: Automatic schema management with data preservation
5. **Health Checks**: Built-in container health monitoring
6. **Security**: Runs as non-root user with proper permissions
7. **Logging**: Structured logging with rotation

### Docker Commands

#### Development Environment

```bash
# Start development environment
docker compose -f docker-compose.dev.yml up --build

# Start in debug mode (enables remote debugger)
docker compose -f docker-compose.dev.yml up --build -e FLASK_DEBUG=1

# View logs
docker compose -f docker-compose.dev.yml logs -f web

# Rebuild without cache
docker compose -f docker-compose.dev.yml build --no-cache

# Stop and remove containers
docker compose -f docker-compose.dev.yml down

# Restart services
docker compose -f docker-compose.dev.yml restart
```

#### Production Environment

```bash
# Start production environment
docker compose up --build

# View logs
docker compose logs -f web

# Stop and remove containers
docker compose down
```

### Environment Variables

Key environment variables that need to be configured:

```bash
# Database Configuration
DATABASE_URL=sqlite:///instance/app.db  # SQLite database path

# Flask Configuration
FLASK_APP=app.app                     # Flask application module
FLASK_ENV=development                 # development or production
FLASK_DEBUG=0                         # Enable debug mode (1) or disable (0)
SECRET_KEY=your-secret-key            # Flask secret key for sessions

# Email Configuration (Optional)
MAIL_SERVER=smtp.example.com          # SMTP server
MAIL_PORT=587                         # SMTP port
MAIL_USE_TLS=1                        # Use TLS for email
MAIL_USERNAME=your-email@example.com  # SMTP username
MAIL_PASSWORD=your-password           # SMTP password
```

### Website Configuration

The application uses a JSON configuration file (`config.json`) to customize the website appearance and content:

```json
{
  "website": {
    "name": "Veranstaltungsmanager",
    "title": "Veranstaltungsverwaltung",
    "description": "Plattform zur Verwaltung von Veranstaltungen und Buchungen"
  },
  "contact": {
    "email": "",
    "phone": ""
  },
  "appearance": {
    "primary_color": "#212529",
    "secondary_color": "#6c757d",
    "logo_icon": "bi-calendar-event"
  }
}
```

#### Configuration Options:

- **website.name**: The name displayed in the navigation bar
- **website.title**: The title displayed in the browser tab
- **website.description**: A brief description of the website (for SEO)
- **contact.email**: Contact email address
- **contact.phone**: Contact phone number
- **appearance.primary_color**: Primary color for the website (hex code)
- **appearance.secondary_color**: Secondary color for the website (hex code)
- **appearance.logo_icon**: Bootstrap icon class for the logo (see [Bootstrap Icons](https://icons.getbootstrap.com/))

#### Editing Configuration:

1. **Through the Admin Interface**: 
   - Log in as an admin user
   - Click on the "Konfiguration" link in the navigation menu
   - Make your changes and save

2. **Manually**:
   - Edit the `config.json` file directly
   - Restart the application for changes to take effect

When using Docker, the configuration file is automatically mounted as a volume, so changes persist between container restarts.

### Database Management

The database migration system has been consolidated into `init_migrations.py`, which handles:
- Automatic schema migrations
- Data backup before migrations
- Data restoration after migrations
- Safe handling of foreign key relationships

The migration process is automatically handled on container startup, but you can also run migrations manually:

```bash
# Run migrations manually
docker compose exec web python init_migrations.py

# Create a new migration
docker compose exec web flask db migrate -m "Description"

# Apply migrations
docker compose exec web flask db upgrade

# Rollback migrations
docker compose exec web flask db downgrade
```

#### Migration Features

The migration system provides:
1. **Automatic Backup**: Data is automatically backed up before migrations
2. **Safe Schema Updates**: Migrations are performed with proper foreign key handling
3. **Data Preservation**: Existing data is restored after schema updates
4. **Error Recovery**: Automatic rollback on failure
5. **Comprehensive Logging**: Detailed logs for debugging

### Debugging

1. **VS Code Configuration**:
   Add this to your `launch.json`:
   ```json
   {
     "name": "Python: Remote Attach",
     "type": "python",
     "request": "attach",
     "connect": {
       "host": "localhost",
       "port": 5678
     },
     "pathMappings": [
       {
         "localRoot": "${workspaceFolder}",
         "remoteRoot": "/app"
       }
     ]
   }
   ```

2. **Start with Debugger**:
   ```bash
   docker compose -f docker-compose.dev.yml up --build -e FLASK_DEBUG=1
   ```

3. **Attach Debugger**: 
   - VS Code: Run the "Python: Remote Attach" configuration
   - PyCharm: Create a Python Debug Server configuration (port 5678)

### Health Checks

The Docker setup includes health checks that monitor:
- Web server availability
- Database connectivity
- Required services status

View health status:
```bash
docker compose ps
```

### Local Development (Without Docker)

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp example.env .env
   ```

4. Initialize the database:
   ```bash
   python init_migrations.py
   ```

5. Run the development server:
   ```bash
   flask run
   ```

## Development Guidelines

- The application uses SQLite for data storage
- Flask-Login handles user authentication
- Templates use Bootstrap for styling
- Configuration is managed through environment variables
- All code changes are automatically reloaded in development
- Database migrations are handled by init_migrations.py
- Logs are available through Docker's logging system

## Security Notes

1. **Docker Security**:
   - Non-root user execution
   - No privilege escalation
   - Minimal runtime dependencies
   - Read-only root filesystem
   - Limited container capabilities
   - Resource limits enforcement

2. **Database Security**:
   - Automatic data backup before migrations
   - Safe schema updates with rollback capability
   - Proper handling of foreign key relationships
   - Secure restoration of data after migrations
   - SQLite file permissions management
   - Database file location security

3. **Application Security**:
   - Secure session management
   - CSRF protection enabled
   - XSS protection headers
   - Secure cookie configuration
   - Rate limiting on sensitive endpoints
   - Input validation and sanitization

4. **Environment Security**:
   - Sensitive data in environment variables
   - Secrets management in production
   - No hardcoded credentials
   - Secure configuration loading
   - Environment-specific settings

## Troubleshooting

### Common Issues

1. **Container Issues**:
   ```bash
   # Check container status
   docker compose ps
   
   # View container logs
   docker compose logs -f web
   
   # Verify network connectivity
   docker compose exec web ping db
   ```

2. **Database Issues**:
   ```bash
   # Check database status
   docker compose exec web python init_migrations.py --status
   
   # Reset migrations
   docker compose exec web python init_migrations.py --reset
   
   # View database logs
   docker compose logs db
   ```

3. **Permission Issues**:
   - Ensure proper file ownership in mounted volumes
   - Check directory permissions for SQLite database
   - Verify user permissions in containers

4. **Application Issues**:
   - Check application logs for errors
   - Verify environment variables are set correctly
   - Ensure all required services are running

### Getting Help

- Check the [Flask Documentation](https://flask.palletsprojects.com/)
- Review the [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)
- Search existing GitHub issues
- Join the Flask community on Discord
