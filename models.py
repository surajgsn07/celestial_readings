from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Admin(UserMixin, db.Model):
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Admin {self.username}>"


class Service(db.Model):
    __tablename__ = "services"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    short_description = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    price = db.Column(db.Float, nullable=False)  # in INR
    icon = db.Column(db.String(50), default="sparkles")  # lucide icon name
    category = db.Column(db.String(50), default="reading")
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship("Booking", backref="service", lazy=True)

    def __repr__(self):
        return f"<Service {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "short_description": self.short_description,
            "duration": self.duration,
            "price": self.price,
            "icon": self.icon,
            "category": self.category,
        }


class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
    customer_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)  # e.g. "10:00 AM"
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.String(50), default="pending"
    )  # pending, awaiting_verification, confirmed, completed, cancelled
    payment_status = db.Column(
        db.String(50), default="unpaid"
    )  # unpaid, awaiting_verification, paid, refunded
    payment_method = db.Column(db.String(20), default="upi")  # upi
    transaction_id = db.Column(db.String(100), nullable=True)  # UTR / UPI Ref ID
    payment_verified_at = db.Column(db.DateTime, nullable=True)
    payment_verified_by = db.Column(db.String(80), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Booking {self.id} - {self.customer_name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "service_name": self.service.name if self.service else "N/A",
            "customer_name": self.customer_name,
            "email": self.email,
            "phone": self.phone,
            "booking_date": self.booking_date.strftime("%Y-%m-%d"),
            "time_slot": self.time_slot,
            "notes": self.notes,
            "status": self.status,
            "payment_status": self.payment_status,
            "payment_method": self.payment_method,
            "transaction_id": self.transaction_id or "",
            "amount": self.amount,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M"),
        }


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ContactMessage from {self.name}>"
