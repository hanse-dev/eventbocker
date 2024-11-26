# Event Management System

A Flask-based event management system for creating and managing events.

## Project Structure
```
nada/
├── app/
│   ├── models/         # Database models
│   ├── routes/         # Route handlers
│   ├── static/         # Static files (CSS, JS, images)
│   ├── templates/      # HTML templates
│   ├── app.py         # Application factory
│   ├── config.py      # Configuration
│   └── extensions.py  # Flask extensions
├── docker/
│   ├── Dockerfile
│   └── docker-entrypoint.sh
├── instance/          # SQLite database
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## Local Development Setup

1. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with admin credentials:
```bash
cp example.env .env
# Edit .env with your settings
```

4. Start the development server:
```bash
python -m flask run
```

The application will be available at `http://localhost:5001`

## Docker Setup

### Option 1: Using Docker Compose (Recommended)

1. Copy the example environment file:
```bash
cp example.env .env
```

2. Edit the `.env` file with your desired settings

3. Build and start the container:
```bash
docker compose up -d
```

The application will be available at `http://localhost:5001`

### Option 2: Using Docker directly

1. Build the image:
```bash
docker build -t nada-app -f nada/docker/Dockerfile .
```

2. Run the container:
```bash
docker run -d -p 5001:5001 \
  -e SECRET_KEY=your_secret_key \
  -e ADMIN_USERNAME=admin \
  -e ADMIN_PASSWORD=your_password \
  --name nada-app nada-app
```

### Persistence

The SQLite database is stored in the `instance` directory, which is mounted as a volume in the Docker container. This means your data will persist even if you restart the container.

### Troubleshooting

- If you see "Internal Server Error", try removing the container and starting again:
```bash
docker compose down
docker compose up -d
```

- To view logs:
```bash
docker compose logs
```

## Database Management

- **Create tables** (automatically done when starting the app):
```bash
flask db create
```

- **Reset database** (warning: this will delete all data):
```bash
flask reset-db
```

- **Create admin user** (if needed):
```bash
flask create-admin admin admin123
```

## Common Tasks

1. **Create Event**:
   - Log in as admin
   - Click "Neue Veranstaltung erstellen"
   - Fill in event details
   - Click "Speichern"

2. **Edit Event**:
   - Log in as admin
   - Find event in admin view
   - Click edit button
   - Update details
   - Click "Speichern"

3. **Toggle Event Visibility**:
   - Log in as admin
   - Find event in admin view
   - Click eye/eye-slash icon to toggle visibility

4. **Book Event**:
   - Navigate to event
   - Click "Jetzt buchen"
   - Fill in booking details
   - Submit booking

## Development

1. **Adding New Features**:
   - Create necessary database models in `models.py`
   - Add routes in appropriate route file
   - Create/update templates in `templates/`
   - Update README if needed

2. **Database Changes**:
   - Update models in `models.py`
   - Reset database if needed (warning: deletes data)
   - Test changes thoroughly

## Security Notes

- Keep `.env` file secure and never commit it
- Change admin password regularly
- Use HTTPS in production
- Keep dependencies updated
