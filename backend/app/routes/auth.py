from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db

from app.models.admin import Admin
from app.models.student import Student
from app.models.company import Company

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