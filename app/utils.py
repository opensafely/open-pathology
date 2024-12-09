import pandas as pd
from config import MEASURES, URLS


def get_codelist_url(measure_name: str):
    endpoint = MEASURES[measure_name]["codelist_endpoint"]
    return f"{URLS['codelists']}{endpoint}"


def get_counts(measure_name: str):
    counts = pd.read_csv(get_csv_url(measure_name, "counts")).to_dict(orient="records")
    return {d["Unnamed: 0"]: d["count"] for d in counts}


def get_csv_url(measure_name: str, tag: str):
    endpoint = MEASURES[measure_name]["url_endpoints"][tag]
    return f"{URLS['published_data']}{endpoint}"
