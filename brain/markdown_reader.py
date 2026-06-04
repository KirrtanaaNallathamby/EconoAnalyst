# brain/markdown_reader.py

from pathlib import Path
import re


def read_markdown(markdown_path: str) -> dict:
    path = Path(markdown_path)

    if not path.exists():
        return {
            "success": False,
            "error": f"Markdown file not found: {markdown_path}",
            "content": "",
            "sources": [],
            "instructions": []
        }

    content = path.read_text(encoding="utf-8")

    url_pattern = r"https?://[^\s\)\]\}>]+"
    sources = re.findall(url_pattern, content)

    instructions = []
    current_section = None

    for line in content.splitlines():
        clean_line = line.strip()

        if not clean_line:
            continue

        if clean_line.startswith("#"):
            heading = clean_line.lower()

            if "instruction" in heading or "dashboard" in heading or "requirement" in heading:
                current_section = "instructions"
            elif "source" in heading or "website" in heading:
                current_section = "sources"
            else:
                current_section = None

            continue

        if current_section == "instructions":
            if clean_line.startswith("-") or clean_line.startswith("*"):
                instruction = clean_line.lstrip("-* ").strip()

                if not instruction.startswith("http"):
                    instructions.append(instruction)

    return {
        "success": True,
        "error": None,
        "content": content,
        "sources": sources,
        "instructions": instructions
    }