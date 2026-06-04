# EcoResearch Backend API Contract

## Endpoint

POST /api/research

## Request

```json
{
  "task": "Analyse Malaysia unemployment trend",
  "markdown_path": "storage/uploaded_markdowns/sample_instruction.md"
}
```

## Response

```json
{
  "success": true,
  "error": null,
  "dashboard_path": "storage/generated_dashboards/unemployment_dashboard_20260604_120000.html"
}
```

## Error Response

```json
{
  "success": false,
  "error": "No datasets available for dashboard generation.",
  "dashboard_path": null
}
```
