# Semantic Employee & Skill Management System

A web-based employee and skill management system built with **Semantic Web technologies** (RDF, OWL, SPARQL) as a 3rd-year B.Tech CSE academic project.

Instead of a traditional relational database, this system stores employee data as a **knowledge graph** — a network of interconnected facts — and uses SPARQL to traverse relationships and answer complex queries.

This project is built with **zero external database dependencies**. It uses `rdflib` as an embedded, in-memory triple store, allowing you to run the entire application with a single command!

---

## What Can This System Do?

| Query | Example |
|-------|---------|
| Find employees with a specific skill | "Who knows Python?" |
| Find employees with AI/ML skills | "Who has AI or Machine Learning skills?" |
| Match employees to a project | "Who is best suited for the AI Chatbot project?" |
| Explore related skills | "What skills are related to Python?" |
| Search by department | "Who works in the AI Department?" |
| Search by certification | "Who has the AWS Certification?" |
| Visualize the knowledge graph | Interactive network visualization |

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML, CSS, JavaScript, Cytoscape.js |
| **Backend** | Python, Flask |
| **Semantic Web** | RDF (Turtle), OWL, SPARQL |
| **Embedded Database** | RDFLib (In-memory Graph) |
| **Testing** | pytest |

---

## Prerequisites

- **Python 3.10+**
- **Git**

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/<username>/semantic-employee-system.git
cd semantic-employee-system
```

### 2. Create & Activate Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Flask Application

Because the database is embedded via `rdflib`, you don't need to start any external servers! Just run:

```bash
python app.py
```

Open `http://127.0.0.1:5000/` in your browser. The application will automatically parse the `ontology/employee_ontology.owl` and `data/employees.ttl` files on startup.

---

## Running Tests

```bash
python -m pytest tests/ -v
```

---

## Project Structure

```text
semantic-employee-system/
├── app.py                      # Flask application
├── config.py                   # Configuration
├── sparql_client.py            # SPARQL query helper (Embedded RDFLib)
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── .gitignore                  # Git ignore rules
│
├── ontology/
│   └── employee_ontology.owl   # OWL ontology (Turtle format)
│
├── data/
│   └── employees.ttl           # RDF data (Turtle format)
│
├── queries/                    # SPARQL query files
│   ├── employee_queries.rq
│   ├── skill_queries.rq
│   ├── project_queries.rq
│   ├── department_queries.rq
│   ├── dashboard_queries.rq
│   └── graph_queries.rq
│
├── templates/                  # HTML templates (Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── employees.html
│   ├── search.html
│   ├── projects.html
│   └── graph.html
│
├── static/
│   ├── css/style.css
│   └── js/
│       └── app.js
│
├── tests/
│   ├── test_rdf.py
│   └── test_api.py
│
└── docs/
    ├── data_model.md
    └── plan.md
```

---

## Key Semantic Web Concepts

| Concept | Description |
|---------|-------------|
| **RDF** | Resource Description Framework — stores data as subject-predicate-object triples |
| **OWL** | Web Ontology Language — defines the schema (classes, properties) |
| **SPARQL** | Query language for RDF data (like SQL for relational databases) |
| **Triple Store** | Database optimized for storing and querying RDF triples |
| **Knowledge Graph** | Network of entities connected by meaningful relationships |

---

## Sample RDF Triple

```turtle
:EMP001 rdf:type   :Employee .
:EMP001 :name      "Aayush Kumar" .
:EMP001 :hasSkill  :Python .
:EMP001 :worksIn   :AIDepartment .
```

This says: *"EMP001 is an Employee named Aayush Kumar who has the skill Python and works in the AI Department."*

---

## License

This project is developed for academic purposes as part of a B.Tech CSE curriculum.

---

## Author

**Aayush** — 3rd Year B.Tech CSE
