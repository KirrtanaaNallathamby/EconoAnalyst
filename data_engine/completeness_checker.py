#data_engine/completeness_checker.py

def check_completeness(required_data: dict, discovery_results: list) -> dict:
    required_items = required_data.get("required_items", [])

    all_candidate_text = ""

    for result in discovery_results:
        for candidate in result.get("candidates", []):
            all_candidate_text += " " + candidate.get("url", "").lower()

    found_items = []
    missing_items = []

    for item in required_items:
        item_words = item.lower().split()

        if any(word in all_candidate_text for word in item_words):
            found_items.append(item)
        else:
            missing_items.append(item)

    structured_candidates = []
    search_page_candidates = []

    for result in discovery_results:
        for candidate in result.get("candidates", []):
            url = candidate.get("url", "").lower()

            is_real_structured_source = (
                candidate.get("is_structured_file")
                or candidate.get("is_api")
                or "api.data.gov.my" in url
                or ".csv" in url
                or ".json" in url
                or ".parquet" in url
                or ".xlsx" in url
            )

            is_search_page = (
                "search=" in url
                or url.endswith("/data-catalogue")
                or "/data-catalogue?" in url
            )

            if is_real_structured_source and not is_search_page:
                structured_candidates.append(candidate)

            if is_search_page:
                search_page_candidates.append(candidate)

    return {
        "found_items": found_items,
        "missing_items": missing_items,
        "structured_candidates": structured_candidates,
        "search_page_candidates": search_page_candidates,
        "has_search_paths": len(search_page_candidates) > 0,
        "has_real_structured_data": len(structured_candidates) > 0,
        "is_enough_for_next_phase": len(structured_candidates) > 0
    }