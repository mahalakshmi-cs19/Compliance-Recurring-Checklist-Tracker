from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db
from models.audit_log import AuditLog
from models.user import User

audit_bp = Blueprint('audit', __name__, url_prefix='/audit')

@audit_bp.route('/', strict_slashes=False)
@login_required
def index():
    if not current_user.can_view_audit:
        flash('Permission denied. Access restricted to Administrators and Auditors.', 'danger')
        return redirect(url_for('dashboard.index'))

    action_filter = request.args.get('action')
    entity_filter = request.args.get('entity_type')
    search_query = request.args.get('q', '').strip()

    query = AuditLog.query.outerjoin(User, AuditLog.user_id == User.id)

    if action_filter:
        query = query.filter(AuditLog.action == action_filter)

    if entity_filter:
        query = query.filter(AuditLog.entity_type == entity_filter)

    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            (AuditLog.details.ilike(search_pattern)) |
            (User.username.ilike(search_pattern)) |
            (User.full_name.ilike(search_pattern))
        )

    logs = query.order_by(AuditLog.timestamp.desc()).limit(200).all()

    # Collect distinct actions and entities for filter dropdowns
    actions = [a[0] for a in db.session.query(AuditLog.action.distinct()).all()]
    entity_types = [e[0] for e in db.session.query(AuditLog.entity_type.distinct()).all()]

    return render_template(
        'audit/index.html',
        logs=logs,
        actions=actions,
        entity_types=entity_types,
        selected_action=action_filter,
        selected_entity=entity_filter,
        search_query=search_query
    )
