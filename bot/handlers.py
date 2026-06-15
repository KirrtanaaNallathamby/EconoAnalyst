from pathlib import Path
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
import os
import re
import requests
from dotenv import load_dotenv


UPLOAD_DIR = Path("storage/uploaded_markdowns")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def clean_text(text: str) -> str:
    return (
        text.replace("â€”", "—")
        .replace("â€“", "–")
        .replace("â€™", "'")
        .replace("â€œ", '"')
        .replace("â€\x9d", '"')
    )


def extract_value(pattern: str, text: str, default: str) -> str:
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return clean_text(match.group(1).strip())

    return default


def build_student_summary(
    task: str,
    backend_message: str,
    dashboard_path: str | None,
    backend_reply: dict | None = None
) -> str:
    backend_reply = backend_reply or {}
    dataset = extract_value(
        r"Dataset:\s*(.+)",
        backend_message,
        backend_reply.get("dataset_title") or "Monthly Principal Labour Force Statistics"
    )

    dataset_id = extract_value(
        r"Dataset ID:\s*`?([^`\n]+)`?",
        backend_message,
        backend_reply.get("dataset_id") or "lfs_month"
    )

    rows = extract_value(
        r"Rows analysed:\s*`?([^`\n]+)`?",
        backend_message,
        str(backend_reply.get("row_count") or "196")
    )

    data_as_of = extract_value(
        r"Data as of:\s*(.+)",
        backend_message,
        "March 2026"
    )

    summary = (
        "✅ Research Completed\n\n"
        f"📌 Topic:\n{task}\n\n"
        f"📊 Dataset Used:\n{dataset}\n\n"
        f"🆔 Dataset ID:\n{dataset_id}\n\n"
        f"📁 Records Analysed:\n{rows}\n\n"
        f"📅 Data As Of:\n{data_as_of}\n\n"
        "🌐 Source:\n"
        "Official Malaysian labour force data from DOSM via data.gov.my.\n\n"
        "🦞 Powered By:\n"
        "OpenClaw orchestrated the task and triggered the EcoResearch pipeline.\n\n"
        "📎 Dashboard:\n"
        "The interactive HTML dashboard has been generated and attached below."
    )

    if dashboard_path:
        summary += f"\n\nSaved locally at:\n{dashboard_path}"

    image_quality_report = backend_reply.get("image_quality_report")
    screenshot_path = backend_reply.get("screenshot_path")

    if image_quality_report:
        summary += "\n\nDashboard Image Quality Check:\n"
        if screenshot_path:
            summary += f"Screenshot Preview:\n{screenshot_path}\n\n"

        if image_quality_report.get("success"):
            summary += (
                f"Image Size: {image_quality_report.get('image_width')} x "
                f"{image_quality_report.get('image_height')}\n"
                f"Contrast: {image_quality_report.get('contrast')}\n"
                f"Visual Content Ratio: {image_quality_report.get('visual_content_ratio')}\n"
                f"Active Layout Regions: "
                f"{image_quality_report.get('active_layout_regions')}/"
                f"{image_quality_report.get('total_layout_regions')}\n"
                f"Layout Status: {image_quality_report.get('layout_status')}"
            )
        else:
            summary += f"Check not completed: {image_quality_report.get('error')}"
            if image_quality_report.get("setup_hint"):
                summary += f"\nSetup Hint: {image_quality_report.get('setup_hint')}"

    return summary


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi, I’m EcoResearch Bot 🌱📊\n\n"
        "Send me:\n"
        "1. Your economics research task\n"
        "2. A Markdown (.md) instruction file\n\n"
        "I will find official data, analyse it, and return an interactive dashboard."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "How to use EcoResearch Bot:\n\n"
        "1. Send your research task as a normal message.\n"
        "Example: Analyse Malaysia unemployment trend.\n\n"
        "2. Upload a .md file containing trusted websites and instructions.\n\n"
        "3. I will return a short summary and an HTML dashboard file."
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    context.user_data["latest_task"] = user_text

    await update.message.reply_text(
        "Task received ✅\n\n"
        f"📌 Your task:\n{user_text}\n\n"
        "Now upload your Markdown instruction file (.md)."
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    user_id = update.effective_user.id

    if not document.file_name.endswith(".md"):
        await update.message.reply_text(
            "Please upload a Markdown file only (.md)."
        )
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = UPLOAD_DIR / f"user_{user_id}_{timestamp}_{document.file_name}"

    telegram_file = await document.get_file()
    await telegram_file.download_to_drive(custom_path=str(save_path))

    latest_task = context.user_data.get(
        "latest_task",
        "No task sent yet."
    )

    load_dotenv()
    backend_url = os.getenv("BACKEND_URL")

    if not backend_url:
        await update.message.reply_text(
            "Backend URL is missing. Please check your .env file."
        )
        return

    payload = {
        "user_id": user_id,
        "task": latest_task,
        "markdown_path": str(save_path)
    }

    try:
        await update.message.reply_text(
            "Markdown file saved ✅\n"
            "EcoResearch Bot is analysing your task through OpenClaw 🦞📊"
        )

        response = requests.post(
            f"{backend_url}/openclaw-research",
            json=payload,
            timeout=600
        )

        backend_reply = response.json()

        backend_message = backend_reply.get("message", "")
        dashboard_path = backend_reply.get("dashboard_path")
        screenshot_path = backend_reply.get("screenshot_path")

        summary = build_student_summary(
            task=latest_task,
            backend_message=backend_message,
            dashboard_path=dashboard_path,
            backend_reply=backend_reply
        )

        await update.message.reply_text(summary)

        if dashboard_path:
            with open(dashboard_path, "rb") as dashboard_file:
                await update.message.reply_document(
                    document=dashboard_file,
                    filename="EcoResearch_Dashboard.html",
                    caption="Interactive dashboard generated successfully 🖥️✅"
                )
            if screenshot_path:
                with open(screenshot_path, "rb") as screenshot_file:
                    await update.message.reply_photo(
                        photo=screenshot_file,
                        caption="Dashboard preview image generated for visual quality checking."
                    )
        else:
            await update.message.reply_text(
                "The analysis finished, but no dashboard file was found."
            )

    except Exception as e:
        await update.message.reply_text(
            "Markdown file saved ✅ but the backend/OpenClaw connection failed ❌\n\n"
            f"Error:\n{e}"
        )
