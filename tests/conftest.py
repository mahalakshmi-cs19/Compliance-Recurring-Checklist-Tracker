import os
import pytest
from app import create_app
from models import db
from models.user import User
from models.checklist import ChecklistTemplate
from models.task import TaskInstance

class TestConfig:
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    WTF_CSRF_ENABLED = False

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_users(app):
    with app.app_context():
        admin = User(username='admin_test', email='admin@test.local', full_name='Admin User', role=User.ROLE_ADMIN)
        admin.set_password('pass123')

        operator = User(username='operator_test', email='op@test.local', full_name='Operator User', role=User.ROLE_OPERATOR)
        operator.set_password('pass123')

        auditor = User(username='auditor_test', email='audit@test.local', full_name='Auditor User', role=User.ROLE_AUDITOR)
        auditor.set_password('pass123')

        db.session.add_all([admin, operator, auditor])
        db.session.commit()

        return {
            'admin_id': admin.id,
            'operator_id': operator.id,
            'auditor_id': auditor.id
        }

@pytest.fixture
def auth_client(client):
    """Helper to log in as specific user."""
    def _login(username, password='pass123'):
        return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)
    return _login
