from app import create_app
from app.database import db
from app.models import Temple, TempleGallery

app = create_app()

def seed_gallery():
    with app.app_context():
        # Removed db.create_all() to prevent hybrid schema issues in production
        # Alembic (flask db upgrade) must be solely responsible for schema creation.
        print("Starting Temple Gallery seed process...")

        # Find Prem Mandir
        prem_mandir = Temple.query.filter_by(name="Prem Mandir").first()
        if not prem_mandir:
            print("Prem Mandir not found. Please run seed.py first.")
            return

        gallery_data = [
            {
                "temple_id": prem_mandir.id,
                "image": "prem_mandir_night.jpg",
                "is_video": False,
                "video_url": None
            },
            {
                "temple_id": prem_mandir.id,
                "image": "prem_mandir_video_thumb.jpg",
                "is_video": True,
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
        ]

        for data in gallery_data:
            existing = TempleGallery.query.filter_by(
                temple_id=data["temple_id"],
                image=data["image"]
            ).first()

            if not existing:
                item = TempleGallery(**data)
                db.session.add(item)
            else:
                existing.is_video = data["is_video"]
                existing.video_url = data["video_url"]

        db.session.commit()
        print("✅ Temple gallery seeded successfully.")

if __name__ == "__main__":
    seed_gallery()
