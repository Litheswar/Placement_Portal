from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db
from sqlalchemy import select, func

from app.models.admin import Admin
from app.models.student import Student
from app.models.company import Company
from app.models.placement_drive import PlacementDrive
from app.models.application import Application

from app.decorators.roles import admin_required, student_required, company_required


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)

# -------------- Admin ------------- 

@auth_bp.route("/admin/login", methods=['POST'])
def admin_login():
    data = request.get_json()
    
    email = data.get("email")
    password = data.get("password")
    
    admin = Admin.query.filter_by(
        email=email
    ).first()
    
    if not admin:
        return jsonify({
            "message": "Invalid email or password"
        }), 401
        
    if not check_password_hash(admin.password_hash, password):
        return jsonify({
            "message": "Invalid email or password"
        }), 401
        
    access_token = create_access_token(
        identity=str(admin.id),
        additional_claims={
            "role": "admin"
        }
    )
    
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "role": "admin"
    }), 200
    
# -------------- Student ------------- 

@auth_bp.route("/student/register", methods=["POST"])
def student_register():

    data = request.get_json()

    email = data.get("email")
    roll_number = data.get("roll_number")

    existing_student = Student.query.filter(
        (Student.email == email) |
        (Student.roll_number == roll_number)
    ).first()

    if existing_student:
        return jsonify({
            "message": "Student already exists"
        }), 409

    student = Student(
        name=data.get("name"),
        email=email,
        password_hash=generate_password_hash(
            data.get("password")
        ),
        roll_number=roll_number,
        branch=data.get("branch"),
        cgpa=data.get("cgpa"),
        graduation_year=data.get("graduation_year"),
        resume_url=data.get("resume_url")
    )

    db.session.add(student)
    db.session.commit()

    return jsonify({
        "message": "Student registered successfully"
    }), 201
    
    
@auth_bp.route("/student/login", methods=["POST"])
def student_login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    student = Student.query.filter_by(
        email=email
    ).first()

    if not student:
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    if not check_password_hash(student.password_hash, password):
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    if not student.is_active:
        return jsonify({
            "message": "Account is inactive"
        }), 403

    if student.is_blacklisted:
        return jsonify({
            "message": "Account is blacklisted"
        }), 403

    access_token = create_access_token(
        identity=str(student.id),
        additional_claims={
            "role": "student"
        }
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "role": "student"
    }), 200
    
    
# -------------- Company ------------- 

@auth_bp.route("/company/register", methods=["POST"])
def company_register():

    data = request.get_json()

    email = data.get("email")

    existing_company = Company.query.filter_by(
        email=email
    ).first()

    if existing_company:
        return jsonify({
            "message": "Company already exists"
        }), 409

    company = Company(
        name=data.get("name"),
        email=email,
        password_hash=generate_password_hash(
            data.get("password")
        ),
        hr_contact=data.get("hr_contact"),
        website=data.get("website"),
        industry=data.get("industry"),
        description=data.get("description"),

        approval_status="pending",
        is_active=True
    )

    db.session.add(company)
    db.session.commit()

    return jsonify({
        "message": "Company registered successfully",
        "approval_status": "pending"
    }), 201
    
    
    
@auth_bp.route("/company/login", methods=["POST"])
def company_login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    company = Company.query.filter_by(
        email=email
    ).first()

    if not company:
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    if not check_password_hash(company.password_hash, password):
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    if not company.is_active:
        return jsonify({
            "message": "Company account is inactive"
        }), 403

    if company.approval_status != "approved":
        return jsonify({
            "message": "Company approval pending"
        }), 403

    access_token = create_access_token(
        identity=str(company.id),
        additional_claims={
            "role": "company"
        }
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "role": "company"
    }), 200
    
    
    
    
# --------------------- TEST ROUTE ------------------
@auth_bp.route("/admin/profile")
@admin_required
def admin_profile():
    
    return jsonify({
        "message": "Welcome Admin"
    })
    

@auth_bp.route("/student/profile")
@student_required
def student_profile():

    return jsonify({
        "message": "Welcome Student"
    })
    
    
@auth_bp.route("/company/profile")
@company_required
def company_profile():

    return jsonify({
        "message": "Welcome Company"
    })


# -------------- Admin: Company Approval -------------

@auth_bp.route("/admin/companies", methods=["GET"])
@admin_required
def admin_list_companies():
    status = request.args.get("status")
    
    query = Company.query
    if status:
        query = query.filter_by(approval_status=status)
    
    companies = query.order_by(Company.created_at.desc()).all()
    
    result = []
    for company in companies:
        result.append({
            "id": company.id,
            "name": company.name,
            "email": company.email,
            "hr_contact": company.hr_contact,
            "website": company.website,
            "industry": company.industry,
            "description": company.description,
            "status": company.approval_status,
            "is_active": company.is_active,
            "created_at": company.created_at.strftime("%Y-%m-%d %H:%M:%S") if company.created_at else None
        })
    
    return jsonify(result), 200


@auth_bp.route("/admin/companies/<int:company_id>", methods=["PATCH"])
@admin_required
def admin_update_company_status(company_id):
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"message": "Company not found"}), 404
    
    data = request.get_json()
    if not data or "approval_status" not in data:
        return jsonify({"message": "Missing approval_status in request body"}), 400
    
    new_status = data["approval_status"]
    if new_status not in ["approved", "rejected"]:
        return jsonify({"message": "Invalid status. Must be 'approved' or 'rejected'"}), 400
    
    company.approval_status = new_status
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while updating company status"}), 500
    
    return jsonify({
        "message": f"Company status updated to '{new_status}' successfully",
        "company": {
            "id": company.id,
            "name": company.name,
            "status": company.approval_status
        }
    }), 200


# -------------- Admin: Dashboard Stats -------------

@auth_bp.route("/admin/dashboard", methods=["GET"])
@admin_required
def admin_dashboard_stats():
    total_students = db.session.scalar(select(func.count()).select_from(Student))
    total_companies = db.session.scalar(select(func.count()).select_from(Company))
    approved_companies = db.session.scalar(select(func.count()).select_from(Company).filter_by(approval_status="approved"))
    pending_companies = db.session.scalar(select(func.count()).select_from(Company).filter_by(approval_status="pending"))
    total_drives = db.session.scalar(select(func.count()).select_from(PlacementDrive))
    approved_drives = db.session.scalar(select(func.count()).select_from(PlacementDrive).filter_by(status="approved"))
    pending_drives = db.session.scalar(select(func.count()).select_from(PlacementDrive).filter_by(status="pending"))
    total_applications = db.session.scalar(select(func.count()).select_from(Application))
    selected_students = db.session.scalar(select(func.count()).select_from(Application).filter_by(result="selected"))
    
    return jsonify({
        "total_students": total_students or 0,
        "total_companies": total_companies or 0,
        "approved_companies": approved_companies or 0,
        "pending_companies": pending_companies or 0,
        "total_drives": total_drives or 0,
        "approved_drives": approved_drives or 0,
        "pending_drives": pending_drives or 0,
        "total_applications": total_applications or 0,
        "selected_students": selected_students or 0
    }), 200