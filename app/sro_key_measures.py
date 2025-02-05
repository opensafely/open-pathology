import measures
import numpy
import streamlit


@streamlit.cache_resource
def get_repository():
    return measures.OSJobsRepository()


def save_value_if_missing(label, value):
    if label not in streamlit.session_state:
        streamlit.session_state[label] = value


def main():
    repository = get_repository()

    selected_measure_name = streamlit.selectbox("Select a measure:", repository.list())

    measure = repository.get(selected_measure_name)

    streamlit.markdown(f"# {measure.name}")

    streamlit.markdown(
        "The codes used for this measure"
        f"are available in [this codelist]({measure.codelist_url})."
    )

    with streamlit.expander("What is it and why does it matter?"):
        streamlit.markdown(measure.explanation)

    with streamlit.expander("Caveats"):
        streamlit.markdown(measure.caveats)

    with streamlit.expander("Single practice scenario"):
        min_value, max_value = measure.range
        idx_start = measure.months.index(
            streamlit.selectbox("Start", options=measure.months[:-1])
        )
        idx_end = measure.months.index(
            streamlit.selectbox(
                "End",
                options=measure.months[idx_start + 1 :],
                index=len(measure.months) - idx_start - 2,
            )
        )
        frequency = streamlit.number_input("Frequency (months)", 1, 12, 3)
        months = measure.months[idx_start : idx_end + 1 : frequency]

        for month in months:
            key = f"{measure.name}_{month.isoformat()}"
            save_value_if_missing(key, numpy.random.uniform(min_value, max_value))
            streamlit.slider(
                month.isoformat(),
                min_value,
                max_value,
                key=key,
            )
            measure.update_scenario_table(month, streamlit.session_state[key])
        measure.scenario_table = measure.scenario_table.loc[months]

    streamlit.altair_chart(
        measure.deciles_chart + measure.scenario_chart, use_container_width=True
    )

    streamlit.markdown(f"**Most common codes ([codelist]({measure.codelist_url}))**")

    streamlit.dataframe(measure.top_5_codes_table)

    streamlit.markdown(
        "Total patients: "
        f"**{measure.unique_patients:,}** "
        f"({measure.total_events:,} events)"
    )

    for from_year, to_year in [(2019, 2020), (2019, 2021)]:
        from_val, to_val, pct_change = measure.change_in_median(from_year, to_year, 4)
        streamlit.markdown(
            f"Change in median from April {from_year} ({from_val:.2f}) "
            f"to April {to_year} ({to_val:.2f}): "
            f"**{pct_change:.2%}**"
        )

    streamlit.markdown(f"Overall classification: **{measure.classification}**")


if __name__ == "__main__":
    main()
