from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity

def admin_required(fn):
    
    @wraps(fn)
    def wrapper(*args, **kwargs):
        
        verify_jwt_in_request()
        claims = get_jwt()
        
        if claims.get("role") != "admin":
            return jsonify({
                "message": "Admin access required"
            }), 403
            
        from app.models.admin import Admin
        admin_id = get_jwt_identity()
        admin = Admin.query.get(int(admin_id))
        if not admin:
            return jsonify({
                "message": "Admin account not found"
            }), 404
            
        return fn(*args, **kwargs)
    
    return wrapper



def student_required(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):

        verify_jwt_in_request()

        claims = get_jwt()

        if claims.get("role") != "student":

            return jsonify({
                "message": "Student access required"
            }), 403

        from app.models.student import Student
        student_id = get_jwt_identity()
        student = Student.query.get(int(student_id))

        if not student:
            return jsonify({
                "message": "Student account not found"
            }), 404

        if not student.is_active:
            return jsonify({
                "message": "Account is inactive"
            }), 403

        if student.is_blacklisted:
            return jsonify({
                "message": "Account is blacklisted"
            }), 403

        return fn(*args, **kwargs)

    return wrapper



def company_required(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):

        verify_jwt_in_request()

        claims = get_jwt()

        if claims.get("role") != "company":

            return jsonify({
                "message": "Company access required"
            }), 403

        from app.models.company import Company
        company_id = get_jwt_identity()
        company = Company.query.get(int(company_id))

        if not company:
            return jsonify({
                "message": "Company account not found"
            }), 404

        if not company.is_active:
            return jsonify({
                "message": "Company account is inactive"
            }), 403

        if company.approval_status != "approved":
            return jsonify({
                "message": "Company approval pending"
            }), 403

        return fn(*args, **kwargs)

    return wrapper