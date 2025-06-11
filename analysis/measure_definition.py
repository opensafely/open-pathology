import argparse
from datetime import date

from ehrql import INTERVAL, Measures, codelist_from_csv, months
from ehrql.tables.core import clinical_events as events
from ehrql.tables.core import patients
from ehrql.tables.tpp import practice_registrations as registrations, clinical_events_ranges as ranges, medications
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

# Configuration
# --------------------------------------------------------------------------------------

search_start = INTERVAL.start_date

if args.test in ['vit_d_ref']:
    is_outside_ref = ranges.numeric_value < ranges.lower_bound
elif args.test in ['psa_ref']:
    is_outside_ref = ranges.numeric_value > ranges.upper_bound
elif 'mtx' in args.test:
    is_outside_ref = ranges.numeric_value > ranges.upper_bound
    search_start = INTERVAL.end_date - months(3)
elif 'diab' in args.test:
    search_start = INTERVAL.end_date - months(6)

# Codelists
# --------------------------------------------------------------------------------------
if 'mtx' in args.test:
    codelist_path = codelists['alt']
elif 'diab' in args.test:
    codelist_path = codelists['hba1c']
else:
    codelist_path = codelists[args.test]

codelist = codelist_from_csv(codelist_path, column="code")
codelist_events = events.where(
    events.snomedct_code.is_in(codelist) & 
    events.date.is_on_or_between(search_start, INTERVAL.end_date)
)
has_codelist_event = codelist_events.exists_for_patient()
last_codelist_event = codelist_events.sort_by(codelist_events.date).last_for_patient()

# Conditions
# --------------------------------------------------------------------------------------

# Define reference range
if 'ref' in args.test:

    tests_outside_ref = ranges.where(
        ranges.snomedct_code.is_in(codelist) & 
        ranges.date.is_on_or_between(search_start, INTERVAL.end_date) & 
        is_outside_ref
    ).exists_for_patient()

# Define methotrexate patients
if 'mtx' in args.test:

    codelist_mtx = codelist_from_csv(codelists[args.test], column = "code")

    # Had methoxtrexate prescribed in last 3 months and last 3-6 months (stable)
    has_mtx_rx = (
        medications.where(
        medications.dmd_code.is_in(codelist_mtx) & 
        medications.date.is_on_or_between(search_start, INTERVAL.end_date)
    ).exists_for_patient()
    ) & (
        medications.where(
        medications.dmd_code.is_in(codelist_mtx) & 
        medications.date.is_on_or_between(search_start - months(3), search_start)
    ).exists_for_patient()
    )

# Define diabetes patients
if 'diab' in args.test:

    codelist_diab = codelist_from_csv(codelists[args.test], column = "code")
    codelist_diab_res = codelist_from_csv(codelists['diab_res'], column = "code")

    prev_events = events.where(events.date.is_on_or_before(INTERVAL.start_date))
    dmlate_date = prev_events.where(events.snomedct_code.is_in(codelist)).sort_by(events.date).last_for_patient().date
    dmreso_date = prev_events.where(events.snomedct_code.is_in(codelist_diab_res)).sort_by(events.date).last_for_patient().date

    # Has diabetes if latest diagnosis is after the latests resolved date or it was never resolved, and latests diagnosis exists
    is_diabetic = (
        ((dmlate_date > dmreso_date) | dmreso_date.is_null()) 
        & dmlate_date.is_not_null()
    ) 

    # Latest hba1c values for each patient, rounded down to nearest integer
    numeric_value = codelist_events.sort_by(events.date).last_for_patient().numeric_value.as_int()    

# Measures
# --------------------------------------------------------------------------------------
measures = Measures()
measures.configure_dummy_data(population_size=100, legacy=True)
measures.configure_disclosure_control(enabled=True)
intervals = months(num_months(start_date, date.today())).starting_on(start_date)

numerator = has_codelist_event
denominator = is_alive & is_adult & is_registered & is_sex_recorded

# Update population criteria for specific tests
if 'psa' in args.test:
    denominator = denominator & is_male
elif 'mtx' in args.test:
    denominator = denominator & has_mtx_rx
elif 'hba1c_diab' in args.test:
    denominator = denominator & is_diabetic

if 'mean' in args.test:
    numerator = numeric_value
    denominator = denominator & has_codelist_event
elif 'ref' in args.test: # These are reference range measures
    numerator = tests_outside_ref
    denominator = denominator & has_codelist_event


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