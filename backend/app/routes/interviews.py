from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db

from app.models.company import Company
from app.models.application import Application
from app.models.placement_drive import PlacementDrive
from app.models.interview_schedule import InterviewSchedule

from datetime import datetime

interviews_bp = Blueprint(
    "interviews",
    __name__,
    url_prefix="/api/interviews"
)


@interviews_bp.route("/schedule/<int:drive_id>", methods=["POST"])
@jwt_required()
def schedule_interview():

    company_id = get_jwt_identity()

    drive_id = request.view_args["drive_id"]

    drive = PlacementDrive.query.filter_by(
        id=drive_id,
        company_id=company_id
    ).first()

    if not drive:
        return jsonify({
            "message": "Drive not found"
        }), 404

    data = request.get_json()

    interview_date = data.get("interview_date")
    interview_mode = data.get("interview_mode")
    location_or_link = data.get("location_or_link")
    notes = data.get("notes")

    existing = InterviewSchedule.query.filter_by(
        drive_id=drive.id
    ).first()

    if existing:
        existing.interview_date = datetime.fromisoformat(
            interview_date
        )
        existing.interview_mode = interview_mode
        existing.location_or_link = location_or_link
        existing.notes = notes

    else:
        schedule = InterviewSchedule(
            drive_id=drive.id,
            interview_date=datetime.fromisoformat(
                interview_date
            ),
            interview_mode=interview_mode,
            location_or_link=location_or_link,
            notes=notes
        )

        db.session.add(schedule)

    db.session.commit()

    return jsonify({
        "message": "Interview scheduled successfully"
    }), 200


@interviews_bp.route("/result/<int:application_id>", methods=["PUT"])
@jwt_required()
def update_result():

    company_id = get_jwt_identity()

    application = Application.query.get(application_id)

    if not application:
        return jsonify({
            "message": "Application not found"
        }), 404

    drive = PlacementDrive.query.get(
        application.drive_id
    )

    if drive.company_id != company_id:
        return jsonify({
            "message": "Unauthorized"
        }), 403

    data = request.get_json()

    result = data.get("result")

    application.result = result

    if result == "selected":
        application.status = "selected"

    elif result == "rejected":
        application.status = "rejected"

    db.session.commit()

    return jsonify({
        "message": "Result updated successfully"
    }), 200