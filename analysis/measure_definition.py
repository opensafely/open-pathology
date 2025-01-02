import argparse
from datetime import date

from ehrql import INTERVAL, Measures, codelist_from_csv, months
from ehrql.tables.core import clinical_events as events
from ehrql.tables.core import patients
from ehrql.tables.tpp import practice_registrations as registrations


parser = argparse.ArgumentParser()
parser.add_argument("--codelist")
args = parser.parse_args()

start_date = date(2024, 4, 1)


def num_months(from_, to_):
    """Returns the number of months between the given dates."""
    return abs(to_.year - from_.year) * 12 + abs(from_.month - to_.month)


# same year, same month
assert num_months(date(2025, 1, 1), date(2025, 1, 31)) == 0
# different year, different month
assert num_months(date(2024, 1, 1), date(2025, 2, 1)) == 13
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


# Codelists
# --------------------------------------------------------------------------------------
codelist = codelist_from_csv(args.codelist, column="code")
codelist_events = events.where(
    events.snomedct_code.is_in(codelist) & events.date.is_during(INTERVAL)
)
has_codelist_event = codelist_events.exists_for_patient()
last_codelist_event = codelist_events.sort_by(codelist_events.date).last_for_patient()


# Measures
# --------------------------------------------------------------------------------------
measures = Measures()
measures.define_defaults(
    denominator=is_alive & is_adult & is_registered & is_sex_recorded
)
intervals = months(num_months(start_date, date.today())).starting_on(start_date)
measures.define_measure(
    name="by_practice",
    numerator=has_codelist_event,
    intervals=intervals,
    group_by={"practice": registration.practice_pseudo_id},
)
measures.define_measure(
    name="by_snomedct_code",
    numerator=has_codelist_event,
    intervals=intervals,
    group_by={"snomedct_code": last_codelist_event.snomedct_code},
)
