import re
import urllib.parse

import requests
import yaml


BASE_URL = "https://jobs.opensafely.org/"
WORKSPACE_ENDPOINT = urllib.parse.urljoin(
    BASE_URL, "api/v2/workspaces/sro-key-measures-dashboard/snapshots/31"
)

FILENAME_TO_ALIAS = {
    "event_counts.csv": "counts_table",
    "top_5_code_table.csv": "top_5_codes_table",
    "deciles_table_counts_per_week_per_practice.csv": "deciles_table",
}


def get_key(file_name):
    match = re.match("output/(?P<shorthand>[^/]+)/(?P<name>.+)", file_name)
    if not match:
        return None
    shorthand, name = match.groups()
    try:
        return (shorthand, FILENAME_TO_ALIAS[name])
    except KeyError:
        return None


def get_file_urls():
    response = requests.get(WORKSPACE_ENDPOINT)
    file_list = response.json()["files"]
    name_to_url = {
        file["name"]: urllib.parse.urljoin(BASE_URL, file["url"]) for file in file_list
    }
    file_urls = {
        key: url for name, url in name_to_url.items() if (key := get_key(name))
    }
    return file_urls


def write_file_urls_to_yaml(file_urls):
    files_by_shorthand = {}
    for (shorthand, alias), url in file_urls.items():
        if shorthand not in files_by_shorthand:
            files_by_shorthand[shorthand] = {}
        files_by_shorthand[shorthand][alias] = url
    with open("app/file_urls.yaml", "w") as f:
        yaml.dump(files_by_shorthand, f)


if __name__ == "__main__":
    file_urls = get_file_urls()
    write_file_urls_to_yaml(file_urls)
