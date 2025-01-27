# Dummy dataset definition used to dump the SQL and understand query efficiency
from ehrql import codelist_from_csv, create_dataset
from ehrql.tables.tpp import clinical_events_ranges

CODELIST = "codelists/opensafely-alanine-aminotransferase-alt-tests.csv"
codelist = codelist_from_csv(CODELIST, column="code")

last_codelist_event = (
    clinical_events_ranges.where(clinical_events_ranges.snomedct_code.is_in(codelist))
    .sort_by(clinical_events_ranges.date)
    .last_for_patient()
)

dataset = create_dataset()
dataset.define_population(last_codelist_event.exists_for_patient())
dataset.last_event_code = last_codelist_event.snomedct_code
dataset.last_event_lower_bound = last_codelist_event.lower_bound
dataset.last_event_comparator = last_codelist_event.comparator
dataset.last_event_value = last_codelist_event.numeric_value
dataset.last_event_upper_bound = last_codelist_event.upper_bound
