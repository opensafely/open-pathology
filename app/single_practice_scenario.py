import altair
import pandas


def get_blank_scenario_table(intervals):
    idx = pandas.Index(intervals, name="date")
    df = pandas.Series(0.0, idx, name="value").to_frame()
    return df


@pandas.api.extensions.register_dataframe_accessor("scenario")
class ScenarioAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def to_chart(self):
        return (
            altair.Chart(self._obj.reset_index())
            .mark_line(color="red")
            .encode(x="date", y="value")
        )
