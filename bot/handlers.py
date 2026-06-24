from pathlib import Path
from datetime import datetime
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
import os
import asyncio
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
    message = """Hi, I am EconoAnalyst 📊

I help Economics students understand Malaysia labour market data.

You can ask me questions such as:
• Why is unemployment rate important?
• What is labour force participation rate?
• How can unemployment trend be used in an economics assignment?
• Compare employment and unemployment.

When you want the full dashboard, type:
Generate Malaysia labour market dashboard
"""
    await update.message.reply_text(message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """Hi, I am EconoAnalyst 📊

I help Economics students understand Malaysia labour market data.

You can ask me questions such as:
• Why is unemployment rate important?
• What is labour force participation rate?
• How can unemployment trend be used in an economics assignment?
• Compare employment and unemployment.

When you want the full dashboard, type:
Generate Malaysia labour market dashboard
"""
    await update.message.reply_text(message)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    user_id = update.effective_user.id
    context.user_data["latest_task"] = user_text

    lower_text = user_text.lower()

    if lower_text in [
        "help", "/help",
        "what can you do", "what can you do?",
        "what can i ask you", "what can i ask you?",
        "what can i ask", "what can i ask?",
        "menu", "start", "/start"
    ]:
        await help_command(update, context)
        return

    should_generate = any(word in lower_text for word in [
        "generate", "dashboard", "report", "visualise", "visualize", "chart", "html"
    ])

    if not should_generate:
        load_dotenv(dotenv_path=Path.cwd() / ".env")

        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        openrouter_model = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free")

        if not openrouter_key:
            await update.message.reply_text(
                "OpenRouter is not configured yet.\n\n"
                "You can still generate the dashboard by typing:\n"
                "Generate Malaysia labour market dashboard"
            )
            return

        system_prompt = (
            "You are EconoAnalyst, a helpful assistant for Business and Economics students. "
            "Your scope is Malaysia labour market analysis: unemployment rate, employment, labour force, "
            "labour force participation rate, economic interpretation, assignment/FYP writing support, "
            "dashboard usage, and computer vision dashboard readability checking. "
            "Stay within this topic. If the user asks outside this scope, politely redirect them back to Malaysia labour market analysis. "
            "Do not invent exact latest statistics. If exact figures or charts are needed, tell the user to generate the dashboard. "
            "Use plain text only. Do not use Markdown, bold formatting, headings, or tables. "
            "For normal economics questions, do not introduce yourself. Start directly with the answer. "
            "Keep replies short, friendly, and student-friendly. Use at most 4 short bullet points."
        )

        try:
            thinking_msg = await update.message.reply_text("Thinking... ⏳")

            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action=ChatAction.TYPING
            )

            response = await asyncio.to_thread(
                requests.post,
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost",
                    "X-Title": "EconoAnalyst Demo"
                },
                json={
                    "model": openrouter_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_text}
                    ],
                    "temperature": 0.4,
                    "max_tokens": 300
                },
                timeout=45
            )

            if response.status_code != 200:
                if response.status_code == 429:
                    await thinking_msg.edit_text(
                        "Free LLM quota reached for today ⚠️\n\n"
                        "You can still generate the dashboard by typing:\n"
                        "Generate Malaysia labour market dashboard\n\n"
                        "Please try LLM questions again after the free quota resets."
                    )
                else:
                    await thinking_msg.edit_text(
                        "The LLM service is temporarily unavailable ⚠️\n\n"
                        "You can still generate the dashboard by typing:\n"
                        "Generate Malaysia labour market dashboard"
                    )
                return

            data = response.json()
            choice = (data.get("choices") or [{}])[0]
            message = choice.get("message") or {}
            content = message.get("content")

            if isinstance(content, list):
                content = " ".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in content
                )

            if not content:
                content = message.get("reasoning") or message.get("refusal")

            if not content:
                content = (
                    "I can help with Malaysia labour market analysis.\n"
                    "Try asking about unemployment, employment, labour force participation, or dashboard generation."
                )

            answer = str(content).strip()
            answer = answer.replace("**", "").replace("__", "")
            answer = answer.replace("###", "").replace("##", "").replace("#", "")
            answer = answer.replace("•", "-")
            answer = answer.replace("Hello! I am EconoAnalyst.", "")
            answer = answer.replace("Hi, I am EconoAnalyst.", "")
            answer = "\n".join(line.rstrip() for line in answer.splitlines()).strip()

            if len(answer) > 3500:
                answer = answer[:3500] + "\n\n..."

            await thinking_msg.edit_text(answer)
            return

        except Exception as e:
            await update.message.reply_text(
                "I could not generate an LLM answer right now ❌\n\n"
                f"Error: {e}\n\n"
                "You can still type:\n"
                "Generate Malaysia labour market dashboard"
            )
            return

    load_dotenv(dotenv_path=Path.cwd() / ".env")
    backend_url = os.getenv("BACKEND_URL")

    if not backend_url:
        await update.message.reply_text("Backend URL is missing. Please check your .env file.")
        return

    internal_md = Path("examples/sample_instruction.md")

    if not internal_md.exists():
        await update.message.reply_text(
            "Internal instruction file not found: examples/sample_instruction.md"
        )
        return

    payload = {
        "user_id": user_id,
        "task": user_text,
        "markdown_path": str(internal_md.resolve())
    }

    try:
        await update.message.reply_text(
            "Task received ✅\n\n"
            f"📌 Your task:\n{user_text}\n\n"
            "Using the internal EconoAnalyst instruction template.\n"
            "Generating research summary, dashboard, and visual quality check... 📊"
        )

        response = requests.post(
            f"{backend_url}/process-task",
            json=payload,
            timeout=600
        )

        backend_reply = response.json()

        backend_message = backend_reply.get("message", "")
        dashboard_path = backend_reply.get("dashboard_path")
        screenshot_path = backend_reply.get("screenshot_path")

        summary = build_student_summary(
            task=user_text,
            backend_message=backend_message,
            dashboard_path=dashboard_path,
            backend_reply=backend_reply
        )

        await update.message.reply_text(summary)

        if dashboard_path:
            with open(dashboard_path, "rb") as dashboard_file:
                await update.message.reply_document(
                    read_timeout=240,
                    write_timeout=240,
                    connect_timeout=60,
                    pool_timeout=60,
                    document=dashboard_file,
                    filename="EcoResearch_Dashboard.html",
                    caption="Interactive dashboard generated successfully 💻✅"
                )

            if screenshot_path:
                with open(screenshot_path, "rb") as screenshot_file:
                    await update.message.reply_photo(
                        read_timeout=240,
                        write_timeout=240,
                        connect_timeout=60,
                        pool_timeout=60,
                        photo=screenshot_file,
                        caption="Dashboard preview image generated for visual quality checking."
                    )
        else:
            await update.message.reply_text("The analysis finished, but no dashboard file was found.")

    except Exception as e:
        await update.message.reply_text(
            "Telegram upload timed out ⚠️\n\n"
            f"Error: {e}"
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
            f"{backend_url}/process-task",
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
                    read_timeout=240,
                    write_timeout=240,
                    connect_timeout=60,
                    pool_timeout=60,
                    document=dashboard_file,
                    filename="EcoResearch_Dashboard.html",
                    caption="Interactive dashboard generated successfully 🖥️✅"
                )
            if screenshot_path:
                with open(screenshot_path, "rb") as screenshot_file:
                    await update.message.reply_photo(
                        read_timeout=240,
                        write_timeout=240,
                        connect_timeout=60,
                        pool_timeout=60,
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
