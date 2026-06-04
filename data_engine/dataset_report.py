#data_engine/dataset_report.py

def build_dataset_report(ranked_datasets: list) -> str:

    response = "Dataset Discovery Results 📊\n\n"

    if not ranked_datasets:

        response += (
            "No dataset candidates were found.\n\n"
            "Next step: use known-source adapters "
            "or LLM fallback."
        )

        return response

    response += "Top dataset candidates:\n\n"

    for idx, dataset in enumerate(ranked_datasets[:5], start=1):

        response += (
            f"{idx}. {dataset['title'][:100]}\n"
            #f"URL: {dataset['url']}\n"
            f"Score: {dataset['score']}\n\n"
        )

    response += (
        "Next phase can attempt dataset download "
        "using these candidates."
    )

    return response