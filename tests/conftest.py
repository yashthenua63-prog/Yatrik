"""
Test configuration and fixtures for Yatrik.
"""
import pytest
from app import create_app
from app.database import db as _db
from app.models import User, Hotel, Restaurant, Driver


@pytest.fixture(scope="session")
def app():
    """Create application for testing."""
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    """Provide a clean database for each test function."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app, db):
    """Test client with a clean DB."""
    return app.test_client()


# ── User Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def admin_user(db, app):
    with app.app_context():
        user = User(name="Admin User", email="admin@yatrik.test", role="ADMIN")
        user.set_password("adminpass123")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def partner_user_a(db, app):
    with app.app_context():
        user = User(name="Partner A", email="partner_a@yatrik.test", role="HOTEL_PARTNER")
        user.set_password("partnerpass123")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def partner_user_b(db, app):
    with app.app_context():
        user = User(name="Partner B", email="partner_b@yatrik.test", role="HOTEL_PARTNER")
        user.set_password("partnerpass123")
        db.session.add(user)
        db.session.commit()
        return user.id

@pytest.fixture
def restaurant_partner_a(db, app):
    with app.app_context():
        user = User(name="Rest Partner A", email="rest_a@yatrik.test", role="RESTAURANT_PARTNER")
        user.set_password("partnerpass123")
        db.session.add(user)
        db.session.commit()
        return user.id

@pytest.fixture
def restaurant_partner_b(db, app):
    with app.app_context():
        user = User(name="Rest Partner B", email="rest_b@yatrik.test", role="RESTAURANT_PARTNER")
        user.set_password("partnerpass123")
        db.session.add(user)
        db.session.commit()
        return user.id

@pytest.fixture
def driver_partner(db, app):
    with app.app_context():
        user = User(name="Driver", email="driver@yatrik.test", role="DRIVER")
        user.set_password("partnerpass123")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def traveler_user(db, app):
    with app.app_context():
        user = User(name="Traveler", email="traveler@yatrik.test", role="TRAVELER")
        user.set_password("travelerpass123")
        db.session.add(user)
        db.session.commit()
        return user.id


def login_as(client, email, password):
    """Helper to log in via test client."""
    return client.post("/auth/login", data={
        "email": email,
        "password": password,
    }, follow_redirects=True)
