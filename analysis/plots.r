library(ggplot2)
library(readr)
library(tidyr)
library(dplyr)
library(glue)

# Extract list of test names based on folder names in output folder
tests <- list.dirs("output/output", full.names = FALSE, recursive = FALSE)
print(tests)

# Iterate over all tests
for(test in tests){
  if(test == 'hba1c_diab_mean_tests'){
    y_axis = 'Mean HbA1c (mmol/mol)'
  } else{
    y_axis = 'Rate per 1000'
  }

  df <- read_csv(glue("output/output/{test}/deciles_table_counts_per_week_per_practice.csv"))

  # Filter only deciles (0, 10, ..., 100)
  df <- filter(df, percentile %in% seq(1, 100, by = 1))  # keep all for now

  # Create a group variable for linetype/legend
  df <- df %>%
    mutate(
      line_group = case_when(
        percentile == 50 ~ "median",
        percentile %% 10 == 0 ~ "decile",
        TRUE ~ "1st–9th, 91st–99th percentile"
      )
    )

  # Convert to factor to control legend order
  df$line_group <- factor(df$line_group,
                          levels = c("1st–9th, 91st–99th percentile", "decile", "median"))

  # Plot
  ggplot(df, aes(x = date, y = value, group = percentile, linetype = line_group)) +
    geom_line(color = "black", linewidth = 0.6) +
    scale_linetype_manual(
      values = c("1st–9th, 91st–99th percentile" = "dotted",
                "decile" = "dashed",
                "median" = "solid")
    ) +
    labs(
      title=glue("Rate of {test}"),
      x = "Interval start",
      y = y_axis,
      linetype = NULL
    ) +
    theme(
      legend.position = "bottom",
      axis.text.x = element_text(angle = 45, hjust = 1)
    )

  ggsave(glue("output/output/{test}/plot.png"))
}
