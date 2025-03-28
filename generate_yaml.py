"""
Description: 
- This script generates the YAML file for the project.

Usage:
- python generate_yaml.py

Output:
- project.yaml
"""

from datetime import datetime, timedelta

# --- YAML HEADER ---

yaml_header = """
version: '4.0'

actions:
"""

# --- YAML MEASURES BODY ----


# Template for measures generation
yaml_template = """
  generate_measures_{test}_tests:
    run: >
      ehrql:v1 generate-measures
        analysis/measure_definition.py
        --output output/{test}_tests/measures.arrow
        --
        --codelist {path}
    outputs:
      highly_sensitive:
        measures: output/{test}_tests/measures.arrow
  generate_processed_data_{test}_tests:
    run: >
      python:latest 
        analysis/write_processed_csv_files.py
        --output-dir output/{test}_tests
        --codelist {path}
    needs:
      [generate_measures_{test}_tests]
    outputs:
      moderately_sensitive:
        decile_table: output/{test}_tests/deciles_table_counts_per_week_per_practice.csv
        code_table: output/{test}_tests/top_5_code_table.csv
        event_counts_table: output/{test}_tests/event_counts.csv

"""

yaml_body = ""
needs = {}
codelists = {'alt': 'codelists/opensafely-alanine-aminotransferase-alt-tests.csv',
             'chol': 'codelists/opensafely-cholesterol-tests.csv',
             'hba1c': 'codelists/opensafely-glycated-haemoglobin-hba1c-tests.csv', 
             'rbc': 'codelists/opensafely-red-blood-cell-rbc-tests.csv', 
             'sodium': 'codelists/opensafely-sodium-tests-numerical-value.csv',
             'systol': 'codelists/opensafely-systolic-blood-pressure-qof.csv'}

for test, path in codelists.items():

    yaml_body += yaml_template.format(test = test, path = path)

yaml = yaml_header + yaml_body
with open("project.yaml", "w") as file:
       file.write(yaml)