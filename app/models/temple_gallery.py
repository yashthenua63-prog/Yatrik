from app.database import db


class TempleGallery(db.Model):

    __tablename__ = "temple_gallery"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    temple_id = db.Column(
        db.Integer,
        db.ForeignKey("temples.id"),
        nullable=False
    )


    image = db.Column(
        db.String(255),
        nullable=False
    )


    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )


    def __repr__(self):
        return f"<TempleGallery {self.image}>"