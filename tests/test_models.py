from datetime import datetime, date, timedelta
from models import db
from models.user import User
from models.checklist import ChecklistTemplate
from models.task import TaskInstance
from models.evidence import TaskEvidence
from models.audit_log import AuditLog

def test_user_creation_and_password_hashing(app):
    with app.app_context():
        user = User(username='johndoe', email='john@example.com', full_name='John Doe', role=User.ROLE_OPERATOR)
        user.set_password('mysecret')
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.check_password('mysecret') is True
        assert user.check_password('wrongpass') is False
        assert user.is_operator is True
        assert user.is_admin is False
        assert user.can_complete_tasks is True
        assert user.can_manage_checklists is False

def test_task_instance_effective_status(app, test_users):
    with app.app_context():
        tmpl = ChecklistTemplate(
            title='Daily Pump Check',
            category='Equipment & Machinery',
            frequency=ChecklistTemplate.FREQ_DAILY,
            created_by_id=test_users['admin_id']
        )
        db.session.add(tmpl)
        db.session.commit()

        # Task in future -> PENDING
        future_due = datetime.utcnow() + timedelta(hours=5)
        task_pending = TaskInstance(
            template_id=tmpl.id,
            cycle_date=date.today(),
            due_datetime=future_due,
            status=TaskInstance.STATUS_PENDING
        )

        # Task in past -> OVERDUE
        past_due = datetime.utcnow() - timedelta(hours=2)
        task_overdue = TaskInstance(
            template_id=tmpl.id,
            cycle_date=date.today() - timedelta(days=1),
            due_datetime=past_due,
            status=TaskInstance.STATUS_PENDING
        )

        # Completed task in past -> COMPLETED
        task_completed = TaskInstance(
            template_id=tmpl.id,
            cycle_date=date.today() - timedelta(days=2),
            due_datetime=past_due,
            status=TaskInstance.STATUS_COMPLETED
        )

        db.session.add_all([task_pending, task_overdue, task_completed])
        db.session.commit()

        assert task_pending.effective_status == TaskInstance.STATUS_PENDING
        assert task_overdue.effective_status == TaskInstance.STATUS_OVERDUE
        assert task_completed.effective_status == TaskInstance.STATUS_COMPLETED
