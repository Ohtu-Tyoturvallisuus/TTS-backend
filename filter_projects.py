""" filter_projects.py """

import json
from collections import defaultdict

# Number of projects to extract
N = 40

# Load the JSON data from the file
with open('projects.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Group projects by starting code
projects = defaultdict(list)
for project in data['Projekti']:
    starting_code = project['ProjectId'].split('-')[0]
    projects[starting_code].append(project)

# Extract n projects
extracted_projects = []
for i, (starting_code, project_list) in enumerate(projects.items()):
    if i >= N:
        break
    extracted_projects.extend(project_list)

# Save the extracted data back to a JSON file
extracted_data = {'Projekti': extracted_projects}
with open('extracted_projects.json', 'w', encoding='utf-8') as file:
    json.dump(extracted_data, file, ensure_ascii=False, indent=4)

print("Extracted", N,  "projects and saved to 'extracted_projects.json'")
