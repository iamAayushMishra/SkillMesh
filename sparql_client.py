"""
SPARQL Client — handles embedded query execution via RDFLib.

Instead of calling an external Fuseki server, this module loads the RDF
data directly into memory on application startup and executes SPARQL queries locally.
"""

from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF
import logging
import re
import threading
from config import ONTOLOGY_PATH, DATA_PATH, NAMESPACE

EX = Namespace(NAMESPACE)

# Initialize the global in-memory graph
kg = Graph()
_data_loaded = False

# rdflib's SPARQL parser (pyparsing) and in-memory store are NOT thread-safe.
# Flask serves requests on several threads, so every graph read/write goes
# through this lock (RLock so locked functions can call each other).
_kg_lock = threading.RLock()


def _run_query(query_string):
    """Run a SPARQL query under the lock; return (variables, rows) fully materialised."""
    with _kg_lock:
        qres = kg.query(query_string)
        return list(qres.vars), list(qres)


def load_data():
    """Loads the ontology and data files into the RDFLib graph."""
    global _data_loaded
    if _data_loaded and len(kg) > 0:
        return  # Already loaded
    try:
        logging.info("Loading ontology into embedded graph...")
        kg.parse(ONTOLOGY_PATH, format="turtle")

        logging.info("Loading employee data into embedded graph...")
        kg.parse(DATA_PATH, format="turtle")

        triple_count = len(kg)
        logging.info(f"Successfully loaded {triple_count} triples into memory.")
        if triple_count == 0:
            logging.warning("Graph is empty after loading — check data files!")
        _data_loaded = True
    except Exception as e:
        logging.error(f"Failed to load RDF data: {e}")
        raise


def ensure_data_loaded():
    """Ensures data is loaded before any query; safe to call multiple times."""
    if not _data_loaded or len(kg) == 0:
        load_data()


# Load the data immediately when the module is imported
load_data()


def execute_query(query_string):
    """
    Execute a SPARQL query against the embedded RDFLib graph.

    Args:
        query_string (str): A valid SPARQL SELECT query.

    Returns:
        list[dict]: A list of result rows, where each row is a dict
                    mapping variable names to their values (stringified).
                    This format exactly matches the old Fuseki/JSON output.

    Raises:
        Exception: For any SPARQL syntax/execution errors.
    """
    ensure_data_loaded()
    try:
        variables, rows = _run_query(query_string)

        results = []
        for row in rows:
            row_dict = {}
            for var in variables:
                val = row[var]
                if val is not None:
                    row_dict[str(var)] = str(val)
            results.append(row_dict)

        return results

    except Exception as e:
        raise Exception(f"Embedded SPARQL error: {e}") from e


def get_lookup_mappings():
    """Build fast lookup dictionaries mapping names/IDs to RDF resources."""
    ensure_data_loaded()
    mappings = {
        "departments": {},
        "skills": {},
        "certifications": {},
        "projects": {}
    }
    
    # Departments
    for row in _run_query(f"PREFIX : <{NAMESPACE}> SELECT ?uri ?name WHERE {{ ?uri a :Department ; :deptName ?name }}")[1]:
        uri = row["uri"]
        name = str(row["name"])
        local = str(uri).split("#")[-1]
        item = {"uri": uri, "local": local, "name": name}
        mappings["departments"][name.lower()] = item
        mappings["departments"][local.lower()] = item

    # Skills
    for row in _run_query(f"PREFIX : <{NAMESPACE}> SELECT ?uri ?name WHERE {{ ?uri a :Skill ; :skillName ?name }}")[1]:
        uri = row["uri"]
        name = str(row["name"])
        local = str(uri).split("#")[-1]
        item = {"uri": uri, "local": local, "name": name}
        mappings["skills"][name.lower()] = item
        mappings["skills"][local.lower()] = item

    # Certifications
    for row in _run_query(f"PREFIX : <{NAMESPACE}> SELECT ?uri ?name WHERE {{ ?uri a :Certification ; :certName ?name }}")[1]:
        uri = row["uri"]
        name = str(row["name"])
        local = str(uri).split("#")[-1]
        item = {"uri": uri, "local": local, "name": name}
        mappings["certifications"][name.lower()] = item
        mappings["certifications"][local.lower()] = item

    # Projects
    for row in _run_query(f"PREFIX : <{NAMESPACE}> SELECT ?uri ?name WHERE {{ ?uri a :Project ; :projectName ?name }}")[1]:
        uri = row["uri"]
        name = str(row["name"])
        local = str(uri).split("#")[-1]
        item = {"uri": uri, "local": local, "name": name}
        mappings["projects"][name.lower()] = item
        mappings["projects"][local.lower()] = item

    return mappings


def get_next_employee_id():
    """Finds all employee IDs and computes the next sequential ID (e.g. EMP016)."""
    ensure_data_loaded()
    qres = _run_query(f"PREFIX : <{NAMESPACE}> SELECT ?id WHERE {{ ?e a :Employee ; :employeeId ?id }}")[1]
    nums = []
    for row in qres:
        emp_id = str(row["id"])
        match = re.search(r"(\d+)", emp_id)
        if match:
            nums.append(int(match.group(1)))
    next_num = max(nums) + 1 if nums else 1
    return f"EMP{next_num:03d}"


def sync_employee_to_ttl(emp_id):
    """
    Reads the employee's current triples from `kg`, generates a clean Turtle block,
    and updates or appends it to DATA_PATH.
    """
    emp_uri = EX[emp_id]
    
    # Check if employee exists in kg
    if (emp_uri, RDF.type, EX.Employee) not in kg:
        remove_employee_from_ttl(emp_id)
        return

    name_nodes = list(kg.objects(emp_uri, EX.name))
    email_nodes = list(kg.objects(emp_uri, EX.email))
    dept_nodes = list(kg.objects(emp_uri, EX.worksIn))
    
    name = str(name_nodes[0]) if name_nodes else ""
    email = str(email_nodes[0]) if email_nodes else ""
    dept_local = str(dept_nodes[0]).split("#")[-1] if dept_nodes else ""
    
    skill_locals = [str(s).split("#")[-1] for s in kg.objects(emp_uri, EX.hasSkill)]
    cert_locals = [str(c).split("#")[-1] for c in kg.objects(emp_uri, EX.hasCertification)]
    project_locals = [str(p).split("#")[-1] for p in kg.objects(emp_uri, EX.worksOn)]
    
    lines = [f":{emp_id} rdf:type :Employee ;"]
    lines.append(f'    :employeeId "{emp_id}" ;')
    lines.append(f'    :name "{name}" ;')
    lines.append(f'    :email "{email}" ;')
    
    props = []
    if dept_local:
        props.append(f"    :worksIn :{dept_local}")
    if skill_locals:
        skills_str = " , ".join(f":{s}" for s in sorted(skill_locals))
        props.append(f"    :hasSkill {skills_str}")
    if cert_locals:
        certs_str = " , ".join(f":{c}" for c in sorted(cert_locals))
        props.append(f"    :hasCertification {certs_str}")
    if project_locals:
        projs_str = " , ".join(f":{p}" for p in sorted(project_locals))
        props.append(f"    :worksOn {projs_str}")

    if not props:
        lines[-1] = lines[-1][:-1] + "."
    else:
        for i, p in enumerate(props):
            if i == len(props) - 1:
                lines.append(f"{p} .")
            else:
                lines.append(f"{p} ;")

    block = "\n".join(lines)
    
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = rf":{re.escape(emp_id)}\s+rdf:type\s+:Employee[\s\S]*?\.\s*(?=\n|$)"
    if re.search(pattern, content):
        content = re.sub(pattern, block + "\n", content)
    else:
        content = content.rstrip() + "\n\n" + block + "\n"

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        f.write(content)


def remove_employee_from_ttl(emp_id):
    """Removes an employee's Turtle block from DATA_PATH."""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = rf"\n*:{re.escape(emp_id)}\s+rdf:type\s+:Employee[\s\S]*?\.\s*(?=\n|$)"
    content = re.sub(pattern, "", content)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        f.write(content.rstrip() + "\n")


def sync_skill_to_ttl(local, skill_name):
    """Appends a new skill entity block to DATA_PATH."""
    block = f":{local} rdf:type :Skill ;\n    :skillName \"{skill_name}\" .\n"
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if f":{local} rdf:type :Skill" in content:
        return

    marker = "# ============================================================\n# SKILL RELATIONSHIPS"
    if marker in content:
        content = content.replace(marker, f"{block}\n{marker}")
    else:
        content = content.rstrip() + f"\n\n{block}\n"

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        f.write(content)


def _add_skill_unlocked(skill_name):
    """
    Creates a new :Skill in the in-memory graph and appends it to DATA_PATH.
    Returns the created/existing skill dict.
    """
    ensure_data_loaded()
    name_clean = skill_name.strip()
    if not name_clean:
        raise ValueError("Skill name cannot be empty.")

    mappings = get_lookup_mappings()
    if name_clean.lower() in mappings["skills"]:
        item = mappings["skills"][name_clean.lower()]
        return {"name": item["name"], "uri": str(item["uri"]), "alreadyExisted": True}

    # Generate a clean URI local name
    local = re.sub(r'[^A-Za-z0-9_]', '', name_clean.title().replace(' ', ''))
    if not local or local[0].isdigit():
        local = f"Skill_{local}" if local else f"Skill_{abs(hash(name_clean)) % 100000}"

    base_local = local
    counter = 1
    while EX[local] in kg.subjects() or EX[local] in kg.objects():
        local = f"{base_local}_{counter}"
        counter += 1

    skill_uri = EX[local]

    # Add to in-memory graph
    kg.add((skill_uri, RDF.type, EX.Skill))
    kg.add((skill_uri, EX.skillName, Literal(name_clean)))

    # Persist to employees.ttl
    sync_skill_to_ttl(local, name_clean)

    return {"name": name_clean, "uri": str(skill_uri), "alreadyExisted": False}


def _add_employee_unlocked(emp_id, name, email, department, skills=None, certifications=None, projects=None):
    """
    Adds a new employee to the in-memory RDFLib graph and updates DATA_PATH.
    """
    emp_uri = EX[emp_id]
    if (emp_uri, RDF.type, EX.Employee) in kg:
        raise ValueError(f"Employee ID '{emp_id}' already exists.")

    mappings = get_lookup_mappings()

    # Resolve department
    dept_item = mappings["departments"].get(department.lower())
    if not dept_item:
        raise ValueError(f"Department '{department}' is not recognized.")

    # Add core properties
    kg.add((emp_uri, RDF.type, EX.Employee))
    kg.add((emp_uri, EX.employeeId, Literal(emp_id)))
    kg.add((emp_uri, EX.name, Literal(name)))
    kg.add((emp_uri, EX.email, Literal(email)))
    kg.add((emp_uri, EX.worksIn, dept_item["uri"]))

    # Add skills (creates new skill entity if it doesn't exist)
    added_skills = []
    if skills:
        for s in skills:
            s_clean = s.strip()
            if not s_clean:
                continue
            item = mappings["skills"].get(s_clean.lower())
            if not item:
                new_skill = _add_skill_unlocked(s_clean)
                skill_uri = URIRef(new_skill["uri"])
                kg.add((emp_uri, EX.hasSkill, skill_uri))
                added_skills.append(new_skill["name"])
                mappings = get_lookup_mappings()
            else:
                kg.add((emp_uri, EX.hasSkill, item["uri"]))
                added_skills.append(item["name"])

    # Add certifications
    added_certs = []
    if certifications:
        for c in certifications:
            c_clean = c.strip()
            item = mappings["certifications"].get(c_clean.lower())
            if item:
                kg.add((emp_uri, EX.hasCertification, item["uri"]))
                added_certs.append(item["name"])

    # Add projects
    added_projects = []
    if projects:
        for p in projects:
            p_clean = p.strip()
            item = mappings["projects"].get(p_clean.lower())
            if item:
                kg.add((emp_uri, EX.worksOn, item["uri"]))
                added_projects.append(item["name"])

    # Persist to Turtle file
    sync_employee_to_ttl(emp_id)

    return {
        "empId": emp_id,
        "name": name,
        "email": email,
        "department": dept_item["name"],
        "skills": added_skills,
        "certifications": added_certs,
        "projects": added_projects,
    }


def _update_employee_projects_unlocked(emp_id, project_names):
    """
    Updates the projects an employee works on in the RDFLib graph and DATA_PATH.
    """
    emp_uri = EX[emp_id]
    if (emp_uri, RDF.type, EX.Employee) not in kg:
        raise ValueError(f"Employee '{emp_id}' not found.")

    mappings = get_lookup_mappings()

    # Remove existing worksOn triples
    for obj in list(kg.objects(emp_uri, EX.worksOn)):
        kg.remove((emp_uri, EX.worksOn, obj))

    # Add new worksOn triples
    assigned = []
    for p in project_names:
        p_clean = p.strip()
        item = mappings["projects"].get(p_clean.lower())
        if item:
            kg.add((emp_uri, EX.worksOn, item["uri"]))
            assigned.append(item["name"])

    # Persist to file
    sync_employee_to_ttl(emp_id)
    return assigned


def _delete_employee_unlocked(emp_id):
    """Deletes an employee from RDFLib graph and DATA_PATH."""
    emp_uri = EX[emp_id]
    if (emp_uri, RDF.type, EX.Employee) not in kg:
        raise ValueError(f"Employee '{emp_id}' not found.")

    # Remove triples where employee is subject
    for p, o in list(kg.predicate_objects(emp_uri)):
        kg.remove((emp_uri, p, o))

    # Remove triples where employee is object (if any)
    for s, p in list(kg.subject_predicates(emp_uri)):
        kg.remove((s, p, emp_uri))

    # Persist removal to file
    remove_employee_from_ttl(emp_id)



# ---- thread-safe public wrappers (mutate kg + TTL file under the lock) ----
def add_employee(*args, **kwargs):
    with _kg_lock:
        return _add_employee_unlocked(*args, **kwargs)


def update_employee_projects(*args, **kwargs):
    with _kg_lock:
        return _update_employee_projects_unlocked(*args, **kwargs)


def delete_employee(*args, **kwargs):
    with _kg_lock:
        return _delete_employee_unlocked(*args, **kwargs)


def add_skill(*args, **kwargs):
    with _kg_lock:
        return _add_skill_unlocked(*args, **kwargs)