import io
from datetime import date, datetime, timedelta
from models import db
from models.checklist import ChecklistTemplate
from models.task import TaskInstance
from models.audit_log import AuditLog

def test_complete_task_with_notes_and_photo(client, app, test_users, auth_client):
    with app.app_context():
        tmpl = ChecklistTemplate(
            title='Eyewash Inspection',
            category='Safety & Emergency',
            frequency=ChecklistTemplate.FREQ_DAILY,
            created_by_id=test_users['admin_id']
        )
        db.session.add(tmpl)
        db.session.commit()

        task = TaskInstance(
            template_id=tmpl.id,
            cycle_date=date.today(),
            due_datetime=datetime.utcnow(),
            status=TaskInstance.STATUS_PENDING
        )
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    # Log in as operator
    auth_client('operator_test', 'pass123')

    # Post completion with notes and mock image
    mock_image_data = (io.BytesIO(b"fake image bytes"), "test_photo.jpg")
    response = client.post(
        f'/tasks/{task_id}/complete',
        data={
            'notes': 'Flow verified, clear water for 3 minutes.',
            'photo_evidence': mock_image_data
        },
        content_type='multipart/form-data',
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b'marked as completed successfully' in response.data

    with app.app_context():
        updated_task = TaskInstance.query.get(task_id)
        assert updated_task.status == TaskInstance.STATUS_COMPLETED
        assert updated_task.notes == 'Flow verified, clear water for 3 minutes.'
        assert updated_task.completed_by_id == test_users['operator_id']
        assert len(updated_task.evidences) == 1
        assert updated_task.evidences[0].original_filename == 'test_photo.jpg'

        # Verify audit log was recorded
        audit = AuditLog.query.filter_by(entity_type='TASK', entity_id=task_id).first()
        assert audit is not None
        assert audit.action == 'TASK_COMPLETED'

def test_auditor_blocked_from_completing_task(client, app, test_users, auth_client):
    with app.app_context():
        tmpl = ChecklistTemplate(
            title='Fire Alarm Audio Test',
            category='Fire Protection',
            frequency=ChecklistTemplate.FREQ_WEEKLY,
            created_by_id=test_users['admin_id']
        )
        db.session.add(tmpl)
        db.session.commit()

        task = TaskInstance(
            template_id=tmpl.id,
            cycle_date=date.today(),
            due_datetime=datetime.utcnow() + timedelta(hours=5),
            status=TaskInstance.STATUS_PENDING
        )
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    # Log in as auditor
    auth_client('auditor_test', 'pass123')

    response = client.post(
        f'/tasks/{task_id}/complete',
        data={'notes': 'Auditor attempt'},
        follow_redirects=True
    )

    assert b'Permission denied' in response.data

    with app.app_context():
        unchanged_task = TaskInstance.query.get(task_id)
        assert unchanged_task.status == TaskInstance.STATUS_PENDING
        assert unchanged_task.status != TaskInstance.STATUS_COMPLETED
