# pyright: ignore [missing-import]
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from extensions import db
from app.models.placement_drive import PlacementDrive
from app.models.company import Company
from app.models.student import Student
from app.models.application import Application
from app.decorators.roles import company_required, admin_required, student_required
from datetime import datetime, date
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from app.models.interview_schedule import InterviewSchedule
drives_bp = Blueprint("drives", __name__, url_prefix="/api")

# Helper: Safely parse JWT identities
def safe_get_jwt_id():
    try:
        return int(get_jwt_identity())
    except (ValueError, TypeError):
        return None

# Helper: Parse and validate input data for creating/editing drive
def validate_drive_data(data):
    required_fields = [
        "job_title", "job_description", "eligibility_cgpa", 
        "eligible_branches", "application_deadline", "package_lpa"
    ]
    for field in required_fields:
        if field not in data:
            return None, f"Missing required field: {field}"
            
    if not isinstance(data["job_title"], str) or not data["job_title"].strip():
        return None, "job_title must be a non-empty string"
        
    if not isinstance(data["job_description"], str) or not data["job_description"].strip():
        return None, "job_description must be a non-empty string"
        
    try:
        eligibility_cgpa = float(data["eligibility_cgpa"])
        if not (0.0 <= eligibility_cgpa <= 10.0):
            return None, "eligibility_cgpa must be between 0.0 and 10.0"
    except (ValueError, TypeError):
        return None, "eligibility_cgpa must be a number"
        
    try:
        package_lpa = float(data["package_lpa"])
        if package_lpa <= 0:
            return None, "package_lpa must be greater than 0"
    except (ValueError, TypeError):
        return None, "package_lpa must be a number"
        
    branches = data["eligible_branches"]
    if not isinstance(branches, list) or not all(isinstance(b, str) and b.strip() for b in branches):
        return None, "eligible_branches must be a list of non-empty strings"
        
    try:
        deadline = datetime.strptime(data["application_deadline"], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None, "application_deadline must be in YYYY-MM-DD format"
        
    return {
        "job_title": data["job_title"].strip(),
        "job_description": data["job_description"].strip(),
        "eligibility_cgpa": eligibility_cgpa,
        "eligible_branches": ", ".join(b.strip() for b in branches),
        "application_deadline": deadline,
        "package_lpa": package_lpa
    }, None


# 1. Company: Create placement drive
@drives_bp.route("/company/drives", methods=["POST"])
@company_required
def create_drive():
    company_id = safe_get_jwt_id()
    if company_id is None:
        return jsonify({"message": "Invalid authentication token payload"}), 401
    
    company = db.session.get(Company, company_id)
    if not company:
        return jsonify({"message": "Company not found"}), 404
        
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body must be JSON"}), 400
        
    validated, error_msg = validate_drive_data(data)
    if error_msg:
        return jsonify({"message": error_msg}), 400
        
    new_drive = PlacementDrive(
        company_id=company_id,
        job_title=validated["job_title"],
        job_description=validated["job_description"],
        eligibility_cgpa=validated["eligibility_cgpa"],
        eligible_branches=validated["eligible_branches"],
        application_deadline=validated["application_deadline"],
        package_lpa=validated["package_lpa"]
    )
    
    try:
        db.session.add(new_drive)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"message": "An error occurred while saving the placement drive"}), 500
    
    return jsonify({
        "message": "Placement drive created successfully",
        "drive": {
            "id": new_drive.id,
            "job_title": new_drive.job_title,
            "status": new_drive.status 
        }
    }), 201


# 2. Admin: Review pending/all drives
@drives_bp.route("/admin/drives", methods=["GET"])
@admin_required
def admin_list_drives():
    status = request.args.get("status")
    
    # Modern 2.0 Select Statement with Eager Loading
    stmt = select(PlacementDrive).options(db.joinedload(PlacementDrive.company))
    if status:
        stmt = stmt.filter_by(status=status)
        
    drives = db.session.scalars(stmt).all()
    
    result = []
    for d in drives:
        branches_list = [b.strip() for b in d.eligible_branches.split(",") if b.strip()]
        result.append({
            "id": d.id,
            "job_title": d.job_title,
            "job_description": d.job_description,
            "eligibility_cgpa": d.eligibility_cgpa,
            "eligible_branches": branches_list,
            "application_deadline": d.application_deadline.strftime("%Y-%m-%d"),
            "package_lpa": d.package_lpa,
            "status": d.status,
            "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S") if d.created_at else None,
            "company": {
                "id": d.company.id,
                "name": d.company.name,
                "email": d.company.email,
                "website": d.company.website,
                "industry": d.company.industry,
                "description": d.company.description
            }
        })
        
    return jsonify(result), 200


# 3. Admin: Approve/Reject a drive
@drives_bp.route("/admin/drives/<int:drive_id>", methods=["PATCH"])
@admin_required
def admin_update_drive_status(drive_id):
    drive = db.session.get(PlacementDrive, drive_id)
    if not drive:
        return jsonify({"message": "Placement drive not found"}), 404
        
    if drive.status != "pending":
        return jsonify({"message": f"Cannot modify status of a drive that is already '{drive.status}'"}), 400
        
    data = request.get_json()
    if not data or "status" not in data:
        return jsonify({"message": "Missing status in request body"}), 400
        
    new_status = data["status"]
    if new_status not in ["approved", "rejected"]:
        return jsonify({"message": "Invalid status. Must be 'approved' or 'rejected'"}), 400
        
    drive.status = new_status
    
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"message": "An error occurred while updating the drive status"}), 500
    
    return jsonify({
        "message": f"Drive status updated to '{new_status}' successfully",
        "drive": {
            "id": drive.id,
            "job_title": drive.job_title,
            "status": drive.status
        }
    }), 200


# 4. Student: Browse approved drives with server-side eligibility checks
@drives_bp.route("/student/drives", methods=["GET"])
@student_required
def student_list_drives():
    student_id = safe_get_jwt_id()
    if student_id is None:
        return jsonify({"message": "Invalid authentication token payload"}), 401
    
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({"message": "Student not found"}), 404
        
    stmt = select(PlacementDrive).filter_by(status="approved").options(db.joinedload(PlacementDrive.company))
    drives = db.session.scalars(stmt).all()
    
    # Get all application drive_ids for the current student
    applied_stmt = select(Application.drive_id).filter_by(student_id=student_id)
    applied_drive_ids = set(db.session.scalars(applied_stmt).all())
    
    result = []
    for d in drives:
        branches_list = [b.strip() for b in d.eligible_branches.split(",") if b.strip()]
        
        
        student_cgpa = student.cgpa or 0.0
        student_branch = student.branch or ""
        
        cgpa_check = student_cgpa >= d.eligibility_cgpa
        branch_check = student_branch in branches_list
        
    
        is_eligible = cgpa_check and branch_check
        has_applied = d.id in applied_drive_ids
        
        result.append({
            "id": d.id,
            "job_title": d.job_title,
            "job_description": d.job_description,
            "eligibility_cgpa": d.eligibility_cgpa,
            "eligible_branches": branches_list,
            "application_deadline": d.application_deadline.strftime("%Y-%m-%d"),
            "package_lpa": d.package_lpa,
            "status": d.status,
            "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S") if d.created_at else None,
            "company": {
                "name": d.company.name,
                "email": d.company.email,
                "website": d.company.website,
                "industry": d.company.industry,
                "description": d.company.description
            },
            "cgpa_check": cgpa_check,
            "branch_check": branch_check,
            "is_eligible": is_eligible,
            "has_applied": has_applied
        })
        
    return jsonify(result), 200


def calculate_completeness(student):
    fields = [
        bool(student.name and student.name.strip()),
        bool(student.email and student.email.strip()),
        bool(student.roll_number and student.roll_number.strip()),
        bool(student.branch and student.branch.strip()),
        bool(student.cgpa is not None and student.cgpa > 0.0),
        bool(student.graduation_year is not None and student.graduation_year > 0),
        bool(student.resume_url and student.resume_url.strip())
    ]
    filled = sum(fields)
    return int(round((filled / len(fields)) * 100))


@drives_bp.route("/student/profile", methods=["GET"])
@student_required
def get_student_profile():
    student_id = safe_get_jwt_id()
    if student_id is None:
        return jsonify({"message": "Invalid authentication token payload"}), 401
    
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({"message": "Student not found"}), 404
        
    completeness = calculate_completeness(student)
    
    return jsonify({
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "roll_number": student.roll_number,
        "branch": student.branch,
        "cgpa": student.cgpa,
        "graduation_year": student.graduation_year,
        "resume_url": student.resume_url,
        "is_blacklisted": student.is_blacklisted,
        "completeness_percentage": completeness
    }), 200


@drives_bp.route("/student/profile", methods=["PATCH"])
@student_required
def update_student_profile():
    student_id = safe_get_jwt_id()
    if student_id is None:
        return jsonify({"message": "Invalid authentication token payload"}), 401
    
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({"message": "Student not found"}), 404
        
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body must be JSON"}), 400
        
    # Validations
    if "roll_number" in data:
        roll = data["roll_number"]
        if not isinstance(roll, str) or not roll.strip():
            return jsonify({"message": "Roll number must be a non-empty string"}), 400
        roll = roll.strip()
        # Check uniqueness
        existing = db.session.scalars(
            select(Student).filter(Student.roll_number == roll, Student.id != student_id)
        ).first()
        if existing:
            return jsonify({"message": "Roll number is already registered by another student"}), 400
        student.roll_number = roll
        
    if "branch" in data:
        branch = data["branch"]
        if not isinstance(branch, str) or not branch.strip():
            return jsonify({"message": "Branch must be a non-empty string"}), 400
        student.branch = branch.strip()
        
    if "cgpa" in data:
        try:
            cgpa = float(data["cgpa"])
            if not (0.0 <= cgpa <= 10.0):
                return jsonify({"message": "CGPA must be between 0.0 and 10.0"}), 400
            student.cgpa = cgpa
        except (ValueError, TypeError):
            return jsonify({"message": "CGPA must be a valid number"}), 400
            
    if "graduation_year" in data:
        try:
            grad_year = int(data["graduation_year"])
            if grad_year <= 0:
                return jsonify({"message": "Graduation year must be a positive integer"}), 400
            student.graduation_year = grad_year
        except (ValueError, TypeError):
            return jsonify({"message": "Graduation year must be a valid integer"}), 400
            
    if "resume_url" in data:
        resume = data["resume_url"]
        if resume is not None and not isinstance(resume, str):
            return jsonify({"message": "Resume URL must be a string"}), 400
        student.resume_url = resume.strip() if resume else None
        
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"message": "An error occurred while updating the profile"}), 500
        
    completeness = calculate_completeness(student)
    
    return jsonify({
        "message": "Profile updated successfully",
        "student": {
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "roll_number": student.roll_number,
            "branch": student.branch,
            "cgpa": student.cgpa,
            "graduation_year": student.graduation_year,
            "resume_url": student.resume_url,
            "is_blacklisted": student.is_blacklisted,
            "completeness_percentage": completeness
        }
    }), 200


@drives_bp.route("/student/applications", methods=["POST"])
@student_required
def student_apply_drive():
    student_id = safe_get_jwt_id()
    if student_id is None:
        return jsonify({"message": "Invalid authentication token payload"}), 401
    
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({"message": "Student not found"}), 404
        
    if student.is_blacklisted:
        return jsonify({"message": "Cannot apply: Student is blacklisted"}), 403
        
    data = request.get_json()
    if not data or "drive_id" not in data:
        return jsonify({"message": "Missing drive_id in request body"}), 400
        
    try:
        drive_id = int(data["drive_id"])
    except (ValueError, TypeError):
        return jsonify({"message": "drive_id must be a valid integer"}), 400
        
    drive = db.session.get(PlacementDrive, drive_id)
    if not drive:
        return jsonify({"message": "Placement drive not found"}), 404
        
    if drive.status != "approved":
        return jsonify({"message": f"Cannot apply: Placement drive is not approved (current status: {drive.status})"}), 400
        
    if drive.application_deadline < date.today():
        return jsonify({"message": "Cannot apply: Application deadline has passed"}), 400
        
    if student.cgpa < drive.eligibility_cgpa:
        return jsonify({"message": f"Cannot apply: CGPA criteria not met (required: {drive.eligibility_cgpa}, yours: {student.cgpa})"}), 400
    if student.cgpa is None or student.branch is None:
        return jsonify({"message": "Cannot apply: Please update your CGPA and Branch in your profile first"}), 400   
    branches_list = [b.strip() for b in drive.eligible_branches.split(",") if b.strip()]
    if student.branch not in branches_list:
        return jsonify({"message": "Cannot apply: Your branch is not eligible for this drive"}), 400
        
    # Check duplicate application
    existing = db.session.scalars(
        select(Application).filter_by(student_id=student_id, drive_id=drive_id)
    ).first()
    if existing:
        return jsonify({"message": "Cannot apply: You have already applied to this placement drive"}), 400
        
    new_app = Application(
        student_id=student_id,
        drive_id=drive_id,
        status="applied"
    )
    
    try:
        db.session.add(new_app)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"message": "An error occurred while submitting the application"}), 500
        
    return jsonify({
        "message": "Application submitted successfully",
        "application": {
            "id": new_app.id,
            "student_id": new_app.student_id,
            "drive_id": new_app.drive_id,
            "status": new_app.status,
            "applied_on": new_app.applied_on.strftime("%Y-%m-%d %H:%M:%S") if new_app.applied_on else None
        }
    }), 201


@drives_bp.route("/student/applications", methods=["GET"])
@student_required
def student_get_applications():
    student_id = safe_get_jwt_id()
    if student_id is None:
        return jsonify({"message": "Invalid authentication token payload"}), 401

    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({"message": "Student not found"}), 404

    try:
        stmt = select(Application).filter_by(student_id=student_id).options(
            db.joinedload(Application.placement_drive).joinedload(PlacementDrive.company),
            db.joinedload(Application.interview_schedule)
        )
        apps = db.session.scalars(stmt).all()
    except Exception:
        # Handle case where interview_schedules table schema is not updated
        stmt = select(Application).filter_by(student_id=student_id).options(
            db.joinedload(Application.placement_drive).joinedload(PlacementDrive.company)
        )
        apps = db.session.scalars(stmt).all()

    result = []
    for app in apps:
        interview_data = None
        if hasattr(app, 'interview_schedule') and app.interview_schedule:
            interview_data = {
                "interview_date": app.interview_schedule.interview_date.strftime("%Y-%m-%d %H:%M") if app.interview_schedule.interview_date else None,
                "interview_mode": app.interview_schedule.interview_mode,
                "location_or_link": app.interview_schedule.location_or_link,
                "notes": app.interview_schedule.notes
            }

        result.append({
            "id": app.id,
            "applied_on": app.applied_on.strftime("%Y-%m-%d %H:%M:%S") if app.applied_on else None,
            "status": app.status,
            "result": app.result,
            "interview": interview_data,
            "drive": {
                "id": app.placement_drive.id,
                "job_title": app.placement_drive.job_title,
                "package_lpa": app.placement_drive.package_lpa,
                "application_deadline": app.placement_drive.application_deadline.strftime("%Y-%m-%d"),
                "company_name": app.placement_drive.company.name
            }
        })

    return jsonify(result), 200


# 5. Company: Close drive manually
@drives_bp.route("/company/drives/<int:drive_id>/close", methods=["PATCH"])
@company_required
def company_close_drive(drive_id):
    company_id = safe_get_jwt_id()
    if company_id is None:
        return jsonify({"message": "Invalid authentication token payload"}), 401
    
    drive = db.session.get(PlacementDrive, drive_id)
    if not drive:
        return jsonify({"message": "Placement drive not found"}), 404
        
    if drive.company_id != company_id:
        return jsonify({"message": "Forbidden: You do not own this placement drive"}), 403
        
    if drive.status != "approved":
        return jsonify({"message": f"Cannot close a drive that is currently '{drive.status}'"}), 400
        
    drive.status = "closed"
    
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"message": "An error occurred while closing the drive"}), 500
    
    return jsonify({
        "message": "Placement drive closed successfully",
        "drive": {
            "id": drive.id,
            "job_title": drive.job_title,
            "status": drive.status
        }
    }), 200


@drives_bp.route("/company/drives", methods=["GET"])
@company_required
def company_list_drives():

    company_id = safe_get_jwt_id()

    stmt = select(PlacementDrive).filter_by(company_id=company_id)

    drives = db.session.scalars(stmt).all()

    result = []

    for d in drives:
        branches_list = [b.strip() for b in d.eligible_branches.split(",") if b.strip()]

        result.append({
            "id": d.id,
            "job_title": d.job_title,
            "job_description": d.job_description,
            "eligibility_cgpa": d.eligibility_cgpa,
            "eligible_branches": branches_list,
            "application_deadline": d.application_deadline.strftime("%Y-%m-%d"),
            "package_lpa": d.package_lpa,
            "status": d.status,
            "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S") if d.created_at else None
        })

    return jsonify(result), 200


@drives_bp.route("/company/drives/<int:drive_id>/applications", methods=["GET"])
@company_required
def company_get_drive_applications(drive_id):

    company_id = safe_get_jwt_id()

    drive = db.session.get(PlacementDrive, drive_id)

    if not drive:
        return jsonify({"message": "Drive not found"}), 404

    if drive.company_id != company_id:
        return jsonify({"message": "Unauthorized"}), 403

    applications = db.session.scalars(
        select(Application)
        .filter_by(drive_id=drive_id)
        .options(db.joinedload(Application.student))
    ).all()

    result = []

    for app in applications:
        result.append({
            "application_id": app.id,
            "student_id": app.student.id,
            "student_name": app.student.name,
            "email": app.student.email,
            "roll_number": app.student.roll_number,
            "branch": app.student.branch,
            "cgpa": app.student.cgpa,
            "status": app.status
        })

    return jsonify(result), 200


# 6. Company: Schedule/Update interview for an application
@drives_bp.route("/company/interviews", methods=["POST"])
@company_required
def company_schedule_interview():
    company_id = safe_get_jwt_id()
    if company_id is None:
        return jsonify({"message": "Invalid authentication token payload"}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body must be JSON"}), 400
    
    application_id = data.get("application_id")
    if not application_id:
        return jsonify({"message": "Missing application_id"}), 400
    
    interview_date = data.get("interview_date")
    if not interview_date:
        return jsonify({"message": "Missing interview_date"}), 400
    
    interview_mode = data.get("interview_mode")
    if not interview_mode or interview_mode not in ["Online", "Offline"]:
        return jsonify({"message": "Invalid interview_mode. Must be 'Online' or 'Offline'"}), 400
    
    location_or_link = data.get("location_or_link")
    if not location_or_link:
        return jsonify({"message": "Missing location_or_link"}), 400
    
    notes = data.get("notes", "")
    
    # Get application and validate
    application = db.session.get(Application, application_id)
    if not application:
        return jsonify({"message": "Application not found"}), 404
    
    # Validate that the drive belongs to the logged-in company
    drive = db.session.get(PlacementDrive, application.drive_id)
    if not drive:
        return jsonify({"message": "Placement drive not found"}), 404
    
    if drive.company_id != company_id:
        return jsonify({"message": "Unauthorized: You can only schedule interviews for your own drives"}), 403
    
    # Check if interview already exists for this application
    existing_interview = db.session.scalars(
        select(InterviewSchedule).filter_by(application_id=application_id)
    ).first()
    
    try:
        interview_date_parsed = datetime.strptime(interview_date, "%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return jsonify({"message": "Invalid interview_date format. Use 'YYYY-MM-DD HH:MM'"}), 400
    
    if existing_interview:
        # Update existing interview
        existing_interview.interview_date = interview_date_parsed
        existing_interview.interview_mode = interview_mode
        existing_interview.location_or_link = location_or_link
        existing_interview.notes = notes
    else:
        # Create new interview
        new_interview = InterviewSchedule(
            application_id=application_id,
            interview_date=interview_date_parsed,
            interview_mode=interview_mode,
            location_or_link=location_or_link,
            notes=notes
        )
        db.session.add(new_interview)
    
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"message": "An error occurred while scheduling the interview"}), 500
    
    return jsonify({
        "message": "Interview scheduled successfully"
    }), 201


# 7. Company: Get interview results for a drive
@drives_bp.route("/company/drives/<int:drive_id>/results", methods=["GET"])
@company_required
def company_get_drive_results(drive_id):
    company_id = safe_get_jwt_id()
    if company_id is None:
        return jsonify({"message": "Invalid authentication token payload"}), 401
    
    drive = db.session.get(PlacementDrive, drive_id)
    if not drive:
        return jsonify({"message": "Drive not found"}), 404
    
    if drive.company_id != company_id:
        return jsonify({"message": "Unauthorized: You can only view results for your own drives"}), 403
    
    applications = db.session.scalars(
        select(Application)
        .filter_by(drive_id=drive_id)
        .options(
            db.joinedload(Application.student),
            db.joinedload(Application.interview_schedule)
        )
    ).all()
    
    result = []
    for app in applications:
        interview_data = None
        if app.interview_schedule:
            interview_data = {
                "interview_date": app.interview_schedule.interview_date.strftime("%Y-%m-%d %H:%M") if app.interview_schedule.interview_date else None,
                "interview_mode": app.interview_schedule.interview_mode,
                "location_or_link": app.interview_schedule.location_or_link
            }
        
        result.append({
            "application_id": app.id,
            "student_id": app.student.id,
            "student_name": app.student.name,
            "email": app.student.email,
            "branch": app.student.branch,
            "cgpa": app.student.cgpa,
            "application_status": app.status,
            "result": app.result,
            "interview": interview_data
        })
    
    return jsonify(result), 200


# 8. Company: Update application result
@drives_bp.route("/company/applications/<int:application_id>/result", methods=["PATCH"])
@company_required
def company_update_application_result(application_id):
    company_id = safe_get_jwt_id()
    if company_id is None:
        return jsonify({"message": "Invalid authentication token payload"}), 401
    
    data = request.get_json()
    if not data or "result" not in data:
        return jsonify({"message": "Missing result in request body"}), 400
    
    new_result = data["result"]
    if new_result not in ["selected", "rejected", "waiting"]:
        return jsonify({"message": "Invalid result. Must be 'selected', 'rejected', or 'waiting'"}), 400
    
    application = db.session.get(Application, application_id)
    if not application:
        return jsonify({"message": "Application not found"}), 404
    
    # Verify the drive belongs to the logged-in company
    drive = db.session.get(PlacementDrive, application.drive_id)
    if not drive:
        return jsonify({"message": "Placement drive not found"}), 404
    
    if drive.company_id != company_id:
        return jsonify({"message": "Unauthorized: You can only update results for your own drives"}), 403
    
    # Verify interview has been scheduled
    interview = db.session.scalars(
        select(InterviewSchedule).filter_by(application_id=application_id)
    ).first()
    if not interview:
        return jsonify({"message": "Cannot update result: Interview has not been scheduled for this application"}), 400
    
    # Update result
    application.result = new_result
    
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"message": "An error occurred while updating the result"}), 500
    
    return jsonify({
        "message": "Result updated successfully"
    }), 200


# 9. Company: Dashboard Stats
@drives_bp.route("/company/dashboard", methods=["GET"])
@company_required
def company_dashboard_stats():
    company_id = safe_get_jwt_id()
    if company_id is None:
        return jsonify({"message": "Invalid authentication token payload"}), 401
    
    total_drives = db.session.scalar(select(func.count()).select_from(PlacementDrive).filter_by(company_id=company_id))
    approved_drives = db.session.scalar(select(func.count()).select_from(PlacementDrive).filter_by(company_id=company_id, status="approved"))
    pending_drives = db.session.scalar(select(func.count()).select_from(PlacementDrive).filter_by(company_id=company_id, status="pending"))
    closed_drives = db.session.scalar(select(func.count()).select_from(PlacementDrive).filter_by(company_id=company_id, status="closed"))
    
    # Get all drive IDs for this company
    company_drive_ids = db.session.scalars(
        select(PlacementDrive.id).filter_by(company_id=company_id)
    ).all()
    
    total_applications = 0
    if company_drive_ids:
        total_applications = db.session.scalar(
            select(func.count()).select_from(Application).filter(Application.drive_id.in_(company_drive_ids))
        ) or 0
    
    # Count interviews scheduled (applications with interview schedule)
    interviews_scheduled = 0
    if company_drive_ids:
        try:
            interviews_scheduled = db.session.scalar(
                select(func.count())
                .select_from(Application)
                .join(InterviewSchedule, Application.id == InterviewSchedule.application_id)
                .filter(Application.drive_id.in_(company_drive_ids))
            ) or 0
        except Exception:
            # Handle case where interview_schedules table schema is not updated
            interviews_scheduled = 0
    
    # Count results
    selected_students = 0
    rejected_students = 0
    waiting_students = 0
    if company_drive_ids:
        selected_students = db.session.scalar(
            select(func.count()).select_from(Application).filter(
                Application.drive_id.in_(company_drive_ids),
                Application.result == "selected"
            )
        ) or 0
        rejected_students = db.session.scalar(
            select(func.count()).select_from(Application).filter(
                Application.drive_id.in_(company_drive_ids),
                Application.result == "rejected"
            )
        ) or 0
        waiting_students = db.session.scalar(
            select(func.count()).select_from(Application).filter(
                Application.drive_id.in_(company_drive_ids),
                Application.result == "waiting"
            )
        ) or 0
    
    return jsonify({
        "total_drives": total_drives or 0,
        "approved_drives": approved_drives or 0,
        "pending_drives": pending_drives or 0,
        "closed_drives": closed_drives or 0,
        "total_applications": total_applications,
        "interviews_scheduled": interviews_scheduled,
        "selected_students": selected_students,
        "rejected_students": rejected_students,
        "waiting_students": waiting_students
    }), 200


# 10. Student: Dashboard Stats
@drives_bp.route("/student/dashboard", methods=["GET"])
@student_required
def student_dashboard_stats():
    student_id = safe_get_jwt_id()
    if student_id is None:
        return jsonify({"message": "Invalid authentication token payload"}), 401
    
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({"message": "Student not found"}), 404
    
    # Count eligible drives (approved drives where student meets criteria)
    eligible_drives = db.session.scalar(
        select(func.count())
        .select_from(PlacementDrive)
        .filter_by(status="approved")
        .filter(PlacementDrive.eligibility_cgpa <= student.cgpa)
    ) or 0
    
    # Count applied drives
    applied_drives = db.session.scalar(
        select(func.count()).select_from(Application).filter_by(student_id=student_id)
    ) or 0
    
    # Count interviews (applications with interview schedule)
    interviews = 0
    try:
        interviews = db.session.scalar(
            select(func.count())
            .select_from(Application)
            .join(InterviewSchedule, Application.id == InterviewSchedule.application_id)
            .filter_by(student_id=student_id)
        ) or 0
    except Exception:
        # Handle case where interview_schedules table schema is not updated
        interviews = 0
    
    # Count results
    selected = db.session.scalar(
        select(func.count()).select_from(Application).filter_by(student_id=student_id, result="selected")
    ) or 0
    rejected = db.session.scalar(
        select(func.count()).select_from(Application).filter_by(student_id=student_id, result="rejected")
    ) or 0
    waiting = db.session.scalar(
        select(func.count()).select_from(Application).filter_by(student_id=student_id, result="waiting")
    ) or 0
    
    return jsonify({
        "eligible_drives": eligible_drives,
        "applied_drives": applied_drives,
        "interviews": interviews,
        "selected": selected,
        "rejected": rejected,
        "waiting": waiting
    }), 200


# 11. Admin: Dashboard Stats
@drives_bp.route("/admin/dashboard", methods=["GET"])
@admin_required
def admin_dashboard_stats():
    # Count students
    total_students = db.session.scalar(select(func.count()).select_from(Student)) or 0
    
    # Count companies
    total_companies = db.session.scalar(select(func.count()).select_from(Company)) or 0
    approved_companies = db.session.scalar(select(func.count()).select_from(Company).filter_by(approval_status="approved")) or 0
    pending_companies = db.session.scalar(select(func.count()).select_from(Company).filter_by(approval_status="pending")) or 0
    
    # Count drives
    total_drives = db.session.scalar(select(func.count()).select_from(PlacementDrive)) or 0
    approved_drives = db.session.scalar(select(func.count()).select_from(PlacementDrive).filter_by(status="approved")) or 0
    pending_drives = db.session.scalar(select(func.count()).select_from(PlacementDrive).filter_by(status="pending")) or 0
    closed_drives = db.session.scalar(select(func.count()).select_from(PlacementDrive).filter_by(status="closed")) or 0
    
    # Count applications
    total_applications = db.session.scalar(select(func.count()).select_from(Application)) or 0
    
    # Count interviews scheduled
    interviews_scheduled = 0
    try:
        interviews_scheduled = db.session.scalar(
            select(func.count())
            .select_from(Application)
            .join(InterviewSchedule, Application.id == InterviewSchedule.application_id)
        ) or 0
    except Exception:
        # Handle case where interview_schedules table schema is not updated
        interviews_scheduled = 0
    
    # Count results
    selected_students = db.session.scalar(
        select(func.count()).select_from(Application).filter_by(result="selected")
    ) or 0
    rejected_students = db.session.scalar(
        select(func.count()).select_from(Application).filter_by(result="rejected")
    ) or 0
    waiting_students = db.session.scalar(
        select(func.count()).select_from(Application).filter_by(result="waiting")
    ) or 0
    
    return jsonify({
        "total_students": total_students,
        "total_companies": total_companies,
        "approved_companies": approved_companies,
        "pending_companies": pending_companies,
        "total_drives": total_drives,
        "approved_drives": approved_drives,
        "pending_drives": pending_drives,
        "closed_drives": closed_drives,
        "total_applications": total_applications,
        "selected_students": selected_students,
        "rejected_students": rejected_students,
        "waiting_students": waiting_students,
        "interviews_scheduled": interviews_scheduled
    }), 200