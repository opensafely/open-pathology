import argparse

from ehrql import INTERVAL, Measures, codelist_from_csv, years
from ehrql.tables.tpp import clinical_events_ranges as ranges
from ehrql.tables.tpp import practice_registrations as registrations


parser = argparse.ArgumentParser()
parser.add_argument("--codelist")
args = parser.parse_args()
index_date = "2018-01-01"

# Codelists
codelist = codelist_from_csv(args.codelist, column="code")
codelist_events = ranges.where(
    ranges.snomedct_code.is_in(codelist) & ranges.date.is_during(INTERVAL)
)

# Stratification variables
region = registrations.for_patient_on(INTERVAL.start_date).practice_nuts1_region_name

# Presence of codelist (denominator)
codelist_event_count = codelist_events.count_for_patient()

# Booleans
has_test_value = ranges.numeric_value.is_not_null()
has_comparator = ranges.comparator.is_not_null()
has_upper_bound = ranges.upper_bound.is_not_null()
has_lower_bound = ranges.lower_bound.is_not_null()

has_2_bound = has_upper_bound & has_lower_bound
has_1_bound = (has_upper_bound | has_lower_bound) & ~has_2_bound
has_0_bound = ~has_upper_bound & ~has_lower_bound

count_measures = dict()
# Venn diagram

# Value and comparator
count_measures["valueT_comparator_T_bounds2"] = ranges.where(
    has_test_value & has_comparator & has_2_bound
).count_for_patient()

count_measures["valueT_comparatorT_bounds1"] = ranges.where(
    has_test_value & has_comparator & has_1_bound
).count_for_patient()

count_measures["valueT_comparatorT_bounds0"] = ranges.where(
    has_test_value & has_comparator & has_0_bound
).count_for_patient()

# Value and no comparator
count_measures["valueT_comparatorF_bounds2"] = ranges.where(
    has_test_value & ~has_comparator & has_2_bound
).count_for_patient()

count_measures["valueT_comparatorF_bounds1"] = ranges.where(
    has_test_value & ~has_comparator & has_1_bound
).count_for_patient()

count_measures["valueT_comparatorF_bounds0"] = ranges.where(
    has_test_value & ~has_comparator & has_0_bound
).count_for_patient()

# No value and comparator
count_measures["valueF_comparatorT_bounds2"] = ranges.where(
    ~has_test_value & has_comparator & has_2_bound
).count_for_patient()

count_measures["valueF_comparatorT_bounds1"] = ranges.where(
    ~has_test_value & has_comparator & has_1_bound
).count_for_patient()

count_measures["valueF_comparatorT_bounds0"] = ranges.where(
    ~has_test_value & has_comparator & has_0_bound
).count_for_patient()

# No value and no comparator
count_measures["valueF_comparatorF_bounds2"] = ranges.where(
    ~has_test_value & ~has_comparator & has_2_bound
).count_for_patient()

count_measures["valueF_comparatorF_bounds1"] = ranges.where(
    ~has_test_value & ~has_comparator & has_1_bound
).count_for_patient()

count_measures["valueF_comparatorF_bounds0"] = ranges.where(
    ~has_test_value & ~has_comparator & has_0_bound
).count_for_patient()

# Measures
# --------------------------------------------------------------------------------------
measures = Measures()
measures.configure_dummy_data(population_size=1000, legacy=True)
measures.define_defaults(
    denominator=codelist_event_count,
    intervals=years(7).starting_on(index_date),
    group_by={"region": region},
)

for m, numerator in count_measures.items():
    measures.define_measure(
        name=m,
        numerator=numerator,
    )
