from app import create_app
from app.database import db
from app.models import Temple


app = create_app()


def seed_temples():
    with app.app_context():

        # Create database tables if they don't exist
        db.create_all()

        temples_data = [

            {
                "name": "Prem Mandir",
                "city": "Vrindavan",
                "description": "A beautiful temple dedicated to Radha Krishna with stunning architecture and evening light shows.",
                "image": "prem_mandir.jpg",
                "opening_time": "05:30 AM",
                "closing_time": "09:30 PM",
                "morning_open": "05:30 AM",
                "morning_close": "12:00 PM",
                "evening_open": "04:30 PM",
                "evening_close": "09:30 PM",
                "latitude": 27.5720564,
                "longitude": 77.671897
            },

            {
                "name": "Banke Bihari Temple",
                "city": "Vrindavan",
                "description": "One of the most famous Krishna temples in Vrindavan.",
                "image": "banke_bihari.jpg",
                "opening_time": "08:45 AM",
                "closing_time": "09:30 PM",
                "morning_open": "08:45 AM",
                "morning_close": "12:00 PM",
                "evening_open": "05:30 PM",
                "evening_close": "09:30 PM",
                "latitude": 27.5797728,
                "longitude": 77.690529
            },

            {
                "name": "ISKCON Vrindavan",
                "city": "Vrindavan",
                "description": "Famous Krishna Balaram Mandir managed by ISKCON.",
                "image": "iskcon.jpg",
                "opening_time": "04:30 AM",
                "closing_time": "09:00 PM",
                "morning_open": "04:30 AM",
                "morning_close": "01:00 PM",
                "evening_open": "04:30 PM",
                "evening_close": "09:00 PM",
                "latitude": 27.5723085,
                "longitude": 77.677389
            },

            {
                "name": "Radha Raman Temple",
                "city": "Vrindavan",
                "description": "Historic temple dedicated to Lord Krishna as Radha Raman.",
                "image": "radha_raman.jpg",
                "opening_time": "08:00 AM",
                "closing_time": "08:00 PM",
                "morning_open": "08:00 AM",
                "morning_close": "12:30 PM",
                "evening_open": "04:00 PM",
                "evening_close": "08:00 PM",
                "latitude": 27.5851923,
                "longitude": 77.6987312
            },

            {
                "name": "Nidhivan",
                "city": "Vrindavan",
                "description": "Sacred place associated with Radha Krishna pastimes.",
                "image": "nidhivan.jpg",
                "opening_time": "06:00 AM",
                "closing_time": "07:00 PM",
                "morning_open": "06:00 AM",
                "morning_close": "12:00 PM",
                "evening_open": "04:00 PM",
                "evening_close": "07:00 PM",
                "latitude": 27.5842125,
                "longitude": 77.6979595
            },
            
            {
                "name": "Shri Krishna Janmasthan",
                "city": "Mathura",
                "description": "The birthplace of Lord Krishna.",
                "image": "janmasthan.jpg",
                "opening_time": "05:00 AM",
                "closing_time": "09:30 PM",
                "morning_open": "05:00 AM",
                "morning_close": "12:00 PM",
                "evening_open": "04:00 PM",
                "evening_close": "09:30 PM",
                "latitude": 27.5049514,
                "longitude": 77.6698642
            },
            
            {
                "name": "Dwarkadhish Temple",
                "city": "Mathura",
                "description": "One of the most visited temples in Mathura, built in 1814.",
                "image": "dwarkadhish.jpg",
                "opening_time": "06:30 AM",
                "closing_time": "07:00 PM",
                "morning_open": "06:30 AM",
                "morning_close": "10:30 AM",
                "evening_open": "04:00 PM",
                "evening_close": "07:00 PM",
                "latitude": 27.4939763,
                "longitude": 77.6830722
            }

        ]

        for data in temples_data:
            temple = Temple.query.filter_by(name=data["name"]).first()
            if not temple:
                temple = Temple(**data)
                db.session.add(temple)
            else:
                for key, value in data.items():
                    setattr(temple, key, value)
        
        db.session.commit()

        print("✅ Yatrik temples seeded/updated successfully.")


if __name__ == "__main__":
    seed_temples()