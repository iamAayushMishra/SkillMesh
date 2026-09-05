"""
SPARQL Client — handles embedded query execution via RDFLib.

Instead of calling an external Fuseki server, this module loads the RDF
data directly into memory on application startup and executes SPARQL queries locally.
"""

from rdflib import Graph
import logging
from config import ONTOLOGY_PATH, DATA_PATH

# Initialize the global in-memory graph
kg = Graph()

def load_data():
    """Loads the ontology and data files into the RDFLib graph."""
    try:
        logging.info("Loading ontology into embedded graph...")
        kg.parse(ONTOLOGY_PATH, format="turtle")
        
        logging.info("Loading employee data into embedded graph...")
        kg.parse(DATA_PATH, format="turtle")
        
        logging.info(f"Successfully loaded {len(kg)} triples into memory.")
    except Exception as e:
        logging.error(f"Failed to load RDF data: {e}")
        raise

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
    try:
        # rdflib returns a Result object
        qres = kg.query(query_string)
        
        results = []
        for row in qres:
            row_dict = {}
            for var in qres.vars:
                val = row[var]
                if val is not None:
                    row_dict[str(var)] = str(val)
            results.append(row_dict)

        return results

    except Exception as e:
        raise Exception(f"Embedded SPARQL error: {e}") from e
