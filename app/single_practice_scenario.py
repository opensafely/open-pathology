import altair
import numpy
import pandas


DATE_COL = "Date"
VALUE_COL = "Rate per 1,000 registered patients"


def get_randomised_scenario_table(intervals, min_value, max_value):
    idx = pandas.Index(intervals, name=DATE_COL)
    df = pandas.Series(0.0, idx, name=VALUE_COL).to_frame()
    df.loc[:, VALUE_COL] = numpy.random.uniform(min_value, max_value, len(df)).round(2)
    return df


@pandas.api.extensions.register_dataframe_accessor("scenario")
class ScenarioAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def to_chart(self):
        return (
            altair.Chart(self._obj.reset_index())
            .mark_line(color="red")
            .encode(x=DATE_COL, y=VALUE_COL)
        )
