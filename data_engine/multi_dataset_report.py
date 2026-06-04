#data_engine/multidataset_report.py

def build_multi_dataset_report(loaded_datasets: list) -> str:

    response = "Multi Dataset Loading Results 📚\n\n"

    if not loaded_datasets:
        response += "No datasets were loaded."
        return response

    response += f"Datasets loaded: {len(loaded_datasets)}\n\n"

    for idx, dataset in enumerate(loaded_datasets, start=1):

        df = dataset["dataframe"]

        response += (
            f"{idx}. {dataset['title']}\n"
            f"Dataset ID: {dataset['dataset_id']}\n"
            f"Rows: {len(df)}\n"
            f"Columns: {len(df.columns)}\n\n"
        )

    response += (
        "These datasets are now available for dashboard generation."
    )

    return response