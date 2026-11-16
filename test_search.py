"""Quick test script to debug the employee search."""
from sparql_client import execute_query

NAMESPACE = "http://example.org/employee#"

PREFIX = f"""
PREFIX : <{NAMESPACE}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
"""

# Test 1: Search by skill (using double quotes like the app does)
print("=== Test 1: Search by skill with double quotes ===")
query1 = PREFIX + """
SELECT ?empId ?name ?email ?deptName
WHERE {
    ?emp rdf:type :Employee .
    ?emp :employeeId ?empId .
    ?emp :name ?name .
    ?emp :email ?email .
    ?emp :worksIn ?dept .
    ?dept :deptName ?deptName .
    ?emp :hasSkill ?skill .
    ?skill :skillName ?skillName .
    FILTER(?skillName = "Python")
}
ORDER BY ?name
"""
try:
    results = execute_query(query1)
    print(f"Found {len(results)} results")
    for r in results:
        print(f"  {r}")
except Exception as e:
    print(f"ERROR: {e}")

# Test 2: Search by department
print("\n=== Test 2: Search by department ===")
query2 = PREFIX + """
SELECT ?empId ?name ?email ?deptName
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
"""
try:
    results = execute_query(query2)
    print(f"Found {len(results)} results")
    for r in results:
        print(f"  {r}")
except Exception as e:
    print(f"ERROR: {e}")

# Test 3: List all employees (basic - no search filter)
print("\n=== Test 3: All employees ===")
query3 = PREFIX + """
SELECT ?empId ?name
WHERE {
    ?emp rdf:type :Employee .
    ?emp :employeeId ?empId .
    ?emp :name ?name .
}
ORDER BY ?empId
"""
try:
    results = execute_query(query3)
    print(f"Found {len(results)} results")
    for r in results:
        print(f"  {r}")
except Exception as e:
    print(f"ERROR: {e}")

# Test 4: List all skills
print("\n=== Test 4: All skills ===")
query4 = PREFIX + """
SELECT ?skillName
WHERE {
    ?skill rdf:type :Skill .
    ?skill :skillName ?skillName .
}
ORDER BY ?skillName
"""
try:
    results = execute_query(query4)
    print(f"Found {len(results)} results")
    for r in results:
        print(f"  {r}")
except Exception as e:
    print(f"ERROR: {e}")

# Test 5: Check what type the skillName values are
print("\n=== Test 5: Skill name types (datatype check) ===")
query5 = PREFIX + """
SELECT ?skillName (DATATYPE(?skillName) AS ?dtype) (LANG(?skillName) AS ?lang)
WHERE {
    ?skill rdf:type :Skill .
    ?skill :skillName ?skillName .
}
LIMIT 3
"""
try:
    results = execute_query(query5)
    for r in results:
        print(f"  {r}")
except Exception as e:
    print(f"ERROR: {e}")

# Test 6: Try with STR() cast
print("\n=== Test 6: Search with STR() cast ===")
query6 = PREFIX + """
SELECT ?empId ?name
WHERE {
    ?emp rdf:type :Employee .
    ?emp :employeeId ?empId .
    ?emp :name ?name .
    ?emp :hasSkill ?skill .
    ?skill :skillName ?skillName .
    FILTER(STR(?skillName) = "Python")
}
ORDER BY ?name
"""
try:
    results = execute_query(query6)
    print(f"Found {len(results)} results")
    for r in results:
        print(f"  {r}")
except Exception as e:
    print(f"ERROR: {e}")
