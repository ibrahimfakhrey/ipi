"""
Main application initialization file
Sets up Flask app, database, login manager, scheduler, JWT, and CORS
"""
from flask import Flask
from flask_login import LoginManager
from flask_apscheduler import APScheduler
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import config
from app.models import db, User
import os


# Initialize login manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'

# Initialize scheduler
scheduler = APScheduler()

# Initialize JWT manager
jwt = JWTManager()


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))


def create_app(config_name='default'):
    """
    Application factory function
    Creates and configures the Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    scheduler.init_app(app)
    jwt.init_app(app)
    
    # Enable CORS for API endpoints
    # Enable CORS for all routes including static files
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from app.routes import auth, main, admin, user_views, api
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(user_views.bp)
    app.register_blueprint(api.api_bp)  # Register API blueprint
    
    # Create database tables
    with app.app_context():
        db.create_all()
        create_admin_user(app)
    
    # Start scheduler for monthly payouts (only in development mode)
    # Skip scheduler in production/PythonAnywhere to avoid threading issues
    if app.config.get('SCHEDULER_ENABLED', False) and not scheduler.running:
        try:
            scheduler.start()
        except RuntimeError as e:
            # Scheduler not available in this environment (e.g., PythonAnywhere)
            app.logger.warning(f"Scheduler not started: {e}")
    
    return app


def create_admin_user(app):
    """Create default admin user if it doesn't exist"""
    from app.models import User
    
    admin = User.query.filter_by(email=app.config['ADMIN_EMAIL']).first()
    if not admin:
        admin = User(
            name='Admin',
            email=app.config['ADMIN_EMAIL'],
            is_admin=True
        )
        admin.set_password(app.config['ADMIN_PASSWORD'])
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user created: {app.config['ADMIN_EMAIL']}")


def schedule_monthly_payouts():
    """
    Scheduled task to distribute monthly rent to all investors
    Runs on the 1st day of each month at 00:00
    """
    from app.models import Apartment
    from datetime import datetime
    
    apartments = Apartment.query.filter_by(is_closed=True).all()
    total_payouts = 0
    
    for apartment in apartments:
        payouts = apartment.distribute_monthly_rent()
        total_payouts += payouts
    
    db.session.commit()
    print(f"Monthly payouts completed: {total_payouts} payments processed at {datetime.utcnow()}")


# Register scheduled tasks
@scheduler.task('cron', id='monthly_rent_distribution', day=1, hour=0, minute=0)
def scheduled_rent_distribution():
    """Monthly rent distribution task"""
    schedule_monthly_payouts()
