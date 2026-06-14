from extensions import db
from datetime import datetime


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    hr_contact = db.Column(
        db.String(20),
        nullable=False
    )

    website = db.Column(
        db.String(255)
    )

    industry = db.Column(
        db.String(100)
    )

    description = db.Column(
        db.Text
    )

    approval_status = db.Column(
        db.String(20),
        default="pending"
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    drives = db.relationship(
        "PlacementDrive",
        backref="company",
        lazy=True
    )