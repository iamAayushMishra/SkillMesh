"""
Semantic Employee & Skill Management System — Flask Application

Main application file that defines all routes (page rendering + API endpoints)
and connects the frontend to the Fuseki triple store via SPARQL queries.
"""

import re
from flask import Flask, render_template, request, jsonify
from sparql_client import (
    execute_query,
    add_employee,
    update_employee_projects,
    delete_employee,
    get_next_employee_id
)
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
        UNION { ?emp rdf:type :employee . }
        UNION { ?skill rdf:type :Skill . }
        UNION { ?skill rdf:type :skill . }
        UNION { ?dept rdf:type :Department . }
        UNION { ?dept rdf:type :department . }
        UNION { ?project rdf:type :Project . }
        UNION { ?project rdf:type :project . }
        UNION { ?cert rdf:type :Certification . }
        UNION { ?cert rdf:type :certification . }
    }
    """
    results, _ = safe_query(query)
    row = results[0] if results else {}

    emp_count = int(row.get("employeeCount", 0)) if row.get("employeeCount") else 0
    skill_count = int(row.get("skillCount", 0)) if row.get("skillCount") else 0
    dept_count = int(row.get("deptCount", 0)) if row.get("deptCount") else 0
    proj_count = int(row.get("projectCount", 0)) if row.get("projectCount") else 0
    cert_count = int(row.get("certCount", 0)) if row.get("certCount") else 0

    # Failsafe fallback directly from in-memory RDF graph
    from sparql_client import kg, EX
    from rdflib.namespace import RDF
    if emp_count == 0:
        emp_count = len(set(kg.subjects(RDF.type, EX.Employee)))
    if skill_count == 0:
        skill_count = len(set(kg.subjects(RDF.type, EX.Skill)))
    if dept_count == 0:
        dept_count = len(set(kg.subjects(RDF.type, EX.Department)))
    if proj_count == 0:
        proj_count = len(set(kg.subjects(RDF.type, EX.Project)))
    if cert_count == 0:
        cert_count = len(set(kg.subjects(RDF.type, EX.Certification)))

    return jsonify({
        "employees": emp_count,
        "skills": skill_count,
        "departments": dept_count,
        "projects": proj_count,
        "certifications": cert_count,
    })


# ============================================================
# API: Employees & Project Assignment
# ============================================================

@app.route("/api/next-emp-id")
def api_next_emp_id():
    """Returns the next sequential employee ID."""
    try:
        next_id = get_next_employee_id()
        return jsonify({"nextId": next_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/employees")
def api_employees():
    query = PREFIX + """
    SELECT ?emp ?empId ?name ?email ?deptName ?deptLocal
    WHERE {
        { ?emp rdf:type :Employee . }
        UNION { ?emp rdf:type :employee . }
        OPTIONAL { ?emp :employeeId ?empId . }
        OPTIONAL { ?emp :name ?name . }
        OPTIONAL { ?emp :email ?email . }
        OPTIONAL {
            ?emp :worksIn ?dept .
            OPTIONAL { ?dept :deptName ?deptName . }
            BIND(REPLACE(STR(?dept), "^.*[#/]", "") AS ?deptLocal)
        }
    }
    ORDER BY ?empId ?name
    """
    results, error = safe_query(query)
    if error:
        return jsonify({"error": error}), 503

    # Query assigned projects (supporting both URI and employeeId)
    proj_query = PREFIX + """
    SELECT ?emp ?empId ?projName ?projLocal
    WHERE {
        ?emp rdf:type :Employee .
        ?emp :worksOn ?proj .
        OPTIONAL { ?emp :employeeId ?empId . }
        OPTIONAL { ?proj :projectName ?projName . }
        BIND(REPLACE(STR(?proj), "^.*[#/]", "") AS ?projLocal)
    }
    """
    proj_results, _ = safe_query(proj_query)
    emp_projects = {}
    if proj_results:
        for r in proj_results:
            p_name = r.get("projName") or r.get("projLocal") or "Project"
            e_id = r.get("empId")
            e_uri = r.get("emp")
            if e_id:
                emp_projects.setdefault(e_id, []).append(p_name)
            if e_uri:
                e_local = e_uri.split("#")[-1] if "#" in e_uri else e_uri.split("/")[-1]
                emp_projects.setdefault(e_local, []).append(p_name)

    employees = []
    seen_ids = set()
    for r in results:
        uri = r.get("emp", "")
        fallback_id = uri.split("#")[-1] if "#" in uri else uri.split("/")[-1]
        emp_id = r.get("empId") or fallback_id
        if emp_id in seen_ids:
            continue
        seen_ids.add(emp_id)

        name = r.get("name") or emp_id
        email = r.get("email") or ""
        dept = r.get("deptName") or r.get("deptLocal") or "Unassigned"
        
        # Deduplicate projects
        p_list = list(dict.fromkeys(emp_projects.get(emp_id, []) + emp_projects.get(fallback_id, [])))

        employees.append({
            "empId": emp_id,
            "name": name,
            "email": email,
            "department": dept,
            "projects": p_list,
        })

    return jsonify({"employees": employees})


@app.route("/api/employees", methods=["POST"])
def api_create_employee():
    """Creates a new employee record and persists to RDF and TTL file."""
    data = request.get_json() or {}
    emp_id = (data.get("empId") or "").strip()
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    department = (data.get("department") or "").strip()
    skills = data.get("skills", [])
    certifications = data.get("certifications", [])
    projects = data.get("projects", [])

    if not name:
        return jsonify({"error": "Employee name is required"}), 400
    if not email:
        return jsonify({"error": "Employee email is required"}), 400
    if not department:
        return jsonify({"error": "Department is required"}), 400

    # Auto-generate ID if blank
    if not emp_id:
        emp_id = get_next_employee_id()

    # Sanitize ID format
    if not re.match(r"^[A-Za-z0-9_-]+$", emp_id):
        return jsonify({"error": "Employee ID can only contain letters, numbers, hyphens, and underscores"}), 400

    if "@" not in email or "." not in email:
        return jsonify({"error": "Please provide a valid email address"}), 400

    try:
        new_emp = add_employee(
            emp_id=emp_id,
            name=name,
            email=email,
            department=department,
            skills=skills,
            certifications=certifications,
            projects=projects
        )
        return jsonify({"success": True, "employee": new_emp}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to add employee: {e}"}), 500


@app.route("/api/employees/<emp_id>")
def api_employee_detail(emp_id):
    # Sanitize input — only allow alphanumeric IDs
    if not emp_id.isalnum():
        return jsonify({"error": "Invalid employee ID format"}), 400

    q_base = PREFIX + f"""
    SELECT ?name ?email ?deptName
    WHERE {{
        ?emp rdf:type :Employee .
        ?emp :employeeId "{emp_id}" .
        ?emp :name ?name .
        ?emp :email ?email .
        ?emp :worksIn ?dept .
        ?dept :deptName ?deptName .
    }}
    """
    results, error = safe_query(q_base)
    if error:
        return jsonify({"error": error}), 503
    if not results:
        return jsonify({"error": "Employee not found", "empId": emp_id}), 404

    r = results[0]

    q_skills = PREFIX + f"""
    SELECT ?skillName WHERE {{
        ?emp rdf:type :Employee ; :employeeId "{emp_id}" ; :hasSkill ?skill .
        ?skill :skillName ?skillName .
    }}
    """
    skills_res, _ = safe_query(q_skills)
    skills = [s["skillName"] for s in (skills_res or [])]

    q_certs = PREFIX + f"""
    SELECT ?certName WHERE {{
        ?emp rdf:type :Employee ; :employeeId "{emp_id}" ; :hasCertification ?cert .
        ?cert :certName ?certName .
    }}
    """
    certs_res, _ = safe_query(q_certs)
    certs = [c["certName"] for c in (certs_res or [])]

    q_projs = PREFIX + f"""
    SELECT ?projName WHERE {{
        ?emp rdf:type :Employee ; :employeeId "{emp_id}" ; :worksOn ?proj .
        ?proj :projectName ?projName .
    }}
    """
    projs_res, _ = safe_query(q_projs)
    projs = [p["projName"] for p in (projs_res or [])]

    return jsonify({
        "empId": emp_id,
        "name": r["name"],
        "email": r["email"],
        "department": r["deptName"],
        "skills": skills,
        "certifications": certs,
        "projects": projs,
    })


@app.route("/api/employees/<emp_id>/projects", methods=["POST", "PUT"])
def api_assign_employee_projects(emp_id):
    """Assign or update projects for an employee."""
    if not emp_id.isalnum():
        return jsonify({"error": "Invalid employee ID format"}), 400

    data = request.get_json() or {}
    project_names = data.get("projects", [])

    if not isinstance(project_names, list):
        return jsonify({"error": "'projects' must be a list of project names"}), 400

    try:
        assigned = update_employee_projects(emp_id, project_names)
        return jsonify({
            "success": True,
            "empId": emp_id,
            "projects": assigned,
            "message": f"Successfully updated projects for {emp_id}"
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to update projects: {e}"}), 500


@app.route("/api/employees/<emp_id>", methods=["DELETE"])
def api_delete_employee(emp_id):
    """Delete an employee from the graph and file."""
    if not emp_id.isalnum():
        return jsonify({"error": "Invalid employee ID format"}), 400

    try:
        delete_employee(emp_id)
        return jsonify({"success": True, "message": f"Employee {emp_id} deleted successfully."})
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to delete employee: {e}"}), 500


@app.route("/api/certifications")
def api_certifications():
    """List all available certifications."""
    query = PREFIX + """
    SELECT ?certName
    WHERE {
        ?cert rdf:type :Certification .
        ?cert :certName ?certName .
    }
    ORDER BY ?certName
    """
    results, error = safe_query(query)
    if error:
        return jsonify({"error": error}), 503

    certifications = [r["certName"] for r in results]
    return jsonify({"certifications": certifications})


@app.route("/api/projects/<project_name>/members")
def api_project_members(project_name):
    """List all employees currently assigned to a project."""
    query = PREFIX + f"""
    SELECT ?empId ?name ?email ?deptName
    WHERE {{
        ?emp rdf:type :Employee .
        ?emp :employeeId ?empId .
        ?emp :name ?name .
        ?emp :email ?email .
        ?emp :worksIn ?dept .
        ?dept :deptName ?deptName .
        ?emp :worksOn ?proj .
        ?proj :projectName ?pName .
        FILTER(?pName = "{project_name}")
    }}
    ORDER BY ?name
    """
    results, error = safe_query(query)
    if error:
        return jsonify({"error": error}), 503

    members = [
        {
            "empId": r["empId"],
            "name": r["name"],
            "email": r["email"],
            "department": r["deptName"],
        }
        for r in results
    ]
    return jsonify({"project": project_name, "members": members})


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
    SELECT ?project ?projectName ?projectDescription
           (GROUP_CONCAT(?skillName; separator=", ") AS ?requiredSkills)
    WHERE {
        { ?project rdf:type :Project . }
        UNION { ?project rdf:type :project . }
        OPTIONAL { ?project :projectName ?projectName . }
        OPTIONAL { ?project :projectDescription ?projectDescription . }
        OPTIONAL {
            ?project :requiresSkill ?skill .
            ?skill :skillName ?skillName .
        }
    }
    GROUP BY ?project ?projectName ?projectDescription
    ORDER BY ?projectName
    """
    results, error = safe_query(query)
    if error:
        return jsonify({"error": error}), 503

    projects = []
    seen = set()
    for r in results:
        uri = r.get("project", "")
        fallback_name = uri.split("#")[-1] if "#" in uri else uri.split("/")[-1]
        name = r.get("projectName") or fallback_name or "Project"
        if name in seen:
            continue
        seen.add(name)

        desc = r.get("projectDescription") or "No description provided."
        req_skills = [s.strip() for s in r.get("requiredSkills", "").split(",") if s.strip()]

        projects.append({
            "name": name,
            "description": desc,
            "requiredSkills": req_skills,
        })
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
    app.run(debug=DEBUG, port=5000, use_reloader=False)
