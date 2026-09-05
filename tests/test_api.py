"""
Tests for Phase 13: Flask API Testing
Uses the Flask test client. Since the RDF database is now embedded natively
using rdflib in sparql_client.py, we don't have to worry about connection failures
to an external Fuseki server. All endpoints should return 200/404 directly.
"""

import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_dashboard_api(client):
    """Test dashboard stats endpoint."""
    res = client.get('/api/dashboard')
    assert res.status_code == 200
    
    data = res.get_json()
    assert "employees" in data
    assert "skills" in data
    assert data["employees"] == 15

def test_employees_list_api(client):
    """Test fetching all employees."""
    res = client.get('/api/employees')
    assert res.status_code == 200
    
    data = res.get_json()
    assert "employees" in data
    assert type(data["employees"]) == list
    assert len(data["employees"]) == 15

def test_employee_detail_api(client):
    """Test fetching a single employee by ID."""
    res = client.get('/api/employees/EMP001')
    assert res.status_code == 200
    
    data = res.get_json()
    assert data["empId"] == "EMP001"
    assert "skills" in data
    assert "department" in data

def test_invalid_employee_id(client):
    """Test SQL/SPARQL injection protection on ID endpoint."""
    res = client.get('/api/employees/invalid" OR 1=1')
    assert res.status_code == 400
    assert "Invalid" in res.get_json()["error"]

def test_page_routes(client):
    """Test that HTML pages render properly."""
    pages = ['/', '/employees', '/search', '/projects', '/graph']
    for page in pages:
        res = client.get(page)
        assert res.status_code == 200
        assert b"<!DOCTYPE html>" in res.data
