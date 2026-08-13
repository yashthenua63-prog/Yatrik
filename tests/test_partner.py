"""
Partner onboarding and CRUD tests.
"""
import pytest
from app.models import Hotel, Restaurant, Driver
from tests.conftest import login_as


class TestHotelOnboarding:
    def test_partner_can_add_hotel(self, client, db, partner_user_a, app):
        """Partner can submit a hotel for verification."""
        login_as(client, "partner_a@yatrik.test", "partnerpass123")
        resp = client.post("/partner/onboard/hotel", data={
            "name": "Krishna Niwas",
            "city": "Vrindavan",
            "address": "Near Banke Bihari",
            "phone": "9999999999",
            "description": "A peaceful stay near the temple.",
        }, follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            hotel = Hotel.query.filter_by(name="Krishna Niwas").first()
            assert hotel is not None
            assert hotel.verification_status == "PENDING"
            assert hotel.owner_id == partner_user_a

    def test_hotel_slug_is_unique(self, client, db, partner_user_a, partner_user_b, app):
        """Two hotels with the same name get different slugs."""
        login_as(client, "partner_a@yatrik.test", "partnerpass123")
        client.post("/partner/onboard/hotel", data={
            "name": "Same Name Hotel", "city": "Vrindavan", "phone": "1111111111"
        })
        # Log in as partner B and add same name
        client.get("/auth/logout")
        login_as(client, "partner_b@yatrik.test", "partnerpass123")
        resp = client.post("/partner/onboard/hotel", data={
            "name": "Same Name Hotel", "city": "Mathura", "phone": "2222222222"
        }, follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            hotels = Hotel.query.filter(Hotel.name == "Same Name Hotel").all()
            slugs = [h.slug for h in hotels]
            assert len(set(slugs)) == len(slugs), "Duplicate slugs found!"

    def test_onboard_form_requires_name(self, client, db, partner_user_a):
        """Hotel form must reject empty name."""
        login_as(client, "partner_a@yatrik.test", "partnerpass123")
        resp = client.post("/partner/onboard/hotel", data={
            "name": "", "city": "Vrindavan",
        }, follow_redirects=True)
        assert resp.status_code == 200
        # Should flash a warning — no hotel created
        assert b"required" in resp.data or b"warning" in resp.data or b"Name" in resp.data


class TestRestaurantOnboarding:
    def test_partner_can_add_restaurant(self, client, db, partner_user_a, app):
        """Partner can submit a restaurant for verification."""
        login_as(client, "partner_a@yatrik.test", "partnerpass123")
        resp = client.post("/partner/onboard/restaurant", data={
            "name": "Satvik Bhojanalay",
            "cuisine": "Pure Veg",
            "city": "Vrindavan",
            "phone": "8888888888",
        }, follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            r = Restaurant.query.filter_by(name="Satvik Bhojanalay").first()
            assert r is not None
            assert r.verification_status == "PENDING"


class TestDriverOnboarding:
    def test_partner_can_register_as_driver(self, client, db, partner_user_a, app):
        """Partner can register as a driver."""
        login_as(client, "partner_a@yatrik.test", "partnerpass123")
        resp = client.post("/partner/onboard/driver", data={
            "name": "Ramesh Driver",
            "phone": "7777777777",
            "vehicle_type": "E-Rickshaw",
            "vehicle_number": "UP85AB1234",
            "service_area": "Vrindavan",
        }, follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            driver = Driver.query.filter_by(phone="7777777777").first()
            assert driver is not None
            assert driver.verification_status == "PENDING"
            assert driver.status == "OFFLINE"

    def test_duplicate_driver_prevented(self, client, db, partner_user_a, partner_user_b, app):
        """Two drivers cannot share the same phone number."""
        login_as(client, "partner_a@yatrik.test", "partnerpass123")
        client.post("/partner/onboard/driver", data={
            "name": "Driver A", "phone": "6666666666",
            "vehicle_type": "Auto", "vehicle_number": "UP85AA0001"
        })
        client.get("/auth/logout")
        login_as(client, "partner_b@yatrik.test", "partnerpass123")
        resp = client.post("/partner/onboard/driver", data={
            "name": "Driver B", "phone": "6666666666",
            "vehicle_type": "E-Rickshaw", "vehicle_number": "UP85BB9999"
        }, follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            count = Driver.query.filter_by(phone="6666666666").count()
            assert count == 1, "Duplicate phone number allowed!"


class TestPartnerEdit:
    def test_edit_hotel_updates_data(self, client, db, partner_user_a, app):
        """Editing a hotel updates the record."""
        from app.models import Hotel
        from app.database import db as _db
        with app.app_context():
            hotel = Hotel(owner_id=partner_user_a, name="Old Name", slug="old-name-edit",
                          city="Vrindavan", verification_status="PENDING")
            _db.session.add(hotel)
            _db.session.commit()
            hotel_id = hotel.id

        login_as(client, "partner_a@yatrik.test", "partnerpass123")
        resp = client.post(f"/partner/hotel/{hotel_id}/edit", data={
            "name": "New Name",
            "city": "Mathura",
            "address": "New Address",
            "phone": "5555555555",
        }, follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            hotel = Hotel.query.get(hotel_id)
            assert hotel.name == "New Name"
            assert hotel.city == "Mathura"
