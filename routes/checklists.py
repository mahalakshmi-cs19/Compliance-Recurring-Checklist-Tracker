from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.checklist import ChecklistTemplate
from models.user import User
from services.audit_service import log_audit_event
from services.recurrence import ensure_recurring_tasks

checklists_bp = Blueprint('checklists', __name__, url_prefix='/checklists')

@checklists_bp.route('/', strict_slashes=False)
@login_required
def list_checklists():
    category = request.args.get('category')
    frequency = request.args.get('frequency')
    status = request.args.get('status')  # 'active', 'inactive', 'all'

    query = ChecklistTemplate.query

    if category:
        query = query.filter_by(category=category)
    if frequency:
        query = query.filter_by(frequency=frequency)
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)

    templates = query.order_by(ChecklistTemplate.created_at.desc()).all()
    users = User.query.filter_by(is_active=True).all()

    return render_template(
        'checklists/list.html',
        templates=templates,
        categories=ChecklistTemplate.CATEGORIES,
        frequencies=ChecklistTemplate.FREQUENCIES,
        selected_category=category,
        selected_frequency=frequency,
        selected_status=status
    )


@checklists_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.can_manage_checklists:
        flash('Permission denied. Only Administrators can create checklist templates.', 'danger')
        return redirect(url_for('checklists.list_checklists'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'General')
        frequency = request.form.get('frequency', ChecklistTemplate.FREQ_DAILY)
        due_hour = int(request.form.get('due_time_hour', 17))
        assigned_user_id = request.form.get('assigned_user_id') or None

        if not title:
            flash('Checklist title is required.', 'warning')
        else:
            tmpl = ChecklistTemplate(
                title=title,
                description=description,
                category=category,
                frequency=frequency,
                due_time_hour=due_hour,
                assigned_user_id=int(assigned_user_id) if assigned_user_id else None,
                created_by_id=current_user.id
            )
            db.session.add(tmpl)
            db.session.commit()

            # Generate initial task instance right away
            ensure_recurring_tasks()

            log_audit_event(
                'CHECKLIST_CREATED',
                'TEMPLATE',
                tmpl.id,
                f"Checklist template '{tmpl.title}' ({tmpl.frequency}) created by {current_user.username}."
            )
            flash(f"Checklist '{tmpl.title}' created and initial recurring task generated.", 'success')
            return redirect(url_for('checklists.list_checklists'))

    operators = User.query.filter(User.role.in_([User.ROLE_OPERATOR, User.ROLE_ADMIN]), User.is_active == True).all()
    return render_template(
        'checklists/form.html',
        template=None,
        categories=ChecklistTemplate.CATEGORIES,
        frequencies=ChecklistTemplate.FREQUENCIES,
        operators=operators
    )


@checklists_bp.route('/<int:template_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(template_id):
    if not current_user.can_manage_checklists:
        flash('Permission denied. Only Administrators can edit checklist templates.', 'danger')
        return redirect(url_for('checklists.list_checklists'))

    tmpl = ChecklistTemplate.query.get_or_404(template_id)

    if request.method == 'POST':
        tmpl.title = request.form.get('title', '').strip()
        tmpl.description = request.form.get('description', '').strip()
        tmpl.category = request.form.get('category', tmpl.category)
        tmpl.frequency = request.form.get('frequency', tmpl.frequency)
        tmpl.due_time_hour = int(request.form.get('due_time_hour', tmpl.due_time_hour))
        assigned_id = request.form.get('assigned_user_id')
        tmpl.assigned_user_id = int(assigned_id) if assigned_id else None

        db.session.commit()

        log_audit_event(
            'CHECKLIST_UPDATED',
            'TEMPLATE',
            tmpl.id,
            f"Checklist template '{tmpl.title}' updated by {current_user.username}."
        )
        flash(f"Checklist '{tmpl.title}' updated successfully.", 'success')
        return redirect(url_for('checklists.list_checklists'))

    operators = User.query.filter(User.role.in_([User.ROLE_OPERATOR, User.ROLE_ADMIN]), User.is_active == True).all()
    return render_template(
        'checklists/form.html',
        template=tmpl,
        categories=ChecklistTemplate.CATEGORIES,
        frequencies=ChecklistTemplate.FREQUENCIES,
        operators=operators
    )


@checklists_bp.route('/<int:template_id>/toggle-status', methods=['POST'])
@login_required
def toggle_status(template_id):
    if not current_user.can_manage_checklists:
        flash('Permission denied. Only Administrators can toggle checklist status.', 'danger')
        return redirect(url_for('checklists.list_checklists'))

    tmpl = ChecklistTemplate.query.get_or_404(template_id)
    tmpl.is_active = not tmpl.is_active
    db.session.commit()

    action_label = "activated" if tmpl.is_active else "deactivated"
    log_audit_event(
        'CHECKLIST_STATUS_CHANGED',
        'TEMPLATE',
        tmpl.id,
        f"Checklist template '{tmpl.title}' was {action_label} by {current_user.username}."
    )
    flash(f"Checklist '{tmpl.title}' is now {action_label}.", 'info')
    return redirect(url_for('checklists.list_checklists'))
