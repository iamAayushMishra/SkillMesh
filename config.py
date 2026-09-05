"""
Configuration for the Semantic Employee & Skill Management System.
Reads environment variables from .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# RDF Namespace
NAMESPACE = os.getenv("RDF_NAMESPACE", "http://example.org/employee#")

# Data Files paths (relative to project root)
ONTOLOGY_PATH = os.path.join(os.path.dirname(__file__), "ontology", "employee_ontology.owl")
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "employees.ttl")

# Flask
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
