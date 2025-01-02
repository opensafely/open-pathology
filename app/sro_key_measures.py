import measures
import streamlit


def main():
    repository = measures.OSJobsRepository()
    shorthands = {v: k for k, v in repository.get_names_dict().items()}

    selected_measure_name = streamlit.selectbox(
        "Select a measure:", sorted(shorthands.keys())
    )

    measure = repository.get(shorthands[selected_measure_name])

    streamlit.markdown(f"# {measure.name}")

    streamlit.markdown(
        "The codes used for this measure"
        f"are available in [this codelist]({measure.codelist_url})."
    )

    with streamlit.expander("What is it and why does it matter?"):
        streamlit.markdown(measure.explanation)

    with streamlit.expander("Caveats"):
        streamlit.markdown(measure.caveats)

    streamlit.altair_chart(measure.deciles_chart, use_container_width=True)

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
