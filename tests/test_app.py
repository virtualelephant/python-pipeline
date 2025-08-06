#!/usr/bin/env python3
"""Unit tests for the python-pipeline Flask application."""
import pytest
from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test the /health endpoint returns a healthy status."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {"status": "healthy", "message": "Application is running"}

def test_index_endpoint(client):
    """Test the / endpoint returns a welcome message."""
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {"message": "Welcome to the micro-services demo!"}