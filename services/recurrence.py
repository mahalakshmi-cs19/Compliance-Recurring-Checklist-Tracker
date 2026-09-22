from datetime import datetime, date, time, timedelta
import calendar
from models import db
from models.checklist import ChecklistTemplate
from models.task import TaskInstance

def get_current_cycle_info(frequency, target_date=None, due_hour=17):
    """
    Computes the cycle date (representative date) and due datetime for a given frequency.
    """
    if target_date is None:
        target_date = date.today()

    if frequency == ChecklistTemplate.FREQ_DAILY:
        cycle_date = target_date
        due_datetime = datetime.combine(target_date, time(hour=due_hour, minute=0, second=0))

    elif frequency == ChecklistTemplate.FREQ_WEEKLY:
        # Cycle date is Monday of current week
        cycle_date = target_date - timedelta(days=target_date.weekday())
        # Due on Sunday of the same week at 23:59:59
        sunday = cycle_date + timedelta(days=6)
        due_datetime = datetime.combine(sunday, time(hour=23, minute=59, second=59))

    elif frequency == ChecklistTemplate.FREQ_MONTHLY:
        # Cycle date is 1st of current month
        cycle_date = date(target_date.year, target_date.month, 1)
        # Due on the last day of the month
        _, last_day = calendar.monthrange(target_date.year, target_date.month)
        due_datetime = datetime.combine(date(target_date.year, target_date.month, last_day), time(hour=23, minute=59, second=59))

    else:
        # Default daily
        cycle_date = target_date
        due_datetime = datetime.combine(target_date, time(hour=due_hour, minute=0, second=0))

    return cycle_date, due_datetime

def ensure_recurring_tasks(target_date=None):
    """
    Scans all active checklist templates and ensures a TaskInstance exists
    for the current cycle (daily, weekly, monthly).
    Also updates any expired pending tasks to OVERDUE status.
    """
    if target_date is None:
        target_date = date.today()

    now = datetime.utcnow()
    active_templates = ChecklistTemplate.query.filter_by(is_active=True).all()
    created_count = 0

    for tmpl in active_templates:
        cycle_date, due_dt = get_current_cycle_info(tmpl.frequency, target_date, tmpl.due_time_hour or 17)

        # Check if an instance already exists for this template in this cycle
        existing = TaskInstance.query.filter_by(
            template_id=tmpl.id,
            cycle_date=cycle_date
        ).first()

        if not existing:
            # Set initial status: if already past due, mark OVERDUE, otherwise PENDING
            initial_status = TaskInstance.STATUS_OVERDUE if now > due_dt else TaskInstance.STATUS_PENDING
            task = TaskInstance(
                template_id=tmpl.id,
                cycle_date=cycle_date,
                due_datetime=due_dt,
                status=initial_status
            )
            db.session.add(task)
            created_count += 1

    # Update any pending tasks that have passed their due_datetime to OVERDUE
    overdue_tasks = TaskInstance.query.filter(
        TaskInstance.status == TaskInstance.STATUS_PENDING,
        TaskInstance.due_datetime < now
    ).all()

    for task in overdue_tasks:
        task.status = TaskInstance.STATUS_OVERDUE

    if created_count > 0 or overdue_tasks:
        db.session.commit()

    return created_count, len(overdue_tasks)
