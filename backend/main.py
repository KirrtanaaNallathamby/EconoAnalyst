#main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from brain.openclaw_brain import run_brain

import subprocess
from pathlib import Path
from datetime import datetime

import os

app = FastAPI(title="EcoResearch Backend")


class ProcessTaskRequest(BaseModel):
    user_id: int = 0
    task: str
    markdown_path: str = ""


class ResearchRequest(BaseModel):
    task: str
    markdown_path: Optional[str] = ""


@app.get("/")
def home():
    return {
        "message": "EcoResearch Backend is running",
        "available_endpoints": [
            "POST /process-task",
            "POST /api/research",
            "POST /openclaw-research"
        ]
    }


@app.post("/process-task")
def process_task(request: ProcessTaskRequest):
    brain_result = run_brain(
        task=request.task,
        markdown_path=request.markdown_path
    )

    dashboard_path = None

    if brain_result.get("dashboard_result"):
        dashboard_path = brain_result["dashboard_result"].get("dashboard_path")

    return {
        "status": "completed" if brain_result.get("success") else "failed",
        "success": brain_result.get("success", False),
        "user_id": request.user_id,
        "task": request.task,
        "markdown_path": request.markdown_path,
        "message": brain_result.get("message"),
        "error": brain_result.get("error"),
        "dashboard_path": dashboard_path,
        "brain_result": brain_result
    }


@app.post("/api/research")
def api_research(request: ResearchRequest):
    brain_result = run_brain(
        task=request.task,
        markdown_path=request.markdown_path or ""
    )

    dashboard_path = None

    if brain_result.get("dashboard_result"):
        dashboard_path = brain_result["dashboard_result"].get("dashboard_path")

    success = brain_result.get("success", False)

    return {
        "success": success,
        "status": "completed" if success else "failed",
        "orchestrated_by": "OpenClaw",
        "openclaw_phase": "Phase 7",
        "task": request.task,
        "markdown_path": request.markdown_path,
        "message": "[OpenClaw Orchestrator ✅]\n\n" + brain_result.get("message", ""),
        "error": brain_result.get("error"),
        "dashboard_path": dashboard_path,
        "brain_result": brain_result
    }


@app.post("/openclaw-research")
def openclaw_research(request: ProcessTaskRequest):
    start_time = datetime.now()

    prompt = (
        "Use the ecoresearch-bot skill to analyse this task.\n"
        f"Task: {request.task}\n"
        f"Markdown path: {request.markdown_path}\n"
        "You must call the local EcoResearch backend through the skill. "
        "Do not answer manually."
    )

    openclaw_path = os.getenv("OPENCLAW_PATH")

    try:
        result = subprocess.run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                openclaw_path,
                "agent",
                "--agent",
                "main",
                "--session-key",
                "main",
                "--message",
                prompt
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600
        )

    except Exception as e:
        return {
            "success": False,
            "status": "failed",
            "orchestrated_by": "OpenClaw",
            "message": (
                "[OpenClaw Orchestrator ❌]\n\n"
                "FastAPI tried to launch OpenClaw, but it failed.\n\n"
                f"Error:\n{e}"
            ),
            "error": str(e),
            "dashboard_path": None
        }

    dashboard_dir = Path("storage/generated_dashboards")
    dashboard_path = None

    if dashboard_dir.exists():
        html_files = list(dashboard_dir.glob("*.html"))

        recent_files = [
            file for file in html_files
            if datetime.fromtimestamp(file.stat().st_mtime) >= start_time
        ]

        if recent_files:
            latest_file = max(
                recent_files,
                key=lambda file: file.stat().st_mtime
            )
            dashboard_path = str(latest_file)

    openclaw_output = (result.stdout or "").strip()
    openclaw_error = (result.stderr or "").strip()

    if not openclaw_output:
        openclaw_output = "OpenClaw ran, but returned no stdout."

    message = (
        "[OpenClaw Orchestrator ✅]\n\n"
        "Telegram successfully routed this task through OpenClaw.\n\n"
        "OpenClaw stdout:\n"
        f"{openclaw_output}\n\n"
    )

    if openclaw_error:
        message += (
            "OpenClaw stderr:\n"
            f"{openclaw_error}\n"
        )

    return {
        "success": result.returncode == 0,
        "status": "completed" if result.returncode == 0 else "failed",
        "orchestrated_by": "OpenClaw",
        "task": request.task,
        "markdown_path": request.markdown_path,
        "message": message,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "dashboard_path": dashboard_path
    }