from flask import Flask 

from config import Config
from extensions import db, migrate

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(Config)
    
    db.__init__app(app)
    migrate.init_app(app, db)
    
    @app.route("/")
    def home():
        return {
            "message": "Placement Portal Backend Running"
        }
        
    return app

