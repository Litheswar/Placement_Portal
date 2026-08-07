from app import create_app
from extensions import db
from app.models.admin import Admin

from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()
    
    admin = Admin.query.filter_by(
        email="admin@placement.com"
    ).first()
    
    if not admin:
        admin = Admin(
            name="Placement Admin",
            email="admin@placement.com",
            password_hash=generate_password_hash("admin123")
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print("Admin account created successfully")
        
    else:
        print("Admin already exists")