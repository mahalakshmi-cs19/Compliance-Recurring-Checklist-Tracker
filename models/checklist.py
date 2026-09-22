from datetime import datetime
from models import db

class ChecklistTemplate(db.Model):
    __tablename__ = 'checklist_templates'

    FREQ_DAILY = 'DAILY'
    FREQ_WEEKLY = 'WEEKLY'
    FREQ_MONTHLY = 'MONTHLY'
    FREQUENCIES = [FREQ_DAILY, FREQ_WEEKLY, FREQ_MONTHLY]

    CATEGORIES = [
        'Safety & Emergency',
        'Fire Protection',
        'Electrical Systems',
        'Equipment & Machinery',
        'Health & Sanitation',
        'Environmental Compliance',
        'General'
    ]

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False, default='General')
    frequency = db.Column(db.String(20), nullable=False, default=FREQ_DAILY)
    due_time_hour = db.Column(db.Integer, default=17)  # 17 = 5:00 PM
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    assigned_user = db.relationship('User', foreign_keys=[assigned_user_id], backref='assigned_templates')
    tasks = db.relationship('TaskInstance', backref='template', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ChecklistTemplate {self.title} ({self.frequency})>'
