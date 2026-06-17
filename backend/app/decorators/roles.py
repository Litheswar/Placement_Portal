from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def admin_request(fn):
    
    @wraps(fn)
    def wrapper(*args, **kwargs):
        
        verify_jwt_in_request()
        claims = get_jwt()
        
        if claims.get("role") != "admin":
            return jsonify({
                "message": "Admin access required"
            }), 403
            
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

        return fn(*args, **kwargs)

    return wrapper