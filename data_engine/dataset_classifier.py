#data_engine/data_classifier.py

from urllib.parse import urlparse


STRUCTURED_EXTENSIONS = [
    ".csv",
    ".json",
    ".parquet",
    ".xlsx",
    ".xls"
]


def classify_link(url: str, text: str = "") -> dict:
    url_lower = url.lower()
    text_lower = text.lower()

    is_structured = any(ext in url_lower for ext in STRUCTURED_EXTENSIONS)

    is_api = (
        "api" in url_lower
        or "api" in text_lower
        or "data-catalogue" in url_lower
        or "datacatalogue" in url_lower
    )

    is_dataset_page = any(word in url_lower or word in text_lower for word in [
        "dataset",
        "data",
        "catalogue",
        "download",
        "table",
        "indicator"
    ])

    parsed = urlparse(url)

    return {
        "url": url,
        "domain": parsed.netloc,
        "is_structured_file": is_structured,
        "is_api": is_api,
        "is_dataset_page": is_dataset_page,
        "score": calculate_score(url_lower, text_lower)
    }


def calculate_score(url_lower: str, text_lower: str) -> int:
    score = 0

    good_words = [
        "csv", "json", "parquet", "xlsx",
        "api", "dataset", "data", "catalogue",
        "download", "table", "indicator",
        "unemployment", "employment", "labour", "lfs",
        "inflation", "cpi", "gdp"
    ]

    for word in good_words:
        if word in url_lower:
            score += 3
        if word in text_lower:
            score += 1

    return score