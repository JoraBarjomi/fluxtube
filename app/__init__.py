from flask import Flask
from config import Config
from .extensions import db, migrate, login
from .filters import number_format, time_ago 
from flask_wtf.csrf import CSRFProtect

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024
    
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf = CSRFProtect(app) 
    
    app.jinja_env.filters['number_format'] = number_format 
    app.jinja_env.filters['time_ago'] = time_ago

    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app