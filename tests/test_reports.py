from datetime import date, datetime
from models import db
from models.checklist import ChecklistTemplate
from models.task import TaskInstance

def test_csv_report_export(client, app, test_users, auth_client):
    with app.app_context():
        tmpl = ChecklistTemplate(
            title='Spill Kit Review',
            category='Environmental Compliance',
            frequency=ChecklistTemplate.FREQ_MONTHLY,
            created_by_id=test_users['admin_id']
        )
        db.session.add(tmpl)
        db.session.commit()

        task = TaskInstance(
            template_id=tmpl.id,
            cycle_date=date.today(),
            due_datetime=datetime.utcnow(),
            status=TaskInstance.STATUS_COMPLETED,
            notes='All absorbent pads stocked.'
        )
        db.session.add(task)
        db.session.commit()

    auth_client('admin_test', 'pass123')
    res = client.get('/reports/export/csv')
    assert res.status_code == 200
    assert 'text/csv' in res.content_type
    assert b'Checklist Title' in res.data
    assert b'Spill Kit Review' in res.data
    assert b'All absorbent pads stocked.' in res.data

def test_pdf_report_export(client, app, test_users, auth_client):
    auth_client('auditor_test', 'pass123')
    res = client.get('/reports/export/pdf')
    assert res.status_code == 200
    assert 'application/pdf' in res.content_type
    # PDF files start with binary header %PDF-
    assert res.data.startswith(b'%PDF')
