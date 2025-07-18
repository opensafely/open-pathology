# This script is used to test the measures definition.

from datetime import date
from dataset_definition import dataset
from dataset_definition import args

test_data_options = {
    # Vit d outside ref
    1: {
        "patients": {"date_of_birth": date(1950, 1, 1), "sex": "male"},
        "medications": [],
        "clinical_events": [
            {"date": date(2018, 4, 15), "snomedct_code": "1031181000000107"}
        ],
        "clinical_events_ranges": [
            {
                "date": date(2018, 4, 15),
                "snomedct_code": "1031181000000107",
                "numeric_value": 4,
                "lower_bound": 7,
            }
        ],
        "practice_registrations": [
            {"start_date": date(2010, 1, 1), "end_date": date(2025, 1, 1)}
        ],
        "expected_in_population": True,
        "expected_columns": {
            "tests_outside_ref": True,
        },
    },
    # Vit d inside ref
    2: {
        "patients": {"date_of_birth": date(1950, 1, 1), "sex": "male"},
        "medications": [],
        "clinical_events": [
            {"date": date(2018, 4, 15), "snomedct_code": "1031181000000107"}
        ],
        "clinical_events_ranges": [
            {
                "date": date(2018, 4, 15),
                "snomedct_code": "1031181000000107",
                "numeric_value": 7,
                "lower_bound": 7,
            }
        ],
        "practice_registrations": [
            {"start_date": date(2010, 1, 1), "end_date": date(2025, 1, 1)}
        ],
        "expected_in_population": True,
        "expected_columns": {
            "tests_outside_ref": False,
        },
    },
    3: {  # PSA outside ref
        "patients": {"date_of_birth": date(1950, 1, 1), "sex": "male"},
        "medications": [],
        "clinical_events": [
            {"date": date(2018, 4, 15), "snomedct_code": "1000381000000105"}
        ],
        "clinical_events_ranges": [
            {
                "date": date(2018, 4, 15),
                "snomedct_code": "1000381000000105",
                "numeric_value": 9,
                "upper_bound": 7,
            }
        ],
        "practice_registrations": [
            {"start_date": date(2010, 1, 1), "end_date": date(2025, 1, 1)}
        ],
        "expected_in_population": True,
        "expected_columns": {
            "tests_outside_ref": True,
        },
    },
    4: {  # PSA inside ref
        "patients": {"date_of_birth": date(1950, 1, 1), "sex": "male"},
        "medications": [],
        "clinical_events": [
            {"date": date(2018, 4, 15), "snomedct_code": "1000381000000105"}
        ],
        "clinical_events_ranges": [
            {
                "date": date(2018, 4, 15),
                "snomedct_code": "1000381000000105",
                "numeric_value": 4,
                "upper_bound": 7,
            }
        ],
        "practice_registrations": [
            {"start_date": date(2010, 1, 1), "end_date": date(2025, 1, 1)}
        ],
        "expected_in_population": True,
        "expected_columns": {
            "tests_outside_ref": False,
        },
    },
    5: {  # alt-mtx-ref within 1 months inside ref
        "patients": {"date_of_birth": date(1950, 1, 1), "sex": "male"},
        "medications": [
            {"date": date(2018, 2, 15), "dmd_code": "12816911000001103"},
            {"date": date(2017, 11, 15), "dmd_code": "12816911000001103"},
        ],
        "clinical_events": [
            {"date": date(2018, 4, 15), "snomedct_code": "1013211000000103"}
        ],
        "clinical_events_ranges": [
            {
                "date": date(2018, 4, 15),
                "snomedct_code": "1013211000000103",
                "numeric_value": 5,
                "lower_bound": 3,
                "upper_bound": 7,
            }
        ],
        "practice_registrations": [
            {"start_date": date(2010, 1, 1), "end_date": date(2025, 1, 1)}
        ],
        "expected_in_population": True,
        "expected_columns": {
            "tests_outside_ref": False,
        },
    },
    6: {  # alt-mtx-ref outside 3 months inside ref
        "patients": {"date_of_birth": date(1950, 1, 1), "sex": "male"},
        "medications": [{"date": date(2018, 1, 15), "dmd_code": "12816911000001103"}],
        "clinical_events": [
            {"date": date(2017, 10, 15), "snomedct_code": "1013211000000103"}
        ],
        "clinical_events_ranges": [
            {
                "date": date(2017, 10, 15),
                "snomedct_code": "1013211000000103",
                "numeric_value": 5,
                "lower_bound": 2,
                "upper_bound": 7,
            }
        ],
        "practice_registrations": [
            {"start_date": date(2010, 1, 1), "end_date": date(2025, 1, 1)}
        ],
        "expected_in_population": False,
        "expected_columns": {
            "tests_outside_ref": False,
        },
    },
    7: {  # alt-mtx-ref within 1 months, proxy null lower bound
        "patients": {"date_of_birth": date(1950, 1, 1), "sex": "male"},
        "medications": [
            {"date": date(2018, 2, 15), "dmd_code": "12816911000001103"},
            {"date": date(2017, 11, 15), "dmd_code": "12816911000001103"},
        ],
        "clinical_events": [
            {"date": date(2018, 4, 15), "snomedct_code": "1013211000000103"}
        ],
        "clinical_events_ranges": [
            {
                "date": date(2018, 4, 15),
                "snomedct_code": "1013211000000103",
                "numeric_value": 5,
                "upper_bound": 7,
                "lower_bound": 0
            }
        ],
        "practice_registrations": [
            {"start_date": date(2010, 1, 1), "end_date": date(2025, 1, 1)}
        ],
        "expected_in_population": True,
        "expected_columns": {
            "tests_outside_ref": False,
        },
    },
    8: {  # alt-mtx-ref within 1 months, proxy null upper bound
        "patients": {"date_of_birth": date(1950, 1, 1), "sex": "male"},
        "medications": [
            {"date": date(2018, 2, 15), "dmd_code": "12816911000001103"},
            {"date": date(2017, 11, 15), "dmd_code": "12816911000001103"},
        ],
        "clinical_events": [
            {"date": date(2018, 4, 15), "snomedct_code": "1013211000000103"}
        ],
        "clinical_events_ranges": [
            {
                "date": date(2018, 4, 15),
                "snomedct_code": "1013211000000103",
                "numeric_value": 5,
                "lower_bound": 1,
                "upper_bound": 0
            }
        ],
        "practice_registrations": [
            {"start_date": date(2010, 1, 1), "end_date": date(2025, 1, 1)}
        ],
        "expected_in_population": False,
        "expected_columns": {
            "tests_outside_ref": False,
        },
    },
    9: {  # hba1c_diab_mean numeric_value within 1 months
        "patients": {"date_of_birth": date(1950, 1, 1), "sex": "male"},
        "medications": [],
        "clinical_events": [
            {"date": date(2018, 3, 15), "snomedct_code": "1196922005"},
            {
                "date": date(2017, 4, 15),
                "snomedct_code": "999791000000106",
                "numeric_value": 4,
            },
        ],
        "clinical_events_ranges": [],
        "practice_registrations": [
            {"start_date": date(2010, 1, 1), "end_date": date(2025, 1, 1)}
        ],
        "expected_in_population": True,
        "expected_columns": {
            "mean": 4,
        },
    },
    10: {  # hba1c_diab numeric_value outside 6 months
        "patients": {"date_of_birth": date(1950, 1, 1), "sex": "male"},
        "medications": [],
        "clinical_events": [
            {"date": date(2015, 10, 15), "snomedct_code": "1196922005"},
            {"date": date(2015, 11, 15), "snomedct_code": "1003671000000109"},
        ],
        "clinical_events_ranges": [
            {
                "date": date(2015, 11, 15),
                "snomedct_code": "999791000000106",
                "numeric_value": 4,
            }
        ],
        "practice_registrations": [
            {"start_date": date(2010, 1, 1), "end_date": date(2025, 1, 1)}
        ],
        "expected_in_population": True,
        "expected_columns": {
            "has_codelist_event": False,
        },
    },
    11: {  # Negative control
        "patients": {"date_of_birth": date(1950, 1, 1), "sex": "male"},
        "medications": [],
        "clinical_events": [],
        "clinical_events_ranges": [],
        "practice_registrations": [
            {"start_date": date(2010, 1, 1), "end_date": date(2025, 1, 1)}
        ],
        "expected_in_population": False,
    },
}

# Choose patients based on choice of test/codelist
if args.test == "vit_d_ref":
    patients = [1, 2]
elif args.test == "psa_ref":
    patients = [3, 4]
elif args.test == "alt_mtx_ref":
    patients = [5, 6, 7, 8]
elif args.test == "hba1c_diab_mean":
    patients = [9]
elif args.test == "hba1c_diab":
    patients = [10]

# Add the negative control patient
patients.append(11)
test_data = {}
for patient in patients:
    test_data[patient] = test_data_options[patient]
