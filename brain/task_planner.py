# brain/task_planner.py

def create_research_plan(task: str, markdown_data: dict) -> dict:
    sources = markdown_data.get("sources", [])
    instructions = markdown_data.get("instructions", [])

    plan_steps = []

    plan_steps.append("Understand the economics research task given by the user.")

    if sources:
        plan_steps.append("Use the trusted websites listed in the Markdown file as data sources.")
    else:
        plan_steps.append("No trusted websites were found in the Markdown file. Ask user to add sources.")

    plan_steps.append("Collect relevant economic data or information from the trusted sources.")
    plan_steps.append("Clean and organise the collected data.")
    plan_steps.append("Analyse patterns, trends, and important observations.")
    plan_steps.append("Generate a visual dashboard for the user.")
    plan_steps.append("Return the dashboard link or downloadable dashboard file through Telegram.")

    return {
        "task": task,
        "sources": sources,
        "instructions": instructions,
        "plan_steps": plan_steps
    }


def format_plan_response(plan: dict) -> str:
    sources = plan.get("sources", [])
    instructions = plan.get("instructions", [])
    plan_steps = plan.get("plan_steps", [])

    response = "Brain received the task successfully 🧠✅\n\n"

    response += f"Task:\n{plan.get('task')}\n\n"

    response += "Trusted sources found:\n"
    if sources:
        for source in sources:
            response += f"- {source}\n"
    else:
        response += "- No sources found in markdown file.\n"

    response += "\nInstructions found:\n"
    if instructions:
        for instruction in instructions:
            response += f"- {instruction}\n"
    else:
        response += "- No bullet-point instructions found.\n"

    response += "\nResearch plan:\n"
    for index, step in enumerate(plan_steps, start=1):
        response += f"{index}. {step}\n"

    return response