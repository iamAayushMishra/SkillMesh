"""
Semantic Employee & Skill Management System — Flask Application

Main application file that defines all routes (page rendering + API endpoints)
and connects the frontend to the Fuseki triple store via SPARQL queries.
"""

from flask import Flask, render_template, request, jsonify
from sparql_client import execute_query
from config import NAMESPACE, SECRET_KEY, DEBUG

app = Flask(__name__)
app.secret_key = SECRET_KEY

PREFIX = f"""
PREFIX : <{NAMESPACE}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
"""


# ============================================================
# HELPER: wrap every API call with Fuseki error handling
# ============================================================

def safe_query(query_string):
    """Execute a SPARQL query with error handling. Returns (results, error)."""
    try:
        results = execute_query(query_string)
        return results, None
    except ConnectionError as e:
        return None, str(e)
    except Exception as e:
        return None, f"SPARQL query error: {e}"


# ============================================================
# PAGE ROUTES (serve HTML templates)
# ============================================================

@app.route("/")
def dashboard_page():
    return render_template("index.html")


@app.route("/employees")
def employees_page():
    return render_template("employees.html")


@app.route("/search")
def search_page():
    return render_template("search.html")


@app.route("/projects")
def projects_page():
    return render_template("projects.html")


@app.route("/graph")
def graph_page():
    return render_template("graph.html")


# ============================================================
# API: Dashboard
# ============================================================

@app.route("/api/dashboard")
def api_dashboard():
    query = PREFIX + """
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
    """
    results, error = safe_query(query)
    if error:
        return jsonify({"error": error}), 503

    row = results[0] if results else {}
    return jsonify({
        "employees": int(row.get("employeeCount", 0)),
        "skills": int(row.get("skillCount", 0)),
        "departments": int(row.get("deptCount", 0)),
        "projects": int(row.get("projectCount", 0)),
        "certifications": int(row.get("certCount", 0)),
    })


# ============================================================
# API: Employees
# ============================================================

@app.route("/api/employees")
def api_employees():
    query = PREFIX + """
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
    """
    results, error = safe_query(query)
    if error:
        return jsonify({"error": error}), 503

    employees = [
        {
            "empId": r["empId"],
            "name": r["name"],
            "email": r["email"],
            "department": r["deptName"],
        }
        for r in results
    ]
    return jsonify({"employees": employees})


@app.route("/api/employees/<emp_id>")
def api_employee_detail(emp_id):
    # Sanitize input — only allow alphanumeric IDs
    if not emp_id.isalnum():
        return jsonify({"error": "Invalid employee ID format"}), 400

    query = PREFIX + f"""
    SELECT ?name ?email ?deptName
           (GROUP_CONCAT(DISTINCT ?skillName; separator=", ") AS ?skills)
           (GROUP_CONCAT(DISTINCT ?certName; separator=", ") AS ?certifications)
           (GROUP_CONCAT(DISTINCT ?projName; separator=", ") AS ?projects)
    WHERE {{
        ?emp rdf:type :Employee .
        ?emp :employeeId ?empId .
        ?emp :name ?name .
        ?emp :email ?email .
        ?emp :worksIn ?dept .
        ?dept :deptName ?deptName .
        OPTIONAL {{ ?emp :hasSkill ?skill . ?skill :skillName ?skillName . }}
        OPTIONAL {{ ?emp :hasCertification ?cert . ?cert :certName ?certName . }}
        OPTIONAL {{ ?emp :worksOn ?proj . ?proj :projectName ?projName . }}
        FILTER(?empId = "{emp_id}")
    }}
    GROUP BY ?name ?email ?deptName
    """
    results, error = safe_query(query)
    if error:
        return jsonify({"error": error}), 503

    if not results:
        return jsonify({"error": "Employee not found", "empId": emp_id}), 404

    r = results[0]
    return jsonify({
        "empId": emp_id,
        "name": r["name"],
        "email": r["email"],
        "department": r["deptName"],
        "skills": [s.strip() for s in r.get("skills", "").split(",") if s.strip()],
        "certifications": [c.strip() for c in r.get("certifications", "").split(",") if c.strip()],
        "projects": [p.strip() for p in r.get("projects", "").split(",") if p.strip()],
    })


# ============================================================
# API: Skills
# ============================================================

@app.route("/api/skills")
def api_skills():
    query = PREFIX + """
    SELECT ?skillName
    WHERE {
        ?skill rdf:type :Skill .
        ?skill :skillName ?skillName .
    }
    ORDER BY ?skillName
    """
    results, error = safe_query(query)
    if error:
        return jsonify({"error": error}), 503

    skills = [r["skillName"] for r in results]
    return jsonify({"skills": skills})


# ============================================================
# API: Departments
# ============================================================

@app.route("/api/departments")
def api_departments():
    query = PREFIX + """
    SELECT ?deptName
    WHERE {
        ?dept rdf:type :Department .
        ?dept :deptName ?deptName .
    }
    ORDER BY ?deptName
    """
    results, error = safe_query(query)
    if error:
        return jsonify({"error": error}), 503

    departments = [r["deptName"] for r in results]
    return jsonify({"departments": departments})


# ============================================================
# API: Projects
# ============================================================

@app.route("/api/projects")
def api_projects():
    query = PREFIX + """
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
    """
    results, error = safe_query(query)
    if error:
        return jsonify({"error": error}), 503

    projects = [
        {
            "name": r["projectName"],
            "description": r["projectDescription"],
            "requiredSkills": [s.strip() for s in r.get("requiredSkills", "").split(",") if s.strip()],
        }
        for r in results
    ]
    return jsonify({"projects": projects})


# ============================================================
# API: Search — Employees by Skill, Department, or Certification
# ============================================================

@app.route("/api/search/employees")
def api_search_employees():
    skill = request.args.get("skill")
    department = request.args.get("department")
    certification = request.args.get("certification")

    if skill:
        query = PREFIX + f"""
        SELECT ?empId ?name ?email ?deptName
        WHERE {{
            ?emp rdf:type :Employee .
            ?emp :employeeId ?empId .
            ?emp :name ?name .
            ?emp :email ?email .
            ?emp :worksIn ?dept .
            ?dept :deptName ?deptName .
            ?emp :hasSkill ?skill .
            ?skill :skillName ?skillName .
            FILTER(?skillName = "{skill}")
        }}
        ORDER BY ?name
        """
        search_type = "skill"
        search_value = skill

    elif department:
        query = PREFIX + f"""
        SELECT ?empId ?name ?email ?deptName
        WHERE {{
            ?emp rdf:type :Employee .
            ?emp :employeeId ?empId .
            ?emp :name ?name .
            ?emp :email ?email .
            ?emp :worksIn ?dept .
            ?dept :deptName ?deptName .
            FILTER(?deptName = "{department}")
        }}
        ORDER BY ?name
        """
        search_type = "department"
        search_value = department

    elif certification:
        query = PREFIX + f"""
        SELECT ?empId ?name ?email ?deptName ?certName
        WHERE {{
            ?emp rdf:type :Employee .
            ?emp :employeeId ?empId .
            ?emp :name ?name .
            ?emp :email ?email .
            ?emp :worksIn ?dept .
            ?dept :deptName ?deptName .
            ?emp :hasCertification ?cert .
            ?cert :certName ?certName .
            FILTER(?certName = "{certification}")
        }}
        ORDER BY ?name
        """
        search_type = "certification"
        search_value = certification

    else:
        return jsonify({"error": "Missing required parameter: skill, department, or certification"}), 400

    results, error = safe_query(query)
    if error:
        return jsonify({"error": error}), 503

    employees = [
        {
            "empId": r["empId"],
            "name": r["name"],
            "email": r["email"],
            "department": r["deptName"],
        }
        for r in results
    ]
    return jsonify({
        "query": search_value,
        "type": search_type,
        "count": len(employees),
        "results": employees,
    })


# ============================================================
# API: Search — Related Skills
# ============================================================

@app.route("/api/search/related-skills")
def api_related_skills():
    skill = request.args.get("skill")
    if not skill:
        return jsonify({"error": "Missing required parameter: skill"}), 400

    query = PREFIX + f"""
    SELECT ?relatedSkillName
    WHERE {{
        ?skill rdf:type :Skill .
        ?skill :skillName ?skillName .
        ?skill :relatedTo ?relatedSkill .
        ?relatedSkill :skillName ?relatedSkillName .
        FILTER(?skillName = "{skill}")
    }}
    """
    results, error = safe_query(query)
    if error:
        return jsonify({"error": error}), 503

    related = [r["relatedSkillName"] for r in results]
    return jsonify({"skill": skill, "relatedSkills": related})


# ============================================================
# API: Project Candidates
# ============================================================

@app.route("/api/projects/<project_name>/candidates")
def api_project_candidates(project_name):
    query = PREFIX + f"""
    SELECT ?empId ?name (COUNT(?skill) AS ?matchingSkills)
           (GROUP_CONCAT(?skillName; separator=", ") AS ?skills)
    WHERE {{
        ?project rdf:type :Project .
        ?project :projectName ?projName .
        ?project :requiresSkill ?skill .
        ?emp rdf:type :Employee .
        ?emp :employeeId ?empId .
        ?emp :name ?name .
        ?emp :hasSkill ?skill .
        ?skill :skillName ?skillName .
        FILTER(?projName = "{project_name}")
    }}
    GROUP BY ?empId ?name
    ORDER BY DESC(?matchingSkills)
    """
    results, error = safe_query(query)
    if error:
        return jsonify({"error": error}), 503

    if not results:
        return jsonify({"error": "Project not found or no matching employees", "project": project_name}), 404

    candidates = [
        {
            "empId": r["empId"],
            "name": r["name"],
            "matchingSkills": int(r["matchingSkills"]),
            "skills": r.get("skills", ""),
        }
        for r in results
    ]
    return jsonify({"project": project_name, "candidates": candidates})


# ============================================================
# API: Graph Data (for Cytoscape.js)
# ============================================================

@app.route("/api/graph")
def api_graph():
    query = PREFIX + """
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
        UNION {
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
        UNION {
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
        UNION {
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
        UNION {
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
        UNION {
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
    """
    results, error = safe_query(query)
    if error:
        return jsonify({"error": error}), 503

    # Build unique nodes and edges for Cytoscape.js
    nodes = {}
    edges = []

    for r in results:
        src_id = r["source"]
        tgt_id = r["target"]

        if src_id not in nodes:
            nodes[src_id] = {"id": src_id, "label": r["sourceLabel"], "type": r["sourceType"]}
        if tgt_id not in nodes:
            nodes[tgt_id] = {"id": tgt_id, "label": r["targetLabel"], "type": r["targetType"]}

        edges.append({
            "source": src_id,
            "target": tgt_id,
            "relationship": r["relationship"],
        })

    return jsonify({
        "nodes": list(nodes.values()),
        "edges": edges,
    })


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Endpoint not found"}), 404
    return render_template("base.html", error="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Internal server error"}), 500
    return render_template("base.html", error="Internal server error"), 500


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    app.run(debug=DEBUG, port=5000)
