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
elif args.test in ['psa_ref']:
    is_outside_ref = ranges.numeric_value > ranges.upper_bound
elif 'mtx' in args.test:
    is_outside_ref = ranges.numeric_value > ranges.upper_bound
    search_start = study_end_date - months(3)
elif 'diab' in args.test:
    search_start = study_end_date - months(6)

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
    events.date.is_on_or_between(search_start, study_end_date)
)
has_codelist_event = codelist_events.exists_for_patient()
last_codelist_event = codelist_events.sort_by(events.date).last_for_patient()

# Reference range logic
# --------------------------------------------------------------------------------------
if 'ref' in args.test:
    tests_outside_ref = ranges.where(
        ranges.snomedct_code.is_in(codelist) &
        ranges.date.is_on_or_between(search_start, study_end_date) &
        is_outside_ref
    ).exists_for_patient()

# Methotrexate logic
# --------------------------------------------------------------------------------------
if 'mtx' in args.test:
    codelist_mtx = codelist_from_csv(codelists[args.test], column="code")
    has_recent_rx = medications.where(
        medications.dmd_code.is_in(codelist_mtx) &
        medications.date.is_on_or_between(search_start, study_end_date)
    ).exists_for_patient()
    has_prior_rx = medications.where(
        medications.dmd_code.is_in(codelist_mtx) &
        medications.date.is_on_or_between(search_start - months(3), search_start)
    ).exists_for_patient()
    has_mtx_rx = has_recent_rx & has_prior_rx

# Diabetes logic
# --------------------------------------------------------------------------------------
if 'diab' in args.test:
    codelist_diab = codelist_from_csv(codelists[args.test], column="code")
    codelist_diab_res = codelist_from_csv(codelists['diab_res'], column="code")
    prev_events = events.where(events.date.is_on_or_before(study_start_date))

    dmlate_date = prev_events.where(events.snomedct_code.is_in(codelist_diab)).sort_by(events.date).last_for_patient().date
    dmreso_date = prev_events.where(events.snomedct_code.is_in(codelist_diab_res)).sort_by(events.date).last_for_patient().date

    is_diabetic = ((dmlate_date > dmreso_date) | dmreso_date.is_null()) & dmlate_date.is_not_null()
    numeric_value = codelist_events.sort_by(events.date).last_for_patient().numeric_value.as_int()

# Population
# --------------------------------------------------------------------------------------
inclusion_criteria = (
    is_alive &
    is_adult &
    is_registered &
    is_sex_recorded
)

# Adjust population for special cases
if 'psa' in args.test:
    inclusion_criteria = inclusion_criteria & is_male
elif 'mtx' in args.test:
    inclusion_criteria = inclusion_criteria & has_mtx_rx
elif 'hba1c_diab' in args.test:
    inclusion_criteria = inclusion_criteria & is_diabetic

dataset.define_population(inclusion_criteria)

# Output columns depending on the test type
if 'mean' in args.test:
    dataset.mean = numeric_value
elif 'ref' in args.test:
    dataset.tests_outside_ref = tests_outside_ref
else:
    dataset.has_codelist_event = has_codelist_event

