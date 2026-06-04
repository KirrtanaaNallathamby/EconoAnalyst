#dashboard/dashboard_generator.py

from pathlib import Path
from datetime import datetime
from string import Template
import plotly.express as px


OUTPUT_DIR = Path("storage/generated_dashboards")
TEMPLATE_PATH = Path("dashboard/templates/dashboard_template.html")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_unemployment_dashboard(loaded_datasets: list, task: str) -> dict:
    if not loaded_datasets:
        return {
            "success": False,
            "error": "No datasets available for dashboard generation.",
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

    return {
        "success": True,
        "error": None,
        "dashboard_path": str(file_path)
    }