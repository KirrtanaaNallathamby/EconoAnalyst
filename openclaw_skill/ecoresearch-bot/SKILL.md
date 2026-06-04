---
name: ecoresearch-bot
description: "Orchestrate EcoResearch Bot economic research tasks through the local FastAPI backend."
---

# EcoResearch Bot

Use this skill when the user asks for economic research, dataset discovery, labour market analysis, unemployment analysis, inflation analysis, GDP analysis, or dashboard generation using EcoResearch Bot.

## Workflow

1. Identify the user's economic research task.
2. If a Markdown instruction file path is provided, pass it to the backend.
3. Call the local EcoResearch FastAPI backend using `scripts/client.py`.
4. Wait for the backend response.
5. Report the generated dashboard path or backend error clearly.

## Backend

Default backend URL:

`http://127.0.0.1:8000`

Main endpoint:

`POST /api/research`

Expected payload:

```json
{
  "task": "Analyse Malaysia unemployment trend",
  "markdown_path": "storage/uploaded_markdowns/sample_instruction.md"
}
```

Expected success response:

```json
{
  "success": true,
  "dashboard_path": "storage/generated_dashboards/..."
}
```

---

## Rules

- Do not invent economic statistics manually.
- Always prefer the backend result.
- If backend fails, explain the error.
- If no Markdown path is provided, still call the backend with an empty markdown path.
- The backend owns dataset discovery, downloading, analysis, and dashboard generation.

---