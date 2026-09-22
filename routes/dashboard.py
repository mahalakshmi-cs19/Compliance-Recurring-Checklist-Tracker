from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import db
from models.checklist import ChecklistTemplate
from models.task import TaskInstance
from models.audit_log import AuditLog
from services.recurrence import ensure_recurring_tasks

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def root():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

@dashboard_bp.route('/dashboard')
@login_required
def index():
    # 1. Ensure current recurring cycles exist and evaluate overdue statuses
    ensure_recurring_tasks()

    today = date.today()
    now = datetime.utcnow()

    # 2. KPI Metrics
    total_templates = ChecklistTemplate.query.filter_by(is_active=True).count()

    pending_tasks = TaskInstance.query.filter_by(status=TaskInstance.STATUS_PENDING).all()
    overdue_tasks = TaskInstance.query.filter_by(status=TaskInstance.STATUS_OVERDUE).all()
    completed_tasks = TaskInstance.query.filter_by(status=TaskInstance.STATUS_COMPLETED).all()

    total_tracked = len(pending_tasks) + len(overdue_tasks) + len(completed_tasks)
    
    # Compliance Rate: Completed / (Completed + Overdue)
    evaluated_count = len(completed_tasks) + len(overdue_tasks)
    compliance_rate = (len(completed_tasks) / evaluated_count * 100) if evaluated_count > 0 else 100.0

    # 3. Actionable lists
    # Overdue tasks (sorted by due_datetime ascending - most urgent first)
    urgent_overdue = TaskInstance.query.filter_by(
        status=TaskInstance.STATUS_OVERDUE
    ).order_by(TaskInstance.due_datetime.asc()).limit(10).all()

    # Upcoming / Pending tasks due today or soon
    upcoming_tasks = TaskInstance.query.filter_by(
        status=TaskInstance.STATUS_PENDING
    ).order_by(TaskInstance.due_datetime.asc()).limit(8).all()

    # Recent completed tasks
    recent_completed = TaskInstance.query.filter_by(
        status=TaskInstance.STATUS_COMPLETED
    ).order_by(TaskInstance.completed_at.desc()).limit(5).all()

    # Recent Audit Log Activity
    recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(6).all()

    return render_template(
        'dashboard/index.html',
        total_templates=total_templates,
        pending_count=len(pending_tasks),
        overdue_count=len(overdue_tasks),
        completed_count=len(completed_tasks),
        compliance_rate=round(compliance_rate, 1),
        urgent_overdue=urgent_overdue,
        upcoming_tasks=upcoming_tasks,
        recent_completed=recent_completed,
        recent_logs=recent_logs
    )
