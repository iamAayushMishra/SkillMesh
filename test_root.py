from sparql_client import kg
from config import NAMESPACE, DATA_PATH
import os
print('NAMESPACE   :', NAMESPACE)
print('DATA_PATH   :', DATA_PATH)
print('file exists :', os.path.exists(DATA_PATH), '| size:', os.path.getsize(DATA_PATH) if os.path.exists(DATA_PATH) else None)
print('triples     :', len(kg))
print('--- distinct rdf:type objects in graph ---')
for r in kg.query('SELECT DISTINCT ?t WHERE { ?s a ?t }'): print(r[0])