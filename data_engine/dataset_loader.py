#data_engine/dataset_loader.py

import re
import pandas as pd


def extract_dataset_id(url: str) -> str | None:
    patterns = [
        r"data-catalogue/([a-zA-Z0-9_/-]+)",
        r"id=([a-zA-Z0-9_/-]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, url)

        if match:
            dataset_id = match.group(1)
            dataset_id = dataset_id.split("?")[0]
            dataset_id = dataset_id.split("&")[0]
            return dataset_id

    return None


def build_data_gov_api_url(dataset_id: str) -> str:
    return f"https://api.data.gov.my/data-catalogue?id={dataset_id}"


def try_load_dataset_from_candidate(candidate: dict) -> dict:
    url = candidate.get("url", "")
    title = candidate.get("title", "Unknown dataset")

    dataset_id = extract_dataset_id(url)

    if not dataset_id:
        return {
            "success": False,
            "title": title,
            "url": url,
            "dataset_id": None,
            "error": "Could not extract dataset ID from URL.",
            "dataframe": None
        }

    api_url = build_data_gov_api_url(dataset_id)

    try:
        df = pd.read_json(api_url)

        return {
            "success": True,
            "title": title,
            "url": url,
            "dataset_id": dataset_id,
            "api_url": api_url,
            "error": None,
            "dataframe": df
        }

    except Exception as e:
        return {
            "success": False,
            "title": title,
            "url": url,
            "dataset_id": dataset_id,
            "api_url": api_url,
            "error": str(e),
            "dataframe": None
        }


def try_load_best_dataset(ranked_datasets: list, max_attempts: int = 5) -> dict:
    attempts = []

    for candidate in ranked_datasets[:max_attempts]:
        result = try_load_dataset_from_candidate(candidate)
        attempts.append(result)

        if result["success"]:
            return {
                "success": True,
                "selected": result,
                "attempts": attempts
            }

    return {
        "success": False,
        "selected": None,
        "attempts": attempts
    }

def load_multiple_datasets(
    ranked_datasets: list,
    max_datasets: int = 3
):
    loaded = []

    for candidate in ranked_datasets[:10]:

        result = try_load_dataset_from_candidate(candidate)

        if result["success"]:
            loaded.append(result)

        if len(loaded) >= max_datasets:
            break

    return loaded