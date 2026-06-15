---
name: ecoresearch-bot
description: "EcoResearch Bot: an OpenClaw skill that helps economics students turn Malaysia unemployment and labour force data into a visual dashboard and simple research insights."
---

# EcoResearch Bot

Use this skill when the user asks for Malaysia unemployment trend analysis, labour force analysis, official economic dataset discovery, or dashboard generation for unemployment-related research.

## 1. Skill Name

EcoResearch Bot

## 2. Target User

Economics students, business students, social science students, and non-technical users who need to understand Malaysia unemployment and labour force trends for assignments, reports, or presentations.

## 3. Real-World Problem

Malaysia unemployment and labour force data is usually stored in official datasets or government data portals. Non-technical students may find it difficult and time-consuming to search for the correct dataset, check whether the data is relevant, read many rows of tabular values, and convert the data into charts that are easy to explain.

EcoResearch Bot helps users transform official Malaysia unemployment trend data into a visual dashboard with simple research insights, so they can understand changes in unemployment rate, labour force size, employed population, unemployed population, and participation rate more quickly.

## 4. Input Format

The user provides:

1. A research task in plain language.

Example:

```text
Analyse Malaysia unemployment trend.
```

2. A Markdown instruction file containing trusted websites and analysis instructions.

Example:

```markdown
## Research Topic
Malaysia unemployment trend analysis.

## Trusted Websites
- https://data.gov.my
- https://www.dosm.gov.my
- https://www.bnm.gov.my

## Instructions
- Use official Malaysian sources only.
- Focus on unemployment trend.
- Generate a visual dashboard.
- Explain the trend in simple language for economics students.
```

## 5. CV or Image-Processing Method

This skill uses **chart generation from tabular data**, **dashboard visualization**, and **dashboard screenshot quality checking**, which are accepted visual-processing and image-processing components for the assignment.

The backend converts official unemployment and labour force datasets into visual charts and dashboard components, including:

- unemployment rate trend line chart
- labour force trend line chart
- employment versus unemployment comparison chart
- labour force participation rate chart
- KPI summary cards for latest values, peak values, lowest values, and trend change

After the HTML dashboard is generated, the backend can also capture the dashboard as a PNG screenshot and perform a basic visual quality check. This check measures image size, contrast, visual content ratio, and active layout regions to verify that the dashboard preview is readable and not visually blank.

This method is useful because raw economic tables are difficult to interpret quickly. Visual dashboards make patterns, peaks, drops, and long-term changes easier for non-technical users to understand. The screenshot quality check adds a simple image-processing validation step to help ensure that the generated visual output is usable before it is sent to the user.

## 6. Step-by-Step Workflow

### Workflow

1. Identify the user's Malaysia unemployment or labour force research task.
2. If a Markdown instruction file path is provided, pass it to the backend.
3. Call the local EcoResearch FastAPI backend using `scripts/client.py`.
4. Wait for the backend response.
5. Report the generated dashboard path or backend error clearly.

### Project Processing Workflow

1. Receive the user's Malaysia unemployment or labour force research task.
2. Receive the uploaded Markdown instruction file.
3. Read trusted websites and instructions from the Markdown file.
4. Detect the required unemployment-related data fields.
5. Search trusted official Malaysian data sources for relevant datasets.
6. Rank possible datasets based on relevance to the task.
7. Load the best official dataset.
8. Check whether the dataset contains the required columns, such as date, unemployment rate, labour force, employed population, unemployed population, and participation rate.
9. Generate visual charts from the tabular data.
10. Build an interactive HTML dashboard.
11. Capture the dashboard as a PNG screenshot preview when the screenshot dependencies are available.
12. Perform dashboard image quality checking using image size, contrast, visual content ratio, and active layout regions.
13. Return a short research summary, the dashboard file, and the screenshot preview when available to the user through Telegram/OpenClaw.

## 7. Output Format

The skill returns:

1. A short text summary containing:

- research topic
- dataset used
- dataset ID
- number of records analysed
- trusted sources checked
- dashboard status

2. A visual output:

- interactive HTML dashboard with charts and KPI cards
- PNG dashboard screenshot preview when available

3. A dashboard image quality check containing:

- screenshot status
- image size
- contrast value
- visual content ratio
- active layout region count
- layout status, such as readable or needs review

Example output:

```text
Research completed successfully.

Topic:
Analyse Malaysia unemployment trend.

Dataset used:
Monthly Principal Labour Force Statistics

Rows analysed:
195

Dashboard:
The interactive HTML dashboard is attached below.

Dashboard image quality check:
Layout status: readable
Contrast: acceptable
Active layout regions: 7/9
```

## 8. Limitation Handling

The system handles limitations as follows:

- If the Markdown instruction file cannot be read, it reports that the instruction file is missing or invalid.
- If trusted sources cannot be reached, it reports that dataset discovery failed.
- If no relevant dataset is found, it reports that no suitable official dataset is available.
- If the selected dataset does not contain required columns, it reports which columns are missing.
- If dashboard generation fails, it returns the reason instead of inventing results.
- If screenshot generation or image quality checking cannot run because Playwright, Chromium, or Pillow is missing, the system still returns the HTML dashboard and reports that the image quality check was not completed.
- The current prototype is mainly tested for Malaysia unemployment and labour force trend analysis.
- The current dashboard generator expects unemployment-related columns and may not work correctly for unrelated economic topics such as GDP or inflation without backend changes.
- The dashboard quality depends on the structure, completeness, and availability of official datasets.

## 9. Ethical Boundary

EcoResearch Bot only analyses official or user-approved economic data sources.

The system must not:

- invent fake economic statistics
- misrepresent official data
- present uncertain analysis as fact
- make political claims beyond what the data supports
- claim that correlation proves causation
- replace expert economic judgement or policy analysis

The tool is designed to support student research, data understanding, and presentation preparation. It should help users interpret visible data trends, but final conclusions should still be checked against official reports and course requirements.

## Backend

Default backend URL:

```text
http://127.0.0.1:8000
```

Main endpoint:

```text
POST /api/research
```

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

## Rules

- Do not invent economic statistics manually.
- Always prefer official datasets and backend results.
- If the backend fails, explain the error clearly.
- If dashboard generation fails, report the reason.
- Keep the task focused on Malaysia unemployment or labour force trend analysis unless the backend is extended for other economic topics.
- The backend owns dataset discovery, analysis, and dashboard generation.
