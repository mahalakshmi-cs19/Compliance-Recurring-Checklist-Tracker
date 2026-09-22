from datetime import datetime, date
from flask import Blueprint, render_template, request, Response, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db
from models.checklist import ChecklistTemplate
from models.task import TaskInstance
from services.recurrence import ensure_recurring_tasks
from services.report_service import generate_csv_report, generate_pdf_report
from services.audit_service import log_audit_event

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

def get_filtered_tasks(args):
    ensure_recurring_tasks()

    query = TaskInstance.query.join(ChecklistTemplate)

    status = args.get('status')
    category = args.get('category')
    frequency = args.get('frequency')
    start_date_str = args.get('start_date')
    end_date_str = args.get('end_date')

    if status and status != 'ALL':
        query = query.filter(TaskInstance.status == status)

    if category and category != 'ALL':
        query = query.filter(ChecklistTemplate.category == category)

    if frequency and frequency != 'ALL':
        query = query.filter(ChecklistTemplate.frequency == frequency)

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(TaskInstance.cycle_date >= start_date)
        except ValueError:
            pass

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(TaskInstance.cycle_date <= end_date)
        except ValueError:
            pass

    return query.order_by(TaskInstance.due_datetime.desc()).all()


@reports_bp.route('/', strict_slashes=False)
@login_required
def index():
    tasks = get_filtered_tasks(request.args)

    total = len(tasks)
    completed = sum(1 for t in tasks if t.effective_status == TaskInstance.STATUS_COMPLETED)
    overdue = sum(1 for t in tasks if t.effective_status == TaskInstance.STATUS_OVERDUE)
    pending = sum(1 for t in tasks if t.effective_status == TaskInstance.STATUS_PENDING)
    compliance_rate = (completed / (completed + overdue) * 100) if (completed + overdue) > 0 else 100.0

    summary_stats = {
        'total': total,
        'completed': completed,
        'overdue': overdue,
        'pending': pending,
        'compliance_rate': round(compliance_rate, 1)
    }

    return render_template(
        'reports/index.html',
        tasks=tasks,
        summary_stats=summary_stats,
        categories=ChecklistTemplate.CATEGORIES,
        frequencies=ChecklistTemplate.FREQUENCIES,
        statuses=TaskInstance.STATUSES,
        selected_status=request.args.get('status', 'ALL'),
        selected_category=request.args.get('category', 'ALL'),
        selected_frequency=request.args.get('frequency', 'ALL'),
        start_date=request.args.get('start_date', ''),
        end_date=request.args.get('end_date', '')
    )


@reports_bp.route('/export/csv')
@login_required
def export_csv():
    tasks = get_filtered_tasks(request.args)
    csv_content = generate_csv_report(tasks)

    log_audit_event(
        'REPORT_GENERATED',
        'REPORT',
        details=f"User {current_user.username} generated CSV compliance report with {len(tasks)} records."
    )

    timestamp_str = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"compliance_report_{timestamp_str}.csv"

    return Response(
        csv_content,
        mimetype='text/csv',
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


@reports_bp.route('/export/pdf')
@login_required
def export_pdf():
    tasks = get_filtered_tasks(request.args)

    total = len(tasks)
    completed = sum(1 for t in tasks if t.effective_status == TaskInstance.STATUS_COMPLETED)
    overdue = sum(1 for t in tasks if t.effective_status == TaskInstance.STATUS_OVERDUE)
    pending = sum(1 for t in tasks if t.effective_status == TaskInstance.STATUS_PENDING)
    compliance_rate = (completed / (completed + overdue) * 100) if (completed + overdue) > 0 else 100.0

    summary_stats = {
        'total': total,
        'completed': completed,
        'overdue': overdue,
        'pending': pending,
        'compliance_rate': compliance_rate
    }

    pdf_buffer = generate_pdf_report(
        tasks,
        summary_stats,
        generated_by_name=f"{current_user.full_name} ({current_user.role})"
    )

    log_audit_event(
        'REPORT_GENERATED',
        'REPORT',
        details=f"User {current_user.username} generated official PDF compliance report with {len(tasks)} records."
    )

    timestamp_str = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"compliance_audit_report_{timestamp_str}.pdf"

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )
