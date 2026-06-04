#data_engine/dataset_ranker.py

def rank_datasets(task: str, datasets: list) -> list:

    task_lower = task.lower()

    ranked = []

    for dataset in datasets:

        score = 0

        title = dataset.get("title", "").lower()
        url = dataset.get("url", "").lower()

        important_words = [
            "unemployment",
            "employment",
            "labour",
            "lfs",
            "rate",
            "survey"
        ]

        for word in important_words:

            if word in title:
                score += 5

            if word in url:
                score += 3

        ranked.append({
            **dataset,
            "score": score
        })

    ranked.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return ranked