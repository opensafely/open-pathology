import measures
import streamlit


@streamlit.cache_resource
def get_repository():
    return measures.OSJobsRepository()


def main():
    repository = get_repository()

    streamlit.title("OpenPathology")

    selected_measure_name = streamlit.selectbox("Select a measure:", repository.list())

    measure = repository.get(selected_measure_name)

    streamlit.header(measure.name)

    streamlit.markdown(
        "The codes used for this measure "
        f"are available in [this codelist]({measure.codelist_url})."
    )

    with streamlit.expander("What is it and why does it matter?"):
        streamlit.markdown(measure.explanation)

    with streamlit.expander("Caveats"):
        streamlit.markdown(measure.caveats)

    streamlit.altair_chart(measure.deciles_chart, use_container_width=True)

    streamlit.subheader(f"Most common codes ([codelist]({measure.codelist_url}))")

    streamlit.dataframe(measure.top_5_codes_table)

    streamlit.markdown(f"Total events: {measure.total_events:,} events")

    for from_year, to_year in [(2019, 2020), (2019, 2021)]:
        from_val, to_val, pct_change = measure.change_in_median(from_year, to_year, 4)
        streamlit.markdown(
            f"Change in median from April {from_year} ({from_val:.2f}) "
            f"to April {to_year} ({to_val:.2f}): "
            f"**{pct_change:.2%}**"
        )


if __name__ == "__main__":
    main()
