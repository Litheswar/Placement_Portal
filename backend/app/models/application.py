from extensions import db
from datetime import datetime


class Application(db.Model):
    __tablename__ = "applications"

    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "drive_id",
            name="unique_student_drive"
        ),
    )

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )

    drive_id = db.Column(
        db.Integer,
        db.ForeignKey("placement_drives.id"),
        nullable=False
    )

    applied_on = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    status = db.Column(
        db.String(20),
        default="applied"
    )

    result = db.Column(
        db.String(20),
        nullable=True
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ----------------------------
    # Relationships
    # ----------------------------

    student = db.relationship(
        "Student",
        back_populates="applications"
    )

    placement_drive = db.relationship(
        "PlacementDrive",
        back_populates="applications"
    )

    interview_schedule = db.relationship(
        "InterviewSchedule",
        back_populates="application",
        uselist=False,
        cascade="all, delete-orphan"
    )