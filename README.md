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

This project is licensed under the MIT License - see the LICENSE file for details.
