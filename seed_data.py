import os
from datetime import datetime, date, timedelta, time
from app import create_app
from models import db
from models.user import User
from models.checklist import ChecklistTemplate
from models.task import TaskInstance
from models.evidence import TaskEvidence
from models.audit_log import AuditLog
from services.recurrence import ensure_recurring_tasks

app = create_app()

def seed_database():
    with app.app_context():
        print("[INFO] Seeding database for Compliance & Recurring Checklist Tracker...")

        # Reset DB tables
        db.create_all()

        # 1. Create Default Demo Users
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@compliance.local',
                'password': 'admin123',
                'full_name': 'Eleanor Vance',
                'role': User.ROLE_ADMIN
            },
            {
                'username': 'operator',
                'email': 'operator@compliance.local',
                'password': 'operator123',
                'full_name': 'Marcus Chen',
                'role': User.ROLE_OPERATOR
            },
            {
                'username': 'auditor',
                'email': 'auditor@compliance.local',
                'password': 'auditor123',
                'full_name': 'Dr. Sarah Jenkins',
                'role': User.ROLE_AUDITOR
            }
        ]

        created_users = {}
        for u_data in users_data:
            existing = User.query.filter_by(username=u_data['username']).first()
            if not existing:
                user = User(
                    username=u_data['username'],
                    email=u_data['email'],
                    full_name=u_data['full_name'],
                    role=u_data['role']
                )
                user.set_password(u_data['password'])
                db.session.add(user)
                db.session.commit()
                created_users[u_data['username']] = user
                print(f"  [OK] User '{user.username}' created ({user.role})")
            else:
                created_users[u_data['username']] = existing

        admin_user = created_users['admin']
        operator_user = created_users['operator']

        # 2. Create Realistic Checklist Templates
        templates_data = [
            {
                'title': 'Fire Extinguisher Gauge & Access Inspection',
                'description': '1. Check pressure gauge needle is firmly in the green zone.\n2. Ensure safety pull-pin and tamper seal are intact.\n3. Verify nozzle is clean and 36-inch clearance is maintained around unit.',
                'category': 'Fire Protection',
                'frequency': ChecklistTemplate.FREQ_DAILY,
                'due_time_hour': 18,
                'assigned_user_id': operator_user.id
            },
            {
                'title': 'Server Room Environmental & AC Redundancy Check',
                'description': '1. Record ambient room temperature (must be between 18°C - 22°C).\n2. Inspect primary and secondary HVAC airflow.\n3. Verify server rack power distribution indicators.',
                'category': 'Equipment & Machinery',
                'frequency': ChecklistTemplate.FREQ_DAILY,
                'due_time_hour': 17,
                'assigned_user_id': operator_user.id
            },
            {
                'title': 'Emergency Eyewash & Safety Shower Flow Test',
                'description': '1. Flush eyewash station for 3 minutes to clear sediment.\n2. Verify water flow reaches both nozzles equally.\n3. Inspect inspection tag and sign with date.',
                'category': 'Safety & Emergency',
                'frequency': ChecklistTemplate.FREQ_WEEKLY,
                'due_time_hour': 16,
                'assigned_user_id': operator_user.id
            },
            {
                'title': 'First Aid Station Inventory & Expiry Review',
                'description': '1. Restock sterile gauze, burn dressings, and adhesive bandages.\n2. Verify antiseptic wipes and saline solutions have at least 6 months validity.',
                'category': 'Health & Sanitation',
                'frequency': ChecklistTemplate.FREQ_WEEKLY,
                'due_time_hour': 17,
                'assigned_user_id': operator_user.id
            },
            {
                'title': 'Chemical Storage Containment & Spill Kit Audit',
                'description': '1. Inspect secondary containment basins for any leaks or cracks.\n2. Verify absorbent pads, neutralizer powder, and disposal bags are fully stocked.\n3. Ensure Safety Data Sheets (SDS) binder is current.',
                'category': 'Environmental Compliance',
                'frequency': ChecklistTemplate.FREQ_MONTHLY,
                'due_time_hour': 17,
                'assigned_user_id': None
            },
            {
                'title': 'Main Electrical Panel Thermal & Clearance Check',
                'description': '1. Inspect breaker panel enclosures for signs of heat discoloration or buzzing.\n2. Verify 1-meter safety boundary in front of panels is free of obstructions.',
                'category': 'Electrical Systems',
                'frequency': ChecklistTemplate.FREQ_MONTHLY,
                'due_time_hour': 17,
                'assigned_user_id': None
            }
        ]

        for t_data in templates_data:
            existing_tmpl = ChecklistTemplate.query.filter_by(title=t_data['title']).first()
            if not existing_tmpl:
                tmpl = ChecklistTemplate(
                    title=t_data['title'],
                    description=t_data['description'],
                    category=t_data['category'],
                    frequency=t_data['frequency'],
                    due_time_hour=t_data['due_time_hour'],
                    assigned_user_id=t_data['assigned_user_id'],
                    created_by_id=admin_user.id
                )
                db.session.add(tmpl)
                db.session.commit()
                print(f"  [OK] Template '{tmpl.title}' ({tmpl.frequency}) created")

        # 3. Generate Current Task Instances via Recurrence Engine
        created_count, _ = ensure_recurring_tasks()
        print(f"  [OK] Generated {created_count} current cycle recurring task instances")

        # 4. Create an intentional Overdue Task to demo the Visual Alert Banner
        fire_tmpl = ChecklistTemplate.query.filter_by(title='Fire Extinguisher Gauge & Access Inspection').first()
        yesterday = date.today() - timedelta(days=1)
        yesterday_due = datetime.combine(yesterday, time(17, 0, 0))

        existing_overdue = TaskInstance.query.filter_by(template_id=fire_tmpl.id, cycle_date=yesterday).first()
        if not existing_overdue:
            overdue_task = TaskInstance(
                template_id=fire_tmpl.id,
                cycle_date=yesterday,
                due_datetime=yesterday_due,
                status=TaskInstance.STATUS_OVERDUE
            )
            db.session.add(overdue_task)
            db.session.commit()
            print(f"  [OK] Created demonstration overdue task #{overdue_task.id} to trigger alert banner")

        # 5. Create a sample Completed Task with notes and sample photo
        server_tmpl = ChecklistTemplate.query.filter_by(title='Server Room Environmental & AC Redundancy Check').first()
        past_date = date.today() - timedelta(days=2)
        past_due = datetime.combine(past_date, time(17, 0, 0))

        existing_done = TaskInstance.query.filter_by(template_id=server_tmpl.id, cycle_date=past_date).first()
        if not existing_done:
            done_task = TaskInstance(
                template_id=server_tmpl.id,
                cycle_date=past_date,
                due_datetime=past_due,
                status=TaskInstance.STATUS_COMPLETED,
                completed_at=datetime.combine(past_date, time(14, 30, 0)),
                completed_by_id=operator_user.id,
                notes="Server Room ambient temperature 19.4°C. Secondary AC unit tested and functioning normally. No alarm lights on UPS bank."
            )
            db.session.add(done_task)
            db.session.commit()

            # Create a mock placeholder evidence photo
            upload_dir = app.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            mock_filename = "demo_server_rack.jpg"
            mock_filepath = os.path.join(upload_dir, mock_filename)

            # Generate a clean placeholder image using Pillow if not present
            if not os.path.exists(mock_filepath):
                try:
                    from PIL import Image, ImageDraw
                    img = Image.new('RGB', (400, 300), color=(30, 41, 59))
                    d = ImageDraw.Draw(img)
                    d.rectangle([20, 20, 380, 280], outline=(59, 130, 246), width=3)
                    d.text((50, 130), "COMPLIANCE VERIFIED: 19.4 C", fill=(16, 185, 129))
                    d.text((50, 160), "Server Room Rack Unit A-04", fill=(203, 213, 225))
                    img.save(mock_filepath, "JPEG")
                except Exception as e:
                    print(f"  Notice: Placeholder image creation skipped: {e}")

            evidence = TaskEvidence(
                task_id=done_task.id,
                filename=mock_filename,
                original_filename="server_rack_inspection.jpg",
                file_size_bytes=10240,
                uploaded_by_id=operator_user.id,
                uploaded_at=datetime.combine(past_date, time(14, 31, 0))
            )
            db.session.add(evidence)
            db.session.commit()
            print(f"  [OK] Created demonstration completed task #{done_task.id} with photo evidence")

        # 6. Seed initial audit log entries
        db.session.add(AuditLog(
            user_id=admin_user.id,
            action='SYSTEM_INITIALIZED',
            entity_type='SYSTEM',
            entity_id=1,
            details='Compliance & Recurring Checklist Tracker system initialized with safety policies.',
            ip_address='127.0.0.1'
        ))
        db.session.commit()
        print("  [OK] Seeded baseline audit logs")

        print("[SUCCESS] Database successfully seeded and ready for demonstration!")

if __name__ == '__main__':
    seed_database()
