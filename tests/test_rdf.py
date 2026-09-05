"""
Tests for Phase 13: Local RDF Validation
Ensures that the ontology and data files are syntactically valid and contain expected triples.
"""

import pytest
from rdflib import Graph, Namespace, RDF, OWL

# Define the namespace matching our config
EMP = Namespace("http://example.org/employee#")

@pytest.fixture
def ontology_graph():
    g = Graph()
    g.parse("ontology/employee_ontology.owl", format="turtle")
    return g

@pytest.fixture
def data_graph():
    g = Graph()
    g.parse("data/employees.ttl", format="turtle")
    return g

def test_ontology_classes(ontology_graph):
    """Test that all 5 required classes exist in the ontology."""
    classes = set(ontology_graph.subjects(RDF.type, OWL.Class))
    expected_classes = {EMP.Employee, EMP.Skill, EMP.Department, EMP.Project, EMP.Certification}
    
    assert expected_classes.issubset(classes), "Ontology is missing required classes"

def test_ontology_object_properties(ontology_graph):
    """Test that object properties exist."""
    obj_props = set(ontology_graph.subjects(RDF.type, OWL.ObjectProperty))
    assert EMP.hasSkill in obj_props
    assert EMP.worksIn in obj_props
    assert EMP.worksOn in obj_props

def test_data_employees_count(data_graph):
    """Test that we have exactly 15 employees loaded."""
    employees = list(data_graph.subjects(RDF.type, EMP.Employee))
    assert len(employees) == 15, f"Expected 15 employees, found {len(employees)}"

def test_data_skills_count(data_graph):
    """Test that we have exactly 8 skills loaded."""
    skills = list(data_graph.subjects(RDF.type, EMP.Skill))
    assert len(skills) == 8, f"Expected 8 skills, found {len(skills)}"

def test_specific_employee_data(data_graph):
    """Test that a specific employee (EMP001) has correct properties."""
    emp = EMP.EMP001
    
    # Check name
    names = list(data_graph.objects(emp, EMP.name))
    assert str(names[0]) == "Aayush Kumar"
    
    # Check worksIn
    depts = list(data_graph.objects(emp, EMP.worksIn))
    assert EMP.AIDepartment in depts
    
    # Check skills
    skills = list(data_graph.objects(emp, EMP.hasSkill))
    assert EMP.Python in skills
    assert EMP.MachineLearning in skills
