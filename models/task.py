from datetime import datetime
from models import db

class TaskInstance(db.Model):
    __tablename__ = 'task_instances'

    STATUS_PENDING = 'PENDING'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_OVERDUE = 'OVERDUE'
    STATUSES = [STATUS_PENDING, STATUS_COMPLETED, STATUS_OVERDUE]

    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('checklist_templates.id'), nullable=False)
    cycle_date = db.Column(db.Date, nullable=False, index=True)
    due_datetime = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default=STATUS_PENDING)
    completed_at = db.Column(db.DateTime, nullable=True)
    completed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to photo/file evidence
    evidences = db.relationship('TaskEvidence', backref='task', lazy=True, cascade='all, delete-orphan')

    @property
    def is_past_due(self):
        """Returns True if task is not completed and past its due date."""
        return self.status != self.STATUS_COMPLETED and datetime.utcnow() > self.due_datetime

    @property
    def effective_status(self):
        """Dynamic calculation: If pending and past due, treat as OVERDUE."""
        if self.status == self.STATUS_COMPLETED:
            return self.STATUS_COMPLETED
        if datetime.utcnow() > self.due_datetime:
            return self.STATUS_OVERDUE
        return self.STATUS_PENDING

    def mark_completed(self, user_id, notes=None):
        self.status = self.STATUS_COMPLETED
        self.completed_at = datetime.utcnow()
        self.completed_by_id = user_id
        if notes:
            self.notes = notes

    def __repr__(self):
        return f'<TaskInstance {self.id} Template={self.template_id} Status={self.status}>'
