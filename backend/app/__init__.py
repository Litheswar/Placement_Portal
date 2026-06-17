from flask import Flask 

from config import Config
from extensions import db, migrate, jwt
from app.models import *
from app.routes.auth import auth_bp


def create_app():
    app = Flask(__name__)
    
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    app.register_blueprint(auth_bp)
    
    
    @app.route("/")
    def home():
        return {
            "message": "Placement Portal Backend Running"
        }
        
    return app

