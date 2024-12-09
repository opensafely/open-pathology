import pandas as pd


# Load data
URL_PUBLISHED = "https://jobs.opensafely.org/service-restoration-observatory/sro-key-measures-dashboard/published"
URL_ENDPOINTS = {"alt": {"deciles": "01GGZ12739P6B7Z00QAJBTBKK3/"}}


def get_data_url(measure, file):
    return f"{URL_PUBLISHED}/{URL_ENDPOINTS[measure][file]}"


df = pd.read_csv(get_data_url("alt", "deciles"))
df
