from flask import request, has_request_context
from flask_login import current_user
from models import db
from models.audit_log import AuditLog

def log_audit_event(action, entity_type, entity_id=None, details=None, user_id=None, ip_address=None):
    """
    Central helper to record immutable audit events across the application.
    Automatically captures current_user and client IP if available in request context.
    """
    if user_id is None and has_request_context():
        if current_user and current_user.is_authenticated:
            user_id = current_user.id

    if ip_address is None and has_request_context():
        ip_address = request.remote_addr

    log_entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address
    )
    db.session.add(log_entry)
    db.session.commit()
    return log_entry
