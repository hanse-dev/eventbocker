"""
Pytest Configuration and Fixtures

This module provides pytest fixtures for testing the Flask application.
It sets up the test environment, including:
- Test Flask application instance
- Test database
- Test client for making requests

The fixtures are designed to provide isolation between tests and clean up
after themselves to prevent test interference.
"""

import os
import pytest
from app.app import create_app
from app.extensions import db as _db
from app.config import TestConfig

@pytest.fixture(scope='session')
def app():
    """
    Create and configure a new app instance for each test session.
    
    This fixture:
    1. Creates a Flask application with test configuration
    2. Uses an in-memory SQLite database for speed and isolation
    3. Provides the app context for the entire test session
    
    The 'session' scope means this fixture is created once per test session
    and reused for all tests, improving performance.
    
    Returns:
        Flask application instance configured for testing
    """
    # Create the test app with SQLite in-memory database
    test_config = TestConfig()
    test_config.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    app = create_app(test_config)
    
    return app

@pytest.fixture(scope='function')
def db(app):
    """
    Create a fresh database for each test function.
    
    This fixture:
    1. Creates all database tables before each test
    2. Provides the database session during the test
    3. Removes the session and drops all tables after the test
    
    The 'function' scope ensures each test gets a fresh database,
    preventing interference between tests.
    
    Args:
        app: The Flask application instance (from app fixture)
    
    Returns:
        SQLAlchemy database instance
    """
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()

@pytest.fixture(scope='function')
def client(app, db):
    """
    Create a test client for the app.
    
    This fixture provides a test client that can be used to make requests
    to the application during testing. It depends on both the app and db
    fixtures to ensure the environment is properly set up.
    
    The 'function' scope ensures each test gets a fresh client.
    
    Args:
        app: The Flask application instance (from app fixture)
        db: The database instance (from db fixture)
    
    Returns:
        Flask test client instance
    """
    return app.test_client()
