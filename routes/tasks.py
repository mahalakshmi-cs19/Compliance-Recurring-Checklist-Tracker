import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db
from models.checklist import ChecklistTemplate
from models.task import TaskInstance
from models.evidence import TaskEvidence
from models.audit_log import AuditLog
from services.audit_service import log_audit_event
from services.recurrence import ensure_recurring_tasks

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

def allowed_file(filename):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']

@tasks_bp.route('/', strict_slashes=False)
@login_required
def list_tasks():
    ensure_recurring_tasks()

    status_filter = request.args.get('status', 'all')
    category_filter = request.args.get('category')
    frequency_filter = request.args.get('frequency')

    query = TaskInstance.query.join(ChecklistTemplate)

    if status_filter == 'pending':
        query = query.filter(TaskInstance.status == TaskInstance.STATUS_PENDING)
    elif status_filter == 'overdue':
        query = query.filter(TaskInstance.status == TaskInstance.STATUS_OVERDUE)
    elif status_filter == 'completed':
        query = query.filter(TaskInstance.status == TaskInstance.STATUS_COMPLETED)

    if category_filter:
        query = query.filter(ChecklistTemplate.category == category_filter)
    if frequency_filter:
        query = query.filter(ChecklistTemplate.frequency == frequency_filter)

    # Order overdue tasks first, then pending by due date, then completed
    tasks = query.order_by(
        (TaskInstance.status == TaskInstance.STATUS_OVERDUE).desc(),
        TaskInstance.due_datetime.asc()
    ).all()

    # Pre-calculate counts for tab badges
    pending_count = TaskInstance.query.filter_by(status=TaskInstance.STATUS_PENDING).count()
    overdue_count = TaskInstance.query.filter_by(status=TaskInstance.STATUS_OVERDUE).count()
    completed_count = TaskInstance.query.filter_by(status=TaskInstance.STATUS_COMPLETED).count()

    return render_template(
        'tasks/list.html',
        tasks=tasks,
        selected_status=status_filter,
        selected_category=category_filter,
        selected_frequency=frequency_filter,
        categories=ChecklistTemplate.CATEGORIES,
        frequencies=ChecklistTemplate.FREQUENCIES,
        pending_count=pending_count,
        overdue_count=overdue_count,
        completed_count=completed_count,
        total_count=pending_count + overdue_count + completed_count
    )


@tasks_bp.route('/<int:task_id>')
@login_required
def detail(task_id):
    ensure_recurring_tasks()
    task = TaskInstance.query.get_or_404(task_id)
    history_logs = AuditLog.query.filter_by(
        entity_type='TASK',
        entity_id=task.id
    ).order_by(AuditLog.timestamp.desc()).all()

    return render_template('tasks/detail.html', task=task, history_logs=history_logs)


@tasks_bp.route('/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    if not current_user.can_complete_tasks:
        flash('Permission denied. Auditors have read-only access.', 'danger')
        return redirect(url_for('tasks.list_tasks'))

    task = TaskInstance.query.get_or_404(task_id)

    if task.status == TaskInstance.STATUS_COMPLETED:
        flash('This task has already been completed.', 'warning')
        return redirect(url_for('tasks.detail', task_id=task.id))

    notes = request.form.get('notes', '').strip()
    task.mark_completed(user_id=current_user.id, notes=notes)

    # Handle Photo Evidence Upload
    uploaded_files = request.files.getlist('photo_evidence')
    saved_evidence_count = 0

    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)

    for file in uploaded_files:
        if file and file.filename != '':
            if allowed_file(file.filename):
                original_name = secure_filename(file.filename)
                ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else 'jpg'
                unique_filename = f"{uuid.uuid4().hex[:12]}_{int(datetime.utcnow().timestamp())}.{ext}"
                file_path = os.path.join(upload_folder, unique_filename)
                
                file.save(file_path)
                file_size = os.path.getsize(file_path)

                evidence = TaskEvidence(
                    task_id=task.id,
                    filename=unique_filename,
                    original_filename=original_name,
                    file_size_bytes=file_size,
                    uploaded_by_id=current_user.id
                )
                db.session.add(evidence)
                saved_evidence_count += 1
            else:
                flash(f"File '{file.filename}' was skipped: only JPG, PNG, and WEBP image formats are allowed.", 'warning')

    db.session.commit()

    log_audit_event(
        'TASK_COMPLETED',
        'TASK',
        task.id,
        f"Task #{task.id} ('{task.template.title}') completed by {current_user.full_name}. Attached {saved_evidence_count} evidence photo(s)."
    )

    flash(f"Task #{task.id} marked as completed successfully!", 'success')
    return redirect(url_for('tasks.detail', task_id=task.id))
