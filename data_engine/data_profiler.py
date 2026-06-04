#data_engine/data_profiler.py

def profile_dataframe(df) -> dict:
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "preview": df.head(5).to_dict(orient="records")
    }