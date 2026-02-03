from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Import here so models are registered before user_loader is defined
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id: str):
        """Flask-Login callback to reload the user object from the user ID."""
        try:
            return User.query.get(int(user_id))
        except (TypeError, ValueError):
            return None

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.patient import patient_bp
    from app.routes.doctor import doctor_bp
    from app.routes.admin import admin_bp
    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Create tables
    with app.app_context():
        db.create_all()
        # Create default admin user if not exists
        from werkzeug.security import generate_password_hash
        if not User.query.filter_by(email='admin@hospital.com').first():
            admin = User(
                name='Admin',
                email='admin@hospital.com',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()

    return app
