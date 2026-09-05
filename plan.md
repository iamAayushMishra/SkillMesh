# Semantic Employee & Skill Management System — Implementation Plan

> **Project title** : Semantic Employee & Skill Management System
> **Project Type:** 3rd-Year B.Tech CSE Academic Project
> **Author:** Aayush
> **Created:** September 2026
> **Status:** Planning

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Data Flow](#3-data-flow)
4. [Project Folder Structure](#4-project-folder-structure)
5. [Dependencies & Packages](#5-dependencies--packages)
6. [Difficulty Classification](#6-difficulty-classification)
7. [Phase 1 — Project Setup](#phase-1--project-setup)
8. [Phase 2 — Data Model Design](#phase-2--data-model-design)
9. [Phase 3 — RDF Representation](#phase-3--rdf-representation)
10. [Phase 4 — OWL Ontology Design](#phase-4--owl-ontology-design)
11. [Phase 5 — Sample RDF Data](#phase-5--sample-rdf-data)
12. [Phase 6 — Apache Jena Fuseki Setup](#phase-6--apache-jena-fuseki-setup)
13. [Phase 7 — SPARQL Queries](#phase-7--sparql-queries)
14. [Phase 8 — Flask Backend](#phase-8--flask-backend)
15. [Phase 9 — Frontend (Core Pages)](#phase-9--frontend-core-pages)
16. [Phase 10 — Semantic Search](#phase-10--semantic-search)
17. [Phase 11 — Knowledge Graph Visualization](#phase-11--knowledge-graph-visualization)
18. [Phase 12 — Error Handling & Polish](#phase-12--error-handling--polish)
19. [Phase 13 — Testing](#phase-13--testing)
20. [Phase 14 — Documentation & Viva Preparation](#phase-14--documentation--viva-preparation)
21. [Git/GitHub Strategy](#git--github-strategy)
22. [Risk Management](#risk-management)
23. [Final Implementation Roadmap](#final-implementation-roadmap)
24. [Viva Preparation](#viva-preparation)

---

## 1. Project Overview

### What Are We Building?

A web-based employee and skill management system that uses **Semantic Web technologies** (RDF, OWL, SPARQL) instead of a traditional relational database. The system stores information about employees, their skills, departments, projects, and certifications as a **knowledge graph** — a network of interconnected facts.

### Why Semantic Web?

In a traditional database, data is stored in rigid tables with fixed columns. If you want to ask "which employees know Python AND work in the AI department AND have a certification related to machine learning?", you need complex SQL JOINs across multiple tables.

With Semantic Web technologies:
- Data is stored as **triples** (subject → predicate → object), e.g., `Aayush → hasSkill → Python`
- Relationships are **first-class citizens**, not hidden inside foreign keys
- You can easily add new types of relationships without altering a schema
- SPARQL lets you traverse the knowledge graph to answer complex questions naturally

### What Questions Can the System Answer?

| # | Question | Semantic Relationships Used |
|---|----------|-----------------------------|
| 1 | Which employees know Python? | `hasSkill` |
| 2 | Which employees have AI/ML skills? | `hasSkill`, `relatedTo` |
| 3 | Who can be assigned to the AI Chatbot project? | `requiresSkill`, `hasSkill` |
| 4 | What skills are related to Python? | `relatedTo` |
| 5 | Which department has ML experts? | `worksIn`, `hasSkill` |
| 6 | Who has the AWS certification? | `hasCertification` |
| 7 | Who has multiple required skills for a project? | `requiresSkill`, `hasSkill` (with counting) |
| 8 | What projects does the AI Department handle? | `handlesProject` |
| 9 | Tell me everything about Employee001 | All properties of a resource |
| 10 | Who works in the Data Science department? | `worksIn` |

---

## 2. System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                        USER (Browser)                       │
└────────────────────────────┬────────────────────────────────┘
                             │  HTTP requests (fetch/AJAX)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND LAYER                          │
│                                                             │
│  HTML Pages        CSS Styles        JavaScript             │
│  ─────────         ──────────        ──────────             │
│  index.html        style.css         app.js                 │
│  employees.html                      search.js              │
│  search.html                         graph.js (Cytoscape)   │
│  graph.html                                                 │
│  projects.html                                              │
│                                                             │
│  Responsibility: Render UI, capture user input, display     │
│  results, visualize the knowledge graph.                    │
└────────────────────────────┬────────────────────────────────┘
                             │  API calls (JSON)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     FLASK BACKEND                           │
│                                                             │
│  app.py (main application)                                  │
│  ─────────────────────────                                  │
│  • Receives HTTP requests from the frontend                 │
│  • Selects and parameterizes the appropriate SPARQL query    │
│  • Sends the SPARQL query to Fuseki via HTTP                │
│  • Converts SPARQL JSON results into clean API responses    │
│  • Serves the HTML templates                                │
│                                                             │
│  Responsibility: Act as a bridge between the frontend       │
│  and the triple store. No business logic beyond query       │
│  construction and result formatting.                        │
└────────────────────────────┬────────────────────────────────┘
                             │  SPARQL over HTTP
                             │  (POST to Fuseki endpoint)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  SPARQL QUERY LAYER                         │
│                                                             │
│  queries/                                                   │
│  ────────                                                   │
│  employee_queries.rq                                        │
│  skill_queries.rq                                           │
│  project_queries.rq                                         │
│  department_queries.rq                                      │
│                                                             │
│  Responsibility: Define reusable SPARQL query templates.    │
│  Each .rq file contains one or more named queries.          │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│               APACHE JENA FUSEKI (Triple Store)             │
│                                                             │
│  • Stores all RDF data (triples)                            │
│  • Loads the OWL ontology                                   │
│  • Exposes a SPARQL endpoint at http://localhost:3030       │
│  • Processes SPARQL queries and returns results             │
│                                                             │
│  Responsibility: Persistent storage and querying of the     │
│  RDF knowledge graph.                                       │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  RDF + OWL KNOWLEDGE GRAPH                  │
│                                                             │
│  ontology/employee_ontology.owl   (class & property defs)   │
│  data/employees.ttl               (instance data)           │
│                                                             │
│  The graph contains:                                        │
│  • Classes: Employee, Skill, Department, Project, Cert      │
│  • Properties: hasSkill, worksIn, hasCertification, etc.    │
│  • Instances: 15 employees, 8 skills, 4 departments, etc.  │
│                                                             │
│  Responsibility: Define the data model and store all facts. │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities Summary

| Layer | Technology | Responsibility |
|-------|-----------|----------------|
| Frontend | HTML/CSS/JS + Cytoscape.js | User interface, input capture, result display, graph visualization |
| Backend | Python + Flask | API endpoints, SPARQL query construction, result formatting, template serving |
| Query Layer | SPARQL (.rq files) | Reusable query templates for different search scenarios |
| Triple Store | Apache Jena Fuseki | Persistent RDF storage, SPARQL query processing |
| Knowledge Graph | RDF (Turtle) + OWL | Data model definition, instance data, semantic relationships |

---

## 3. Data Flow

### Example: User Searches for "Employees with Python Skill"

```text
Step 1: User types "Python" in the search box and clicks "Search"
              │
              ▼
Step 2: Frontend JavaScript sends a GET request:
        fetch("/api/search/employees?skill=Python")
              │
              ▼
Step 3: Flask route handler receives the request
        @app.route("/api/search/employees")
        def search_employees():
            skill = request.args.get("skill")  → "Python"
              │
              ▼
Step 4: Flask constructs a SPARQL query:
        SELECT ?name ?email ?dept WHERE {
            ?emp rdf:type :Employee .
            ?emp :hasSkill :Python .
            ?emp :name ?name .
            ?emp :email ?email .
            ?emp :worksIn ?dept .
        }
              │
              ▼
Step 5: Flask sends this query to Fuseki via HTTP POST:
        POST http://localhost:3030/employees/sparql
        Content-Type: application/sparql-query
              │
              ▼
Step 6: Fuseki searches the RDF graph for triples matching the pattern
        and returns results as JSON:
        {
          "results": {
            "bindings": [
              { "name": {"value": "Aayush"}, "email": {...}, "dept": {...} },
              { "name": {"value": "Priya"},  "email": {...}, "dept": {...} }
            ]
          }
        }
              │
              ▼
Step 7: Flask parses the Fuseki JSON and returns a clean API response:
        {
          "employees": [
            { "name": "Aayush", "email": "aayush@company.com", "department": "AI Department" },
            { "name": "Priya",  "email": "priya@company.com",  "department": "Data Science" }
          ]
        }
              │
              ▼
Step 8: Frontend JavaScript receives the JSON and renders a table/cards
        showing the matching employees.
```

---

## 4. Project Folder Structure

```text
semantic-employee-system/
│
├── app.py                          # Main Flask application
├── config.py                       # Configuration (Fuseki URL, etc.)
├── sparql_client.py                # SPARQL query execution helper
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── plan.md                         # This planning document
│
├── ontology/
│   └── employee_ontology.owl       # OWL ontology (Turtle format)
│
├── data/
│   └── employees.ttl               # Sample RDF data (Turtle format)
│
├── queries/
│   ├── employee_queries.rq         # SPARQL queries for employees
│   ├── skill_queries.rq            # SPARQL queries for skills
│   ├── project_queries.rq         # SPARQL queries for projects
│   ├── department_queries.rq       # SPARQL queries for departments
│   ├── dashboard_queries.rq        # SPARQL queries for dashboard counts
│   └── graph_queries.rq            # SPARQL queries for graph visualization
│
├── templates/
│   ├── base.html                   # Base HTML template (shared layout)
│   ├── index.html                  # Dashboard page
│   ├── employees.html              # Employee listing & detail page
│   ├── search.html                 # Semantic search page
│   ├── projects.html               # Projects & candidate matching page
│   └── graph.html                  # Knowledge graph visualization page
│
├── static/
│   ├── css/
│   │   └── style.css               # All CSS styles
│   ├── js/
│   │   ├── app.js                  # Shared JavaScript utilities
│   │   ├── search.js               # Semantic search logic
│   │   └── graph.js                # Cytoscape.js graph visualization
│   └── img/                        # Any images/icons (optional)
│
├── tests/
│   ├── test_rdf.py                 # RDF validation tests
│   ├── test_sparql.py              # SPARQL query tests
│   └── test_api.py                 # Flask API tests
│
└── docs/
    ├── data_model.md               # Data model design document
    └── report.md                   # Final project report (Phase 14)
```

---

## 5. Dependencies & Packages

### Python Packages (requirements.txt)

```text
Flask==3.1.1
requests==2.32.3
rdflib==7.1.4
SPARQLWrapper==2.0.0
pytest==8.3.5
```

| Package | Purpose |
|---------|---------|
| **Flask** | Web framework — serves pages and API endpoints |
| **requests** | HTTP library — used to send SPARQL queries to Fuseki |
| **rdflib** | RDF library — used for local RDF parsing and validation during development |
| **SPARQLWrapper** | Python wrapper for SPARQL endpoints — simplifies communication with Fuseki |
| **pytest** | Testing framework — used for automated tests |

### Frontend Libraries (loaded via CDN)

| Library | Version | Purpose |
|---------|---------|---------|
| **Cytoscape.js** | 3.30+ | Knowledge graph visualization |

> **Note:** We use CDN links for frontend libraries to avoid npm/node complexity. This is appropriate for a student project.

### External Tools

| Tool | Version | Purpose |
|------|---------|---------|
| **Apache Jena Fuseki** | 5.x | Triple store with SPARQL endpoint |
| **Python** | 3.10+ | Backend runtime |
| **Git** | Any | Version control |

---

## 6. Difficulty Classification

### Must Have (Required for basic project)

These features are **mandatory**. The project is incomplete without them.

- [ ] RDF data model with Turtle serialization
- [ ] OWL ontology defining classes and properties
- [ ] Sample dataset (15 employees, 8 skills, 4 departments, 3 projects, 5 certifications)
- [ ] Apache Jena Fuseki setup with data loaded
- [ ] At least 7 working SPARQL queries
- [ ] Flask backend with API endpoints
- [ ] Dashboard page showing counts
- [ ] Employee listing page
- [ ] Semantic search (search by skill, department)
- [ ] Basic knowledge graph visualization with Cytoscape.js
- [ ] Error handling for common failures

### Good to Have (Implement if basic system works)

These improve the project but are not essential.

- [ ] Project-to-employee matching page
- [ ] Skill relationship exploration (related skills)
- [ ] Employee detail page with all relationships
- [ ] Graph filtering (show/hide node types)
- [ ] Responsive mobile layout

### Optional (Only if time permits)

These are stretch goals. Do NOT attempt unless everything else is complete.

- [ ] SPARQL query builder UI (let user write custom queries)
- [ ] Export search results as CSV
- [ ] Dark mode toggle
- [ ] Graph layout switching (circle, grid, hierarchical)
- [ ] Add/edit employee data through the UI (SPARQL UPDATE)

> **Explicitly NOT in scope:** Machine learning, LLMs, microservices, Docker, Kubernetes, authentication, real-time systems, advanced OWL reasoning (e.g., DL reasoning, SWRL rules), cloud deployment.

---

## Phase 1 — Project Setup

### Objective

Set up the development environment, install all required tools, create the project folder structure, and verify that everything works.

### Why This Phase Is Needed

Every subsequent phase depends on having a working development environment. Setting up early prevents debugging environment issues later when you're trying to focus on code logic.

### Prerequisites

- Python 3.10+ installed
- A code editor (VS Code recommended)
- Git installed
- Internet connection (to download Fuseki and Python packages)

### Tasks

1. **Create the project directory**
   ```bash
   mkdir semantic-employee-system
   cd semantic-employee-system
   ```

2. **Initialize Git**
   ```bash
   git init
   ```

3. **Create a `.gitignore` file**
   ```text
   __pycache__/
   *.pyc
   venv/
   .env
   apache-jena-fuseki-*/
   *.db
   .vscode/
   ```

4. **Create a Python virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   # source venv/bin/activate   # macOS/Linux
   ```

5. **Create `requirements.txt`** with the dependencies listed in Section 5.

6. **Install Python packages**
   ```bash
   pip install -r requirements.txt
   ```

7. **Download Apache Jena Fuseki**
   - Go to: https://jena.apache.org/download/
   - Download the latest `apache-jena-fuseki-5.x.x.zip`
   - Extract to a folder (e.g., `C:\Tools\apache-jena-fuseki-5.x.x\`)
   - **Do NOT put Fuseki inside the project folder** (it's a large binary; add the extraction path to `.gitignore` or keep it outside)

8. **Verify Fuseki runs**
   ```bash
   cd C:\Tools\apache-jena-fuseki-5.x.x
   fuseki-server --help
   ```
   You should see help text. Don't start the server yet — we have no data.

9. **Create the folder structure** (empty folders and placeholder files)
   ```text
   semantic-employee-system/
   ├── app.py                  # empty, just: # Flask application
   ├── config.py               # empty placeholder
   ├── requirements.txt        # filled above
   ├── .gitignore              # filled above
   ├── README.md               # project title and one-line description
   ├── ontology/               # empty folder
   ├── data/                   # empty folder
   ├── queries/                # empty folder
   ├── templates/              # empty folder
   ├── static/
   │   ├── css/                # empty folder
   │   ├── js/                 # empty folder
   │   └── img/                # empty folder
   ├── tests/                  # empty folder
   └── docs/                   # empty folder
   ```

10. **Create `config.py`** with basic configuration
    ```python
    # config.py
    FUSEKI_URL = "http://localhost:3030"
    DATASET_NAME = "employees"
    SPARQL_ENDPOINT = f"{FUSEKI_URL}/{DATASET_NAME}/sparql"
    UPDATE_ENDPOINT = f"{FUSEKI_URL}/{DATASET_NAME}/update"
    DATA_ENDPOINT = f"{FUSEKI_URL}/{DATASET_NAME}/data"
    ```

11. **Create a minimal `app.py`** to verify Flask works
    ```python
    from flask import Flask

    app = Flask(__name__)

    @app.route("/")
    def home():
        return "Semantic Employee System is running!"

    if __name__ == "__main__":
        app.run(debug=True)
    ```

12. **Test Flask**
    ```bash
    python app.py
    ```
    Open `http://127.0.0.1:5000/` in a browser. You should see the message.

13. **First Git commit**
    ```bash
    git add .
    git commit -m "Initial project setup with folder structure and Flask skeleton"
    ```

### Files/Folders to Create or Modify

```text
semantic-employee-system/
├── .gitignore              [NEW]
├── README.md               [NEW]
├── requirements.txt        [NEW]
├── config.py               [NEW]
├── app.py                  [NEW] (minimal Flask app)
├── ontology/               [NEW] (empty)
├── data/                   [NEW] (empty)
├── queries/                [NEW] (empty)
├── templates/              [NEW] (empty)
├── static/css/             [NEW] (empty)
├── static/js/              [NEW] (empty)
├── static/img/             [NEW] (empty)
├── tests/                  [NEW] (empty)
└── docs/                   [NEW] (empty)
```

### Expected Output

After completing this phase:
- You have a working Python virtual environment with all packages installed
- Flask starts and serves a test page at `http://127.0.0.1:5000/`
- Apache Jena Fuseki is downloaded and its `--help` command works
- The project folder structure is in place
- Git repository is initialized with the first commit

### How to Test

| Test | How | Expected Result |
|------|-----|-----------------|
| Python version | `python --version` | 3.10 or higher |
| Virtual environment | `pip list` | Shows Flask, rdflib, SPARQLWrapper, requests |
| Flask runs | `python app.py`, visit `http://127.0.0.1:5000/` | Browser shows the test message |
| Fuseki installed | `fuseki-server --help` | Prints help text without errors |
| Git works | `git log --oneline` | Shows the initial commit |

### Completion Checklist

- [ ] Python 3.10+ installed and verified
- [ ] Virtual environment created and activated
- [ ] All Python packages installed (`pip install -r requirements.txt`)
- [ ] Apache Jena Fuseki downloaded and `--help` works
- [ ] Project folder structure created
- [ ] `config.py` created with Fuseki URL
- [ ] `app.py` runs and shows test message in browser
- [ ] `.gitignore` created
- [ ] First Git commit made

---

## Phase 2 — Data Model Design

### Objective

Design the conceptual data model — define what **entities** exist, what **attributes** they have, and what **relationships** connect them. This is a paper/document exercise, not a coding task.

### Why This Phase Is Needed

Before writing any RDF or OWL, you must clearly understand your data. Jumping straight into Turtle syntax without a clear model leads to messy, inconsistent data. This phase forces you to think about the domain.

### Prerequisites

- Phase 1 completed (project setup)

### Key Concepts Introduced

**Entity:** A thing in your domain (e.g., an Employee, a Skill).
**Attribute:** A property of an entity (e.g., an Employee has a name).
**Relationship:** A connection between two entities (e.g., an Employee `hasSkill` Python).

### Tasks

1. **Define Entities (Classes)**

   | Entity | Description | Example Instances |
   |--------|-------------|-------------------|
   | **Employee** | A person who works in the company | Aayush, Priya, Rahul |
   | **Skill** | A technical or soft skill | Python, Java, Machine Learning |
   | **Department** | An organizational unit | AI Department, HR |
   | **Project** | A company project | AI Chatbot, Employee Analytics |
   | **Certification** | A professional certification | AWS Certification, Python Certification |

2. **Define Attributes (Data Properties)**

   These connect an entity to a **literal value** (a string, number, etc.).

   | Entity | Attribute | Data Type | Example |
   |--------|-----------|-----------|---------|
   | Employee | employeeId | string | "EMP001" |
   | Employee | name | string | "Aayush Kumar" |
   | Employee | email | string | "aayush@company.com" |
   | Skill | skillName | string | "Python" |
   | Department | deptName | string | "AI Department" |
   | Project | projectName | string | "AI Chatbot" |
   | Project | projectDescription | string | "An AI-powered chatbot" |
   | Certification | certName | string | "AWS Certification" |

3. **Define Relationships (Object Properties)**

   These connect an entity to **another entity**.

   | Relationship | Domain (From) | Range (To) | Meaning | Example |
   |-------------|---------------|------------|---------|---------|
   | `hasSkill` | Employee | Skill | Employee possesses this skill | Aayush → hasSkill → Python |
   | `worksIn` | Employee | Department | Employee belongs to this department | Aayush → worksIn → AI Department |
   | `hasCertification` | Employee | Certification | Employee holds this certification | Aayush → hasCertification → Python Cert |
   | `worksOn` | Employee | Project | Employee is assigned to this project | Aayush → worksOn → AI Chatbot |
   | `requiresSkill` | Project | Skill | Project needs this skill | AI Chatbot → requiresSkill → Python |
   | `relatedTo` | Skill | Skill | Two skills are related | Python → relatedTo → Machine Learning |
   | `handlesProject` | Department | Project | Department manages this project | AI Dept → handlesProject → AI Chatbot |
   | `certifiesSkill` | Certification | Skill | Certification validates this skill | Python Cert → certifiesSkill → Python |

   > **Domain:** The type of entity the relationship starts from.
   > **Range:** The type of entity the relationship points to.
   > For example, `hasSkill` has domain `Employee` and range `Skill` — meaning only employees can "have" skills, and skills are what they "have."

4. **Define the Sample Dataset**

   **Employees (15):**

   | ID | Name | Email | Department | Skills | Certifications |
   |----|------|-------|------------|--------|----------------|
   | EMP001 | Aayush Kumar | aayush@company.com | AI Department | Python, Machine Learning, AI | Python Cert, Data Science Cert |
   | EMP002 | Priya Sharma | priya@company.com | Data Science | Python, SQL, Machine Learning | Data Science Cert |
   | EMP003 | Rahul Verma | rahul@company.com | Software Dev | Java, JavaScript, SQL | AWS Cert |
   | EMP004 | Sneha Patel | sneha@company.com | AI Department | Python, AI, RDF | Python Cert |
   | EMP005 | Vikram Singh | vikram@company.com | Software Dev | Java, JavaScript, SPARQL | — |
   | EMP006 | Ananya Gupta | ananya@company.com | Data Science | Python, SQL, SPARQL | Data Science Cert |
   | EMP007 | Rohan Desai | rohan@company.com | HR | JavaScript, SQL | — |
   | EMP008 | Meera Nair | meera@company.com | AI Department | Python, Machine Learning, SPARQL | ML Cert |
   | EMP009 | Arjun Reddy | arjun@company.com | Software Dev | Java, Python, SQL | Java Cert |
   | EMP010 | Kavita Joshi | kavita@company.com | Data Science | Python, Machine Learning, AI | Data Science Cert, ML Cert |
   | EMP011 | Deepak Mehta | deepak@company.com | Software Dev | JavaScript, Java, RDF | AWS Cert |
   | EMP012 | Ishita Roy | ishita@company.com | HR | SQL, JavaScript | — |
   | EMP013 | Nikhil Rao | nikhil@company.com | AI Department | Python, AI, Machine Learning | Python Cert, ML Cert |
   | EMP014 | Sanya Kapoor | sanya@company.com | Data Science | SQL, Python, SPARQL | Data Science Cert |
   | EMP015 | Amit Tiwari | amit@company.com | Software Dev | Java, JavaScript, Python | Java Cert, AWS Cert |

   **Skills (8):**
   Python, Java, Machine Learning, Artificial Intelligence (AI), SQL, JavaScript, RDF, SPARQL

   **Departments (4):**
   AI Department, Software Development, Data Science, HR

   **Projects (3):**

   | Project | Department | Required Skills |
   |---------|------------|-----------------|
   | AI Chatbot | AI Department | Python, AI, Machine Learning |
   | Employee Analytics | Data Science | Python, SQL, Machine Learning |
   | Semantic Search System | Software Dev | Python, RDF, SPARQL |

   **Certifications (5):**

   | Certification | Certifies Skill |
   |---------------|-----------------|
   | Python Certification | Python |
   | AWS Certification | Java (cloud deployment) |
   | Data Science Certification | Machine Learning |
   | Machine Learning Certification | Machine Learning |
   | Java Certification | Java |

   **Skill Relationships (relatedTo):**

   | Skill A | relatedTo | Skill B |
   |---------|-----------|---------|
   | Python | relatedTo | Machine Learning |
   | Python | relatedTo | AI |
   | Machine Learning | relatedTo | AI |
   | Machine Learning | relatedTo | SQL |
   | JavaScript | relatedTo | Java |
   | RDF | relatedTo | SPARQL |
   | RDF | relatedTo | Python |
   | SPARQL | relatedTo | SQL |

5. **Draw the Relationship Diagram**

   Create a simple hand-drawn or text-based diagram showing how entities connect:

   ```text
   ┌──────────┐     hasSkill      ┌──────────┐
   │ Employee │──────────────────▶│  Skill   │
   └──────────┘                   └──────────┘
        │                              │
        │ worksIn                      │ relatedTo
        ▼                              ▼
   ┌──────────┐                   ┌──────────┐
   │Department│                   │  Skill   │
   └──────────┘                   └──────────┘
        │
        │ handlesProject
        ▼
   ┌──────────┐     requiresSkill  ┌──────────┐
   │ Project  │───────────────────▶│  Skill   │
   └──────────┘                    └──────────┘

   ┌──────────┐     hasCertification  ┌───────────────┐
   │ Employee │──────────────────────▶│ Certification │
   └──────────┘                       └───────────────┘
                                            │
                                            │ certifiesSkill
                                            ▼
                                       ┌──────────┐
                                       │  Skill   │
                                       └──────────┘
   ```

### Files/Folders to Create or Modify

```text
docs/
└── data_model.md      [NEW] — Document containing all the tables and diagrams above
```

> **Note:** This phase is primarily a design exercise. The `data_model.md` document serves as a reference for subsequent phases. You can also keep these notes in a notebook.

### Expected Output

After completing this phase:
- You have a clear, written list of all entities, attributes, and relationships
- You have a complete sample dataset with 15 employees, 8 skills, 4 departments, 3 projects, 5 certifications
- You understand what **domain** and **range** mean for each property
- You have a visual diagram of how entities connect

### How to Test

| Test | How | Expected Result |
|------|-----|-----------------|
| Entities complete | Review the entity list | 5 entity types defined |
| Attributes complete | Review the attribute table | Every entity has at least one attribute |
| Relationships complete | Review the relationship table | 8 relationships with domain/range |
| Dataset complete | Count instances | 15 employees, 8 skills, 4 departments, 3 projects, 5 certs |
| No dangling references | Check that every department, skill, cert in the employee table exists in the respective entity list | All references valid |

### Completion Checklist

- [ ] All 5 entity types defined with descriptions
- [ ] All data attributes (data properties) listed with types
- [ ] All 8 relationships (object properties) listed with domain and range
- [ ] Sample dataset complete: 15 employees with all fields
- [ ] Skills, departments, projects, certifications listed
- [ ] Skill-to-skill relationships defined
- [ ] Relationship diagram drawn
- [ ] `docs/data_model.md` created
- [ ] Git commit: `"Add data model design document"`

---

## Phase 3 — RDF Representation

### Objective

Translate the data model from Phase 2 into **RDF triples** using **Turtle (.ttl) syntax**. Understand what RDF is and how it represents data.

### Why This Phase Is Needed

RDF (Resource Description Framework) is the foundation of Semantic Web. Every piece of data in our system will be stored as RDF triples. You must understand how to represent real-world information as triples before building anything else.

### Prerequisites

- Phase 2 completed (data model designed)

### Key Concepts Introduced

**RDF (Resource Description Framework):**
A standard for describing resources on the web. Everything is represented as a **triple**: three parts that form a statement.

**RDF Triple:**
```text
Subject  →  Predicate  →  Object
(Who/What)  (Relationship)  (Value/Target)
```

Example:
```text
Aayush  →  hasSkill  →  Python
```
This says: "Aayush has the skill Python."

**Types of Objects:**
- **URI (Resource):** Another entity, e.g., `:Python` — used for relationships between entities
- **Literal (Value):** A plain value, e.g., `"Aayush Kumar"` — used for attributes like names

**Turtle Format (.ttl):**
Turtle is a compact, human-readable way to write RDF. It uses:
- `@prefix` declarations to shorten URIs
- `:Subject :predicate :Object .` for resource-to-resource triples
- `:Subject :predicate "value" .` for resource-to-literal triples
- Semicolons (`;`) to add multiple predicates for the same subject
- Commas (`,`) to add multiple objects for the same predicate

**Namespace / Prefix:**
Instead of writing full URIs like `http://example.org/employee/Employee001`, we define a prefix:
```turtle
@prefix :     <http://example.org/employee#> .
```
Then we can write just `:Employee001`.

### Tasks

1. **Define the namespace (prefix)**

   Our project will use this base namespace:
   ```turtle
   @prefix :     <http://example.org/employee#> .
   @prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
   @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
   @prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
   ```

   | Prefix | Full URI | Purpose |
   |--------|----------|---------|
   | `:` | `http://example.org/employee#` | Our project's custom namespace |
   | `rdf:` | W3C RDF namespace | Standard RDF vocabulary (e.g., `rdf:type`) |
   | `rdfs:` | W3C RDFS namespace | Labels, comments |
   | `xsd:` | W3C XML Schema | Data types (string, integer) |

2. **Understand the triple pattern for each relationship**

   | Statement | Subject | Predicate | Object | Object Type |
   |-----------|---------|-----------|--------|-------------|
   | Aayush is an Employee | `:EMP001` | `rdf:type` | `:Employee` | URI |
   | Aayush's name is "Aayush Kumar" | `:EMP001` | `:name` | `"Aayush Kumar"` | Literal |
   | Aayush has skill Python | `:EMP001` | `:hasSkill` | `:Python` | URI |
   | Aayush works in AI Dept | `:EMP001` | `:worksIn` | `:AIDepartment` | URI |
   | Python is a Skill | `:Python` | `rdf:type` | `:Skill` | URI |
   | Python is related to ML | `:Python` | `:relatedTo` | `:MachineLearning` | URI |

3. **Write sample RDF in Turtle format**

   Create the file `data/employees.ttl` with the following structure. Here is an example for the first two employees, all skills, and one project:

   ```turtle
   @prefix :     <http://example.org/employee#> .
   @prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
   @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
   @prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

   # ============================================================
   # SKILLS
   # ============================================================

   :Python rdf:type :Skill ;
       :skillName "Python" .

   :Java rdf:type :Skill ;
       :skillName "Java" .

   :MachineLearning rdf:type :Skill ;
       :skillName "Machine Learning" .

   :ArtificialIntelligence rdf:type :Skill ;
       :skillName "Artificial Intelligence" .

   :SQL rdf:type :Skill ;
       :skillName "SQL" .

   :JavaScript rdf:type :Skill ;
       :skillName "JavaScript" .

   :RDFSkill rdf:type :Skill ;
       :skillName "RDF" .

   :SPARQLSkill rdf:type :Skill ;
       :skillName "SPARQL" .

   # ============================================================
   # SKILL RELATIONSHIPS
   # ============================================================

   :Python :relatedTo :MachineLearning , :ArtificialIntelligence .
   :MachineLearning :relatedTo :ArtificialIntelligence , :SQL .
   :JavaScript :relatedTo :Java .
   :RDFSkill :relatedTo :SPARQLSkill , :Python .
   :SPARQLSkill :relatedTo :SQL .

   # ============================================================
   # DEPARTMENTS
   # ============================================================

   :AIDepartment rdf:type :Department ;
       :deptName "AI Department" .

   :SoftwareDevelopment rdf:type :Department ;
       :deptName "Software Development" .

   :DataScience rdf:type :Department ;
       :deptName "Data Science" .

   :HR rdf:type :Department ;
       :deptName "HR" .

   # ============================================================
   # PROJECTS
   # ============================================================

   :AIChatbot rdf:type :Project ;
       :projectName "AI Chatbot" ;
       :projectDescription "An AI-powered chatbot for customer support" ;
       :requiresSkill :Python , :ArtificialIntelligence , :MachineLearning .

   :EmployeeAnalytics rdf:type :Project ;
       :projectName "Employee Analytics" ;
       :projectDescription "Analytics dashboard for employee performance" ;
       :requiresSkill :Python , :SQL , :MachineLearning .

   :SemanticSearchSystem rdf:type :Project ;
       :projectName "Semantic Search System" ;
       :projectDescription "A search system using semantic web technologies" ;
       :requiresSkill :Python , :RDFSkill , :SPARQLSkill .

   # ============================================================
   # DEPARTMENT → PROJECT RELATIONSHIPS
   # ============================================================

   :AIDepartment :handlesProject :AIChatbot .
   :DataScience :handlesProject :EmployeeAnalytics .
   :SoftwareDevelopment :handlesProject :SemanticSearchSystem .

   # ============================================================
   # CERTIFICATIONS
   # ============================================================

   :PythonCertification rdf:type :Certification ;
       :certName "Python Certification" ;
       :certifiesSkill :Python .

   :AWSCertification rdf:type :Certification ;
       :certName "AWS Certification" ;
       :certifiesSkill :Java .

   :DataScienceCertification rdf:type :Certification ;
       :certName "Data Science Certification" ;
       :certifiesSkill :MachineLearning .

   :MLCertification rdf:type :Certification ;
       :certName "Machine Learning Certification" ;
       :certifiesSkill :MachineLearning .

   :JavaCertification rdf:type :Certification ;
       :certName "Java Certification" ;
       :certifiesSkill :Java .

   # ============================================================
   # EMPLOYEES
   # ============================================================

   :EMP001 rdf:type :Employee ;
       :employeeId "EMP001" ;
       :name "Aayush Kumar" ;
       :email "aayush@company.com" ;
       :worksIn :AIDepartment ;
       :hasSkill :Python , :MachineLearning , :ArtificialIntelligence ;
       :hasCertification :PythonCertification , :DataScienceCertification ;
       :worksOn :AIChatbot .

   :EMP002 rdf:type :Employee ;
       :employeeId "EMP002" ;
       :name "Priya Sharma" ;
       :email "priya@company.com" ;
       :worksIn :DataScience ;
       :hasSkill :Python , :SQL , :MachineLearning ;
       :hasCertification :DataScienceCertification ;
       :worksOn :EmployeeAnalytics .

   # ... (Continue for EMP003 through EMP015 following the same pattern)
   # Refer to the dataset table in Phase 2 for all employee data.
   ```

   > **Important:** In the actual implementation, write ALL 15 employees. The `# ...` comment above is just to save space in the plan.

4. **Validate the Turtle file using rdflib**

   Create a quick validation script:
   ```python
   # tests/test_rdf.py (temporary usage)
   from rdflib import Graph

   g = Graph()
   g.parse("data/employees.ttl", format="turtle")
   print(f"Loaded {len(g)} triples")
   for s, p, o in list(g)[:5]:
       print(f"  {s} → {p} → {o}")
   ```

### Files/Folders to Create or Modify

```text
data/
└── employees.ttl       [NEW] — Full RDF dataset in Turtle format
tests/
└── test_rdf.py         [NEW] — RDF validation script (basic version)
```

### Expected Output

After completing this phase:
- You have a valid `employees.ttl` file with all 15 employees, 8 skills, 4 departments, 3 projects, 5 certifications, and their relationships
- The file parses without errors using rdflib
- You can count the total number of triples (should be approximately 150–200 triples)

### How to Test

| Test | How | Expected Result |
|------|-----|-----------------|
| File parses | Run `python tests/test_rdf.py` | No errors, prints triple count |
| Triple count reasonable | Check the count | ~150–200 triples |
| Spot check | Inspect printed triples | Makes sense (e.g., `:EMP001 :hasSkill :Python`) |
| All employees present | Search file for `EMP001` through `EMP015` | All 15 found |
| All skills present | Search for each skill name | All 8 found |

### Completion Checklist

- [ ] `data/employees.ttl` created with all data from Phase 2
- [ ] All 15 employees represented with all attributes and relationships
- [ ] All 8 skills, 4 departments, 3 projects, 5 certifications defined
- [ ] Skill `relatedTo` relationships included
- [ ] Department `handlesProject` relationships included
- [ ] File parses successfully with rdflib
- [ ] `tests/test_rdf.py` written and passes
- [ ] Git commit: `"Add RDF data model in Turtle format"`

---

## Phase 4 — OWL Ontology Design

### Objective

Create an **OWL ontology** that formally defines the classes (entity types), object properties (relationships), and data properties (attributes) used in our RDF data.

### Why This Phase Is Needed

The RDF data from Phase 3 is just a collection of triples. The ontology gives **meaning** to those triples — it says "Employee is a class," "hasSkill connects an Employee to a Skill," etc. Without an ontology:
- There's no formal definition of what types of entities exist
- There's no specification of valid relationships
- The data is just arbitrary triples without structure

An ontology makes the knowledge graph **self-describing**.

### Prerequisites

- Phase 2 completed (data model)
- Phase 3 completed (RDF data exists)

### Key Concepts Introduced

**OWL (Web Ontology Language):**
A language for defining ontologies. An ontology is like a "schema" for RDF data — it defines what classes exist and what properties connect them.

**Class:**
A category of things. `Employee` is a class. Every individual employee (`:EMP001`) is an **instance** of the `Employee` class.

**Object Property:**
A relationship between two resources (entities). Example: `hasSkill` connects an `Employee` to a `Skill`.

**Data Property:**
A relationship between a resource and a literal value. Example: `name` connects an `Employee` to a string like `"Aayush Kumar"`.

**Domain:**
The class that a property "starts from." If `hasSkill` has domain `Employee`, it means only employees can have skills.

**Range:**
The class that a property "points to." If `hasSkill` has range `Skill`, it means the thing they "have" must be a skill.

> **Note:** We are using OWL at a basic level. We will NOT use advanced features like:
> - Cardinality restrictions (e.g., "an employee must have at least 1 skill")
> - Transitive/symmetric property declarations
> - Disjoint classes
> - Union/intersection of classes
>
> These are powerful but add complexity unnecessary for this project.

### Tasks

1. **Create the ontology file `ontology/employee_ontology.owl`**

   We will write it in **Turtle format** (not XML), which is easier to read. OWL ontologies can be serialized in Turtle.

   ```turtle
   @prefix :     <http://example.org/employee#> .
   @prefix owl:  <http://www.w3.org/2002/07/owl#> .
   @prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
   @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
   @prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

   # ============================================================
   # ONTOLOGY DECLARATION
   # ============================================================

   <http://example.org/employee> rdf:type owl:Ontology ;
       rdfs:label "Employee Skill Management Ontology" ;
       rdfs:comment "Ontology for managing employees, skills, departments, projects, and certifications." .

   # ============================================================
   # CLASSES
   # ============================================================

   :Employee rdf:type owl:Class ;
       rdfs:label "Employee" ;
       rdfs:comment "A person who works in the organization." .

   :Skill rdf:type owl:Class ;
       rdfs:label "Skill" ;
       rdfs:comment "A technical or professional skill." .

   :Department rdf:type owl:Class ;
       rdfs:label "Department" ;
       rdfs:comment "An organizational department." .

   :Project rdf:type owl:Class ;
       rdfs:label "Project" ;
       rdfs:comment "A company project that requires certain skills." .

   :Certification rdf:type owl:Class ;
       rdfs:label "Certification" ;
       rdfs:comment "A professional certification held by an employee." .

   # ============================================================
   # OBJECT PROPERTIES (entity-to-entity relationships)
   # ============================================================

   :hasSkill rdf:type owl:ObjectProperty ;
       rdfs:label "has skill" ;
       rdfs:comment "Links an employee to a skill they possess." ;
       rdfs:domain :Employee ;
       rdfs:range :Skill .

   :worksIn rdf:type owl:ObjectProperty ;
       rdfs:label "works in" ;
       rdfs:comment "Links an employee to their department." ;
       rdfs:domain :Employee ;
       rdfs:range :Department .

   :hasCertification rdf:type owl:ObjectProperty ;
       rdfs:label "has certification" ;
       rdfs:comment "Links an employee to a certification they hold." ;
       rdfs:domain :Employee ;
       rdfs:range :Certification .

   :worksOn rdf:type owl:ObjectProperty ;
       rdfs:label "works on" ;
       rdfs:comment "Links an employee to a project they are assigned to." ;
       rdfs:domain :Employee ;
       rdfs:range :Project .

   :requiresSkill rdf:type owl:ObjectProperty ;
       rdfs:label "requires skill" ;
       rdfs:comment "Links a project to a skill it requires." ;
       rdfs:domain :Project ;
       rdfs:range :Skill .

   :relatedTo rdf:type owl:ObjectProperty ;
       rdfs:label "related to" ;
       rdfs:comment "Links a skill to another related skill." ;
       rdfs:domain :Skill ;
       rdfs:range :Skill .

   :handlesProject rdf:type owl:ObjectProperty ;
       rdfs:label "handles project" ;
       rdfs:comment "Links a department to a project it manages." ;
       rdfs:domain :Department ;
       rdfs:range :Project .

   :certifiesSkill rdf:type owl:ObjectProperty ;
       rdfs:label "certifies skill" ;
       rdfs:comment "Links a certification to the skill it validates." ;
       rdfs:domain :Certification ;
       rdfs:range :Skill .

   # ============================================================
   # DATA PROPERTIES (entity-to-literal attributes)
   # ============================================================

   :employeeId rdf:type owl:DatatypeProperty ;
       rdfs:label "employee ID" ;
       rdfs:domain :Employee ;
       rdfs:range xsd:string .

   :name rdf:type owl:DatatypeProperty ;
       rdfs:label "name" ;
       rdfs:domain :Employee ;
       rdfs:range xsd:string .

   :email rdf:type owl:DatatypeProperty ;
       rdfs:label "email" ;
       rdfs:domain :Employee ;
       rdfs:range xsd:string .

   :skillName rdf:type owl:DatatypeProperty ;
       rdfs:label "skill name" ;
       rdfs:domain :Skill ;
       rdfs:range xsd:string .

   :deptName rdf:type owl:DatatypeProperty ;
       rdfs:label "department name" ;
       rdfs:domain :Department ;
       rdfs:range xsd:string .

   :projectName rdf:type owl:DatatypeProperty ;
       rdfs:label "project name" ;
       rdfs:domain :Project ;
       rdfs:range xsd:string .

   :projectDescription rdf:type owl:DatatypeProperty ;
       rdfs:label "project description" ;
       rdfs:domain :Project ;
       rdfs:range xsd:string .

   :certName rdf:type owl:DatatypeProperty ;
       rdfs:label "certification name" ;
       rdfs:domain :Certification ;
       rdfs:range xsd:string .
   ```

2. **Ontology Summary Table**

   | Component | Count | Examples |
   |-----------|-------|---------|
   | Classes | 5 | Employee, Skill, Department, Project, Certification |
   | Object Properties | 8 | hasSkill, worksIn, hasCertification, worksOn, requiresSkill, relatedTo, handlesProject, certifiesSkill |
   | Data Properties | 8 | employeeId, name, email, skillName, deptName, projectName, projectDescription, certName |

3. **Validate the ontology using rdflib**

   Add to `tests/test_rdf.py`:
   ```python
   def test_ontology():
       g = Graph()
       g.parse("ontology/employee_ontology.owl", format="turtle")
       print(f"Ontology loaded: {len(g)} triples")

       # Check that all 5 classes exist
       classes = list(g.subjects(RDF.type, OWL.Class))
       print(f"Classes found: {len(classes)}")
       assert len(classes) == 5

       # Check that object properties exist
       obj_props = list(g.subjects(RDF.type, OWL.ObjectProperty))
       print(f"Object properties found: {len(obj_props)}")
       assert len(obj_props) == 8
   ```

### Files/Folders to Create or Modify

```text
ontology/
└── employee_ontology.owl    [NEW] — OWL ontology in Turtle format
tests/
└── test_rdf.py              [MODIFY] — Add ontology validation
```

### Expected Output

After completing this phase:
- You have a valid OWL ontology file that defines 5 classes, 8 object properties, and 8 data properties
- The ontology parses without errors
- Every relationship used in `employees.ttl` has a corresponding property definition in the ontology
- Domain and range are specified for all properties

### How to Test

| Test | How | Expected Result |
|------|-----|-----------------|
| Ontology parses | Parse with rdflib | No errors |
| 5 classes defined | Count `owl:Class` instances | 5 |
| 8 object properties | Count `owl:ObjectProperty` instances | 8 |
| 8 data properties | Count `owl:DatatypeProperty` instances | 8 |
| Consistency | Every predicate used in `employees.ttl` is defined in the ontology | All match |

### Completion Checklist

- [ ] `ontology/employee_ontology.owl` created in Turtle format
- [ ] 5 classes defined: Employee, Skill, Department, Project, Certification
- [ ] 8 object properties defined with domain and range
- [ ] 8 data properties defined with domain and range
- [ ] Ontology has `rdfs:label` and `rdfs:comment` for all elements
- [ ] Ontology parses successfully with rdflib
- [ ] Tests updated and pass
- [ ] Git commit: `"Add OWL ontology for employee skill management"`

---

## Phase 5 — Sample RDF Data

### Objective

Complete the `employees.ttl` file with ALL 15 employees and verify that the RDF data is consistent with the ontology from Phase 4.

### Why This Phase Is Needed

Phase 3 showed the Turtle format and included a partial dataset. This phase ensures the complete dataset is written and validated. We need complete data before loading it into Fuseki.

### Prerequisites

- Phase 3 completed (Turtle format understood, partial data exists)
- Phase 4 completed (ontology defines valid classes and properties)

### Tasks

1. **Complete `data/employees.ttl`** with all 15 employees (EMP001 through EMP015) following the exact data from the Phase 2 dataset table.

2. **Ensure the data file imports/uses the same namespace** as the ontology:
   ```turtle
   @prefix : <http://example.org/employee#> .
   ```

3. **Validate the complete dataset**

   Update `tests/test_rdf.py` with comprehensive checks:
   ```python
   def test_complete_data():
       g = Graph()
       g.parse("data/employees.ttl", format="turtle")

       EMP = Namespace("http://example.org/employee#")

       # Count employees
       employees = list(g.subjects(RDF.type, EMP.Employee))
       assert len(employees) == 15, f"Expected 15 employees, got {len(employees)}"

       # Count skills
       skills = list(g.subjects(RDF.type, EMP.Skill))
       assert len(skills) == 8, f"Expected 8 skills, got {len(skills)}"

       # Count departments
       departments = list(g.subjects(RDF.type, EMP.Department))
       assert len(departments) == 4

       # Count projects
       projects = list(g.subjects(RDF.type, EMP.Project))
       assert len(projects) == 3

       # Count certifications
       certifications = list(g.subjects(RDF.type, EMP.Certification))
       assert len(certifications) == 5

       # Check a specific employee
       aayush_skills = list(g.objects(EMP.EMP001, EMP.hasSkill))
       assert len(aayush_skills) == 3  # Python, ML, AI

       print("All data validation tests passed!")
   ```

4. **Count total triples** — should be approximately 150–200.

### Files/Folders to Create or Modify

```text
data/
└── employees.ttl       [MODIFY] — Complete all 15 employees
tests/
└── test_rdf.py         [MODIFY] — Add comprehensive data validation
```

### Expected Output

- Complete `employees.ttl` with all entities and relationships
- All validation tests pass
- Triple count is in the expected range

### How to Test

| Test | How | Expected Result |
|------|-----|-----------------|
| All tests pass | `python -m pytest tests/test_rdf.py -v` | All green |
| 15 employees | Count in test | Exactly 15 |
| 8 skills | Count in test | Exactly 8 |
| Spot check EMP001 | Verify skills count | 3 skills |

### Completion Checklist

- [ ] `data/employees.ttl` contains all 15 employees with complete data
- [ ] All skills, departments, projects, certifications, relationships included
- [ ] Validation tests pass (correct counts for all entity types)
- [ ] No syntax errors in Turtle file
- [ ] Git commit: `"Complete sample RDF data for all 15 employees"`

---

## Phase 6 — Apache Jena Fuseki Setup

### Objective

Set up Apache Jena Fuseki as the triple store, create a dataset, load the RDF data and ontology, and verify that the SPARQL endpoint works.

### Why This Phase Is Needed

Fuseki is where our knowledge graph lives in production. While rdflib can parse RDF locally, Fuseki provides a **SPARQL endpoint** — an HTTP server that accepts SPARQL queries and returns results. This is what Flask will communicate with.

### Prerequisites

- Phase 1 completed (Fuseki downloaded)
- Phase 5 completed (complete RDF data and ontology ready)

### Key Concepts Introduced

**Triple Store:**
A database specifically designed to store and query RDF triples. Unlike relational databases (MySQL, PostgreSQL) that store data in tables, a triple store stores data as subject-predicate-object triples and supports SPARQL for querying.

**SPARQL Endpoint:**
An HTTP URL where you can send SPARQL queries and receive results. Fuseki provides this at `http://localhost:3030/<dataset>/sparql`.

**Dataset:**
In Fuseki, a dataset is a named collection of RDF graphs. We will create one dataset called `employees`.

### Tasks

1. **Start Fuseki**
   ```bash
   cd C:\Tools\apache-jena-fuseki-5.x.x
   fuseki-server --port=3030
   ```
   Open `http://localhost:3030/` in a browser — you should see the Fuseki admin UI.

2. **Create a dataset via the Fuseki UI**
   - Go to `http://localhost:3030/` → "Manage" tab
   - Click "Add new dataset"
   - Dataset name: `employees`
   - Dataset type: **In-Memory** (simpler for development; use **Persistent (TDB2)** for production)
   - Click "Create dataset"

   > **Alternative (command line):**
   > ```bash
   > fuseki-server --mem /employees
   > ```
   > This starts Fuseki with an in-memory dataset named `employees`.

3. **Upload the ontology**
   - Go to `http://localhost:3030/` → select dataset `employees` → "Upload data"
   - Choose file: `ontology/employee_ontology.owl`
   - Click "Upload"

4. **Upload the RDF data**
   - Same page → "Upload data"
   - Choose file: `data/employees.ttl`
   - Click "Upload"

5. **Test with a simple SPARQL query**
   - Go to `http://localhost:3030/` → select dataset `employees` → "Query"
   - Enter this query:
     ```sparql
     SELECT ?s ?p ?o
     WHERE { ?s ?p ?o }
     LIMIT 10
     ```
   - Click "Run Query"
   - You should see 10 triples from your data

6. **Test a specific query**
   ```sparql
   PREFIX : <http://example.org/employee#>

   SELECT ?name
   WHERE {
       ?emp rdf:type :Employee .
       ?emp :name ?name .
   }
   ```
   Expected: 15 employee names

7. **Test from Python** (verify programmatic access)
   ```python
   # Quick test script (can be in tests/ or run interactively)
   from SPARQLWrapper import SPARQLWrapper, JSON

   sparql = SPARQLWrapper("http://localhost:3030/employees/sparql")
   sparql.setQuery("""
       PREFIX : <http://example.org/employee#>
       SELECT ?name WHERE {
           ?emp rdf:type :Employee .
           ?emp :name ?name .
       }
   """)
   sparql.setReturnFormat(JSON)
   results = sparql.query().convert()

   for result in results["results"]["bindings"]:
       print(result["name"]["value"])
   ```
   Expected: Prints all 15 employee names.

8. **Document the Fuseki startup process** in `README.md` so you can repeat it easily.

### Files/Folders to Create or Modify

```text
README.md               [MODIFY] — Add Fuseki setup instructions
tests/
└── test_sparql.py      [NEW] — SPARQL connectivity test
```

### Expected Output

After completing this phase:
- Fuseki is running at `http://localhost:3030/`
- Dataset `employees` is created and loaded with ontology + data
- SPARQL queries return correct results in the Fuseki UI
- Python can connect to Fuseki and execute SPARQL queries programmatically

### How to Test

| Test | How | Expected Result |
|------|-----|-----------------|
| Fuseki admin UI | Visit `http://localhost:3030/` | Admin interface loads |
| Simple query | Run `SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10` | Returns 10 rows |
| Employee count | Query for all employees | 15 results |
| Python connectivity | Run the test script above | 15 names printed |

### Completion Checklist

- [ ] Fuseki downloaded, extracted, and starts without errors
- [ ] Dataset `employees` created
- [ ] Ontology (`employee_ontology.owl`) uploaded to Fuseki
- [ ] RDF data (`employees.ttl`) uploaded to Fuseki
- [ ] Simple SPARQL queries work in Fuseki web UI
- [ ] Python can query Fuseki using SPARQLWrapper
- [ ] `README.md` updated with Fuseki setup instructions
- [ ] `tests/test_sparql.py` created and passes
- [ ] Git commit: `"Configure Apache Jena Fuseki and load RDF data"`

> **Important Note:** Fuseki stores data in memory by default. Every time you restart Fuseki, you need to re-upload the data. If you want persistent storage, use `--tdb2` mode (see Fuseki documentation). For development, in-memory is fine — just re-upload after each restart.

---

## Phase 7 — SPARQL Queries

### Objective

Write and test all the SPARQL queries that the application will need. Save them as `.rq` files for reuse in the Flask backend.

### Why This Phase Is Needed

SPARQL is how we "ask questions" to the knowledge graph. Getting the queries right before building the Flask backend means we can test them independently in the Fuseki UI. If a query is wrong, we fix it here — not while debugging Flask routes.

### Prerequisites

- Phase 6 completed (Fuseki running with data loaded)

### Key Concepts Introduced

**SPARQL (SPARQL Protocol and RDF Query Language):**
Think of SPARQL as "SQL for RDF." Instead of querying tables, you query a graph of triples.

**Basic SPARQL structure:**
```sparql
PREFIX : <http://example.org/employee#>

SELECT ?variable1 ?variable2        ← What you want to retrieve
WHERE {
    ?subject :predicate ?object .   ← Pattern to match in the graph
}
```

**Pattern Matching:**
`?emp :hasSkill :Python .` means "find any entity (`?emp`) that has the `:hasSkill` relationship pointing to `:Python`."

**Variables:**
Start with `?` — SPARQL finds all possible values that satisfy the pattern.

**FILTER:**
Add conditions like `FILTER(?count >= 2)` to narrow results.

### Tasks

Write each query, test it in Fuseki, then save it to a `.rq` file.

---

#### Query 1: Find Employees with a Specific Skill

**Question answered:** "Which employees know Python?"
**Relationships used:** `rdf:type`, `hasSkill`, `name`, `skillName`

```sparql
PREFIX : <http://example.org/employee#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?empId ?name ?email
WHERE {
    ?emp rdf:type :Employee .
    ?emp :employeeId ?empId .
    ?emp :name ?name .
    ?emp :email ?email .
    ?emp :hasSkill ?skill .
    ?skill :skillName ?skillName .
    FILTER(?skillName = "Python")
}
ORDER BY ?name
```

**Expected result:** All employees who have Python as a skill (EMP001, EMP002, EMP004, EMP006, EMP008, EMP009, EMP010, EMP013, EMP014, EMP015).

> **Note for Flask:** The `"Python"` value will be parameterized — replaced with the user's search term.

---

#### Query 2: Find Employees with AI or Machine Learning Skills

**Question answered:** "Which employees have AI/ML skills?"
**Relationships used:** `hasSkill`, `skillName`

```sparql
PREFIX : <http://example.org/employee#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?empId ?name ?email ?skillName
WHERE {
    ?emp rdf:type :Employee .
    ?emp :employeeId ?empId .
    ?emp :name ?name .
    ?emp :email ?email .
    ?emp :hasSkill ?skill .
    ?skill :skillName ?skillName .
    FILTER(?skillName = "Machine Learning" || ?skillName = "Artificial Intelligence")
}
ORDER BY ?name
```

**Expected result:** Employees with either AI or ML skills. Some employees may appear twice (once per matching skill) — `DISTINCT` on the employee level prevents duplicates, but we keep `?skillName` to show which skill matched.

---

#### Query 3: Find Employees in a Specific Department

**Question answered:** "Who works in the AI Department?"
**Relationships used:** `worksIn`, `deptName`

```sparql
PREFIX : <http://example.org/employee#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?empId ?name ?email
WHERE {
    ?emp rdf:type :Employee .
    ?emp :employeeId ?empId .
    ?emp :name ?name .
    ?emp :email ?email .
    ?emp :worksIn ?dept .
    ?dept :deptName ?deptName .
    FILTER(?deptName = "AI Department")
}
ORDER BY ?name
```

**Expected result:** EMP001 (Aayush), EMP004 (Sneha), EMP008 (Meera), EMP013 (Nikhil).

---

#### Query 4: Find Skills Related to a Skill

**Question answered:** "What skills are related to Python?"
**Relationships used:** `relatedTo`, `skillName`

```sparql
PREFIX : <http://example.org/employee#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?relatedSkillName
WHERE {
    ?skill rdf:type :Skill .
    ?skill :skillName ?skillName .
    ?skill :relatedTo ?relatedSkill .
    ?relatedSkill :skillName ?relatedSkillName .
    FILTER(?skillName = "Python")
}
```

**Expected result:** Machine Learning, Artificial Intelligence (because `Python :relatedTo :MachineLearning, :ArtificialIntelligence`).

---

#### Query 5: Find Employees with a Specific Certification

**Question answered:** "Who has the AWS certification?"
**Relationships used:** `hasCertification`, `certName`

```sparql
PREFIX : <http://example.org/employee#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?empId ?name ?email ?certName
WHERE {
    ?emp rdf:type :Employee .
    ?emp :employeeId ?empId .
    ?emp :name ?name .
    ?emp :email ?email .
    ?emp :hasCertification ?cert .
    ?cert :certName ?certName .
    FILTER(?certName = "AWS Certification")
}
ORDER BY ?name
```

**Expected result:** EMP003 (Rahul), EMP011 (Deepak), EMP015 (Amit).

---

#### Query 6: Find Employees Suitable for a Project (Skill Matching)

**Question answered:** "Who can work on the AI Chatbot project based on required skills?"
**Relationships used:** `requiresSkill`, `hasSkill`

```sparql
PREFIX : <http://example.org/employee#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?empId ?name (COUNT(?skill) AS ?matchingSkills) (GROUP_CONCAT(?skillName; separator=", ") AS ?skills)
WHERE {
    ?project rdf:type :Project .
    ?project :projectName ?projName .
    ?project :requiresSkill ?skill .
    ?emp rdf:type :Employee .
    ?emp :employeeId ?empId .
    ?emp :name ?name .
    ?emp :hasSkill ?skill .
    ?skill :skillName ?skillName .
    FILTER(?projName = "AI Chatbot")
}
GROUP BY ?empId ?name
ORDER BY DESC(?matchingSkills)
```

**Expected result:** Employees ordered by how many of the AI Chatbot's required skills (Python, AI, ML) they possess. EMP001 (Aayush) and EMP013 (Nikhil) should have all 3 skills.

---

#### Query 7: Find Projects Handled by a Department

**Question answered:** "What projects does the AI Department handle?"
**Relationships used:** `handlesProject`, `projectName`

```sparql
PREFIX : <http://example.org/employee#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?projectName ?projectDescription
WHERE {
    ?dept rdf:type :Department .
    ?dept :deptName ?deptName .
    ?dept :handlesProject ?project .
    ?project :projectName ?projectName .
    ?project :projectDescription ?projectDescription .
    FILTER(?deptName = "AI Department")
}
```

**Expected result:** AI Chatbot.

---

#### Query 8: Get All Information About an Employee

**Question answered:** "Tell me everything about EMP001."
**Relationships used:** All properties of the employee

```sparql
PREFIX : <http://example.org/employee#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?property ?value
WHERE {
    :EMP001 ?property ?value .
}
```

**Expected result:** All triples where `:EMP001` is the subject — name, email, skills, department, certifications, project.

> **For a more structured version** (used in the employee detail page):

```sparql
PREFIX : <http://example.org/employee#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?name ?email ?deptName
       (GROUP_CONCAT(DISTINCT ?skillName; separator=", ") AS ?skills)
       (GROUP_CONCAT(DISTINCT ?certName; separator=", ") AS ?certifications)
       (GROUP_CONCAT(DISTINCT ?projName; separator=", ") AS ?projects)
WHERE {
    ?emp rdf:type :Employee .
    ?emp :employeeId ?empId .
    ?emp :name ?name .
    ?emp :email ?email .
    ?emp :worksIn ?dept .
    ?dept :deptName ?deptName .
    OPTIONAL { ?emp :hasSkill ?skill . ?skill :skillName ?skillName . }
    OPTIONAL { ?emp :hasCertification ?cert . ?cert :certName ?certName . }
    OPTIONAL { ?emp :worksOn ?proj . ?proj :projectName ?projName . }
    FILTER(?empId = "EMP001")
}
GROUP BY ?name ?email ?deptName
```

---

#### Query 9: Get All Employees (for listing page)

**Question answered:** "Show all employees."

```sparql
PREFIX : <http://example.org/employee#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?empId ?name ?email ?deptName
WHERE {
    ?emp rdf:type :Employee .
    ?emp :employeeId ?empId .
    ?emp :name ?name .
    ?emp :email ?email .
    ?emp :worksIn ?dept .
    ?dept :deptName ?deptName .
}
ORDER BY ?empId
```

---

#### Query 10: Find Employees with Multiple Required Skills for a Project

**Question answered:** "Which employees have at least 2 of the required skills for the AI Chatbot?"
**Relationships used:** `requiresSkill`, `hasSkill`, with `HAVING` clause

```sparql
PREFIX : <http://example.org/employee#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?empId ?name (COUNT(?skill) AS ?matchingSkills)
WHERE {
    ?project rdf:type :Project .
    ?project :projectName "AI Chatbot" .
    ?project :requiresSkill ?skill .
    ?emp rdf:type :Employee .
    ?emp :employeeId ?empId .
    ?emp :name ?name .
    ?emp :hasSkill ?skill .
}
GROUP BY ?empId ?name
HAVING (COUNT(?skill) >= 2)
ORDER BY DESC(?matchingSkills)
```

**Expected result:** Employees with 2 or more of: Python, AI, Machine Learning.

---

#### Query 11: Dashboard Counts

**Question answered:** "How many employees, skills, departments, projects do we have?"

```sparql
PREFIX : <http://example.org/employee#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT
    (COUNT(DISTINCT ?emp) AS ?employeeCount)
    (COUNT(DISTINCT ?skill) AS ?skillCount)
    (COUNT(DISTINCT ?dept) AS ?deptCount)
    (COUNT(DISTINCT ?project) AS ?projectCount)
    (COUNT(DISTINCT ?cert) AS ?certCount)
WHERE {
    { ?emp rdf:type :Employee . }
    UNION { ?skill rdf:type :Skill . }
    UNION { ?dept rdf:type :Department . }
    UNION { ?project rdf:type :Project . }
    UNION { ?cert rdf:type :Certification . }
}
```

---

#### Query 12: Get All Skills (for dropdowns/listings)

```sparql
PREFIX : <http://example.org/employee#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?skillName
WHERE {
    ?skill rdf:type :Skill .
    ?skill :skillName ?skillName .
}
ORDER BY ?skillName
```

---

#### Query 13: Get All Departments

```sparql
PREFIX : <http://example.org/employee#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?deptName
WHERE {
    ?dept rdf:type :Department .
    ?dept :deptName ?deptName .
}
ORDER BY ?deptName
```

---

#### Query 14: Get All Projects with Required Skills

```sparql
PREFIX : <http://example.org/employee#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?projectName ?projectDescription
       (GROUP_CONCAT(?skillName; separator=", ") AS ?requiredSkills)
WHERE {
    ?project rdf:type :Project .
    ?project :projectName ?projectName .
    ?project :projectDescription ?projectDescription .
    ?project :requiresSkill ?skill .
    ?skill :skillName ?skillName .
}
GROUP BY ?projectName ?projectDescription
ORDER BY ?projectName
```

---

#### Query 15: Knowledge Graph Data (for Cytoscape.js visualization)

**Question answered:** "Give me all relationships for graph visualization."

```sparql
PREFIX : <http://example.org/employee#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?source ?sourceLabel ?sourceType ?relationship ?target ?targetLabel ?targetType
WHERE {
    {
        ?s rdf:type :Employee .
        ?s :name ?sourceLabel .
        ?s :hasSkill ?t .
        ?t :skillName ?targetLabel .
        BIND("Employee" AS ?sourceType)
        BIND("Skill" AS ?targetType)
        BIND("hasSkill" AS ?relationship)
        BIND(STR(?s) AS ?source)
        BIND(STR(?t) AS ?target)
    }
    UNION
    {
        ?s rdf:type :Employee .
        ?s :name ?sourceLabel .
        ?s :worksIn ?t .
        ?t :deptName ?targetLabel .
        BIND("Employee" AS ?sourceType)
        BIND("Department" AS ?targetType)
        BIND("worksIn" AS ?relationship)
        BIND(STR(?s) AS ?source)
        BIND(STR(?t) AS ?target)
    }
    UNION
    {
        ?s rdf:type :Employee .
        ?s :name ?sourceLabel .
        ?s :worksOn ?t .
        ?t :projectName ?targetLabel .
        BIND("Employee" AS ?sourceType)
        BIND("Project" AS ?targetType)
        BIND("worksOn" AS ?relationship)
        BIND(STR(?s) AS ?source)
        BIND(STR(?t) AS ?target)
    }
    UNION
    {
        ?s rdf:type :Skill .
        ?s :skillName ?sourceLabel .
        ?s :relatedTo ?t .
        ?t :skillName ?targetLabel .
        BIND("Skill" AS ?sourceType)
        BIND("Skill" AS ?targetType)
        BIND("relatedTo" AS ?relationship)
        BIND(STR(?s) AS ?source)
        BIND(STR(?t) AS ?target)
    }
    UNION
    {
        ?s rdf:type :Department .
        ?s :deptName ?sourceLabel .
        ?s :handlesProject ?t .
        ?t :projectName ?targetLabel .
        BIND("Department" AS ?sourceType)
        BIND("Project" AS ?targetType)
        BIND("handlesProject" AS ?relationship)
        BIND(STR(?s) AS ?source)
        BIND(STR(?t) AS ?target)
    }
    UNION
    {
        ?s rdf:type :Project .
        ?s :projectName ?sourceLabel .
        ?s :requiresSkill ?t .
        ?t :skillName ?targetLabel .
        BIND("Project" AS ?sourceType)
        BIND("Skill" AS ?targetType)
        BIND("requiresSkill" AS ?relationship)
        BIND(STR(?s) AS ?source)
        BIND(STR(?t) AS ?target)
    }
}
```

---

### Save Queries to Files

Organize queries into files by topic:

```text
queries/
├── employee_queries.rq      # Queries 1, 2, 3, 5, 8, 9, 10
├── skill_queries.rq         # Queries 4, 12
├── project_queries.rq       # Queries 6, 7, 14
├── department_queries.rq    # Queries 3 (dept version), 13
├── dashboard_queries.rq     # Query 11
└── graph_queries.rq         # Query 15
```

> **Note:** In the `.rq` files, store each query with a comment header like `# QUERY: employees_by_skill`. In the Flask backend, you will either read these files or embed the queries in Python strings. Both approaches work — embedding in Python is simpler for a student project.

### Files/Folders to Create or Modify

```text
queries/
├── employee_queries.rq      [NEW]
├── skill_queries.rq         [NEW]
├── project_queries.rq       [NEW]
├── department_queries.rq    [NEW]
├── dashboard_queries.rq     [NEW]
└── graph_queries.rq         [NEW]
tests/
└── test_sparql.py           [MODIFY] — Add query result validation
```

### Expected Output

After completing this phase:
- All 15 SPARQL queries are written, tested in Fuseki, and saved to `.rq` files
- Each query returns the expected results
- You understand how to parameterize queries for Flask

### How to Test

Test every query in the Fuseki UI (`http://localhost:3030/` → Query tab) and verify:

| Query | Expected Result |
|-------|----------------|
| Q1 (employees by skill = Python) | ~10 employees |
| Q2 (AI/ML employees) | Multiple employees with AI or ML |
| Q3 (employees in AI Dept) | 4 employees |
| Q4 (skills related to Python) | Machine Learning, AI |
| Q5 (employees with AWS Cert) | 3 employees |
| Q6 (candidates for AI Chatbot) | Employees ranked by matching skills |
| Q7 (projects by AI Dept) | AI Chatbot |
| Q8 (all info about EMP001) | All Aayush's data |
| Q9 (all employees) | 15 employees |
| Q10 (multi-skill match) | Employees with ≥2 skills |
| Q11 (dashboard counts) | 15, 8, 4, 3, 5 |
| Q12 (all skills) | 8 skills |
| Q13 (all departments) | 4 departments |
| Q14 (projects with skills) | 3 projects |
| Q15 (graph data) | All edges for visualization |

### Completion Checklist

- [ ] All 15 SPARQL queries written
- [ ] Every query tested in Fuseki UI with correct results
- [ ] Queries saved to `.rq` files organized by topic
- [ ] `tests/test_sparql.py` updated with automated query tests
- [ ] Git commit: `"Add all SPARQL queries for employee management"`

---

## Phase 8 — Flask Backend

### Objective

Build the Flask backend with API endpoints that receive requests, execute SPARQL queries against Fuseki, and return JSON responses.

### Why This Phase Is Needed

The backend is the bridge between the frontend and the triple store. The frontend doesn't talk to Fuseki directly — Flask handles query construction, error handling, and response formatting.

### Prerequisites

- Phase 6 completed (Fuseki running with data)
- Phase 7 completed (SPARQL queries tested)

### Tasks

1. **Create `config.py`** (update from Phase 1)

   ```python
   # config.py
   FUSEKI_URL = "http://localhost:3030"
   DATASET_NAME = "employees"
   SPARQL_ENDPOINT = f"{FUSEKI_URL}/{DATASET_NAME}/sparql"

   # Namespace used in our RDF data
   NAMESPACE = "http://example.org/employee#"
   ```

2. **Create a SPARQL helper module** — `sparql_client.py`

   This module encapsulates all communication with Fuseki:
   ```python
   # sparql_client.py
   # - Contains a function: execute_query(query_string) → dict
   # - Uses SPARQLWrapper to send queries to Fuseki
   # - Returns parsed JSON results
   # - Handles connection errors (Fuseki not running, etc.)
   ```

3. **Create `app.py`** with the following API endpoints:

   | Endpoint | Method | Description | SPARQL Query Used |
   |----------|--------|-------------|-------------------|
   | `/` | GET | Serves the dashboard page (HTML) | — |
   | `/employees` | GET | Serves the employees page (HTML) | — |
   | `/search` | GET | Serves the search page (HTML) | — |
   | `/projects` | GET | Serves the projects page (HTML) | — |
   | `/graph` | GET | Serves the graph visualization page (HTML) | — |
   | `/api/dashboard` | GET | Returns counts (employees, skills, depts, projects, certs) | Q11 |
   | `/api/employees` | GET | Returns all employees | Q9 |
   | `/api/employees/<emp_id>` | GET | Returns details of a specific employee | Q8 |
   | `/api/skills` | GET | Returns all skills | Q12 |
   | `/api/departments` | GET | Returns all departments | Q13 |
   | `/api/projects` | GET | Returns all projects with required skills | Q14 |
   | `/api/search/employees` | GET | Search employees by skill or department | Q1, Q2, Q3 |
   | `/api/search/related-skills` | GET | Find skills related to a given skill | Q4 |
   | `/api/search/certifications` | GET | Find employees by certification | Q5 |
   | `/api/projects/<project_name>/candidates` | GET | Find matching employees for a project | Q6 |
   | `/api/graph` | GET | Return all graph edges for visualization | Q15 |

4. **Endpoint Details**

   **`GET /api/dashboard`**
   - Parameters: None
   - Response:
     ```json
     {
       "employees": 15,
       "skills": 8,
       "departments": 4,
       "projects": 3,
       "certifications": 5
     }
     ```

   **`GET /api/employees`**
   - Parameters: None
   - Response:
     ```json
     {
       "employees": [
         {"empId": "EMP001", "name": "Aayush Kumar", "email": "aayush@company.com", "department": "AI Department"},
         ...
       ]
     }
     ```

   **`GET /api/employees/<emp_id>`**
   - Parameters: `emp_id` (path parameter, e.g., `EMP001`)
   - Response:
     ```json
     {
       "empId": "EMP001",
       "name": "Aayush Kumar",
       "email": "aayush@company.com",
       "department": "AI Department",
       "skills": ["Python", "Machine Learning", "Artificial Intelligence"],
       "certifications": ["Python Certification", "Data Science Certification"],
       "projects": ["AI Chatbot"]
     }
     ```
   - Error (employee not found):
     ```json
     { "error": "Employee not found", "empId": "EMP999" }
     ```
     HTTP status: 404

   **`GET /api/search/employees?skill=Python`**
   - Parameters: `skill` (query string)
   - Response:
     ```json
     {
       "query": "Python",
       "type": "skill",
       "results": [
         {"empId": "EMP001", "name": "Aayush Kumar", "email": "aayush@company.com"},
         ...
       ]
     }
     ```

   **`GET /api/search/employees?department=AI Department`**
   - Parameters: `department` (query string)
   - Response: Same structure with `"type": "department"`

   **`GET /api/search/related-skills?skill=Python`**
   - Parameters: `skill` (query string)
   - Response:
     ```json
     {
       "skill": "Python",
       "relatedSkills": ["Machine Learning", "Artificial Intelligence"]
     }
     ```

   **`GET /api/projects/<project_name>/candidates`**
   - Parameters: `project_name` (path parameter, URL-encoded)
   - Response:
     ```json
     {
       "project": "AI Chatbot",
       "candidates": [
         {"empId": "EMP001", "name": "Aayush Kumar", "matchingSkills": 3, "skills": "Python, AI, ML"},
         {"empId": "EMP013", "name": "Nikhil Rao", "matchingSkills": 3, "skills": "Python, AI, ML"},
         ...
       ]
     }
     ```

   **`GET /api/graph`**
   - Parameters: None
   - Response:
     ```json
     {
       "nodes": [
         {"id": "...", "label": "Aayush Kumar", "type": "Employee"},
         {"id": "...", "label": "Python", "type": "Skill"},
         ...
       ],
       "edges": [
         {"source": "...", "target": "...", "relationship": "hasSkill"},
         ...
       ]
     }
     ```

5. **Enable CORS** (if frontend is served separately during development)

   For simplicity, we serve HTML templates from Flask itself (using `render_template`), so CORS is not needed. But if you decide to develop the frontend separately, add:
   ```python
   from flask_cors import CORS
   CORS(app)
   ```
   And add `flask-cors` to `requirements.txt`.

### Files/Folders to Create or Modify

```text
app.py                  [MODIFY] — Full Flask application with all routes
config.py               [MODIFY] — Finalize configuration
sparql_client.py        [NEW] — SPARQL query execution helper
requirements.txt        [MODIFY] — Add any new dependencies if needed
```

### Expected Output

After completing this phase:
- Flask app runs at `http://127.0.0.1:5000/`
- All `/api/` endpoints return correct JSON when tested with a browser or `curl`
- SPARQL queries are executed against Fuseki and results are properly formatted

### How to Test

1. **Start Fuseki** with data loaded
2. **Start Flask:** `python app.py`
3. **Test each endpoint** using the browser address bar or `curl`:

| Endpoint | Test URL | Expected |
|----------|----------|----------|
| Dashboard | `http://127.0.0.1:5000/api/dashboard` | JSON with counts |
| All employees | `http://127.0.0.1:5000/api/employees` | 15 employees |
| One employee | `http://127.0.0.1:5000/api/employees/EMP001` | Aayush's details |
| Search by skill | `http://127.0.0.1:5000/api/search/employees?skill=Python` | Python employees |
| Related skills | `http://127.0.0.1:5000/api/search/related-skills?skill=Python` | ML, AI |
| Project candidates | `http://127.0.0.1:5000/api/projects/AI%20Chatbot/candidates` | Ranked candidates |
| Graph data | `http://127.0.0.1:5000/api/graph` | Nodes and edges |
| Invalid employee | `http://127.0.0.1:5000/api/employees/EMP999` | 404 error JSON |

### Completion Checklist

- [ ] `config.py` updated with all necessary settings
- [ ] `sparql_client.py` created with `execute_query()` function
- [ ] `app.py` created with all API endpoints listed above
- [ ] All endpoints return correct JSON responses
- [ ] Error handling for invalid IDs and missing parameters
- [ ] Error handling for Fuseki connection failure
- [ ] All endpoints tested manually
- [ ] `tests/test_api.py` created with basic endpoint tests
- [ ] Git commit: `"Add Flask backend with all API endpoints"`

---

## Phase 9 — Frontend (Core Pages)

### Objective

Build the HTML/CSS/JavaScript frontend with a dashboard, employee listing, and basic navigation. Connect the frontend to the Flask API.

### Why This Phase Is Needed

The frontend is how users interact with the system. Without it, the project is just an API — which is not suitable for a demo or viva.

### Prerequisites

- Phase 8 completed (Flask API working)

### Tasks

1. **Create `templates/base.html`** — shared layout

   This is the base template that all pages extend. It contains:
   - HTML boilerplate (`<!DOCTYPE html>`, `<head>`, etc.)
   - Navigation bar with links to: Dashboard, Employees, Search, Projects, Knowledge Graph
   - A `{% block content %}{% endblock %}` for page-specific content
   - Links to `style.css` and common JS
   - CDN link for Cytoscape.js (loaded on all pages, used only on graph page)

2. **Create `static/css/style.css`** — styling

   Design a clean, modern interface:
   - Color scheme: Use a professional palette (e.g., blues and grays, or a dark theme)
   - Navigation bar: Horizontal, fixed at top
   - Cards: For dashboard stats and employee info
   - Tables: For employee listings and search results
   - Responsive: Basic responsiveness (flex/grid)
   - Animations: Subtle hover effects on cards and buttons

   > Keep CSS manageable — one file is fine for this project.

3. **Create `templates/index.html`** — Dashboard

   The dashboard shows:
   - **Stat cards** showing counts: Employees, Skills, Departments, Projects, Certifications
   - On page load, JS fetches `/api/dashboard` and populates the cards
   - Optional: A welcome message explaining the system

   ```text
   ┌──────────────────────────────────────────────────────┐
   │ Navigation:  Dashboard | Employees | Search | ...   │
   ├──────────────────────────────────────────────────────┤
   │                                                      │
   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐│
   │  │ 15       │ │ 8        │ │ 4        │ │ 3       ││
   │  │Employees │ │ Skills   │ │  Depts   │ │Projects ││
   │  └──────────┘ └──────────┘ └──────────┘ └─────────┘│
   │                                                      │
   └──────────────────────────────────────────────────────┘
   ```

4. **Create `templates/employees.html`** — Employee listing

   - On page load, JS fetches `/api/employees` and renders a table or card grid
   - Each employee shows: ID, Name, Email, Department
   - Clicking an employee shows a detail modal or expands to show skills, certifications, projects (fetched from `/api/employees/<id>`)

   ```text
   ┌──────────────────────────────────────────────────────┐
   │ Employees                                            │
   ├──────────────────────────────────────────────────────┤
   │ ID      Name           Email              Dept      │
   │ EMP001  Aayush Kumar   aayush@company...  AI Dept   │
   │ EMP002  Priya Sharma   priya@company...   Data Sci  │
   │ ...                                                  │
   └──────────────────────────────────────────────────────┘
   ```

5. **Create `static/js/app.js`** — shared JavaScript utilities

   Contains:
   - A helper function to make API calls: `async function apiGet(url)`
   - A helper to create HTML elements from data
   - Error display function

6. **Wire up Flask template rendering**

   In `app.py`, the non-API routes should render templates:
   ```python
   @app.route("/")
   def dashboard():
       return render_template("index.html")

   @app.route("/employees")
   def employees_page():
       return render_template("employees.html")
   ```

### Files/Folders to Create or Modify

```text
templates/
├── base.html           [NEW] — Base template with navigation
├── index.html          [NEW] — Dashboard page
└── employees.html      [NEW] — Employee listing page
static/
├── css/
│   └── style.css       [NEW] — All styles
└── js/
    └── app.js          [NEW] — Shared JS utilities + dashboard/employee logic
app.py                  [MODIFY] — Add template rendering routes
```

### Expected Output

After completing this phase:
- Dashboard page loads at `http://127.0.0.1:5000/` and shows stat cards with real data
- Employees page loads at `http://127.0.0.1:5000/employees` and shows all 15 employees
- Clicking an employee shows their full details (skills, certifications, projects)
- Navigation bar works across all pages
- The UI looks clean and professional

### How to Test

| Test | How | Expected Result |
|------|-----|-----------------|
| Dashboard loads | Visit `http://127.0.0.1:5000/` | Page renders with stat cards |
| Stats are correct | Check card values | 15 employees, 8 skills, etc. |
| Employees load | Visit `http://127.0.0.1:5000/employees` | Table shows 15 employees |
| Employee details | Click an employee | Skills, certs, projects appear |
| Navigation works | Click each nav link | Correct page loads |
| No console errors | Open browser DevTools → Console | No JavaScript errors |

### Completion Checklist

- [ ] `templates/base.html` created with navigation and layout
- [ ] `templates/index.html` created — dashboard with stat cards
- [ ] `templates/employees.html` created — employee listing with detail view
- [ ] `static/css/style.css` created with professional styling
- [ ] `static/js/app.js` created with API helper and page logic
- [ ] Dashboard fetches and displays live data from `/api/dashboard`
- [ ] Employee page fetches and displays data from `/api/employees`
- [ ] Employee detail view works (fetches from `/api/employees/<id>`)
- [ ] Navigation bar links work
- [ ] No JavaScript console errors
- [ ] Git commit: `"Add frontend dashboard and employee pages"`

---

## Phase 10 — Semantic Search

### Objective

Build the semantic search page where users can search for employees by skill, department, or certification, and explore related skills.

### Why This Phase Is Needed

Semantic search is the **key differentiator** of this project from a regular employee database. It demonstrates how SPARQL can traverse the knowledge graph to answer complex questions. This is the feature you'll spend the most time explaining during your viva.

### Prerequisites

- Phase 8 completed (search API endpoints working)
- Phase 9 completed (frontend foundation built)

### Tasks

1. **Create `templates/search.html`** — Search page

   Layout:
   ```text
   ┌──────────────────────────────────────────────────────┐
   │ Semantic Search                                      │
   ├──────────────────────────────────────────────────────┤
   │                                                      │
   │  Search Type: [Skill ▼] [Department ▼] [Cert ▼]     │
   │                                                      │
   │  Search Term: [_dropdown/input_______] [🔍 Search]   │
   │                                                      │
   │  ── Related Skills ──────────────────────────────    │
   │  Python is related to: Machine Learning, AI          │
   │                                                      │
   │  ── Matching Employees ──────────────────────────    │
   │  ┌───────────────────────────────────────────────┐   │
   │  │ Aayush Kumar  | aayush@company.com | AI Dept │   │
   │  │ Priya Sharma  | priya@company.com  | Data Sci│   │
   │  │ ...                                           │   │
   │  └───────────────────────────────────────────────┘   │
   └──────────────────────────────────────────────────────┘
   ```

2. **Implement search functionality in `static/js/search.js`**

   - On page load, fetch `/api/skills`, `/api/departments` to populate dropdowns
   - When user selects a search type (skill/department/certification) and value, call the appropriate API endpoint
   - Display results in a table
   - If searching by skill, also fetch and display related skills from `/api/search/related-skills`

3. **Create `templates/projects.html`** — Project matching page

   Layout:
   ```text
   ┌──────────────────────────────────────────────────────┐
   │ Project Skill Matching                               │
   ├──────────────────────────────────────────────────────┤
   │                                                      │
   │  Select Project: [AI Chatbot ▼]                      │
   │                                                      │
   │  Required Skills: Python, AI, Machine Learning       │
   │                                                      │
   │  ── Matching Employees ──────────────────────────    │
   │  │ Name          │ Matching Skills │ Skills     │    │
   │  │ Aayush Kumar  │ 3/3            │ Python,... │    │
   │  │ Nikhil Rao    │ 3/3            │ Python,... │    │
   │  │ Priya Sharma  │ 2/3            │ Python,... │    │
   │  │ ...                                          │    │
   │  └──────────────────────────────────────────────┘    │
   └──────────────────────────────────────────────────────┘
   ```

4. **Wire up Flask routes**

   ```python
   @app.route("/search")
   def search_page():
       return render_template("search.html")

   @app.route("/projects")
   def projects_page():
       return render_template("projects.html")
   ```

### Files/Folders to Create or Modify

```text
templates/
├── search.html         [NEW] — Semantic search page
└── projects.html       [NEW] — Project matching page
static/js/
└── search.js           [NEW] — Search and project matching logic
app.py                  [MODIFY] — Add template routes for search/projects
```

### Expected Output

After completing this phase:
- Search page works: user can select "Skill → Python" and see matching employees
- Related skills are displayed when searching by skill
- Project matching page works: user selects a project and sees ranked employee candidates
- Empty results are handled gracefully (shows "No results found" message)

### How to Test

| Test | How | Expected Result |
|------|-----|-----------------|
| Search by skill | Select Skill → Python → Search | Shows ~10 employees |
| Search by department | Select Department → AI Department | Shows 4 employees |
| Search by certification | Select Certification → AWS | Shows 3 employees |
| Related skills | Search by Python skill | Shows "Related: Machine Learning, AI" |
| Project candidates | Select "AI Chatbot" | Shows employees ranked by matching skills |
| Empty result | Search for a non-existent skill | Shows "No results found" |

### Completion Checklist

- [ ] `templates/search.html` created
- [ ] `templates/projects.html` created
- [ ] `static/js/search.js` created with all search logic
- [ ] Skill search works and shows matching employees
- [ ] Department search works
- [ ] Certification search works
- [ ] Related skills are displayed for skill searches
- [ ] Project matching works with ranked candidates
- [ ] Empty results handled gracefully
- [ ] Git commit: `"Add semantic search and project matching pages"`

---

## Phase 11 — Knowledge Graph Visualization

### Objective

Build an interactive knowledge graph visualization using **Cytoscape.js** that shows the relationships between employees, skills, departments, projects, and certifications.

### Why This Phase Is Needed

A knowledge graph visualization is the most visually impressive part of the project. It turns abstract RDF triples into a visual network that anyone can understand. This is excellent for demos and vivas.

### Prerequisites

- Phase 8 completed (graph API endpoint `/api/graph` working)
- Phase 9 completed (frontend foundation)

### Key Concepts Introduced

**Cytoscape.js:**
A JavaScript library for displaying and interacting with graph networks in the browser. It takes nodes (circles) and edges (lines) and arranges them in a layout. We provide data; Cytoscape.js handles the rendering.

### Tasks

1. **Create `templates/graph.html`** — Graph visualization page

   Layout:
   ```text
   ┌──────────────────────────────────────────────────────┐
   │ Knowledge Graph                                      │
   ├──────────────────────────────────────────────────────┤
   │ Filter: [✓ Employees] [✓ Skills] [✓ Depts] [✓ Proj] │
   │                                                      │
   │  ┌──────────────────────────────────────────────┐    │
   │  │                                              │    │
   │  │         ○ AI Dept                            │    │
   │  │        / \                                   │    │
   │  │       /   \                                  │    │
   │  │   ○ Aayush  ○ Sneha                         │    │
   │  │    |   \                                     │    │
   │  │    |    ○ Python ── ○ Machine Learning       │    │
   │  │    |                                         │    │
   │  │    ○ AI Chatbot                              │    │
   │  │                                              │    │
   │  └──────────────────────────────────────────────┘    │
   │                                                      │
   │ Legend: 🔵 Employee  🟢 Skill  🟠 Department  🔴 Proj│
   └──────────────────────────────────────────────────────┘
   ```

2. **Create `static/js/graph.js`** — Graph visualization logic

   Steps:
   1. Fetch data from `/api/graph`
   2. Transform the API response into Cytoscape.js format:
      ```javascript
      // Cytoscape.js expects:
      const elements = {
          nodes: [
              { data: { id: "emp001", label: "Aayush Kumar", type: "Employee" } },
              { data: { id: "python", label: "Python", type: "Skill" } },
              ...
          ],
          edges: [
              { data: { source: "emp001", target: "python", label: "hasSkill" } },
              ...
          ]
      };
      ```
   3. Initialize Cytoscape:
      ```javascript
      const cy = cytoscape({
          container: document.getElementById('graph-container'),
          elements: elements,
          style: [
              // Node styles by type (different colors for Employee, Skill, etc.)
              // Edge styles with labels
          ],
          layout: {
              name: 'cose'  // Force-directed layout — good default
          }
      });
      ```
   4. Color nodes by type:
      - **Employee** → Blue
      - **Skill** → Green
      - **Department** → Orange
      - **Project** → Red
      - **Certification** → Purple
   5. Show edge labels (hasSkill, worksIn, etc.)
   6. Add click handler: clicking a node shows its details in a side panel or tooltip

3. **Add filter checkboxes** (Good to Have)

   Allow user to show/hide node types. When "Employees" is unchecked, hide all Employee nodes and their edges.

### Files/Folders to Create or Modify

```text
templates/
└── graph.html          [NEW] — Knowledge graph page
static/js/
└── graph.js            [NEW] — Cytoscape.js visualization logic
static/css/
└── style.css           [MODIFY] — Add graph container styles
```

### Expected Output

After completing this phase:
- Knowledge graph page shows an interactive network visualization
- Nodes are colored by type with a legend
- Edges show relationship labels
- User can drag nodes, zoom in/out, and pan
- Clicking a node optionally shows details

### How to Test

| Test | How | Expected Result |
|------|-----|-----------------|
| Graph loads | Visit `/graph` | Network visualization appears |
| Nodes visible | Check the graph | Multiple colored nodes |
| Edges visible | Check connections | Lines between related nodes |
| Interactive | Drag a node | Node moves; connected edges follow |
| Zoom | Scroll wheel | Graph zooms in/out |
| Colors correct | Check legend against nodes | Employee=blue, Skill=green, etc. |
| No console errors | DevTools → Console | Clean |

### Completion Checklist

- [ ] `templates/graph.html` created with Cytoscape.js container
- [ ] `static/js/graph.js` created with data fetching and visualization
- [ ] Cytoscape.js loaded via CDN
- [ ] Nodes colored by entity type
- [ ] Edge labels shown
- [ ] Graph is interactive (drag, zoom, pan)
- [ ] Legend showing node type colors
- [ ] Filter checkboxes work (Good to Have)
- [ ] Git commit: `"Add knowledge graph visualization with Cytoscape.js"`

---

## Phase 12 — Error Handling & Polish

### Objective

Add comprehensive error handling throughout the application and polish the user experience.

### Why This Phase Is Needed

Without error handling, the application crashes or shows confusing errors when something goes wrong (invalid input, Fuseki down, empty results). Good error handling makes the app feel professional and is important for the viva.

### Prerequisites

- Phases 8–11 completed (full application working)

### Tasks

1. **Backend error handling** — Update `app.py` and `sparql_client.py`:

   | Error Scenario | Status Code | Response |
   |----------------|-------------|----------|
   | Invalid employee ID (not found) | 404 | `{"error": "Employee not found", "empId": "EMP999"}` |
   | Unknown skill (no results) | 200 | `{"query": "UnknownSkill", "results": [], "message": "No employees found with this skill"}` |
   | Unknown project | 404 | `{"error": "Project not found"}` |
   | Fuseki not running | 503 | `{"error": "Triple store unavailable. Please ensure Fuseki is running."}` |
   | Missing search parameter | 400 | `{"error": "Missing required parameter: skill or department"}` |
   | Invalid API route | 404 | `{"error": "Endpoint not found"}` |

2. **Frontend error handling** — Update JavaScript:

   - Show user-friendly error messages in the UI (not just console.log)
   - Display a "Connection error: Please make sure the server is running" message if API calls fail
   - Show "No results found" with a friendly message when search returns empty
   - Show a loading spinner while waiting for API responses

3. **UI Polish**:

   - Loading states: Show a spinner or "Loading..." while fetching data
   - Empty states: Show a message when no data matches the search
   - Consistent styling across all pages
   - Ensure all pages render correctly at different browser widths
   - Add a favicon (optional)

4. **Add a custom error page** for 404 and 500 errors in Flask

### Files/Folders to Create or Modify

```text
app.py                  [MODIFY] — Add error handlers
sparql_client.py        [MODIFY] — Add try/except for connection errors
static/js/app.js        [MODIFY] — Add error display functions
static/js/search.js     [MODIFY] — Add loading/empty/error states
static/css/style.css    [MODIFY] — Add loading spinner, error message styles
templates/
└── error.html          [NEW] — Generic error page template (optional)
```

### Expected Output

- Application handles all error scenarios gracefully
- User sees friendly messages instead of crashes or blank screens
- Loading indicators appear during data fetching

### How to Test

| Test | How | Expected Result |
|------|-----|-----------------|
| Invalid employee | Visit `/api/employees/EMP999` | 404 JSON error |
| Fuseki down | Stop Fuseki, then visit `/api/employees` | 503 error with friendly message |
| Empty search | Search for "COBOL" skill | "No employees found" message |
| Missing param | Visit `/api/search/employees` (no params) | 400 error |
| Loading state | Search with DevTools network throttling on "Slow 3G" | Spinner visible |

### Completion Checklist

- [ ] Backend returns proper HTTP status codes for all error scenarios
- [ ] Frontend displays user-friendly error messages
- [ ] Loading spinners appear during data fetching
- [ ] Empty states show "No results found" messages
- [ ] Fuseki connection failure is handled gracefully
- [ ] 404 page works for invalid routes
- [ ] Git commit: `"Add error handling and UI polish"`

---

## Phase 13 — Testing

### Objective

Write and run automated tests for the RDF data, SPARQL queries, and Flask API. Perform manual testing for the frontend.

### Why This Phase Is Needed

Testing ensures everything works correctly and helps catch regressions. It's also an important section in your project report and viva.

### Prerequisites

- All previous phases completed

### Tasks

1. **RDF Validation Tests** (`tests/test_rdf.py`)

   ```python
   # Test that employees.ttl is valid Turtle
   # Test that the ontology is valid
   # Test entity counts (15 employees, 8 skills, etc.)
   # Test specific relationships exist
   # Test that all predicates used in data are defined in ontology
   ```

2. **SPARQL Query Tests** (`tests/test_sparql.py`)

   ```python
   # Requires Fuseki to be running
   # Test each SPARQL query returns expected results
   # Test Q1: Employees with Python skill → at least 5 results
   # Test Q3: Employees in AI Department → exactly 4 results
   # Test Q4: Skills related to Python → includes "Machine Learning"
   # Test Q11: Dashboard counts → 15, 8, 4, 3, 5
   ```

3. **Flask API Tests** (`tests/test_api.py`)

   ```python
   # Use Flask test client
   # Test GET /api/dashboard → 200, correct JSON structure
   # Test GET /api/employees → 200, 15 employees
   # Test GET /api/employees/EMP001 → 200, name is "Aayush Kumar"
   # Test GET /api/employees/EMP999 → 404
   # Test GET /api/search/employees?skill=Python → 200, results non-empty
   # Test GET /api/search/employees (no params) → 400
   # Test GET /api/graph → 200, has nodes and edges
   ```

4. **Manual Frontend Testing Checklist**

   | Page | Test | Expected |
   |------|------|----------|
   | Dashboard | Page loads | Stat cards with correct numbers |
   | Dashboard | Cards visible | 5 cards displayed |
   | Employees | Page loads | Table/cards with 15 employees |
   | Employees | Click employee | Details expand/modal shows |
   | Search | Search by skill | Matching employees shown |
   | Search | Search by department | Matching employees shown |
   | Search | Related skills shown | Displayed below search |
   | Projects | Select project | Candidates listed |
   | Graph | Page loads | Cytoscape graph renders |
   | Graph | Drag node | Node moves |
   | Graph | Zoom | Graph zooms |
   | Navigation | All links work | Correct pages load |
   | Errors | Stop Fuseki, search | Error message shown |

5. **Run all tests**
   ```bash
   python -m pytest tests/ -v
   ```

### Files/Folders to Create or Modify

```text
tests/
├── test_rdf.py         [MODIFY] — Complete RDF validation tests
├── test_sparql.py      [MODIFY] — Complete SPARQL query tests
└── test_api.py         [NEW/MODIFY] — Flask API tests
```

### Expected Output

- All automated tests pass
- Manual frontend testing checklist completed with all items verified

### How to Test

```bash
# Run all tests
python -m pytest tests/ -v

# Expected: all tests green
```

### Completion Checklist

- [ ] `tests/test_rdf.py` — RDF validation tests pass
- [ ] `tests/test_sparql.py` — SPARQL query tests pass (Fuseki running)
- [ ] `tests/test_api.py` — Flask API tests pass (Fuseki running)
- [ ] Manual frontend testing — all items verified
- [ ] All tests documented in the project report
- [ ] Git commit: `"Add automated tests for RDF, SPARQL, and API"`

---

## Phase 14 — Documentation & Viva Preparation

### Objective

Write the final project report and prepare for the viva/project review.

### Why This Phase Is Needed

Documentation is a required deliverable for any academic project. The viva is where you demonstrate understanding. Without preparation, even a well-built project can get a poor grade.

### Prerequisites

- All previous phases completed and tested

### Tasks

1. **Write the Project Report** (`docs/report.md`)

   Structure:

   | # | Section | Contents |
   |---|---------|----------|
   | 1 | Abstract | 200-word summary of the project |
   | 2 | Introduction | What is Semantic Web and why it matters |
   | 3 | Problem Statement | Limitations of traditional employee databases |
   | 4 | Objectives | What the system aims to achieve (bulleted list) |
   | 5 | Existing System | How companies currently manage employee skills (tables, spreadsheets) |
   | 6 | Proposed System | Our knowledge-graph-based approach |
   | 7 | Technologies Used | Table of all technologies with version numbers |
   | 8 | System Architecture | Architecture diagram from Section 2 of this plan |
   | 9 | RDF Model | Explain triples, Turtle format, show examples |
   | 10 | OWL Ontology | Explain classes, properties, domain/range |
   | 11 | SPARQL Queries | Show 5–7 key queries with explanations |
   | 12 | Database/Triple Store | Explain Fuseki, how data is loaded and queried |
   | 13 | Application Screenshots | Screenshots of every page |
   | 14 | Testing | Test results, what was tested and how |
   | 15 | Results | Key findings: "the system successfully answers X types of queries" |
   | 16 | Limitations | List 4–5 honest limitations |
   | 17 | Future Scope | List 4–5 possible improvements |
   | 18 | Conclusion | 1 paragraph summary |
   | 19 | References | Books, websites, papers used |

2. **Update `README.md`** with:
   - Project description
   - Technology stack
   - Setup instructions (Python, Fuseki, running the app)
   - Screenshots
   - How to run tests
   - Folder structure explanation

3. **Take screenshots** of every page for the report

4. **Prepare for viva** — study the concepts in the Viva Preparation section (end of this document)

### Files/Folders to Create or Modify

```text
docs/
└── report.md           [NEW] — Complete project report
README.md               [MODIFY] — Final documentation
```

### Expected Output

- Complete project report with all 19 sections
- Comprehensive README.md
- Screenshots included
- You can confidently explain every concept from the viva list

### How to Test

| Test | How | Expected Result |
|------|-----|-----------------|
| Report completeness | Check each section | All 19 sections present |
| Screenshots | Open report | Images render correctly |
| README | Read through | Covers setup, usage, and structure |
| Viva readiness | Have someone quiz you on 10 concepts | You can explain each in 2–3 sentences |

### Completion Checklist

- [ ] `docs/report.md` created with all 19 sections
- [ ] Screenshots taken and included
- [ ] `README.md` updated with complete documentation
- [ ] All viva questions reviewed and answers prepared
- [ ] Final Git commit: `"Add project documentation and finalize"`
- [ ] Git tag: `git tag v1.0`

---

## Git / GitHub Strategy

### Repository Setup

```bash
git init
git remote add origin https://github.com/<username>/semantic-employee-system.git
```

### Commit Strategy

Make one commit per phase completion. Use clear, descriptive messages:

| Phase | Commit Message |
|-------|---------------|
| 1 | `Initial project setup with folder structure and Flask skeleton` |
| 2 | `Add data model design document` |
| 3 | `Add RDF data model in Turtle format` |
| 4 | `Add OWL ontology for employee skill management` |
| 5 | `Complete sample RDF data for all 15 employees` |
| 6 | `Configure Apache Jena Fuseki and load RDF data` |
| 7 | `Add all SPARQL queries for employee management` |
| 8 | `Add Flask backend with all API endpoints` |
| 9 | `Add frontend dashboard and employee pages` |
| 10 | `Add semantic search and project matching pages` |
| 11 | `Add knowledge graph visualization with Cytoscape.js` |
| 12 | `Add error handling and UI polish` |
| 13 | `Add automated tests for RDF, SPARQL, and API` |
| 14 | `Add project documentation and finalize` |

### Branching

Use a **simple branching strategy**:
- `main` branch — stable, working code
- Work directly on `main` for simplicity (this is a solo student project, not a team project)
- If you want to experiment, create a branch: `git checkout -b experiment/feature-name`

> **Do NOT** overcomplicate with Git Flow, release branches, or pull request workflows. This is a solo academic project.

### Pushing to GitHub

```bash
git push -u origin main
```

Push after each phase is complete and tested.

---

## Risk Management

### Risk 1: Difficulty Understanding RDF

| Aspect | Detail |
|--------|--------|
| **Likely cause** | RDF is a new concept; thinking in triples instead of tables is unfamiliar |
| **Simple solution** | Practice by hand: write 5 triples about yourself (your name, your skills, your department). Read the W3C Turtle primer. Use rdflib to parse and print triples. |
| **How to verify the fix** | You can look at any Turtle file and explain what each triple means in plain English |

### Risk 2: OWL Ontology Errors

| Aspect | Detail |
|--------|--------|
| **Likely cause** | Typos in property names, wrong domain/range, missing prefix declarations |
| **Simple solution** | Use rdflib to parse the ontology file — it will report syntax errors. Keep the ontology simple. Compare property names used in `employees.ttl` against those defined in `employee_ontology.owl`. |
| **How to verify the fix** | `python -c "from rdflib import Graph; g = Graph(); g.parse('ontology/employee_ontology.owl', format='turtle'); print('OK')"` |

### Risk 3: Fuseki Configuration Problems

| Aspect | Detail |
|--------|--------|
| **Likely cause** | Java not installed (Fuseki requires Java), port 3030 already in use, dataset not created |
| **Simple solution** | Install Java (JDK 11+). Check port: `netstat -an | findstr 3030`. Create dataset via UI. Re-upload data after restart if using in-memory mode. |
| **How to verify the fix** | Fuseki admin UI loads at `http://localhost:3030/` and a simple `SELECT *` query returns results |

### Risk 4: SPARQL Query Errors

| Aspect | Detail |
|--------|--------|
| **Likely cause** | Syntax errors, wrong property names, missing PREFIX declarations, mismatched variable names |
| **Simple solution** | Always test queries in the Fuseki UI first (it shows error messages). Start with the simplest possible query and add complexity step by step. Ensure PREFIX declarations match the namespace in your data. |
| **How to verify the fix** | Query runs in Fuseki UI without errors and returns expected results |

### Risk 5: Flask–Fuseki Connection Issues

| Aspect | Detail |
|--------|--------|
| **Likely cause** | Wrong Fuseki URL in config, Fuseki not running, network issues |
| **Simple solution** | Verify the URL in `config.py`. Test connectivity manually: `curl http://localhost:3030/employees/sparql`. Ensure Fuseki is started before Flask. Add try/except in `sparql_client.py` with clear error messages. |
| **How to verify the fix** | `/api/employees` returns JSON with 15 employees |

### Risk 6: Frontend–Backend Integration Problems

| Aspect | Detail |
|--------|--------|
| **Likely cause** | Wrong API URL in JavaScript, CORS issues (if frontend and backend on different ports), JSON parsing errors |
| **Simple solution** | Since we serve HTML from Flask (same origin), CORS is not an issue. Use browser DevTools → Network tab to inspect API requests and responses. Console.log the response before processing it. |
| **How to verify the fix** | Network tab shows successful API calls with correct JSON responses |

### Risk 7: Incorrect RDF Relationships

| Aspect | Detail |
|--------|--------|
| **Likely cause** | Domain and range mismatch (e.g., accidentally using `hasSkill` on a Department), wrong object URIs |
| **Simple solution** | Review the data model from Phase 2. For each triple in `employees.ttl`, verify: is the subject the right type? Is the predicate appropriate? Is the object the right entity? |
| **How to verify the fix** | SPARQL queries return logically correct results (e.g., "employees in AI Department" doesn't return skills) |

### Risk 8: Cytoscape.js Graph Not Rendering

| Aspect | Detail |
|--------|--------|
| **Likely cause** | CDN link broken, container div has zero height, data format incorrect |
| **Simple solution** | Check CDN link loads (visit the URL directly). Give the graph container explicit height in CSS (e.g., `height: 600px`). Console.log the data before passing to Cytoscape. |
| **How to verify the fix** | Graph renders with visible nodes and edges |

---

## Final Implementation Roadmap

```text
PHASE 1  → Project Setup (Environment, tools, folder structure)
    ↓
PHASE 2  → Data Model Design (Entities, attributes, relationships on paper)
    ↓
PHASE 3  → RDF Representation (Learn Turtle, write partial data)
    ↓
PHASE 4  → OWL Ontology Design (Define classes and properties)
    ↓
PHASE 5  → Sample RDF Data (Complete all 15 employees in Turtle)
    ↓
PHASE 6  → Apache Jena Fuseki Setup (Install, create dataset, load data)
    ↓
PHASE 7  → SPARQL Queries (Write and test all 15 queries)
    ↓
PHASE 8  → Flask Backend (API endpoints, SPARQL integration)
    ↓
PHASE 9  → Frontend Core Pages (Dashboard, employees, navigation)
    ↓
PHASE 10 → Semantic Search (Search page, project matching)
    ↓
PHASE 11 → Knowledge Graph Visualization (Cytoscape.js)
    ↓
PHASE 12 → Error Handling & Polish (Graceful errors, loading states)
    ↓
PHASE 13 → Testing (Automated + manual)
    ↓
PHASE 14 → Documentation & Viva Preparation (Report, README)
```

### Recommended Implementation Order

Follow the phases **exactly in order** (1 → 14). Each phase builds on the previous one. The dependency chain is:

```text
Setup → Data Model → RDF → Ontology → Data → Fuseki → SPARQL → Flask → Frontend → Search → Graph → Polish → Test → Docs
```

### Time Estimation

| Phase | Estimated Time | Cumulative |
|-------|---------------|------------|
| Phase 1 — Setup | 2–3 hours | 3 hours |
| Phase 2 — Data Model | 2–3 hours | 6 hours |
| Phase 3 — RDF | 3–4 hours | 10 hours |
| Phase 4 — OWL Ontology | 2–3 hours | 13 hours |
| Phase 5 — Sample Data | 2–3 hours | 16 hours |
| Phase 6 — Fuseki | 2–3 hours | 19 hours |
| Phase 7 — SPARQL | 4–5 hours | 24 hours |
| Phase 8 — Flask | 5–6 hours | 30 hours |
| Phase 9 — Frontend | 6–8 hours | 38 hours |
| Phase 10 — Search | 4–5 hours | 43 hours |
| Phase 11 — Graph | 4–5 hours | 48 hours |
| Phase 12 — Polish | 3–4 hours | 52 hours |
| Phase 13 — Testing | 3–4 hours | 56 hours |
| Phase 14 — Docs | 4–5 hours | 61 hours |

**Total estimated time: ~60 hours** (spread over 3–4 weeks)

### Phases That Can Be Skipped If Short on Time

| Phase | Can Skip? | Impact |
|-------|-----------|--------|
| Phase 12 (Error Handling) | Partially | App works but crashes on edge cases |
| Phase 11 (Graph Visualization) | Yes, with reduced grade | Loses the visual impact, but core functionality remains |
| Phase 13 (Testing) | Partially | Skip automated tests; keep manual testing |
| Phase 10 (Search, partially) | Project matching can be skipped | Loses project-to-employee feature |

> **Never skip:** Phases 1–9. These are the absolute minimum for a working project.

### Minimum Viable Project (if extremely short on time)

If you can only complete 8 phases, do these:
1. Setup → 2. Data Model → 3. RDF → 4. Ontology → 5. Data → 6. Fuseki → 7. SPARQL → 8. Flask → 9. Frontend (basic)

This gives you a working system with RDF + OWL + SPARQL + Flask + Web UI — enough to demonstrate Semantic Web technologies.

---

## Viva Preparation

### Important Concepts to Explain

---

#### 1. What is Semantic Web?

The Semantic Web is an extension of the World Wide Web where information is given well-defined meaning, making it easier for machines to process and understand data. It was proposed by Tim Berners-Lee (inventor of the Web). Instead of web pages designed for humans, the Semantic Web creates a "web of data" that machines can interpret. Key technologies include RDF, OWL, and SPARQL.

---

#### 2. What is RDF?

RDF (Resource Description Framework) is a standard model for data representation on the web. It represents information as **triples** — three-part statements that describe relationships between resources. Everything in RDF is either a **resource** (identified by a URI) or a **literal** (a plain value like a string or number). RDF can be serialized in formats like Turtle, XML, or JSON-LD.

---

#### 3. What is an RDF Triple?

An RDF triple consists of three parts:
- **Subject:** The entity the triple is about (e.g., `:EMP001`)
- **Predicate:** The property or relationship (e.g., `:hasSkill`)
- **Object:** The value or related entity (e.g., `:Python`)

Together, they form a statement: "EMP001 has the skill Python." Every piece of data in our system is represented as one or more triples.

---

#### 4. RDF vs Relational Database

| Aspect | Relational Database | RDF |
|--------|-------------------|-----|
| Data model | Tables with fixed columns | Graph of triples |
| Schema | Must define tables/columns first | Schema-free (ontology is optional) |
| Relationships | Foreign keys + JOINs | Relationships are first-class (predicates) |
| Query language | SQL | SPARQL |
| Adding new data types | Requires ALTER TABLE | Just add new triples |
| Best for | Structured, predictable data | Interconnected, flexible data |

---

#### 5. What is OWL?

OWL (Web Ontology Language) is a language for defining **ontologies** — formal descriptions of the types of things (classes), relationships (properties), and constraints in a domain. In our project, OWL defines that `Employee`, `Skill`, `Department` are classes, and `hasSkill` is a relationship from `Employee` to `Skill`.

---

#### 6. Why Use an Ontology?

An ontology provides:
- **Shared vocabulary:** Everyone uses the same terms for the same concepts
- **Formal semantics:** Machines can understand what "Employee" and "hasSkill" mean
- **Validation:** We can check that data follows the expected structure (e.g., only Employees can "have" Skills)
- **Interoperability:** Other systems can understand our data if they read our ontology

---

#### 7. What is SPARQL?

SPARQL (SPARQL Protocol and RDF Query Language) is the query language for RDF data — similar to how SQL is the query language for relational databases. SPARQL uses **pattern matching** to find triples in the graph. You write a pattern with variables (e.g., `?emp :hasSkill :Python`), and SPARQL finds all triples that match.

---

#### 8. RDF vs OWL

| Aspect | RDF | OWL |
|--------|-----|-----|
| Purpose | Data representation | Data modeling / schema |
| Contains | Actual data (triples) | Class and property definitions |
| Example | `:EMP001 :hasSkill :Python .` | `:hasSkill rdf:type owl:ObjectProperty .` |
| Analogy | Rows in a database | Table schema definition |

RDF stores the **instances** (actual data). OWL defines the **structure** (what types of things and relationships exist). They work together.

---

#### 9. What is a Triple Store?

A triple store is a database optimized for storing and querying RDF triples. Unlike relational databases that store data in tables, a triple store stores data as subject-predicate-object triples and provides a SPARQL endpoint for querying. Examples: Apache Jena Fuseki, GraphDB, Virtuoso, Stardog.

---

#### 10. Why Apache Jena Fuseki?

We chose Fuseki because:
- It's **free and open-source**
- It provides a **built-in SPARQL endpoint** (HTTP server for queries)
- It has a **web-based admin UI** for easy management
- It's part of the **Apache Jena** project — one of the most widely used RDF frameworks
- It's **easy to set up** — just download and run, no complex installation
- It supports **Turtle and other RDF formats** natively

---

#### 11. What is RDFLib?

RDFLib is a Python library for working with RDF. It can **parse** RDF files (Turtle, XML, etc.), create and manipulate RDF graphs in memory, and **serialize** them back to files. In our project, we use RDFLib mainly for **validation** — checking that our Turtle files are syntactically correct and contain the expected data.

---

#### 12. How Does Flask Communicate with Fuseki?

Flask communicates with Fuseki via **HTTP**:
1. Flask constructs a SPARQL query string
2. Flask sends an HTTP POST request to `http://localhost:3030/employees/sparql` with the query
3. Fuseki processes the query against its RDF graph
4. Fuseki returns results as JSON
5. Flask parses the JSON and formats it for the frontend

We use the `SPARQLWrapper` Python library to handle the HTTP communication.

---

#### 13. How Does Semantic Search Work?

Semantic search uses the **relationships in the knowledge graph** to find results. Unlike keyword search (which matches text), semantic search traverses the graph:

1. User searches for "Python"
2. System finds all employees with `:hasSkill :Python` (direct match)
3. System also finds skills `:relatedTo :Python` (like Machine Learning)
4. System can find employees who have related skills (indirect match)

This is powerful because relationships like `relatedTo` are explicitly modeled — the system doesn't need to "guess" that Python and Machine Learning are related.

---

#### 14. Why is This Different from a Normal Employee Database?

In a traditional database:
- Data is in rigid tables (employees table, skills table, employee_skills junction table)
- Queries require complex JOINs to traverse relationships
- Adding a new type of relationship requires schema changes (ALTER TABLE)
- No built-in concept of "related skills" or "skill similarity"

In our Semantic Web system:
- Data is a flexible graph of interconnected facts
- SPARQL naturally traverses relationships without complex JOINs
- Adding new relationships is as simple as adding new triples
- Relationships like `relatedTo` are explicit and queryable
- The system is self-describing (the ontology explains what the data means)

---

#### 15. What is a Knowledge Graph?

A knowledge graph is a network of real-world entities (people, things, concepts) connected by meaningful relationships. It stores information as nodes (entities) and edges (relationships). Google's Knowledge Graph, Wikipedia's Wikidata, and our employee system are all examples. RDF is the standard format for building knowledge graphs.

---

#### 16. What Are Subjects, Predicates, and Objects?

In the triple `:EMP001 :hasSkill :Python`:
- **Subject** (`:EMP001`): The entity the statement is about — "who" or "what"
- **Predicate** (`:hasSkill`): The relationship or property — "how they are related"
- **Object** (`:Python`): The value or related entity — "to what"

Think of it as a simple sentence: "Aayush (subject) has the skill (predicate) Python (object)."

---

#### 17. What Are Classes and Properties?

**Classes** are categories of things: `Employee`, `Skill`, `Department`. They are defined in the OWL ontology. Individual entities (`:EMP001`, `:Python`) are **instances** of classes.

**Properties** are the relationships:
- **Object Properties** connect two resources: `hasSkill`, `worksIn`
- **Data Properties** connect a resource to a literal value: `name`, `email`

---

#### 18. What Are Domain and Range?

**Domain** is the class that a property "belongs to" (starts from):
- `hasSkill` has domain `Employee` → only employees can have skills

**Range** is the class that a property "points to" (ends at):
- `hasSkill` has range `Skill` → skills are what employees have

Together, domain and range constrain how properties are used: `Employee --hasSkill--> Skill` is valid, but `Department --hasSkill--> Project` would violate the domain/range.

---

#### 19. How Does Project-to-Employee Matching Work?

1. Each project has `requiresSkill` relationships pointing to skills it needs
   - Example: `AI Chatbot → requiresSkill → Python, AI, Machine Learning`
2. Each employee has `hasSkill` relationships pointing to skills they possess
3. The SPARQL query finds the **intersection**: skills that are both required by the project AND possessed by the employee
4. Employees are ranked by how many required skills they match
5. An employee matching all 3 out of 3 required skills is a better candidate than one matching 2 out of 3

The SPARQL `GROUP BY` and `COUNT` clauses handle the counting and ranking.

---

> **Tip for viva:** For each concept, prepare to:
> 1. Define it in one sentence
> 2. Give an example from your project
> 3. Explain why you used it instead of an alternative
> 4. Show it working in your application

---

*End of Implementation Plan*
