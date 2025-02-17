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
has_equality_comparator = ranges.comparator.is_in(['=','~'])
has_differential_comparator = (ranges.comparator.is_not_null() & ~has_equality_comparator)
has_upper_bound = ranges.upper_bound.is_not_null()
has_lower_bound = ranges.lower_bound.is_not_null()

# Generate all combinations of test_value, equality_comparator, differential_comparator, upper_bound, and lower_bound
# E.g. valT_equalT_diffF_uppT_lowF
count_measures = dict()
for value in [True, False]:
    # Use zip to exclude equal_compT, diff_compT (since both can't be true)
    for equal_comp, diff_comp in zip([True, False, False], [False, True, False]):
            for upper in [True, False]:
                for lower in [True, False]:
                    key = f"val{'T' if value else 'F'}_equal{'T' if equal_comp else 'F'}_diff{'T' if diff_comp else 'F'}_upp{'T' if upper else 'F'}_low{'T' if lower else 'F'}"
                    count_measures[key] = codelist_events.where(
                        (has_test_value if value else ~has_test_value) &
                        (has_equality_comparator if equal_comp else ~has_equality_comparator) &
                        (has_differential_comparator if diff_comp else ~has_differential_comparator) &
                        (has_upper_bound if upper else ~has_upper_bound) &
                        (has_lower_bound if lower else ~has_lower_bound)
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
