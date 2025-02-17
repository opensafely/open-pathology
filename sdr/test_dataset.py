from datetime import date
from dataset import dataset

test_data = {
    1: { 
        "clinical_events_ranges": [{'numeric_value': 30, "snomedct_code": "1013211000000103", "date": date(2020, 4, 1), "lower_bound": 23, "upper_bound": 76, "comparator": '<'}, 
                                  {'numeric_value': 30, "snomedct_code": "1013211000000103", "date": date(2020, 4, 1), "lower_bound": 23, "upper_bound": 76, "comparator": '~'}],
        "patients": {"sex": 'male'},
        "practice_registrations": {},
        "expected_in_population": True,
        "expected_columns": {
            "valT_equalF_diffT_uppT_lowT": 1,
            "valT_equalT_diffF_uppT_lowT": 1,
        },
    }
}