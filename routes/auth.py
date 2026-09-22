from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User
from services.audit_service import log_audit_event

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact an administrator.', 'danger')
                return render_template('auth/login.html')

            login_user(user)
            log_audit_event('USER_LOGIN', 'USER', user.id, f"User '{user.username}' logged in successfully.")
            flash(f'Welcome back, {user.full_name}!', 'success')

            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Invalid username/email or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    log_audit_event('USER_LOGOUT', 'USER', current_user.id, f"User '{current_user.username}' logged out.")
    logout_user()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/users', methods=['GET', 'POST'])
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Access denied. Administrator privileges required.', 'danger')
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', User.ROLE_OPERATOR)

        # Validation
        if not username or not email or not password or not full_name:
            flash('All fields are required to create a user account.', 'warning')
        elif User.query.filter_by(username=username).first():
            flash('A user with that username already exists.', 'warning')
        elif User.query.filter_by(email=email).first():
            flash('A user with that email already exists.', 'warning')
        elif role not in User.ROLES:
            flash('Invalid role selected.', 'danger')
        else:
            new_user = User(
                username=username,
                email=email,
                full_name=full_name,
                role=role
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            log_audit_event(
                'USER_CREATED',
                'USER',
                new_user.id,
                f"Admin '{current_user.username}' created user '{new_user.username}' with role '{new_user.role}'."
            )
            flash(f"User account '{new_user.username}' created successfully.", 'success')
            return redirect(url_for('auth.manage_users'))

    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('auth/users.html', users=users, roles=User.ROLES)


@auth_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    if not current_user.is_admin:
        flash('Access denied. Administrator privileges required.', 'danger')
        return redirect(url_for('dashboard.index'))

    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'warning')
        return redirect(url_for('auth.manage_users'))

    user.is_active = not user.is_active
    db.session.commit()

    status_str = "activated" if user.is_active else "deactivated"
    log_audit_event(
        'USER_STATUS_UPDATED',
        'USER',
        user.id,
        f"Admin '{current_user.username}' {status_str} user '{user.username}'."
    )
    flash(f"User '{user.username}' has been {status_str}.", 'info')
    return redirect(url_for('auth.manage_users'))
