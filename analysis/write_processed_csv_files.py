import argparse
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).parents[1]


def get_deciles_table(df_measure_output):
    """
    Get the deciles table for a given measure.
    args:
    df_measure_output: pd.DataFrame
        The dataframe containing the rounded & redacted output from the generate-measures action
    returns:
        The deciles table for the measure as a pd.DataFrame
    """
    percentiles = pd.Series(
        [*range(0, 10, 1), *range(10, 90, 10), *range(90, 100, 1)],
    )

    df_practice = df_measure_output.loc[
        df_measure_output["measure"] == "by_practice",
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


def get_event_counts_and_top_5_codes_tables(df_measure_output, codelist_path):
    """
    Get the event counts and top 5 codes tables for a given measure.
    args:
    df_measure_output: pd.DataFrame
        The dataframe containing the rounded & redacted output from the generate-measures action
    codelist_path: string
        The path of the codelist
    returns:
        The event counts table for the measure as a pd.DataFrame
        The top 5 codes table for the measure as a pd.DataFrame
    """
    codelist = pd.read_csv(
        codelist_path,
        header=0,
        names=["Code", "Description"],
        dtype={"Code": str},
    )

    events = (
        df_measure_output.groupby(["snomedct_code", "interval_start"])["numerator"]
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
    # Calculate proportion of codes
    df_code_counts["Proportion of codes (%)"] = (round(
        100 * df_code_counts['Events'] / df_code_counts['Events'].sum(), 2)
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


def main(output_dir, codelist_path):
    """
    For a given output directory, read in the rounded & redacted measures file, 
    write the deciles table, event counts table and top 5 codes table to CSV files.
    These files are SDC-compliant as they are derived from the rounded & redacted measures files.
    args:
    output_dir: pathlike
        The directory of the output
    codelist_path: string
        The path to the codelist
    """
    df = pd.read_feather(output_dir / "measures.arrow")
    df["practice"] = df["practice"].astype("Int64")

    deciles_table = get_deciles_table(df)
    deciles_table.to_csv(
        output_dir / "deciles_table_counts_per_week_per_practice.csv",
        index=False,
    )

    event_counts, top_5_code_table = get_event_counts_and_top_5_codes_tables(
        df, codelist_path
    )
    event_counts.to_csv(
        output_dir / "event_counts.csv",
    )
    top_5_code_table.to_csv(
        output_dir / "top_5_code_table.csv",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--codelist")
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    codelist_path = args.codelist
    output_dir = BASE_DIR / Path(args.output_dir)
    main(output_dir, codelist_path)
