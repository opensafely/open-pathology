from urllib.parse import urljoin

import altair as alt
import pandas as pd
import streamlit as st
from config import BASE_URLS, MEASURES


def get_codelist_url(measure_name: str):
    return urljoin(BASE_URLS["codelists"], MEASURES[measure_name]["codelist_url"])


def get_csv_url(measure_name: str, tag: str):
    return urljoin(BASE_URLS["published_data"], MEASURES[measure_name]["csv_urls"][tag])


def get_decile_data(measure_name):
    def get_label(percentile):
        if percentile == 50:
            return "Median"
        return "Decile" if percentile % 10 == 0 else "Percentile"

    chart_data = pd.read_csv(get_csv_url(measure_name, "deciles"), parse_dates=["date"])
    chart_data["label"] = chart_data["percentile"].apply(get_label)
    return chart_data


def get_decile_chart(df):
    return (
        alt.Chart(df, title="Rate per 1000 registered patients")
        .mark_line()
        .encode(
            x=alt.X("date:T", axis=alt.Axis(format="%b %Y", labelAngle=-90)),
            y=alt.Y("value", title="rate per 1000"),
            detail="percentile",
            strokeDash=alt.StrokeDash(
                "label",
                scale=alt.Scale(
                    domain=["Percentile", "Decile", "Median"],
                    range=[[1, 1], [5, 5], [0, 0]],
                ),
                legend={
                    "values": ["1st-9th, 91st-99th percentile", "decile", "median"],
                    "labelLimit": 200,  # Prevents the labels from being truncated
                },
            ),
        )
    )


def get_median_change_from_april_to_april(df, start, end):
    template = "Change in median from April {start} ({val_start:.2f}) - April {end} ({val_end:.2f}): **{percentage_change:.2f}%**"
    val_start, val_end = (
        df[
            (df["date"].dt.year.isin([start, end]))
            & (df["date"].dt.month == 4)
            & (df["percentile"] == 50)
        ]
        .sort_values("date")
        .loc[:, "value"]
    )

    return template.format(
        start=start,
        end=end,
        val_start=val_start,
        val_end=val_end,
        percentage_change=((val_end - val_start) / val_start) * 100,
    )


if __name__ == "__main__":
    measure_name = "alt"

    # Variables
    measure = MEASURES[measure_name]

    codelist_url = get_codelist_url(measure_name)
    counts = (
        pd.read_csv(get_csv_url(measure_name, "counts"), index_col=0)
        .to_dict()
        .get("count")
    )

    df_decile = get_decile_data(measure_name)
    df_top_5 = pd.read_csv(get_csv_url(measure_name, "top_5_code"), index_col=0)

    # Layout
    st.markdown(measure["title"])
    st.markdown(
        f"The codes used for this measure are available in this [codelist]({codelist_url})."
    )
    with st.expander("What is it and why does it matter?"):
        st.markdown(measure["explanation"])
    with st.expander("Caveats"):
        st.markdown(measure["caveats"])

    st.altair_chart(get_decile_chart(df_decile), use_container_width=True)

    st.markdown(f"**Most Common Codes [(Codelist)]({codelist_url})**")
    st.table(
        df_top_5.style.format(subset=["Proportion of codes (%)"], formatter="{:.2f}")
    )

    st.markdown(
        f"Total patients: {counts['unique_patients']/1e6:.2f}M ({counts['total_events']/1e6:.2f}M events)"
    )

    st.markdown(get_median_change_from_april_to_april(df_decile, start=2019, end=2020))
    st.markdown(get_median_change_from_april_to_april(df_decile, start=2019, end=2021))

    st.markdown(f"Overall classification: **{measure['classification']}**")
