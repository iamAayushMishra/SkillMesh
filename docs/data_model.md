# Data Model Design

## Entities (Classes)

| Entity | Description | Example Instances |
|--------|-------------|-------------------|
| **Employee** | A person who works in the company | Aayush Kumar, Priya Sharma |
| **Skill** | A technical or professional skill | Python, Machine Learning |
| **Department** | An organizational unit | AI Department, HR |
| **Project** | A company project | AI Chatbot, Employee Analytics |
| **Certification** | A professional certification | AWS Certification |

## Data Properties (Attributes)

| Entity | Attribute | Type | Example |
|--------|-----------|------|---------|
| Employee | employeeId | string | "EMP001" |
| Employee | name | string | "Aayush Kumar" |
| Employee | email | string | "aayush@company.com" |
| Skill | skillName | string | "Python" |
| Department | deptName | string | "AI Department" |
| Project | projectName | string | "AI Chatbot" |
| Project | projectDescription | string | "An AI-powered chatbot" |
| Certification | certName | string | "AWS Certification" |

## Object Properties (Relationships)

| Relationship | Domain → Range | Meaning |
|-------------|----------------|---------|
| hasSkill | Employee → Skill | Employee possesses this skill |
| worksIn | Employee → Department | Employee belongs to this department |
| hasCertification | Employee → Certification | Employee holds this certification |
| worksOn | Employee → Project | Employee is assigned to project |
| requiresSkill | Project → Skill | Project needs this skill |
| relatedTo | Skill → Skill | Two skills are related |
| handlesProject | Department → Project | Department manages this project |
| certifiesSkill | Certification → Skill | Certification validates this skill |

## Sample Dataset

### Employees (15)

| ID | Name | Email | Department | Skills | Certifications |
|----|------|-------|------------|--------|----------------|
| EMP001 | Aayush Kumar | aayush@company.com | AI Department | Python, ML, AI | Python Cert, DS Cert |
| EMP002 | Priya Sharma | priya@company.com | Data Science | Python, SQL, ML | DS Cert |
| EMP003 | Rahul Verma | rahul@company.com | Software Dev | Java, JavaScript, SQL | AWS Cert |
| EMP004 | Sneha Patel | sneha@company.com | AI Department | Python, AI, RDF | Python Cert |
| EMP005 | Vikram Singh | vikram@company.com | Software Dev | Java, JavaScript, SPARQL | — |
| EMP006 | Ananya Gupta | ananya@company.com | Data Science | Python, SQL, SPARQL | DS Cert |
| EMP007 | Rohan Desai | rohan@company.com | HR | JavaScript, SQL | — |
| EMP008 | Meera Nair | meera@company.com | AI Department | Python, ML, SPARQL | ML Cert |
| EMP009 | Arjun Reddy | arjun@company.com | Software Dev | Java, Python, SQL | Java Cert |
| EMP010 | Kavita Joshi | kavita@company.com | Data Science | Python, ML, AI | DS Cert, ML Cert |
| EMP011 | Deepak Mehta | deepak@company.com | Software Dev | JavaScript, Java, RDF | AWS Cert |
| EMP012 | Ishita Roy | ishita@company.com | HR | SQL, JavaScript | — |
| EMP013 | Nikhil Rao | nikhil@company.com | AI Department | Python, AI, ML | Python Cert, ML Cert |
| EMP014 | Sanya Kapoor | sanya@company.com | Data Science | SQL, Python, SPARQL | DS Cert |
| EMP015 | Amit Tiwari | amit@company.com | Software Dev | Java, JavaScript, Python | Java Cert, AWS Cert |

### Skills (8)
Python, Java, Machine Learning, Artificial Intelligence, SQL, JavaScript, RDF, SPARQL

### Departments (4)
AI Department, Software Development, Data Science, HR

### Projects (3)

| Project | Department | Required Skills |
|---------|------------|-----------------|
| AI Chatbot | AI Department | Python, AI, ML |
| Employee Analytics | Data Science | Python, SQL, ML |
| Semantic Search System | Software Dev | Python, RDF, SPARQL |

### Certifications (5)

| Certification | Certifies Skill |
|---------------|-----------------|
| Python Certification | Python |
| AWS Certification | Java |
| Data Science Certification | Machine Learning |
| Machine Learning Certification | Machine Learning |
| Java Certification | Java |

### Skill Relationships

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
