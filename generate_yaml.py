"""
Description: 
- This script generates the YAML file for the project.

Usage:
- python generate_yaml.py

Output:
- project.yaml
"""

from datetime import datetime, timedelta
from analysis.config import codelists
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
        --test {test}
    outputs:
      highly_sensitive:
        measures: output/{test}_tests/measures.arrow
  generate_processed_data_{test}_tests:
    run: >
      python:latest 
        analysis/write_processed_csv_files.py
        --output-dir output/{test}_tests
        --test {test}
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

tests = codelists
del tests['diab_res']

for test in tests.keys():

    yaml_body += yaml_template.format(test = test)

yaml = yaml_header + yaml_body
with open("project.yaml", "w") as file:
       file.write(yaml)