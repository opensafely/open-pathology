import argparse
from datetime import date

from ehrql import INTERVAL, Measures, codelist_from_csv, months
from ehrql.tables.core import clinical_events as events
from ehrql.tables.core import patients
from ehrql.tables.tpp import practice_registrations as registrations, clinical_events_ranges as ranges
from config import codelists

parser = argparse.ArgumentParser()
parser.add_argument("--test")
args = parser.parse_args()

start_date = date(2018, 4, 1)


def num_months(from_, to_):
    """Returns the number of months between the given dates."""
    return abs((to_.year - from_.year) * 12 + to_.month - from_.month)


# same year, same month
assert num_months(date(2025, 1, 1), date(2025, 1, 31)) == 0
# different year, different month
assert num_months(date(2024, 1, 1), date(2025, 2, 1)) == 13
assert num_months(date(2024, 2, 1), date(2025, 1, 1)) == 11
# to_ before from_
assert num_months(date(2025, 2, 1), date(2024, 1, 1)) == 13


# Demographic variables
# --------------------------------------------------------------------------------------
is_alive = patients.is_alive_on(INTERVAL.start_date)

age = patients.age_on(INTERVAL.start_date)
is_adult = (age >= 18) & (age < 120)

registration = registrations.for_patient_on(INTERVAL.start_date)
is_registered = registration.exists_for_patient()

is_sex_recorded = patients.sex.is_in(["male", "female"])

is_male = patients.sex.is_in(['male'])

# Codelists
# --------------------------------------------------------------------------------------
codelist_path = codelists[args.test]
codelist = codelist_from_csv(codelist_path, column="code")
codelist_events = events.where(
    events.snomedct_code.is_in(codelist) & events.date.is_during(INTERVAL)
)
has_codelist_event = codelist_events.exists_for_patient()
last_codelist_event = codelist_events.sort_by(codelist_events.date).last_for_patient()

# Conditions
# --------------------------------------------------------------------------------------

# Define reference range for vit_d and psa tests
if args.test in ['vit_d_ref', 'psa_ref']:

    if args.test == 'vit_d_ref':
        is_outside_ref = ranges.numeric_value < ranges.lower_bound
    elif args.test == 'psa_ref':
        is_outside_ref = ranges.numeric_value > ranges.upper_bound

    tests_outside_ref = ranges.where(
        ranges.snomedct_code.is_in(codelist) & ranges.date.is_during(INTERVAL) & is_outside_ref
    ).exists_for_patient()
    

# Measures
# --------------------------------------------------------------------------------------
measures = Measures()
measures.configure_dummy_data(population_size=100, legacy=True)
measures.configure_disclosure_control(enabled=True)
intervals = months(num_months(start_date, date.today())).starting_on(start_date)

numerator = has_codelist_event
denominator = is_alive & is_adult & is_registered & is_sex_recorded

if args.test in ['psa', 'psa_ref']:
    denominator = denominator & is_male

if args.test in ['vit_d_ref', 'psa_ref']:
    numerator = tests_outside_ref
    denominator = numerator & denominator

measures.define_defaults(
    numerator = numerator,
    denominator = denominator,
    intervals = intervals
)

measures.define_measure(
    name="by_practice",
    group_by={"practice": registration.practice_pseudo_id},
)
measures.define_measure(
    name="by_snomedct_code",
    group_by={"snomedct_code": last_codelist_event.snomedct_code},
)