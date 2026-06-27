from extensions import db
from datetime import datetime


class PlacementDrive(db.Model):
    __tablename__ = "placement_drives"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    company_id = db.Column(
        db.Integer,
        db.ForeignKey("companies.id"),
        nullable=False
    )

    job_title = db.Column(
        db.String(150),
        nullable=False
    )

    job_description = db.Column(
        db.Text,
        nullable=False
    )

    eligibility_cgpa = db.Column(
        db.Float,
        nullable=False
    )

    eligible_branches = db.Column(
        db.Text,
        nullable=False
    )

    application_deadline = db.Column(
        db.Date,
        nullable=False
    )

    package_lpa = db.Column(
        db.Float,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="pending"
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
        back_populates="placement_drive",
        lazy=True
    )

    company = db.relationship(
        "Company",
        back_populates="drives"
    )