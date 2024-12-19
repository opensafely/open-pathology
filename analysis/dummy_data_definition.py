import utils
from ehrql import Dataset
from ehrql.tables.core import patients
from variables import (
    get_measures_variables,
    get_population_variables,
    key_measures,
)


dataset = Dataset()
dataset.configure_dummy_data(population_size=1000 * len(key_measures), legacy=False)

data_start_date = "2019-01-01"
data_end_date = utils.get_start_of_latest_full_month().strftime("%Y-%m-%d")

population_variables = get_population_variables(data_start_date)

# Use the denominator to define the population
# Place additional constraints to get around quirks of the dummy data generator:
# - Have everyone be alive only for the dummy data because otherwise we get so few alive people
dataset.define_population(
    population_variables["denominator"] & patients.date_of_death.is_null()
)

# Define dataset fields from the numerators
measures_variables = get_measures_variables(data_start_date, data_end_date)
dataset.practice = population_variables["registered_practice_id"]
for m in key_measures:
    setattr(dataset, f"{m}_binary_flag", measures_variables[m + "_binary_flag"])
    setattr(dataset, f"{m}_code", measures_variables[m + "_code"])
