---
name: econoanalyst-bot
description: "EconoAnalyst Bot: an OpenClaw skill that helps Business and Economics students understand Malaysia labour market data, answer labour-market questions, generate a visual dashboard, and perform CV-based dashboard readability checking."
---

# EconoAnalyst Bot

Use this skill when the user asks about Malaysia labour market analysis, unemployment rate, labour force participation rate, employment trend, official labour market dataset discovery, or dashboard generation.

## 1. Skill Name

EconoAnalyst Bot

## 2. Target User

Business and Economics students, FYP students, postgraduate researchers, lecturers, policy analysts, and non-technical users who need to understand Malaysia labour market trends for assignments, reports, research, or presentations.

## 3. Real-World Problem

Malaysia labour market data is usually stored in official datasets or government data portals. Students and non-technical users may find it difficult and time-consuming to search for the correct dataset, understand labour market indicators, clean the data, create charts, and interpret the trend.

EconoAnalyst helps users by combining natural language interaction, official labour market data, automated dashboard generation, and computer vision-based dashboard readability checking.

## 4. Input Format

The user interacts through Telegram.

The user may provide:

1. A normal labour market question in plain language.

Example:

```text
Why is unemployment rate important?
```

2. A dashboard generation command.

Example:

```text
Generate Malaysia labour market dashboard
```

The user does not need to upload a Markdown file or dataset during the demo.

For dashboard generation, the backend uses an internal EconoAnalyst instruction template that defines the trusted data sources, analysis requirements, and expected dashboard output.

## 5. Internal Instruction Template

The internal instruction template contains:

- research topic
- trusted official data sources
- dataset requirements
- analysis instructions
- dashboard output requirements
- visual quality checking requirements

Example trusted sources include:

- https://data.gov.my
- https://www.dosm.gov.my
- https://www.bnm.gov.my

This template is used internally by the backend. It is not uploaded by the user during the Telegram demo.

## 6. CV or Image-Processing Method

This skill uses dashboard screenshot generation, image preprocessing, and computer vision-based quality checking.

After the HTML dashboard is generated, the backend captures a PNG screenshot preview and performs a visual quality check.

The visual quality check includes:

- image size checking
- grayscale conversion
- contrast analysis
- visual content ratio
- active layout region detection
- readability status classification

This helps verify that the generated dashboard preview is readable and not visually blank before it is sent to the user.

## 7. Step-by-Step Workflow

### User Interaction Workflow

1. Receive the user's Telegram message.
2. Identify whether the message is a normal labour market question or a dashboard generation request.
3. For normal labour market questions, use the LLM to provide a short student-friendly explanation.
4. For dashboard requests, send the task to the FastAPI backend.
5. The backend uses the internal EconoAnalyst instruction template.
6. The backend retrieves or uses the official DOSM/data.gov.my labour market dataset.
7. The backend generates charts, KPI cards, and an interactive HTML dashboard.
8. The dashboard is captured as a PNG preview image.
9. Computer vision checks the screenshot readability and layout quality.
10. Telegram returns the research summary, HTML dashboard file, preview image, and CV quality metrics to the user.

### Dashboard Processing Workflow

1. Use the internal EconoAnalyst instruction template.
2. Identify official Malaysia labour market data sources.
3. Retrieve the relevant labour force dataset.
4. Analyse unemployment rate, employment rate, labour force, employed population, unemployed population, and labour force participation rate.
5. Generate charts and dashboard KPI cards.
6. Build an interactive HTML dashboard.
7. Capture the dashboard screenshot preview.
8. Perform CV-based visual quality checking.
9. Return the dashboard output through Telegram.

## 8. Output Format

The skill can return:

1. A short plain-text explanation for labour market questions.

2. A dashboard package containing:

- research summary
- dataset used
- dataset ID
- number of records analysed
- latest data period
- trusted source
- interactive HTML dashboard
- PNG dashboard screenshot preview
- dashboard image quality check

3. A dashboard image quality check containing:

- screenshot status
- image size
- contrast value
- visual content ratio
- active layout region count
- layout status, such as readable or needs review

## 9. Safety and Reliability Rules

- Do not invent economic statistics manually.
- Prefer official Malaysian labour market datasets and backend results.
- Keep the task focused on Malaysia unemployment and labour force trend analysis.
- Use the internal EconoAnalyst instruction template for dashboard generation.
- The user does not need to upload a Markdown file or dataset during the demo.
- If the backend fails, explain the error clearly.
- If the LLM quota is reached, show a friendly fallback message.
- The screenshot quality check only verifies visual readability, not the correctness of the economic analysis.

## 10. Future Enhancement

Future versions can support:

- user-uploaded CSV or Excel datasets
- pasted small datasets in Telegram messages
- additional economics topics such as GDP, inflation, and household income
- PDF report generation
- stronger computer vision evaluation with OCR and chart-level validation
