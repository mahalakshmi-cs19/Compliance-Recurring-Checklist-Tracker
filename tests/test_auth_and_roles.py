from flask import url_for

def test_unauthenticated_redirect(client):
    res = client.get('/dashboard')
    assert res.status_code == 302
    assert '/login' in res.location

def test_login_success_and_logout(client, test_users, auth_client):
    # Success
    res = auth_client('operator_test', 'pass123')
    assert res.status_code == 200
    assert b'Compliance Tasks Worklist' in res.data or b'Safety & Compliance Dashboard' in res.data

    # Logout
    logout_res = client.get('/logout', follow_redirects=True)
    assert logout_res.status_code == 200
    assert b'Sign In' in logout_res.data

def test_operator_cannot_access_admin_user_management(client, test_users, auth_client):
    auth_client('operator_test', 'pass123')
    res = client.get('/users', follow_redirects=True)
    # Should be blocked and redirected to dashboard with flash warning
    assert b'Administrator privileges required' in res.data

def test_admin_can_access_user_management(client, test_users, auth_client):
    auth_client('admin_test', 'pass123')
    res = client.get('/users')
    assert res.status_code == 200
    assert b'Team & User Management' in res.data

def test_auditor_access(client, test_users, auth_client):
    auth_client('auditor_test', 'pass123')
    
    # Auditor can view reports and audit logs
    audit_res = client.get('/audit')
    assert audit_res.status_code == 200
    assert b'Compliance Audit Trail' in audit_res.data

    reports_res = client.get('/reports')
    assert reports_res.status_code == 200
    assert b'Compliance & Audit Reports' in reports_res.data or b'Compliance &amp; Audit Reports' in reports_res.data
