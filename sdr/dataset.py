from datetime import date
import argparse
from ehrql import INTERVAL, Measures, codelist_from_csv, months, years
from ehrql.tables.core import clinical_events as events
from ehrql.tables.core import patients
from ehrql.tables.tpp import practice_registrations as registrations
from ehrql import create_dataset

dataset = create_dataset()
parser = argparse.ArgumentParser()
parser.add_argument("--codelist")
args = parser.parse_args()
index_date = "2020-03-31"
end_date = "2021-03-31"

# Codelists
# --------------------------------------------------------------------------------------
codelist = codelist_from_csv(args.codelist, column="code")
codelist_events = events.where(
    events.snomedct_code.is_in(codelist) & events.date.is_on_or_between(index_date, end_date)
)

dataset.region = registrations.for_patient_on(index_date).practice_nuts1_region_name

dataset.codelist_event_count = codelist_events.count_for_patient()

dataset.test_value_count = codelist_events.where(events.numeric_value.is_not_null()).count_for_patient()

dataset.define_population(patients.exists_for_patient())