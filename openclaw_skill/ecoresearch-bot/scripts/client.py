#!/usr/bin/env python3

import argparse
import json
import os
import sys
from pathlib import Path

import requests


BASE_URL = os.environ.get(
    "ECORESEARCH_BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


def call_research_backend(task: str, markdown_path: str | None):
    payload = {
        "task": task,
        "markdown_path": markdown_path or ""
    }

    response = requests.post(
        f"{BASE_URL}/api/research",
        json=payload,
        timeout=120
    )

    if not response.ok:
        print(
            json.dumps(
                {
                    "success": False,
                    "error": f"Backend error {response.status_code}: {response.text}"
                },
                indent=2
            )
        )
        sys.exit(1)

    try:
        print(json.dumps(response.json(), indent=2))
    except Exception:
        print(response.text)


def main():
    parser = argparse.ArgumentParser(
        description="EcoResearch Bot OpenClaw client"
    )

    parser.add_argument(
        "research",
        choices=["research"],
        help="Run EcoResearch backend research pipeline"
    )

    parser.add_argument(
        "--task",
        required=True,
        help="Economic research task"
    )

    parser.add_argument(
        "--markdown-path",
        default="",
        help="Path to uploaded Markdown instruction file"
    )

    args = parser.parse_args()

    call_research_backend(
        task=args.task,
        markdown_path=args.markdown_path
    )


if __name__ == "__main__":
    main()