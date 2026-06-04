#data_engine/requirement_detector.py

def detect_required_data(task: str) -> dict:
    task_lower = task.lower()

    required_items = []
    keywords = []

    if "unemployment" in task_lower or "employment" in task_lower:
        required_items.extend([
            "unemployment rate",
            "year or date",
            "labour force",
            "employed population",
            "unemployed population"
        ])
        keywords.extend([
            "unemployment",
            "employment",
            "labour force",
            "lfs",
            "jobless"
        ])

    elif "inflation" in task_lower or "cpi" in task_lower:
        required_items.extend([
            "inflation rate",
            "consumer price index",
            "year or date",
            "month",
            "price index"
        ])
        keywords.extend([
            "inflation",
            "cpi",
            "consumer price index",
            "prices"
        ])

    elif "gdp" in task_lower:
        required_items.extend([
            "GDP value",
            "GDP growth",
            "year or date",
            "sector"
        ])
        keywords.extend([
            "gdp",
            "gross domestic product",
            "economic growth"
        ])

    else:
        required_items.extend([
            "main economic indicator",
            "year or date",
            "trend values",
            "source metadata"
        ])
        keywords.extend(task_lower.split())

    return {
        "task": task,
        "required_items": list(dict.fromkeys(required_items)),
        "search_keywords": list(dict.fromkeys(keywords))
    }