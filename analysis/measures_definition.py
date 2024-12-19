import utils
from ehrql import Measures, months
from variables import get_measures_variables, get_population_variables, key_measures


population_variables = get_population_variables()
measures_variables = get_measures_variables()

measures = Measures()
measures.configure_disclosure_control(enabled=False)
measures.define_defaults(
    denominator=population_variables["denominator"],
)


start_date = "2019-01-01"
num_intervals = utils.calculate_num_intervals(start_date)


for m in key_measures:
    measures.define_measure(
        name=f"{m}_practice",
        numerator=measures_variables[m + "_binary_flag"],
        intervals=months(num_intervals).starting_on(start_date),
        group_by={
            "practice": population_variables["registered_practice_id"],
        },
    )

    measures.define_measure(
        name=f"{m}_code",
        numerator=measures_variables[m + "_binary_flag"],
        intervals=months(num_intervals).starting_on(start_date),
        group_by={m + "_code": measures_variables[m + "_code"]},
    )
