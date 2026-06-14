from extensions import db
from datetime import datetime


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
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

    roll_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    branch = db.Column(
        db.String(50),
        nullable=False
    )

    cgpa = db.Column(
        db.Float,
        nullable=False
    )

    graduation_year = db.Column(
        db.Integer,
        nullable=False
    )

    resume_url = db.Column(
        db.String(255)
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    is_blacklisted = db.Column(
        db.Boolean,
        default=False
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

    applications = db.relationship(
        "Application",
        backref="student",
        lazy=True
    )