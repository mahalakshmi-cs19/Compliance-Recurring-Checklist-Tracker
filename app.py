import os
from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db
from models.user import User

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.checklists import checklists_bp
    from routes.tasks import tasks_bp
    from routes.reports import reports_bp
    from routes.audit import audit_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(checklists_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(audit_bp)

    # Custom Jinja Template Filters
    @app.template_filter('format_datetime')
    def format_datetime(value, fmt='%b %d, %Y %I:%M %p'):
        if value is None:
            return '-'
        return value.strftime(fmt)

    @app.template_filter('format_date')
    def format_date(value, fmt='%b %d, %Y'):
        if value is None:
            return '-'
        return value.strftime(fmt)

    @app.template_filter('status_badge_class')
    def status_badge_class(status):
        mapping = {
            'COMPLETED': 'bg-success',
            'PENDING': 'bg-warning text-dark',
            'OVERDUE': 'bg-danger'
        }
        return mapping.get(status, 'bg-secondary')

    # Ensure upload directory exists and create tables
    with app.app_context():
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    print("==================================================================")
    print("  Compliance & Recurring Checklist Tracker Starting...")
    print("  Local Server: http://127.0.0.1:5000")
    print("==================================================================")
    app.run(debug=True, port=5000)
