import dataclasses
import pathlib

import altair
import pandas
import structlog
import yaml


log = structlog.get_logger(__name__)

PERCENTILE = "Percentile"
DECILE = "Decile"
MEDIAN = "Median"


@dataclasses.dataclass
class Measure:
    name: str
    explanation: str
    caveats: str
    codelist_url: str
    total_events: int
    top_5_codes_table: pandas.DataFrame
    deciles_table: pandas.DataFrame
    chart_units: str

    def __repr__(self):
        return f"Measure(name='{self.name}')"

    def change_in_median(self, from_year, to_year, month):
        # Pandas wants these to be strings
        from_year = str(from_year)
        to_year = str(to_year)

        dt = self.deciles_table  # convenient alias
        is_month = dt["date"].dt.month == month
        is_median = dt["label"] == MEDIAN
        # set index to date to allow convenient selection by year
        value = dt.loc[is_month & is_median].set_index("date").loc[:, "value"]

        # .values is a numpy array
        from_val = value[from_year].values[0]
        to_val = value[to_year].values[0]
        pct_change = (to_val - from_val) / from_val

        return from_val, to_val, pct_change

    @property
    def deciles_chart(self):
        # selections
        legend_selection = altair.selection_point(bind="legend", fields=["label"])

        # encodings
        stroke_dash = altair.StrokeDash(
            "label",
            title=None,
            scale=altair.Scale(
                domain=[PERCENTILE, DECILE, MEDIAN],
                range=[[1, 1], [5, 5], [0, 0]],
            ),
            legend=altair.Legend(orient="bottom"),
        )
        stroke_width = (
            altair.when(altair.datum.type == MEDIAN)
            .then(altair.value(1))
            .otherwise(altair.value(0.5))
        )
        opacity = (
            altair.when(legend_selection)
            .then(altair.value(1))
            .otherwise(altair.value(0.2))
        )

        # chart
        chart = (
            altair.Chart(self.deciles_table, title=self.chart_units)
            .mark_line()
            .encode(
                altair.X("date", title=None),
                altair.Y("value", title=None),
                detail="percentile",
                strokeDash=stroke_dash,
                strokeWidth=stroke_width,
                opacity=opacity,
            )
            .add_params(legend_selection)
        )
        return chart


class OSJobsRepository:
    def __init__(self):
        path = pathlib.Path(__file__).parent.joinpath("measures.yaml")
        self._records = {r["name"]: r for r in yaml.load(path.read_text(), yaml.Loader)}
        self._measures = {}  # the repository

    def get(self, name):
        """Get the measure with the given name from the repository."""
        log.info(f'Getting "{name}" from the repository')
        if name not in self._measures:
            self._measures[name] = self._construct(name)
        return self._measures[name]

    def _construct(self, name):
        """Construct the measure with the given name from information stored on the
        local file system and on OS Jobs."""
        log.info(f'Constructing "{name}"')
        record = self._records[name]

        # The following helpers don't need access to instance attributes, so we define
        # them as functions rather than as methods. Doing so makes them easier to mock.
        counts = _get_counts(record["counts_table_url"])
        top_5_codes_table = _get_top_5_codes_table(record["top_5_codes_table_url"])
        deciles_table = _get_deciles_table(record["deciles_table_url"])

        return Measure(
            name,
            record["explanation"],
            record["caveats"],
            record["codelist_url"],
            counts["total_events"],
            top_5_codes_table,
            deciles_table,
            record["chart_units"],
        )

    def list(self):
        """List the names of all the measures in the repository."""
        return self._records.keys()


def _get_counts(counts_table_url):
    log.info(f"Getting counts table from {counts_table_url}")
    return pandas.read_csv(counts_table_url, index_col=0).to_dict().get("count")


def _get_top_5_codes_table(top_5_codes_table_url):
    log.info(f"Getting top 5 codes table from {top_5_codes_table_url}")
    top_5_codes_table = pandas.read_csv(
        top_5_codes_table_url, index_col=0, dtype={"Code": str}
    )
    top_5_codes_table.index = pandas.RangeIndex(
        1, len(top_5_codes_table) + 1, name="Rank"
    )
    return top_5_codes_table


def _get_deciles_table(deciles_table_url):
    log.info(f"Getting deciles table from {deciles_table_url}")
    deciles_table = pandas.read_csv(deciles_table_url, parse_dates=["date"])
    deciles_table.loc[:, "label"] = PERCENTILE
    deciles_table.loc[deciles_table["percentile"] % 10 == 0, "label"] = DECILE
    deciles_table.loc[deciles_table["percentile"] == 50, "label"] = MEDIAN
    return deciles_table
