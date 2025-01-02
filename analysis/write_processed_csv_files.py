from pathlib import Path

import pandas as pd
import yaml


BASE_DIR = Path(__file__).parents[1]
OUTPUT_DIR = BASE_DIR / "output"
CODELIST_FILENAMES = {
    r["shorthand"]: r["codelist_filename"]
    for r in yaml.load(BASE_DIR.joinpath("measures.yaml").read_text(), yaml.Loader)
}


def get_deciles_table(df_measure_output, measure_shorthand):
    """
    Get the deciles table for a given measure.
    args:
    df_measure_output: pd.DataFrame
        The dataframe containing the output from the generate-measures action
    measure_shorthand: str
        The shorthand for the measure
    returns:
        The deciles table for the measure as a pd.DataFrame
    """
    percentiles = pd.Series(
        [*range(0, 10, 1), *range(10, 90, 10), *range(90, 100, 1)],
    )

    df_practice = df_measure_output.loc[
        df_measure_output["measure"] == measure_shorthand + "_practice",
        ["interval_start", "ratio", "practice"],
    ]
    # Remove practices that have zero events during the study period
    df_practice = df_practice.loc[~df_practice["ratio"].isna()]

    df_quantiles = (
        df_practice.groupby("interval_start")["ratio"]
        .quantile(percentiles / 100)
        .reset_index(name="value")
    )

    df_quantiles = df_quantiles.rename(
        columns={"interval_start": "date", "level_1": "percentile"}
    )
    df_quantiles["percentile"] = (df_quantiles["percentile"] * 100).astype(int)
    df_quantiles["value"] = df_quantiles["value"] * 1000  # Rate per 1000 patients
    return df_quantiles


def get_event_counts_and_top_5_codes_tables(df_measure_output, measure_shorthand):
    """
    Get the event counts and top 5 codes tables for a given measure.
    args:
    df_measure_output: pd.DataFrame
        The dataframe containing the output from the generate-measures action
    measure_shorthand: str
        The shorthand for the measure
    returns:
        The event counts table for the measure as a pd.DataFrame
        The top 5 codes table for the measure as a pd.DataFrame
    """
    codelist = pd.read_csv(
        Path("codelists") / CODELIST_FILENAMES[measure_shorthand],
        header=0,
        names=["Code", "Description"],
        dtype={"Code": str},
    )

    events = (
        df_measure_output.groupby([f"{measure_shorthand}_code", "interval_start"])[
            "numerator"
        ]
        .sum()
        .rename("Events")
        .rename_axis(["Code", "Date"])
    )

    # Populate the event counts table
    df_event_counts = pd.DataFrame(
        columns=["count"], index=["total_events", "events_in_latest_period"]
    )
    df_event_counts.loc["total_events"] = events.sum()
    df_event_counts.loc["events_in_latest_period"] = (
        events.groupby(level="Date").sum().sort_index(ascending=False).iloc[0]
    )

    # Tabulate the Top 5 codes by event count
    df_code_counts = (
        events.groupby(level="Code")
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .merge(codelist, on="Code")
    )
    # Use event counts rounded to the nearest 5, and drop the column
    rounded_counts = 5 * round(df_code_counts.pop("Events") / 5)
    df_code_counts["Proportion of codes (%)"] = round(
        100 * rounded_counts / rounded_counts.sum(), 2
    ).astype(str)

    if len(df_code_counts) > 1:
        df_code_counts.loc[
            df_code_counts["Proportion of codes (%)"].str.replace("0", "") == ".",
            "Proportion of codes (%)",
        ] = "< 0.005"

        df_code_counts.loc[
            df_code_counts["Proportion of codes (%)"].str.startswith("100."),
            "Proportion of codes (%)",
        ] = "> 99.995"

    return df_event_counts, df_code_counts.loc[:4]


def main(measures):
    """
    For a given list of measures, write the deciles table, event counts table and top 5 codes table to CSV files.
    args:
    measures: list [str]
        A list of measure shorthands
    """
    df = pd.read_csv(
        "output/measures.csv.gz",
        parse_dates=["interval_start", "interval_end"],
        dtype={
            "practice": str,  # Mix of int and nulls so use str to avoid float
            **{f"{m}_code": str for m in measures},
        },
    )

    for m in measures:
        deciles_table = get_deciles_table(df, m)
        deciles_table.to_csv(
            OUTPUT_DIR / f"{m}_deciles_table_counts_per_week_per_practice.csv",
            index=False,
        )

        event_counts, top_5_code_table = get_event_counts_and_top_5_codes_tables(df, m)
        event_counts.to_csv(
            OUTPUT_DIR / f"{m}_event_counts.csv",
        )
        top_5_code_table.to_csv(
            OUTPUT_DIR / f"{m}_top_5_code_table.csv",
        )


if __name__ == "__main__":
    main(["alt"])
