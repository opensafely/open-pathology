# .py file for now but deliberately made easy to convert to .json if needed
MEASURES = {
    "alt": {
        "title": "# Liver Function Testing - Alanine Transferaminase (ALT)",
        "caveats": """**In a small number of places, an ALT test may NOT be included within a liver function test.**
                    We use codes which represent results reported to GPs so tests requested but not yet reported are not included.
                    Only tests results returned to GPs are included,
                    which will usually exclude tests requested while a person is in hospital and other settings like a private clinic.""",
        "classification": "recovery",
        "codelist_endpoint": "opensafely/alanine-aminotransferase-alt-tests/2298df3e/",
        "explanation": """An ALT blood test is one of a group of liver function tests (LFTs) which are used to detect problems with the function of the liver.
                        It is often used to monitor patients on medications which may affect the liver or which rely on the liver to break them down within the body.
                        They are also tested for patients with known or suspected liver dysfunction.""",
        "url_endpoints": {
            "counts": "01GGZ127420DXX35BM0MMQNW8N/",
            "deciles": "01GGZ12739P6B7Z00QAJBTBKK3/",
            "top_5_code": "01GGWFEGKSB1ANPP4X5V2FM3FR/",
        },
    }
}

CHART_CONFIG = {
    "deciles": {
        "color": "percentile",
        "title": "Rate per 1000 registered patients",
        "unit": "rate per 1000",
    }
}

URLS = {
    "codelists": "https://www.opencodelists.org/codelist/",
    "published_data": "https://jobs.opensafely.org/service-restoration-observatory/sro-key-measures-dashboard/published/",
}
