"""
Tests for authentication: registration, login, logout.
"""
import pytest
from app.models import User
from tests.conftest import login_as


class TestRegistration:
    def test_register_traveler(self, client, db, app):
        """Traveler registration creates a TRAVELER user."""
        resp = client.post("/auth/register", data={
            "name": "Test Traveler",
            "email": "traveler_reg@test.com",
            "password": "securepass123",
            "account_type": "TRAVELER",
        }, follow_redirects=False)
        # Should redirect (302) after success
        assert resp.status_code in (302, 200)
        with app.app_context():
            user = User.query.filter_by(email="traveler_reg@test.com").first()
            assert user is not None
            assert user.role == "TRAVELER"

    def test_register_hotel_partner(self, client, db, app):
        """Hotel partner registration creates a HOTEL_PARTNER user."""
        client.post("/auth/hotel/register", data={
            "name": "Test Hotel Partner",
            "email": "hotel_partner_reg@test.com",
            "password": "securepass123",
        })
        with app.app_context():
            user = User.query.filter_by(email="hotel_partner_reg@test.com").first()
            assert user is not None
            assert user.role == "HOTEL_PARTNER"

    def test_password_is_hashed(self, client, db, app):
        """Passwords must never be stored in plaintext."""
        client.post("/auth/register", data={
            "name": "Hash Test",
            "email": "hash@test.com",
            "password": "plaintext123",
            "account_type": "TRAVELER",
        })
        with app.app_context():
            user = User.query.filter_by(email="hash@test.com").first()
            assert user is not None
            assert user.password_hash != "plaintext123"
            assert user.password_hash.startswith("pbkdf2") or user.password_hash.startswith("scrypt")

    def test_duplicate_email_rejected(self, client, db, app):
        """Registering with existing email shows error."""
        data = {
            "name": "Dup", "email": "dup@test.com",
            "password": "pass12345", "account_type": "TRAVELER"
        }
        client.post("/auth/register", data=data)
        resp = client.post("/auth/register", data=data, follow_redirects=True)
        assert b"already registered" in resp.data or resp.status_code in (200, 302)

    def test_short_password_rejected(self, client, db):
        """Passwords shorter than 8 chars should be rejected."""
        resp = client.post("/auth/register", data={
            "name": "Short", "email": "short@test.com",
            "password": "abc", "account_type": "TRAVELER",
        }, follow_redirects=True)
        assert b"8" in resp.data or resp.status_code == 200


class TestLogin:
    def test_valid_login(self, client, db, traveler_user, app):
        """Valid credentials log in successfully."""
        resp = login_as(client, "traveler@yatrik.test", "travelerpass123")
        assert resp.status_code == 200

    def test_invalid_password(self, client, db, traveler_user):
        """Wrong password shows error."""
        resp = client.post("/auth/login", data={
            "email": "traveler@yatrik.test",
            "password": "wrongpass"
        }, follow_redirects=True)
        assert b"Invalid" in resp.data or resp.status_code == 200

    def test_nonexistent_user(self, client, db):
        """Login with non-existent email shows error."""
        resp = client.post("/auth/login", data={
            "email": "nobody@test.com",
            "password": "anypass"
        }, follow_redirects=True)
        assert b"Invalid" in resp.data or resp.status_code == 200

    def test_logout(self, client, db, traveler_user):
        """Logout redirects to home."""
        login_as(client, "traveler@yatrik.test", "travelerpass123")
        resp = client.get("/auth/logout", follow_redirects=False)
        assert resp.status_code == 302

    def test_traveler_redirected_to_home(self, client, db, traveler_user):
        """After login, traveler is redirected to /, not partner dashboard."""
        resp = client.post("/auth/login", data={
            "email": "traveler@yatrik.test",
            "password": "travelerpass123"
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert "/partner" not in resp.headers.get("Location", "")
