import dataclasses
import pathlib
import re
import urllib.parse

import altair
import pandas
import requests
import structlog
import yaml


log = structlog.get_logger(__name__)

PERCENTILE = "Percentile"
DECILE = "Decile"
MEDIAN = "Median"


@dataclasses.dataclass
class Measure:
    name: str
    is_pathology: bool
    explanation: str
    caveats: str
    classification: str
    codelist_url: str
    total_events: int
    top_5_codes_table: pandas.DataFrame
    deciles_table: pandas.DataFrame

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
            altair.Chart(self.deciles_table, title="Rate per 1,000 registered patients")
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


class OSJobsWorkspace:
    def __init__(
        self, endpoint, file_structure="output/(?P<shorthand>[^/]+)/(?P<name>.+)"
    ):
        self.base_url = "https://jobs.opensafely.org/"
        self.endpoint_url = urllib.parse.urljoin(self.base_url, endpoint)
        self.file_structure = file_structure

    def get_file_urls(self):
        response = requests.get(self.endpoint_url)
        file_list = response.json()["files"]
        name_to_url = {
            file["name"]: urllib.parse.urljoin(self.base_url, file["url"])
            for file in file_list
        }
        file_urls = {
            key: url for name, url in name_to_url.items() if (key := self.get_key(name))
        }
        return file_urls

    def get_key(self, file_name):
        match = re.match(self.file_structure, file_name)
        if not match:
            return None
        return (match.group("shorthand"), match.group("name"))


class OSJobsRepository:
    def __init__(self, file_urls):
        path = pathlib.Path(__file__).parent.joinpath("measures.yaml")
        self._file_urls = file_urls
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
        counts = self._get_counts(record["shorthand"])
        top_5_codes_table = self._get_top_5_codes_table(record["shorthand"])
        deciles_table = self._get_deciles_table(record["shorthand"])

        return Measure(
            name,
            record["is_pathology"],
            record["explanation"],
            record["caveats"],
            record["classification"],
            record["codelist_url"],
            counts["total_events"],
            top_5_codes_table,
            deciles_table,
        )

    def _get_counts(self, shorthand):
        return _get_counts(self._file_urls[(shorthand, "event_counts.csv")])

    def _get_top_5_codes_table(self, shorthand):
        return _get_top_5_codes_table(
            self._file_urls[(shorthand, "top_5_code_table.csv")]
        )

    def _get_deciles_table(self, shorthand):
        return _get_deciles_table(
            self._file_urls[
                (shorthand, "deciles_table_counts_per_week_per_practice.csv")
            ]
        )

    def list(self):
        """
        List the names of all the measures in the repository.
        Pathology measures are listed first alphabetically, followed by other measures alphabetically.
        """
        pathology_measures = [
            name for name, record in self._records.items() if record["is_pathology"]
        ]
        other_measures = [
            name for name, record in self._records.items() if not record["is_pathology"]
        ]
        return sorted(pathology_measures) + sorted(other_measures)


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
