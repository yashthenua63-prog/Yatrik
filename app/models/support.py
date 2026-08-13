from app.database import db


class SupportTicket(db.Model):
    __tablename__ = "support_tickets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)   # nullable for guests
    user = db.relationship('User', backref='support_tickets')

    # Contact (for guests who are not logged in)
    contact_name = db.Column(db.String(150))
    contact_email = db.Column(db.String(150))

    category = db.Column(db.String(50), nullable=False)
    # VERIFICATION / PROFILE / TECHNICAL / ACCOUNT / RIDE / CUSTOMER_ISSUE / OTHER

    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)

    status = db.Column(db.String(20), default='OPEN')
    # OPEN / IN_PROGRESS / RESOLVED / CLOSED

    admin_response = db.Column(db.Text)   # Internal — never expose publicly

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<SupportTicket #{self.id} [{self.status}]>"
