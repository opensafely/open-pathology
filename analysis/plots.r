# This script generates decile charts for all pathology tests
# USAGE: Rscript analysis/plots.r
# ARGS: --released: Alters the file path to a nested folder containing released data. 
#                   Requires released data to be stored in format "output/output/[test]/*.csv"
#       --sim: Uses simulated data, needed when testing locally

library(ggplot2)
library(readr)
library(tidyr)
library(dplyr)
library(glue)
library(optparse)
library(lubridate)
library(patchwork)

# ------ Configuration ---------------------------------------------------------------------

# Define option list
option_list <- list(
  make_option("--released", action = "store_true", default = FALSE, 
              help = "Uses data located in released folder"),
  make_option("--sim", action = "store_true", default = FALSE, 
              help = "Uses simulated data, needed when testing locally")            
)

# Parse arguments
opt <- parse_args(OptionParser(option_list = option_list))

if (opt$released){
  path = "output/output" # path of released data
} else {
  path = "output"
}
if (opt$sim){
  sim = "_sim"
} else {
  sim = ""
}

# Extract list of test names based on folder names in output folder
tests <- list.dirs(path, full.names = FALSE, recursive = FALSE)

# ------ Plotting ---------------------------------------------------------------------

# Iterate over all tests
for(test in tests){

  # ----- Generate decile plots ------------------------------------

  if(test == 'hba1c_diab_mean_tests'){
    y_axis = 'Mean HbA1c (mmol/mol)'
  } else{
    y_axis = 'Rate per 1000'
  }

  # Construct file path
  file_path <- glue("{path}/{test}/deciles_table_counts_per_week_per_practice{sim}.csv")
  
  # Skip iteration if file doesn't exist
  if (file.exists(file_path)) {
    
    message(glue("Skipping {test} - file not found"))
    df <- read_csv(file_path)

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
    decile_plot <- ggplot(df, aes(x = date, y = value, group = percentile, linetype = line_group)) +
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

    ggsave(glue("{path}/{test}/plot{sim}.png"), decile_plot)
  }

  # ----- Generate demograph plots ------------------------------------

  # Construct file path
  file_path <- glue("{path}/{test}/demographic_table_counts_per_week{sim}.csv")
  
  # Skip iteration if file doesn't exist
  if (!file.exists(file_path)) {
    message(glue("Skipping {test} demograph breakdown - file not found"))
    next
  }
  df <- read_csv(file_path)

  # Process data
  df <- df %>% mutate(interval_start = as.Date(interval_start))
  df$ratio <- df$ratio * 1000
  df$ethnicity <- recode(df$ethnicity, "1" = "White", "2" = "Mixed", "3" = "Asian or Asian British",
                          "4" = "Black or Black British", "5" = "Chinese or Other Ethnic Group")

  # One plot per measure using color instead of facets
  p_region <- df %>%
    filter(measure == "by_region" & !is.na(region)) %>%
    ggplot(aes(x = interval_start, y = ratio, color = region)) +
    geom_line() +
    labs(title = "By Region", x = NULL, y = "Rate per 1000")

  p_ethnicity <- df %>%
    filter(measure == "by_ethnicity" & !is.na(ethnicity)) %>%
    ggplot(aes(x = interval_start, y = ratio, color = as.factor(ethnicity))) +
    geom_line() +
    labs(title = "By Ethnicity", x = NULL, y = "Rate per 1000", color = "Ethnicity")

  p_imd <- df %>%
    filter(measure == "by_IMD" & !is.na(IMD)) %>%
    ggplot(aes(x = interval_start, y = ratio, color = as.factor(IMD))) +
    geom_line() +
    labs(title = "By IMD", x = NULL, y = "Rate per 1000", color = "IMD Quintile")

  p_sex <- df %>%
    filter(measure == "by_sex" & !is.na(sex)) %>%
    ggplot(aes(x = interval_start, y = ratio, color = sex)) +
    geom_line() +
    labs(title = "By Sex", x = NULL, y = "Rate per 1000")

  # Combine plots using patchwork (2 rows)
  demograph_plot <- (p_region | p_ethnicity) /
                 (p_imd | p_sex) + 
                 plot_annotation(
                  title = glue("Rate of {test}"),
  )

  ggsave(glue("{path}/{test}/demograph_plot{sim}.png"), demograph_plot, width = 20, height = 12)
}
