import pytest

from app import create_app
from config import TestConfig
from db import db

@pytest.fixture
def app():
    """
    Pytest fixture to create and configure a Flask application for testing.

    Returns:
        - Flask app instance configured for testing.
    """
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """
    Pytest fixture to provide a test client for the Flask application.

    Returns:
        - Flask test client instance for testing routes and endpoints.
    """
    return app.test_client()

@pytest.fixture
def session(app):
    """
    Pytest fixture to provide a database session for testing.

    Returns:
        - SQLAlchemy session instance for database operations during tests.
    """
    with app.app_context():
        yield db.session
