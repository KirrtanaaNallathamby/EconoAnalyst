#data_engine/download_report.py

def build_download_report(download_result: dict) -> str:
    response = "Dataset Download Results 📥\n\n"

    if not download_result["success"]:
        response += "No dataset could be downloaded yet.\n\n"
        response += "Attempted datasets:\n"

        for attempt in download_result.get("attempts", []):
            response += (
                f"- {attempt.get('title')}\n"
                f"  Dataset ID: {attempt.get('dataset_id')}\n"
                f"  Error: {attempt.get('error')}\n\n"
            )

        response += (
            "Next step: improve the data.gov.my adapter to extract the exact API/download link."
        )

        return response

    selected = download_result["selected"]
    profile = selected["profile"]

    response += f"Selected dataset:\n{selected['title']}\n\n"
    response += f"Dataset ID:\n{selected['dataset_id']}\n\n"
    response += f"API URL:\n{selected['api_url']}\n\n"

    response += f"Rows: {profile['rows']}\n"
    response += f"Columns: {len(profile['columns'])}\n\n"

    response += "Column names:\n"

    for col in profile["columns"][:15]:
        response += f"- {col}\n"

    #response += "\nSample rows:\n"

    #for row in profile["preview"][:3]:
    #    response += f"- {row}\n"

    response += "\nDataset is ready for analysis and dashboard generation."

    return response