from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    ROLE_ADMIN = 'ADMIN'
    ROLE_OPERATOR = 'OPERATOR'
    ROLE_AUDITOR = 'AUDITOR'
    ROLES = [ROLE_ADMIN, ROLE_OPERATOR, ROLE_AUDITOR]

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_OPERATOR)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    created_templates = db.relationship('ChecklistTemplate', backref='creator', lazy=True, foreign_keys='ChecklistTemplate.created_by_id')
    completed_tasks = db.relationship('TaskInstance', backref='completer', lazy=True, foreign_keys='TaskInstance.completed_by_id')
    uploaded_evidences = db.relationship('TaskEvidence', backref='uploader', lazy=True, foreign_keys='TaskEvidence.uploaded_by_id')
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True, foreign_keys='AuditLog.user_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_operator(self):
        return self.role == self.ROLE_OPERATOR

    @property
    def is_auditor(self):
        return self.role == self.ROLE_AUDITOR

    @property
    def can_manage_checklists(self):
        return self.is_admin

    @property
    def can_complete_tasks(self):
        return self.is_admin or self.is_operator

    @property
    def can_view_audit(self):
        return self.is_admin or self.is_auditor

    @property
    def can_manage_users(self):
        return self.is_admin

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
