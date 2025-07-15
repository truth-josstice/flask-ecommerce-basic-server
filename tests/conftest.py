import pytest
from app import app, db

@pytest.fixture
def client():
    # Configure app for testing
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"]= "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFACTIONS"] = False
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()