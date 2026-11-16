"""
Tests for Adding Employees and Assigning Projects via API
"""

import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_next_emp_id(client):
    res = client.get('/api/next-emp-id')
    assert res.status_code == 200
    data = res.get_json()
    assert "nextId" in data
    assert data["nextId"].startswith("EMP")

def test_certifications_api(client):
    res = client.get('/api/certifications')
    assert res.status_code == 200
    data = res.get_json()
    assert "certifications" in data
    assert "Python Certification" in data["certifications"]

def test_add_employee_and_assign_projects_flow(client):
    # 1. Get next ID
    res = client.get('/api/next-emp-id')
    new_id = res.get_json()["nextId"]

    # 2. Create employee with department, skills, and assigned projects
    payload = {
        "empId": new_id,
        "name": "Test Engineer",
        "email": "test.engineer@company.com",
        "department": "Software Development",
        "skills": ["Python", "JavaScript"],
        "certifications": ["Python Certification"],
        "projects": ["Semantic Search System"]
    }
    create_res = client.post('/api/employees', json=payload)
    assert create_res.status_code == 201
    created_data = create_res.get_json()
    assert created_data["success"] is True
    assert created_data["employee"]["empId"] == new_id
    assert "Semantic Search System" in created_data["employee"]["projects"]

    # 3. Retrieve employee detail
    detail_res = client.get(f'/api/employees/{new_id}')
    assert detail_res.status_code == 200
    detail = detail_res.get_json()
    assert detail["name"] == "Test Engineer"
    assert "Python" in detail["skills"]
    assert "Semantic Search System" in detail["projects"]

    # 4. Update assigned projects
    update_proj_res = client.post(f'/api/employees/{new_id}/projects', json={
        "projects": ["AIChatbot", "Semantic Search System"]
    })
    assert update_proj_res.status_code == 200
    upd_data = update_proj_res.get_json()
    assert "AI Chatbot" in upd_data["projects"]
    assert "Semantic Search System" in upd_data["projects"]

    # 5. Check project members endpoint
    members_res = client.get('/api/projects/AI Chatbot/members')
    assert members_res.status_code == 200
    member_ids = [m["empId"] for m in members_res.get_json()["members"]]
    assert new_id in member_ids

    # 6. Delete created test employee (cleanup)
    del_res = client.delete(f'/api/employees/{new_id}')
    assert del_res.status_code == 200
    assert del_res.get_json()["success"] is True

    # 7. Verify deletion
    verify_res = client.get(f'/api/employees/{new_id}')
    assert verify_res.status_code == 404
