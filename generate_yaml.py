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
  generate_measures_{test}_tests_light:
    run: >
      ehrql:v1 generate-measures
        analysis/measure_definition.py
        --output output/{test}_tests/measures_light.arrow
        --
        --test {test}
        --light
    outputs:
      highly_sensitive:
        measures: output/{test}_tests/measures_light.arrow
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
        monthly_tables: output/{test}_tests/*table_counts_per_week*.csv
        code_table: output/{test}_tests/top_5_code_table.csv
        event_counts_table: output/{test}_tests/event_counts.csv
  generate_processed_data_{test}_tests_light:
    run: >
      python:latest 
        analysis/write_processed_csv_files.py
        --output-dir output/{test}_tests
        --test {test}
        --light
    needs:
      [generate_measures_{test}_tests_light]
    outputs:
      moderately_sensitive:
        monthly_tables: output/{test}_tests/*per_week_per_practice_light.csv
        code_table: output/{test}_tests/top_5_code_table_light.csv
        event_counts_table: output/{test}_tests/event_counts_light.csv
  generate_dataset_test_{test}:
    run: >
        ehrql:v1 generate-dataset
        analysis/dataset_definition.py
        --test-data-file analysis/test_dataset.py
        --output output/tests/{test}_dataset.csv
        --
        --test {test}
    outputs:
      highly_sensitive:
        population: output/tests/{test}_dataset.csv
"""

yaml_body = ""
needs = {}

tests = codelists
del tests['diab_res']
del tests['alt_numeric']

for test in tests.keys():

    yaml_body += yaml_template.format(test = test)

yaml_plots = """
  generate_plots:
    run: >
      r:latest 
        analysis/plots.r
    outputs:
      moderately_sensitive:
        plots: output*.png
"""

yaml = yaml_header + yaml_body + yaml_plots
with open("project.yaml", "w") as file:
       file.write(yaml)