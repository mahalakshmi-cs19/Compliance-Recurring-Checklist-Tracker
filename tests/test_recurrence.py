from datetime import date, timedelta
from models import db
from models.checklist import ChecklistTemplate
from models.task import TaskInstance
from services.recurrence import get_current_cycle_info, ensure_recurring_tasks

def test_cycle_date_calculations():
    test_date = date(2026, 9, 20)  # Sunday

    # Daily: same date
    d_cycle, d_due = get_current_cycle_info(ChecklistTemplate.FREQ_DAILY, test_date, due_hour=17)
    assert d_cycle == test_date
    assert d_due.hour == 17

    # Weekly: Monday of current week
    w_cycle, w_due = get_current_cycle_info(ChecklistTemplate.FREQ_WEEKLY, test_date)
    assert w_cycle.weekday() == 0  # Monday
    assert w_due.weekday() == 6    # Sunday end of week

    # Monthly: 1st of month
    m_cycle, m_due = get_current_cycle_info(ChecklistTemplate.FREQ_MONTHLY, test_date)
    assert m_cycle == date(2026, 9, 1)
    assert m_due.day == 30         # September has 30 days

def test_ensure_recurring_tasks_creates_instances(app, test_users):
    with app.app_context():
        # Create 1 daily, 1 weekly, 1 monthly template
        t1 = ChecklistTemplate(title='Daily Test', category='Safety & Emergency', frequency=ChecklistTemplate.FREQ_DAILY, created_by_id=test_users['admin_id'])
        t2 = ChecklistTemplate(title='Weekly Test', category='Fire Protection', frequency=ChecklistTemplate.FREQ_WEEKLY, created_by_id=test_users['admin_id'])
        t3 = ChecklistTemplate(title='Inactive Monthly', category='General', frequency=ChecklistTemplate.FREQ_MONTHLY, is_active=False, created_by_id=test_users['admin_id'])

        db.session.add_all([t1, t2, t3])
        db.session.commit()

        # First run: should create 2 tasks (for active templates t1 and t2)
        created, _ = ensure_recurring_tasks()
        assert created == 2

        all_tasks = TaskInstance.query.all()
        assert len(all_tasks) == 2

        # Second run: should create 0 tasks (idempotent, no duplicates)
        created_second, _ = ensure_recurring_tasks()
        assert created_second == 0
        assert TaskInstance.query.count() == 2
