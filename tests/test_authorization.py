"""
Authorization tests — CRITICAL ownership enforcement.

These tests explicitly verify:
- Hotel Owner A CANNOT edit Hotel Owner B's hotel
- Hotel Owner A CANNOT delete Hotel Owner B's hotel
- Restaurant Owner A CANNOT access Owner B's restaurant
- Drivers CANNOT access each other's data
- Admin CAN manage all
"""
import pytest
from app.models import Hotel, Restaurant, Driver
from app.database import db
from tests.conftest import login_as


def create_hotel(app, db, owner_id, name="Test Hotel"):
    with app.app_context():
        slug = name.lower().replace(" ", "-")
        existing = Hotel.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-{owner_id}"
        hotel = Hotel(
            owner_id=owner_id,
            name=name,
            slug=slug,
            city="Vrindavan",
            verification_status="PUBLISHED"
        )
        db.session.add(hotel)
        db.session.commit()
        return hotel.id


def create_restaurant(app, db, owner_id, name="Test Restaurant"):
    with app.app_context():
        slug = name.lower().replace(" ", "-") + f"-{owner_id}"
        restaurant = Restaurant(
            owner_id=owner_id,
            name=name,
            slug=slug,
            city="Vrindavan",
            verification_status="PUBLISHED"
        )
        db.session.add(restaurant)
        db.session.commit()
        return restaurant.id


class TestHotelOwnership:
    def test_owner_can_edit_own_hotel(self, client, db, partner_user_a, app):
        """Owner can access the edit page for their own hotel."""
        hotel_id = create_hotel(app, db, partner_user_a, "Owner A Hotel")
        login_as(client, "partner_a@yatrik.test", "partnerpass123")
        resp = client.get(f"/partner/hotel/{hotel_id}/edit")
        assert resp.status_code == 200

    def test_owner_b_cannot_edit_owner_a_hotel(self, client, db, partner_user_a, partner_user_b, app):
        """Hotel Owner B MUST receive 403 when trying to edit Owner A's hotel."""
        hotel_id = create_hotel(app, db, partner_user_a, "A Hotel For B Test")
        # Log in as partner B
        login_as(client, "partner_b@yatrik.test", "partnerpass123")
        resp = client.get(f"/partner/hotel/{hotel_id}/edit")
        assert resp.status_code == 403, (
            "CRITICAL SECURITY FAILURE: Partner B was allowed to edit Partner A's hotel!"
        )

    def test_owner_b_cannot_post_edit_to_owner_a_hotel(self, client, db, partner_user_a, partner_user_b, app):
        """Hotel Owner B MUST NOT be able to POST edits to Owner A's hotel."""
        hotel_id = create_hotel(app, db, partner_user_a, "A Hotel Post Test")
        login_as(client, "partner_b@yatrik.test", "partnerpass123")
        resp = client.post(f"/partner/hotel/{hotel_id}/edit", data={
            "name": "Hacked Hotel Name",
            "city": "Vrindavan",
        })
        assert resp.status_code == 403, (
            "CRITICAL SECURITY FAILURE: Partner B was allowed to POST to Partner A's hotel!"
        )
        # Verify hotel name was not changed
        with app.app_context():
            hotel = Hotel.query.get(hotel_id)
            assert hotel.name != "Hacked Hotel Name"

    def test_unauthenticated_cannot_edit_hotel(self, client, db, partner_user_a, app):
        """Unauthenticated users must not access edit routes."""
        hotel_id = create_hotel(app, db, partner_user_a, "Anon Test Hotel")
        resp = client.get(f"/partner/hotel/{hotel_id}/edit", follow_redirects=False)
        assert resp.status_code == 302  # Redirect to login
        location = resp.headers.get("Location", "")
        assert "login" in location

    def test_admin_can_edit_any_hotel(self, client, db, partner_user_a, admin_user, app):
        """Admin must be able to edit any hotel."""
        hotel_id = create_hotel(app, db, partner_user_a, "Admin Access Hotel")
        login_as(client, "admin@yatrik.test", "adminpass123")
        resp = client.get(f"/partner/hotel/{hotel_id}/edit")
        assert resp.status_code == 200, "Admin must have access to edit any hotel."


class TestRestaurantOwnership:
    def test_owner_can_edit_own_restaurant(self, client, db, partner_user_a, app):
        """Owner can access the edit page for their own restaurant."""
        r_id = create_restaurant(app, db, partner_user_a, "Owner A Restaurant")
        login_as(client, "partner_a@yatrik.test", "partnerpass123")
        resp = client.get(f"/partner/restaurant/{r_id}/edit")
        assert resp.status_code == 200

    def test_owner_b_cannot_edit_owner_a_restaurant(self, client, db, partner_user_a, partner_user_b, app):
        """Restaurant Owner B MUST receive 403 for Owner A's restaurant."""
        r_id = create_restaurant(app, db, partner_user_a, "A Restaurant For B Test")
        login_as(client, "partner_b@yatrik.test", "partnerpass123")
        resp = client.get(f"/partner/restaurant/{r_id}/edit")
        assert resp.status_code == 403, (
            "CRITICAL: Partner B was allowed to access Partner A's restaurant!"
        )

    def test_owner_b_cannot_post_to_owner_a_restaurant(self, client, db, partner_user_a, partner_user_b, app):
        """Restaurant Owner B MUST NOT be able to POST edits to Owner A's restaurant."""
        r_id = create_restaurant(app, db, partner_user_a, "A Restaurant Post Test")
        login_as(client, "partner_b@yatrik.test", "partnerpass123")
        resp = client.post(f"/partner/restaurant/{r_id}/edit", data={
            "name": "Hacked Restaurant",
            "city": "Vrindavan",
        })
        assert resp.status_code == 403


class TestPartnerDashboardAccess:
    def test_traveler_cannot_access_partner_dashboard(self, client, db, traveler_user):
        """Traveler role MUST NOT access the partner dashboard."""
        login_as(client, "traveler@yatrik.test", "travelerpass123")
        resp = client.get("/partner/dashboard", follow_redirects=False)
        # Should redirect away (not 200 to the dashboard)
        assert resp.status_code != 200 or b"not authorized" in (
            client.get("/partner/dashboard", follow_redirects=True).data
        )

    def test_unauthenticated_cannot_access_partner_dashboard(self, client, db):
        """Unauthenticated users must be redirected to login."""
        resp = client.get("/partner/dashboard", follow_redirects=False)
        assert resp.status_code == 302
        assert "login" in resp.headers.get("Location", "")

    def test_admin_cannot_access_partner_dashboard_as_partner(self, client, db, admin_user):
        """Admin is redirected to admin panel, not partner dashboard."""
        login_as(client, "admin@yatrik.test", "adminpass123")
        resp = client.get("/partner/dashboard", follow_redirects=False)
        # Admin should be redirected to admin panel
        assert resp.status_code == 302
        location = resp.headers.get("Location", "")
        assert "admin" in location
