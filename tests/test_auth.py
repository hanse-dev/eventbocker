import pytest
from flask import url_for
from app.models.models import User

def test_register_user(client, db):
    """Test user registration."""
    response = client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'test123',
        'name': 'Test User'
    })
    assert response.status_code == 201
    assert b'User registered successfully' in response.data
    
    # Verify user exists in database
    user = User.query.filter_by(email='test@example.com').first()
    assert user is not None
    assert user.email == 'test@example.com'
    assert user.name == 'Test User'

def test_login_user(client, db):
    """Test user login."""
    # First register a user
    client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'test123',
        'name': 'Test User'
    })
    
    # Try to login
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'test123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_invalid_login(client, db):
    """Test login with invalid credentials."""
    response = client.post('/auth/login', json={
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
