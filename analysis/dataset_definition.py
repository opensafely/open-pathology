# This dataset definition is used for testing measures definitions

from ehrql import create_dataset
from datetime import date
from ehrql import codelist_from_csv, months, create_dataset
from ehrql.tables.core import clinical_events as events
from ehrql.tables.tpp import patients, practice_registrations as registrations, clinical_events_ranges as ranges, medications
from config import codelists
import argparse

# Parse input test choice
parser = argparse.ArgumentParser()
parser.add_argument("--test")
args = parser.parse_args()
dataset = create_dataset()


# Entry point
# --------------------------------------------------------------------------------------
dataset = create_dataset()
study_start_date = date(2018, 4, 1)
study_end_date = date(2018, 5, 1)

# Utilities
# --------------------------------------------------------------------------------------
def num_months(from_, to_):
    return abs((to_.year - from_.year) * 12 + to_.month - from_.month)

# Demographics
# --------------------------------------------------------------------------------------
is_alive = patients.is_alive_on(study_start_date)
age = patients.age_on(study_start_date)
is_adult = (age >= 18) & (age < 120)
registration = registrations.for_patient_on(study_start_date)
is_registered = registration.exists_for_patient()
is_sex_recorded = patients.sex.is_in(["male", "female"])
is_male = patients.sex.is_in(["male"])

# Codelist and search period setup
# --------------------------------------------------------------------------------------

search_start = study_start_date

if args.test in ['vit_d_ref']:
    is_outside_ref = ranges.numeric_value < ranges.lower_bound
    search_start = study_start_date
elif args.test in ['psa_ref']:
    is_outside_ref = ranges.numeric_value > ranges.upper_bound
    search_start = study_start_date
#elif args.test in ['alt_mtx_ref', 'alt_mtx']:
is_outside_ref = ranges.numeric_value > ranges.upper_bound
#search_start = study_start_date - months(3)

# Codelists
# --------------------------------------------------------------------------------------

# Use clinical_events table instead of clinical_events_ranges (unless ref ranges needed)
# because clinical_events table queries are much faster
if 'ref' in args.test:
    events_table = ranges
else:
    events_table = events

# Configure test codelist path specifically if another codelist is also required (e.g. diabetes, methotrexate)
if 'alt' in args.test:

    # Use numeric alt codelist for reference range measure
    if 'ref' in args.test:
        codelist_path = codelists['alt_numeric']

    codelist_path = codelists['alt']
# hb1c_numeric codelist is needed to remove misleading % value from mean calculation
elif 'hba1c' in args.test:
    codelist_path = codelists['hba1c_numeric']
else:
    codelist_path = codelists[args.test]

codelist = codelist_from_csv(codelist_path, column="code")
codelist_events = events_table.where(
    events_table.snomedct_code.is_in(codelist) & 
    # Use 'search_start' to adapt interval start date for longer searches (e.g. last 3 months for alt with methotrexate)
    events_table.date.is_on_or_between(search_start, study_end_date)
)
print(codelist_events)
has_codelist_event = codelist_events.exists_for_patient()
last_codelist_event = codelist_events.sort_by(codelist_events.date).last_for_patient()

# Conditions
# --------------------------------------------------------------------------------------

# Define tests outside reference range
if 'ref' in args.test:

    tests_outside_ref = codelist_events.where(
        codelist_events.exists_for_patient() & 
        is_outside_ref
    ).exists_for_patient()

# Define methotrexate patients
if 'mtx' in args.test:

    codelist_mtx = codelist_from_csv(codelists[args.test], column = "code")

    # Had methoxtrexate prescribed in last 3 months and last 3-6 months (stable)
    has_mtx_rx = (
        medications.where(
        medications.dmd_code.is_in(codelist_mtx) & 
        medications.date.is_on_or_between(study_start_date - months(3), study_start_date)
    ).exists_for_patient()
    ) & (
        medications.where(
        medications.dmd_code.is_in(codelist_mtx) & 
        medications.date.is_on_or_between(study_start_date - months(6), study_start_date - months(3))
    ).exists_for_patient()
    )

# Define diabetes patients
if 'diab' in args.test:

    codelist_diab = codelist_from_csv(codelists[args.test], column = "code")
    codelist_diab_res = codelist_from_csv(codelists['diab_res'], column = "code")

    prev_events = events.where(events.date.is_on_or_before(study_start_date))
    dmlate_date = prev_events.where(events.snomedct_code.is_in(codelist)).sort_by(events.date).last_for_patient().date
    dmreso_date = prev_events.where(events.snomedct_code.is_in(codelist_diab_res)).sort_by(events.date).last_for_patient().date

    # Has diabetes if latest diagnosis is after the latests resolved date or it was never resolved, and latests diagnosis exists
    is_diabetic = (
        ((dmlate_date > dmreso_date) | dmreso_date.is_null()) 
        & dmlate_date.is_not_null()
    ) 

    # Latest hba1c values for each patient, rounded down to nearest integer
    numeric_value = codelist_events.sort_by(events.date).last_for_patient().numeric_value.as_int()    


numerator = has_codelist_event
# When testing, add has_codelist_event to denominator 
# to have sufficient events for downstream processing to work
denominator = is_alive & is_adult & is_registered & is_sex_recorded

# Update population criteria for specific tests
if 'psa' in args.test:
    denominator = denominator & is_male
elif 'mtx' in args.test:
    denominator = denominator & has_mtx_rx
elif 'hba1c_diab' in args.test:
    denominator = denominator & is_diabetic

# Remove tests with unreliable numeric values for measures that depend on that field
if 'mean' in args.test:
    
    numerator = numeric_value

    has_codelist_event = (codelist_events.where(
                    (codelist_events.numeric_value.is_not_null()) & 
                    (codelist_events.numeric_value > 0))
                    .exists_for_patient())

    denominator = denominator & has_codelist_event
# Remove tests with unreliable numeric values & reference ranges for measures that depend on that field
elif 'ref' in args.test:

    numerator = tests_outside_ref

    has_codelist_event = (events_table.where(
                    (events_table.numeric_value.is_not_null()) & 
                    (events_table.numeric_value > 0) &

                    (events_table.upper_bound.is_not_null()) & 
                    (events_table.upper_bound > 0) &
                    
                    (events_table.lower_bound.is_not_null()) & 
                    (events_table.lower_bound > 0) 
                    )
                    .exists_for_patient())

    denominator = denominator & has_codelist_event

dataset.define_population(denominator)

# Output columns depending on the test type
if 'mean' in args.test:
    dataset.mean = numeric_value
elif 'ref' in args.test:
    dataset.tests_outside_ref = tests_outside_ref
else:
    dataset.has_codelist_event = has_codelist_event

