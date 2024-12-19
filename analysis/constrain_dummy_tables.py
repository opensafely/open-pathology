# Simple script to modify (customise) randomly generated dummy tables
# The goal is to lead to better downstream dummy data
# This is done by imposing constraints that are not supported by additional_population_constraint yet

import random
from datetime import datetime

import pandas as pd


dummy_tables_path = "dummy_tables"


# 1. Assign all patients randomly to one of a fixed number of practices
num_practices = 100

df_pr = pd.read_csv(f"{dummy_tables_path}/practice_registrations.csv")
df_pr["practice_pseudo_id"] = random.choices(range(1, num_practices + 1), k=len(df_pr))
df_pr.to_csv(f"{dummy_tables_path}/practice_registrations.csv", index=False)

# 2. Constrain clinical events to after a certain year, ignoring leap year dates
# Assumes all patients are alive, which is a constraint in the dummy data definition
# The existing event date is always after the patient's date of birth
# TODO: Tidy up this stuff if we're really using it, as in 2025 it'll throw 1/5 of the data out
possible_years = range(2019, datetime.now().year + 1)


def replace_date(date):
    # Keep leap year dates unchanged as they are rare and not worth the effort to deal with
    if "-02-29" in date:
        return date
    # Do not change if the year is already in range to avoid events before birth
    if int(date[:4]) in possible_years:
        return date
    return f"{random.choice(possible_years)}-{date[5:]}"


df_ce = pd.read_csv(
    f"{dummy_tables_path}/clinical_events.csv",
    converters={"date": replace_date},
    dtype={"snomedct_code": str},
)
df_ce.to_csv(f"{dummy_tables_path}/clinical_events.csv", index=False)
