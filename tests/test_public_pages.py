"""
Public page tests — verify all public routes return 200 and correct content.
"""
import pytest


class TestHomepage:
    def test_homepage_loads(self, client, db):
        """Homepage must return 200."""
        resp = client.get("/")
        assert resp.status_code == 200

    def test_homepage_has_brand(self, client, db):
        """Homepage must mention Yatrik."""
        resp = client.get("/")
        assert b"Yatrik" in resp.data


class TestTemplePages:
    def test_temple_list_loads(self, client, db, app):
        """Temple listing page must return 200."""
        resp = client.get("/temples")
        assert resp.status_code == 200

    def test_explore_page_loads(self, client, db):
        """Explore page loads."""
        resp = client.get("/explore")
        assert resp.status_code == 200

    def test_nonexistent_temple_is_404(self, client, db):
        """Non-existent temple ID returns 404."""
        resp = client.get("/temples/99999")
        assert resp.status_code == 404


class TestHotelPages:
    def test_hotels_list_loads(self, client, db):
        """Hotels listing page loads."""
        resp = client.get("/hotels")
        assert resp.status_code == 200

    def test_hotels_only_shows_published(self, client, db, app, partner_user_a):
        """Only PUBLISHED hotels appear in the listing."""
        from app.models import Hotel
        from app.database import db as _db
        with app.app_context():
            # Add a PENDING hotel
            h = Hotel(owner_id=partner_user_a, name="Pending Hotel Test",
                      slug="pending-hotel-test", city="Vrindavan",
                      verification_status="PENDING")
            _db.session.add(h)
            _db.session.commit()

        resp = client.get("/hotels")
        assert b"Pending Hotel Test" not in resp.data

    def test_nonexistent_hotel_is_404(self, client, db):
        """Non-existent hotel slug returns 404."""
        resp = client.get("/hotels/nonexistent-hotel-xyz")
        assert resp.status_code == 404


class TestRestaurantPages:
    def test_restaurants_list_loads(self, client, db):
        """Restaurants listing page loads."""
        resp = client.get("/restaurants")
        assert resp.status_code == 200

    def test_restaurants_only_shows_published(self, client, db, app, partner_user_a):
        """Only PUBLISHED restaurants appear in the listing."""
        from app.models import Restaurant
        from app.database import db as _db
        with app.app_context():
            r = Restaurant(owner_id=partner_user_a, name="Pending Restaurant Test",
                           slug="pending-restaurant-test", city="Vrindavan",
                           verification_status="PENDING")
            _db.session.add(r)
            _db.session.commit()

        resp = client.get("/restaurants")
        assert b"Pending Restaurant Test" not in resp.data

    def test_nonexistent_restaurant_is_404(self, client, db):
        """Non-existent restaurant slug returns 404."""
        resp = client.get("/restaurants/nonexistent-xyz")
        assert resp.status_code == 404


class TestStaticPages:
    def test_about_loads(self, client, db):
        resp = client.get("/about")
        assert resp.status_code == 200

    def test_privacy_loads(self, client, db):
        resp = client.get("/privacy")
        assert resp.status_code == 200

    def test_terms_loads(self, client, db):
        resp = client.get("/terms")
        assert resp.status_code == 200

    def test_safety_loads(self, client, db):
        resp = client.get("/safety")
        assert resp.status_code == 200


class TestNewPages:
    def test_events_page_loads(self, client, db):
        resp = client.get("/events")
        assert resp.status_code == 200

    def test_food_trails_page_loads(self, client, db):
        resp = client.get("/food-trails")
        assert resp.status_code == 200

    def test_darshan_planner_loads(self, client, db):
        resp = client.get("/darshan-planner")
        assert resp.status_code == 200

    def test_braj_trip_os_loads(self, client, db):
        resp = client.get("/plan-my-trip")
        assert resp.status_code == 200

    def test_braj_circuit_loads(self, client, db):
        resp = client.get("/braj-circuit")
        assert resp.status_code == 200

    def test_planner_page_loads(self, client, db):
        resp = client.get("/planner")
        assert resp.status_code == 200

    def test_ride_page_loads(self, client, db):
        resp = client.get("/ride")
        assert resp.status_code == 200

    def test_saved_page_loads(self, client, db):
        resp = client.get("/saved")
        assert resp.status_code == 200

    def test_health_check(self, client, db):
        resp = client.get("/health")
        assert resp.status_code == 200


class TestErrorPages:
    def test_404_returns_404(self, client, db):
        resp = client.get("/this-page-does-not-exist-xyz")
        assert resp.status_code == 404

    def test_admin_panel_protected(self, client, db):
        """Admin panel must not be accessible without login."""
        resp = client.get("/admin-yatrik-secret/", follow_redirects=False)
        # Should redirect to login (302) not serve admin panel (200)
        assert resp.status_code in (302, 403)
