# brain/response_builder.py

def build_user_summary(
    task: str,
    markdown_data: dict,
    loaded_datasets: list,
    dashboard_result: dict
) -> str:
    sources = markdown_data.get("sources", [])
    instructions = markdown_data.get("instructions", [])

    dataset_name = "Official dataset selected by EcoResearch Bot"
    dataset_id = "N/A"
    row_count = "N/A"

    if loaded_datasets:
        selected = loaded_datasets[0]
        dataset_name = selected.get("title", dataset_name)
        dataset_id = selected.get("dataset_id", "N/A")

        dataframe = selected.get("dataframe")
        if dataframe is not None:
            row_count = len(dataframe)

    dashboard_path = dashboard_result.get("dashboard_path")

    if dashboard_result.get("success"):
        status_line = "✅ Research completed successfully."
        dashboard_line = "The interactive HTML dashboard is attached below."
    else:
        status_line = "⚠️ Research completed, but dashboard generation failed."
        dashboard_line = f"Reason: {dashboard_result.get('error')}"

    summary = (
        f"{status_line}\n\n"
        f"📌 Topic:\n{task}\n\n"
        f"📊 Dataset used:\n{dataset_name}\n\n"
        f"🆔 Dataset ID:\n{dataset_id}\n\n"
        f"📁 Rows analysed:\n{row_count}\n\n"
    )

    if sources:
        summary += "🌐 Trusted sources checked:\n"
        for source in sources[:3]:
            summary += f"- {source}\n"
        summary += "\n"

    if instructions:
        summary += "📝 Instructions followed:\n"
        for instruction in instructions[:5]:
            summary += f"- {instruction}\n"
        summary += "\n"

    summary += (
        "🦞 Orchestration:\n"
        "This request was routed through OpenClaw before the research pipeline was executed.\n\n"
        f"📎 Dashboard:\n{dashboard_line}"
    )

    if dashboard_path:
        summary += f"\n\nSaved path:\n{dashboard_path}"

    screenshot_path = dashboard_result.get("screenshot_path")
    image_quality_report = dashboard_result.get("image_quality_report")

    if image_quality_report:
        summary += "\n\nDashboard image quality check:\n"

        if screenshot_path:
            summary += f"- Screenshot preview: {screenshot_path}\n"

        if image_quality_report.get("success"):
            summary += (
                f"- Image size: {image_quality_report.get('image_width')} x {image_quality_report.get('image_height')}\n"
                f"- Contrast: {image_quality_report.get('contrast')}\n"
                f"- Visual content ratio: {image_quality_report.get('visual_content_ratio')}\n"
                f"- Active layout regions: "
                f"{image_quality_report.get('active_layout_regions')}/"
                f"{image_quality_report.get('total_layout_regions')}\n"
                f"- Layout status: {image_quality_report.get('layout_status')}\n"
            )
        else:
            summary += f"- Check not completed: {image_quality_report.get('error')}\n"
            if image_quality_report.get("setup_hint"):
                summary += f"- Setup hint: {image_quality_report.get('setup_hint')}\n"

    return summary


def build_developer_log(
    plan_response: str,
    discovery_report: str,
    dataset_report: str,
    download_report: str,
    multi_dataset_report: str,
    dashboard_result: dict
) -> str:
    log = plan_response
    log += "\n\n" + discovery_report
    log += "\n\n" + dataset_report
    log += "\n\n" + download_report
    log += "\n\n" + multi_dataset_report

    if dashboard_result.get("success"):
        log += (
            "\n\nDashboard generated successfully 🖥️✅\n"
            f"Dashboard path: {dashboard_result.get('dashboard_path')}"
        )
        if dashboard_result.get("screenshot_path"):
            log += f"\nScreenshot path: {dashboard_result.get('screenshot_path')}"
        if dashboard_result.get("image_quality_report"):
            log += f"\nImage quality report: {dashboard_result.get('image_quality_report')}"
    else:
        log += (
            "\n\nDashboard generation failed ❌\n"
            f"Reason: {dashboard_result.get('error')}"
        )

    return log
