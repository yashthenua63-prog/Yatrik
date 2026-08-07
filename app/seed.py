from app import create_app
from app.database import db
from app.models import Temple


app = create_app()


with app.app_context():

    # Old data clear (development)
    Temple.query.delete()


    temples = [

        Temple(
            name="Prem Mandir",
            city="Vrindavan",
            description="A beautiful temple dedicated to Radha Krishna with stunning architecture and evening light shows.",
            image="prem_mandir.jpg",
            opening_time="05:30 AM",
            closing_time="09:30 PM",
            morning_open="05:30 AM",
            morning_close="12:00 PM",
            evening_open="04:30 PM",
            evening_close="09:30 PM",
            latitude=27.5720564,
            longitude=77.671897
        ),


        Temple(
            name="Banke Bihari Temple",
            city="Vrindavan",
            description="One of the most famous Krishna temples in Vrindavan.",
            image="banke_bihari.jpg",
            opening_time="08:45 AM",
            closing_time="09:30 PM",
            morning_open="08:45 AM",
            morning_close="12:00 PM",
            evening_open="05:30 PM",
            evening_close="09:30 PM",
            latitude=27.5797728,
            longitude=77.690529
        ),


        Temple(
            name="ISKCON Vrindavan",
            city="Vrindavan",
            description="Famous Krishna Balaram Mandir managed by ISKCON.",
            image="iskcon.jpg",
            opening_time="04:30 AM",
            closing_time="09:00 PM",
            morning_open="04:30 AM",
            morning_close="01:00 PM",
            evening_open="04:30 PM",
            evening_close="09:00 PM",
            latitude=27.5723085,
            longitude=77.677389
        ),


        Temple(
            name="Radha Raman Temple",
            city="Vrindavan",
            description="Historic temple dedicated to Lord Krishna as Radha Raman.",
            image="radha_raman.jpg",
            opening_time="08:00 AM",
            closing_time="08:00 PM",
            morning_open="08:00 AM",
            morning_close="12:30 PM",
            evening_open="04:00 PM",
            evening_close="08:00 PM",
            latitude=27.5851923,
            longitude=77.6987312
        ),


        Temple(
            name="Nidhivan",
            city="Vrindavan",
            description="Sacred place associated with Radha Krishna pastimes.",
            image="nidhivan.jpg",
            opening_time="06:00 AM",
            closing_time="07:00 PM",
            morning_open="06:00 AM",
            morning_close="12:00 PM",
            evening_open="04:00 PM",
            evening_close="07:00 PM",
            latitude=27.5842125,
            longitude=77.6979595
        )

    ]


    db.session.add_all(temples)

    db.session.commit()


    print("✅ Temple coordinates updated successfully!")