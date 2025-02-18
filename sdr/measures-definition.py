from datetime import date
import argparse
from ehrql import INTERVAL, Measures, codelist_from_csv, months, years
from ehrql.tables.core import clinical_events as events
from ehrql.tables.core import patients
from ehrql.tables.tpp import practice_registrations as registrations

parser = argparse.ArgumentParser()
parser.add_argument("--codelist")
args = parser.parse_args()

# Codelists
# --------------------------------------------------------------------------------------
codelist = codelist_from_csv(args.codelist, column="code")
codelist_events = events.where(
    events.snomedct_code.is_in(codelist) & events.date.is_during(INTERVAL)
)

index_date = "2018-01-01"

region = registrations.for_patient_on(INTERVAL.start_date).practice_nuts1_region_name

codelist_event_count = codelist_events.count_for_patient()

test_value_count = codelist_events.where(events.numeric_value.is_not_null()).count_for_patient()


# Measures
# --------------------------------------------------------------------------------------
measures = Measures()
measures.configure_dummy_data(population_size=1000, legacy=True)
measures.define_defaults(
    denominator= codelist_event_count
)

intervals = years(7).starting_on(index_date)
measures.define_measure(
    name="test_value_present",
    numerator=test_value_count,
    intervals=intervals,
    group_by={"region": region},
)