Product Requirements Document (PRD)

1. Project Title

Compliance & Recurring Checklist Tracker

---

2. Problem Statement

Organizations need to regularly perform compliance and inspection activities. Managing these activities manually can make it difficult to remember recurring tasks, identify overdue work, record completion details, and maintain a proper history.

The Compliance & Recurring Checklist Tracker provides a centralized web-based system for creating compliance checklists, generating recurring tasks, tracking their status, recording completion details, and maintaining audit information.

---

3. Project Objective

The main objective of this project is to provide a simple system that helps users:

- Create and manage compliance checklists.
- Schedule recurring compliance activities.
- Track pending, completed, and overdue tasks.
- Record notes and comments during task completion.
- Upload photo evidence when required.
- Monitor compliance activity.
- Generate reports.
- Maintain an audit trail.
- Manage users and roles.

---

4. Target Users

The system is designed for organizations where employees or operators need to complete recurring compliance and inspection activities.

Main User Types

- Administrator – manages checklists, users, and system activities.
- Operator/Inspector – performs assigned compliance tasks and records completion details.

---

5. Functional Requirements

FR-01: User Authentication

The system shall allow authorized users to log in securely.

FR-02: User Management

The administrator shall be able to manage system users and their roles.

FR-03: Checklist Management

The administrator shall be able to create and manage compliance checklist templates.

Checklist information includes:

- Checklist title
- Description/instructions
- Category
- Frequency
- Due time
- Assigned operator

FR-04: Recurring Tasks

The system shall generate recurring tasks based on the checklist frequency.

Supported frequencies include:

- Daily
- Weekly
- Monthly

FR-05: Task Tracking

Users shall be able to view compliance tasks and identify their current status.

The system supports:

- Pending
- Completed
- Overdue

FR-06: Task Completion

An assigned user shall be able to complete a task and record:

- Inspector notes
- Comments
- Completion information
- Photo evidence when applicable

FR-07: Overdue Monitoring

The system shall identify overdue compliance tasks and display them separately for monitoring.

FR-08: Reports

The system shall provide reports based on compliance task information.

Reports can be filtered using information such as:

- Status
- Category
- Frequency
- Date range

FR-09: Data Export

The system shall provide options to export compliance information in supported formats such as:

- CSV
- Excel
- PDF

FR-10: Audit Trail

The system shall maintain an audit trail containing information about important system activities.

FR-11: Dashboard

The system shall provide a dashboard showing important compliance information such as:

- Compliance health
- Pending tasks
- Overdue tasks
- Recently completed tasks
- Audit activity

---

6. Non-Functional Requirements

Performance

The system should respond quickly for normal organizational usage.

Usability

The interface should be simple and easy to understand for users with basic computer knowledge.

Reliability

Task and completion information should be stored consistently in the database.

Security

Only authorized users should be able to access protected application features.

Maintainability

The application should use a modular structure so that features can be maintained and extended easily.

---

7. Technical Requirements

Frontend

- HTML
- CSS
- JavaScript
- Jinja templates

Backend

- Python
- Flask
- Flask-Login

Database

- SQLite
- SQLAlchemy

Development Tools

- Visual Studio Code
- Git
- GitHub

Testing

- Python testing framework
- Application-level testing

---

8. System Architecture

The project follows a web application architecture.

User
  |
  v
Frontend
(HTML / CSS / JavaScript)
  |
  v
Flask Application
  |
  +---- Routes
  |
  +---- Services
  |
  +---- Models
  |
  v
SQLite Database

---

9. Main Modules

9.1 Authentication Module

Handles user login and access control.

9.2 Dashboard Module

Provides an overview of the current compliance status.

9.3 Checklist Module

Allows administrators to create and manage checklist templates.

9.4 Task Module

Handles recurring compliance tasks and their status.

9.5 Reports Module

Provides filtering, reporting, and export functionality.

9.6 Audit Module

Maintains records of important system activities.

9.7 User Module

Handles user information, roles, and account status.

---

10. Data Requirements

The system stores information related to:

- Users
- Checklist templates
- Recurring tasks
- Task completion records
- Notes and comments
- Audit events
- Uploaded evidence

The application uses SQLite as the database for local development.

---

11. User Workflow

The basic workflow is:

Login
   ↓
Dashboard
   ↓
Create / Manage Checklist
   ↓
Recurring Task Generated
   ↓
Task Assigned
   ↓
User Performs Inspection
   ↓
Add Notes / Evidence
   ↓
Mark Task Completed
   ↓
Record Stored
   ↓
Reports / Audit Trail

---

12. Example Use Case

Daily Fire Safety Inspection

An administrator creates a checklist named:

Daily Fire Safety Inspection

The checklist contains instructions to check:

- Fire extinguishers
- Emergency exits
- Alarms
- Safety equipment

The system generates a recurring task.

The assigned inspector performs the inspection and records notes such as:

«Fire extinguishers and emergency exits were checked. All equipment was accessible and in good condition.»

The task is then marked as completed and becomes available in the completed records and reports.

---

13. Project Structure

The project is organized into separate components:

Compliance & Recurring Checklist Tracker/
│
├── app.py
├── config.py
├── README.md
├── PRD.md
├── TEAM_PARTICIPATION.md
├── requirements.txt
├── run.bat
│
├── Models/
├── Routes/
├── Services/
├── Templates/
├── Static/
└── tests/

Important Files and Folders

app.py
Starts and configures the Flask application.

Routes/
Contains application routes and request handling.

Services/
Contains application-level business logic.

Models/
Contains database models.

Templates/
Contains frontend HTML templates.

Static/
Contains CSS, JavaScript, and other static resources.

tests/
Contains project tests.

---

14. Project Status

The core implementation of the project has been completed and tested.

Implemented areas include:

- User authentication
- Dashboard
- Checklist management
- Recurring tasks
- Task completion
- Pending and overdue tracking
- Notes and comments
- Photo evidence support
- Reports
- CSV/Excel/PDF export
- Audit trail
- User management
- Git and GitHub integration

---

15. Future Enhancements

Possible future improvements include:

- Email notifications
- More advanced user permissions
- Additional dashboard visualizations
- Automated reminders
- Mobile-friendly improvements
- More detailed compliance analytics
- Additional report formats

---

16. Conclusion

The Compliance & Recurring Checklist Tracker is designed to simplify recurring compliance activities by providing a centralized system for checklist management, task tracking, completion records, reporting, and auditing.

The project demonstrates the use of Python, Flask, HTML, CSS, JavaScript, SQLite, Git, and GitHub to develop a practical web-based application.