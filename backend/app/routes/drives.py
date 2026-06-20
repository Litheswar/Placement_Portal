
# pyright: ignore [missing-import]
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from extensions import db
from app.models.placement_drive import PlacementDrive
from app.models.company import Company
from app.models.student import Student
from app.decorators.roles import company_required, admin_required, student_required
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

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
    
    result = []
    for d in drives:
        branches_list = [b.strip() for b in d.eligible_branches.split(",") if b.strip()]
        
        cgpa_check = student.cgpa >= d.eligibility_cgpa
        branch_check = student.branch in branches_list
        is_eligible = cgpa_check and branch_check
        
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
            "is_eligible": is_eligible
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


# 6. Company: Get own drives
@drives_bp.route("/company/drives", methods=["GET"])
@company_required
def company_list_drives():
    company_id = safe_get_jwt_id()
    if company_id is None:
        return jsonify({"message": "Invalid authentication token payload"}), 401
    
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