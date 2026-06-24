#dashboard/dashboard_generator.py

from pathlib import Path
from datetime import datetime
from string import Template
import pandas as pd
import plotly.express as px


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "storage" / "generated_dashboards"
TEMPLATE_PATH = PROJECT_ROOT / "dashboard" / "templates" / "dashboard_template.html"
LFS_MONTH_CSV_URL = "https://storage.dosm.gov.my/labour/lfs_month.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def export_dashboard_screenshot(html_path: Path, screenshot_path: Path) -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        return {
            "success": False,
            "error": "Playwright is not installed yet.",
            "detail": str(e),
            "setup_hint": "Run: pip install -r requirements.txt, then python -m playwright install chromium",
            "screenshot_path": None
        }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1366, "height": 1200})
            page.goto(html_path.resolve().as_uri(), wait_until="networkidle", timeout=45000)
            page.screenshot(path=str(screenshot_path), full_page=True)
            browser.close()

        return {
            "success": True,
            "error": None,
            "screenshot_path": str(screenshot_path)
        }
    except Exception as e:
        return {
            "success": False,
            "error": "Dashboard screenshot could not be generated.",
            "detail": str(e),
            "setup_hint": "If Chromium is missing, run: python -m playwright install chromium",
            "screenshot_path": None
        }


def check_dashboard_image_quality(screenshot_path: Path) -> dict:
    try:
        from PIL import Image, ImageStat
    except Exception as e:
        return {
            "success": False,
            "error": "Pillow is not installed yet.",
            "detail": str(e),
            "setup_hint": "Run: pip install -r requirements.txt"
        }

    try:
        image = Image.open(screenshot_path).convert("RGB")
        width, height = image.size
        grayscale = image.convert("L")
        stat = ImageStat.Stat(grayscale)

        brightness = stat.mean[0]
        contrast = stat.stddev[0]
        pixels = list(image.getdata())
        non_white_pixels = sum(
            1 for red, green, blue in pixels
            if min(abs(red - 255), abs(green - 255), abs(blue - 255)) > 18
        )
        visual_content_ratio = non_white_pixels / len(pixels)

        active_regions = 0
        total_regions = 9

        for row in range(3):
            for col in range(3):
                left = int(width * col / 3)
                upper = int(height * row / 3)
                right = int(width * (col + 1) / 3)
                lower = int(height * (row + 1) / 3)
                region = image.crop((left, upper, right, lower))
                region_pixels = list(region.getdata())
                region_non_white = sum(
                    1 for red, green, blue in region_pixels
                    if min(abs(red - 255), abs(green - 255), abs(blue - 255)) > 18
                )
                region_ratio = region_non_white / len(region_pixels)
                if region_ratio > 0.04:
                    active_regions += 1

        is_readable = (
            width >= 1000
            and height >= 700
            and contrast >= 20
            and visual_content_ratio >= 0.08
            and active_regions >= 4
        )

        return {
            "success": True,
            "image_width": width,
            "image_height": height,
            "brightness": round(brightness, 2),
            "contrast": round(contrast, 2),
            "visual_content_ratio": round(visual_content_ratio, 4),
            "active_layout_regions": active_regions,
            "total_layout_regions": total_regions,
            "layout_status": "readable" if is_readable else "needs review",
            "is_readable": is_readable
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Dashboard image quality check failed: {e}"
        }


def _load_official_lfs_month_dataset() -> dict:
    df = pd.read_csv(LFS_MONTH_CSV_URL)

    return {
        "success": True,
        "title": "Monthly Principal Labour Force Statistics",
        "url": "https://data.gov.my/data-catalogue/lfs_month",
        "dataset_id": "lfs_month",
        "download_url": LFS_MONTH_CSV_URL,
        "error": None,
        "dataframe": df
    }


def generate_unemployment_dashboard(loaded_datasets: list, task: str) -> dict:
    if not loaded_datasets:
        try:
            loaded_datasets = [_load_official_lfs_month_dataset()]
        except Exception as e:
            return {
                "success": False,
                "error": f"Could not load official lfs_month CSV from DOSM/data.gov.my: {e}",
                "dashboard_path": None
            }

    selected = loaded_datasets[0]
    df = selected["dataframe"].copy()

    required_columns = [
        "date",
        "u_rate",
        "lf",
        "p_rate",
        "lf_employed",
        "lf_unemployed"
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        return {
            "success": False,
            "error": f"Dataset is missing required columns: {missing_columns}",
            "dashboard_path": None
        }

    df = df.sort_values("date")
    df["date"] = df["date"].astype(str)

    latest_row = df.iloc[-1]
    earliest_row = df.iloc[0]

    latest_rate = latest_row["u_rate"]
    earliest_rate = earliest_row["u_rate"]
    change = round(latest_rate - earliest_rate, 2)

    latest_labour_force = round(latest_row["lf"], 1)
    latest_employed = round(latest_row["lf_employed"], 1)
    latest_unemployed = round(latest_row["lf_unemployed"], 1)
    latest_participation = round(latest_row["p_rate"], 1)

    peak_row = df.loc[df["u_rate"].idxmax()]
    lowest_row = df.loc[df["u_rate"].idxmin()]

    peak_rate = peak_row["u_rate"]
    peak_date = peak_row["date"]

    lowest_rate = lowest_row["u_rate"]
    lowest_date = lowest_row["date"]

    charts = {}

    chart_configs = {
        "unemployment_chart": px.line(
            df,
            x="date",
            y="u_rate",
            title="Malaysia Unemployment Rate Trend",
            markers=True
        ),
        "labour_force_chart": px.line(
            df,
            x="date",
            y="lf",
            title="Labour Force Trend",
            markers=True
        ),
        "employment_chart": px.line(
            df,
            x="date",
            y=["lf_employed", "lf_unemployed"],
            title="Employment vs Unemployment",
            markers=True
        ),
        "participation_chart": px.line(
            df,
            x="date",
            y="p_rate",
            title="Labour Force Participation Rate",
            markers=True
        )
    }

    for i, (name, fig) in enumerate(chart_configs.items()):
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e5e7eb"),
            title_font=dict(size=20),
            xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
            legend=dict(
                bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e5e7eb")
            ),
            margin=dict(l=40, r=30, t=70, b=40)
        )

        charts[name] = fig.to_html(
            full_html=False,
            include_plotlyjs="cdn" if i == 0 else False
        )

    template = Template(TEMPLATE_PATH.read_text(encoding="utf-8"))

    html = template.safe_substitute(
        task=task,
        latest_rate=latest_rate,
        earliest_rate=earliest_rate,
        change=change,
        latest_labour_force=latest_labour_force,
        latest_employed=latest_employed,
        latest_unemployed=latest_unemployed,
        latest_participation=latest_participation,
        peak_rate=peak_rate,
        peak_date=peak_date,
        lowest_rate=lowest_rate,
        lowest_date=lowest_date,
        dataset_title=selected["title"],
        dataset_id=selected["dataset_id"],
        row_count=len(df),
        column_count=len(df.columns),
        generated_at=datetime.now().strftime("%d %B %Y, %I:%M %p"),
        **charts
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = OUTPUT_DIR / f"unemployment_dashboard_{timestamp}.html"

    file_path.write_text(html, encoding="utf-8")

    screenshot_path = OUTPUT_DIR / f"unemployment_dashboard_{timestamp}.png"
    screenshot_result = export_dashboard_screenshot(file_path, screenshot_path)

    if screenshot_result.get("success"):
        image_quality_report = check_dashboard_image_quality(screenshot_path)
    else:
        image_quality_report = {
            "success": False,
            "error": screenshot_result.get("error"),
            "detail": screenshot_result.get("detail"),
            "setup_hint": screenshot_result.get("setup_hint")
        }

    return {
        "success": True,
        "error": None,
        "dashboard_path": str(file_path),
        "dataset_title": selected.get("title", "Monthly Principal Labour Force Statistics"),
        "dataset_id": selected.get("dataset_id", "lfs_month"),
        "row_count": len(df),
        "screenshot_path": screenshot_result.get("screenshot_path"),
        "screenshot_result": screenshot_result,
        "image_quality_report": image_quality_report
    }
