#brain/openclaw_brain.py

from brain.markdown_reader import read_markdown
from brain.task_planner import create_research_plan, format_plan_response
from brain.response_builder import build_user_summary, build_developer_log

from data_engine.requirement_detector import detect_required_data
from data_engine.source_discovery import discover_sources
from data_engine.completeness_checker import check_completeness
from data_engine.discovery_report import build_discovery_report
from data_engine.dataset_discovery import discover_dataset_pages
from data_engine.dataset_ranker import rank_datasets
from data_engine.dataset_report import build_dataset_report
from data_engine.dataset_loader import try_load_best_dataset
from data_engine.data_profiler import profile_dataframe
from data_engine.download_report import build_download_report
from data_engine.multi_dataset_report import build_multi_dataset_report
from data_engine.dataset_loader import load_multiple_datasets

from dashboard.dashboard_generator import generate_unemployment_dashboard


def run_brain(task: str, markdown_path: str) -> dict:
    markdown_data = read_markdown(markdown_path)

    if not markdown_data["success"]:
        return {
            "success": False,
            "message": markdown_data["error"],
            "user_summary": markdown_data["error"],
            "developer_log": markdown_data["error"],
            "dashboard_result": {
                "success": False,
                "error": markdown_data["error"],
                "dashboard_path": None
            }
        }

    plan = create_research_plan(task, markdown_data)
    sources = markdown_data.get("sources", [])

    required_data = detect_required_data(task)

    discovery_results = []

    for source in sources:
        result = discover_sources(
            homepage_url=source,
            search_keywords=required_data["search_keywords"]
        )
        discovery_results.append(result)

    completeness = check_completeness(
        required_data=required_data,
        discovery_results=discovery_results
    )

    discovery_report = build_discovery_report(
        required_data=required_data,
        discovery_results=discovery_results,
        completeness=completeness
    )

    all_datasets = []

    for result in discovery_results:
        for candidate in result.get("candidates", []):
            dataset_result = discover_dataset_pages(candidate["url"])

            if dataset_result["success"]:
                all_datasets.extend(dataset_result["datasets"])

    ranked_datasets = rank_datasets(
        task,
        all_datasets
    )

    loaded_datasets = load_multiple_datasets(
        ranked_datasets=ranked_datasets,
        max_datasets=3
    )

    dashboard_result = generate_unemployment_dashboard(
        loaded_datasets=loaded_datasets,
        task=task
    )

    dataset_report = build_dataset_report(ranked_datasets)

    download_result = try_load_best_dataset(
        ranked_datasets=ranked_datasets,
        max_attempts=5
    )

    if download_result["success"]:
        df = download_result["selected"]["dataframe"]
        profile = profile_dataframe(df)
        download_result["selected"]["profile"] = profile

    download_report = build_download_report(download_result)

    multi_dataset_report = build_multi_dataset_report(
        loaded_datasets
    )

    plan_response = format_plan_response(plan)

    developer_log = build_developer_log(
        plan_response=plan_response,
        discovery_report=discovery_report,
        dataset_report=dataset_report,
        download_report=download_report,
        multi_dataset_report=multi_dataset_report,
        dashboard_result=dashboard_result
    )

    user_summary = build_user_summary(
        task=task,
        markdown_data=markdown_data,
        loaded_datasets=loaded_datasets,
        dashboard_result=dashboard_result
    )

    return {
        "success": True,
        "message": user_summary,
        "user_summary": user_summary,
        "developer_log": developer_log,
        "plan": plan,
        "required_data": required_data,
        "discovery_results": discovery_results,
        "completeness": completeness,
        "ranked_datasets": ranked_datasets,
        "loaded_dataset_count": len(loaded_datasets),
        "dashboard_result": dashboard_result
    }