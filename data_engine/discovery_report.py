#data_engine/discovery_report.py

def build_discovery_report(required_data: dict, discovery_results: list, completeness: dict) -> str:
    response = "Phase 5 Source Discovery completed 🔎✅\n\n"

    response += "Data needed for this task:\n"
    for item in required_data.get("required_items", []):
        response += f"- {item}\n"

    response += "\nSearch keywords used:\n"
    for keyword in required_data.get("search_keywords", []):
        response += f"- {keyword}\n"

    response += "\nDiscovered candidate sources:\n"

    has_candidates = False

    for result in discovery_results:
        response += f"\nFrom: {result['source']}\n"

        if not result["success"]:
            response += f"- Could not access source: {result['error']}\n"
            continue

        candidates = result.get("candidates", [])

        if not candidates:
            response += "- No useful dataset/API links discovered.\n"
            continue

        has_candidates = True

        for candidate in candidates[:5]:
            tags = []

            if candidate["is_structured_file"]:
                tags.append("structured file")

            if candidate["is_api"]:
                tags.append("API")

            if candidate["is_dataset_page"]:
                tags.append("dataset page")

            tag_text = ", ".join(tags) if tags else "general link"

            response += f"- {candidate['url']} ({tag_text}, score: {candidate['score']})\n"

    response += "\nCompleteness check:\n"

    response += "\nFound items:\n"
    if completeness["found_items"]:
        for item in completeness["found_items"]:
            response += f"- {item}\n"
    else:
        response += "- None confidently found yet.\n"

    response += "\nMissing items:\n"
    if completeness["missing_items"]:
        for item in completeness["missing_items"]:
            response += f"- {item}\n"
    else:
        response += "- No major missing items detected.\n"

    response += "\nDecision:\n"

    if completeness["has_real_structured_data"]:
        response += (
            "Real structured/API data was found. "
            "Next phase can attempt dataset download and dashboard generation."
        )
    elif completeness["has_search_paths"]:
        response += (
            "Relevant official search paths were found, but exact datasets were not downloaded yet. "
            "Next step should search inside these catalogue pages or use a known-source data.gov.my adapter."
        )
    else:
        response += (
            "Structured data was not confidently found. "
            "Next step should use known-source adapters or LLM fallback explanation."
        )

    return response