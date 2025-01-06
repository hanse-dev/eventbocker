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
│   ├── Dockerfile          # Production build
│   ├── Dockerfile.dev      # Development build
│   ├── docker-entrypoint.sh
│   └── docker-entrypoint.dev.sh
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
   # For development
   docker-compose -f docker-compose.dev.yml up --build

   # For production
   docker-compose up --build
   ```

3. Initialize the database (first time only):
   ```bash
   docker-compose exec web python init_db.py
   ```

### Local Development

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
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

## Docker Commands

### Development Environment

```bash
# Start development environment (with auto-reload)
docker-compose -f docker-compose.dev.yml up --build

# Rebuild without cache (if dependencies changed)
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up

# Stop and remove containers
docker-compose -f docker-compose.dev.yml down

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Restart services
docker-compose -f docker-compose.dev.yml restart
```

### Production Environment

```bash
# Start production environment
docker-compose up --build

# Rebuild without cache
docker-compose build --no-cache
docker-compose up

# Stop and remove containers
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart
```

### Database Management in Docker

```bash
# Initialize database (first time or reset)
docker-compose exec web python init_db.py

# Access database shell
docker-compose exec web flask shell
```

## Database Management

### Migrations

The project uses Flask-Migrate (Alembic) for database migrations. Here are the common migration commands:

1. Initialize migrations (first time only):
   ```bash
   docker-compose -f docker-compose.dev.yml exec web flask db init
   ```

2. Create a new migration after model changes:
   ```bash
   docker-compose -f docker-compose.dev.yml exec web flask db migrate -m "Description of changes"
   ```

3. Apply pending migrations:
   ```bash
   docker-compose -f docker-compose.dev.yml exec web flask db upgrade
   ```

4. Rollback migrations:
   ```bash
   docker-compose -f docker-compose.dev.yml exec web flask db downgrade
   ```

Note: Migrations are automatically applied when the container starts up.

### Manual Database Initialization

For first-time setup or resetting the database:
```bash
docker-compose -f docker-compose.dev.yml exec web python init_db.py
```

## Email Configuration

The system supports sending emails for event notifications and confirmations. To set up email functionality:

1. Configure your email settings in the `.env` file:
   ```bash
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

2. Test email configuration:
   ```bash
   # Using Docker
   docker-compose exec web python -c "from app.extensions import mail; mail.send_message(subject='Test', recipients=['test@example.com'], body='Test email')"

   # Local development
   flask shell
   >>> from app.extensions import mail
   >>> mail.send_message(subject='Test', recipients=['test@example.com'], body='Test email')
   ```

Note: Make sure to never commit your actual email credentials to version control. Always use environment variables for sensitive information.

## Development

- The application uses SQLite for data storage
- Flask-Login handles user authentication
- Templates use Bootstrap for styling
- Configuration is managed through environment variables

## Testing

Run the tests with:
```bash
python -m pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.
