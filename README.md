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
├── init_db.py       # Database initialization script
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
   docker-compose -f docker-compose.dev.yml up --build

   # For production
   docker-compose up --build
   ```

The application will be available at:
- Development: http://localhost:5001 (with hot-reload and debugging on port 5678)
- Production: http://localhost:5001 (with Gunicorn server)

### Docker Development Features

Our Docker setup includes several developer-friendly features:

1. **Hot Reload**: Code changes are automatically detected and reloaded
2. **Remote Debugging**: Available on port 5678 (use VS Code or PyCharm)
3. **Pip Cache**: Dependencies are cached between builds
4. **Database Migrations**: Automatically handled on startup
5. **Health Checks**: Built-in container health monitoring
6. **Security**: Runs as non-root user with proper permissions
7. **Logging**: Structured logging with rotation

### Docker Commands

#### Development Environment

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up --build

# Start in debug mode (enables remote debugger)
FLASK_DEBUG=1 docker-compose -f docker-compose.dev.yml up --build

# View logs with timestamps
docker-compose -f docker-compose.dev.yml logs -f --timestamps

# Rebuild without cache (if dependencies changed)
docker-compose -f docker-compose.dev.yml build --no-cache

# Stop and remove containers
docker-compose -f docker-compose.dev.yml down

# Restart services
docker-compose -f docker-compose.dev.yml restart
```

#### Production Environment

```bash
# Start production environment
docker-compose up --build

# View logs with timestamps
docker-compose logs -f --timestamps

# Stop and remove containers
docker-compose down
```

### Database Management

Database migrations are automatically handled by the entrypoint script, but you can also run them manually:

```bash
# Create a new migration
docker-compose -f docker-compose.dev.yml exec web flask db migrate -m "Description"

# Apply migrations manually
docker-compose -f docker-compose.dev.yml exec web flask db upgrade

# Rollback migrations
docker-compose -f docker-compose.dev.yml exec web flask db downgrade
```

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
   FLASK_DEBUG=1 docker-compose -f docker-compose.dev.yml up --build
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
docker-compose ps
# or
docker ps
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
   python init_db.py
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
- Database migrations are automatically applied on startup
- Logs are available through Docker's logging system

## Security Notes

1. The Docker setup includes several security features:
   - Non-root user execution
   - No privilege escalation
   - Minimal runtime dependencies
   - Proper file permissions
   - Environment variable management

2. Never commit sensitive information:
   - Use `.env` files for local development
   - Use secure secrets management in production
   - Keep API keys and credentials private

## Troubleshooting

1. **Container won't start**:
   - Check logs: `docker-compose -f docker-compose.dev.yml logs -f web`
   - Verify environment variables: `docker-compose -f docker-compose.dev.yml config`
   - Check port conflicts: `netstat -ano | findstr 5001`

2. **Hot reload not working**:
   - Ensure volumes are properly mounted
   - Check file permissions
   - Verify FLASK_DEBUG=1 is set

3. **Database issues**:
   - Check instance folder permissions
   - Verify DATABASE_URL in .env
   - Review migration logs
