from extensions import db
from datetime import datetime

class InterviewSchedule(db.Model):
    __tablename__ = "interview_schedules"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    application_id = db.Column(
        db.Integer,
        db.ForeignKey("applications.id"),
        nullable=False,
        unique=True
    )

    interview_date = db.Column(
        db.DateTime,
        nullable=False
    )

    interview_mode = db.Column(
        db.String(20),
        nullable=False
    )

    location_or_link = db.Column(
        db.String(255),
        nullable=False
    )

    notes = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    application = db.relationship(
        "Application",
        back_populates="interview_schedule"
    )