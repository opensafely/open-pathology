import argparse
from datetime import date

from ehrql import INTERVAL, Measures, codelist_from_csv, months, show
from ehrql.tables.core import clinical_events as events
from ehrql.tables.core import patients
from ehrql.tables.tpp import practice_registrations as registrations, clinical_events_ranges as ranges, medications, addresses
from config import codelists

# Parse input test choice
parser = argparse.ArgumentParser()
parser.add_argument("--test")
parser.add_argument("--light", action= 'store_true')
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

# Registered at the start of the interval 
is_registered = registrations.exists_for_patient_on(INTERVAL.start_date)

is_sex_recorded = patients.sex.is_in(["male", "female"])

is_male = patients.sex.is_in(['male'])

# Breakdown variables
# --------------------------------------------------------------------------------------

imd = addresses.for_patient_on(INTERVAL.start_date).imd_quintile

ethnicity_codelist = codelist_from_csv("codelists/opensafely-ethnicity-snomed-0removed.csv", 
                                       column="code",
                                       category_column="Grouping_6")
ethnicity = (
    events.where(events.snomedct_code.is_in(ethnicity_codelist))
    .where(events.date.is_on_or_before(INTERVAL.start_date))
    .sort_by(events.date)
    .last_for_patient()
    .snomedct_code.to_category(ethnicity_codelist)
)

sex = patients.sex

region = (registrations.for_patient_on(INTERVAL.start_date)
          .practice_nuts1_region_name)

# Configuration
# --------------------------------------------------------------------------------------

search_start = INTERVAL.start_date

# Change intervals for alt mtx in 3 months and hba1c diab in 6 months
if args.test == 'alt_mtx':
    # Tests in last 3 months would include the specified month (e.g. Interval starting on April = {April, March, February})
    search_start = INTERVAL.end_date - months(3)
elif args.test == 'hba1c_diab':
    search_start = INTERVAL.end_date - months(6)

# Filter to codelist events
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
    else: 
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
    events_table.date.is_on_or_between(search_start, INTERVAL.end_date)
)

# Quality Assurance
# --------------------------------------------------------------------------------------

# Apply QA on numeric value when calculating mean or reference ranges
if ('mean' in args.test) | ('ref' in args.test):

    codelist_events = codelist_events.where(
                        (codelist_events.numeric_value.is_not_null()) & 
                        (codelist_events.numeric_value > 0))

    if 'ref' in args.test:

        # Apply additional QA on upper/lower bound for reference ranges
        if args.test == 'vit_d_ref':
            
            is_outside_ref = codelist_events.numeric_value < codelist_events.lower_bound

            codelist_events = codelist_events.where(
                        (codelist_events.lower_bound.is_not_null()) & 
                        (codelist_events.lower_bound > 0) 
                        )
            
        elif args.test in ['psa_ref', 'alt_mtx_ref']:

            is_outside_ref = codelist_events.numeric_value > codelist_events.upper_bound

            codelist_events = codelist_events.where(
                        (codelist_events.upper_bound.is_not_null()) & 
                        (codelist_events.upper_bound > 0) 
                        )
            
        tests_outside_ref = codelist_events.where(is_outside_ref).exists_for_patient()
    
# Defining subpopulations
# --------------------------------------------------------------------------------------

# Define methotrexate patients
if 'mtx' in args.test:

    codelist_mtx = codelist_from_csv(codelists[args.test], column = "code")

    # Had methoxtrexate prescribed in last 3 months and last 3-6 months (stable)
    has_mtx_rx = (
        medications.where(
        medications.dmd_code.is_in(codelist_mtx) & 
        medications.date.is_on_or_between(INTERVAL.start_date - months(3), INTERVAL.end_date)
    ).exists_for_patient()
    ) & (
        medications.where(
        medications.dmd_code.is_in(codelist_mtx) & 
        medications.date.is_on_or_between(INTERVAL.start_date - months(6), INTERVAL.start_date - months(3))
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

# Defining Measures
# --------------------------------------------------------------------------------------

measures = Measures()
measures.configure_dummy_data(population_size=10, legacy=True)

# Disable rounding & redaction for reference range measures & vit d
if ('ref' in args.test) | ('vit_d' in args.test):
    measures.configure_disclosure_control(enabled=False)
else:
    measures.configure_disclosure_control(enabled=True)

if args.light == True:
    # Run a single year for test run
    intervals = months(12).starting_on(start_date)
else:
    intervals = months(num_months(start_date, date.today())).starting_on(start_date)

has_codelist_event = codelist_events.exists_for_patient()
last_codelist_event = codelist_events.sort_by(codelist_events.date).last_for_patient()

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

# Add test taken as requirement to denominator reference range measures
if 'ref' in args.test:

    numerator = tests_outside_ref
    denominator = denominator & has_codelist_event

# For mean, sum(numeric_value) / sum(patients who had a test) = mean value of tests (ratio column)
if 'mean' in args.test:

    # Latest values for each patient, rounded down to nearest integer
    numerator = codelist_events.sort_by(events.date).last_for_patient().numeric_value.as_int() 
    denominator = denominator & has_codelist_event

measures.define_defaults(
    numerator = numerator,
    denominator = denominator,
    intervals = intervals
)

measures.define_measure(
    name="by_practice",
    group_by={"practice": registrations.for_patient_on(INTERVAL.start_date).practice_pseudo_id}
)

measures.define_measure(
    name="by_snomedct_code",
    group_by={"snomedct_code": last_codelist_event.snomedct_code},
)

# Additional breakdowns for original measures
demographic_measures = ['alt', 'chol', 'hba1c', 'hba1c_numeric', 'rbc', 'sodium', 'systol']

if args.test in demographic_measures:
    measures.define_measure(
        name="by_IMD",
        group_by={"IMD": imd},
    )
    measures.define_measure(
        name="by_ethnicity",
        group_by={"ethnicity": ethnicity},
    )
    measures.define_measure(
        name="by_sex",
        group_by={"sex": sex},
    )
    measures.define_measure(
        name="by_region",
        group_by={"region": region},
    )

