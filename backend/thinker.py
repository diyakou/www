import g4f
import json
import os
from prompts import SYSTEM_PROMPT

PROJECT_DIRECTORY = "project_files"

def get_project_structure():
    """Returns a string representing the project's file and directory structure."""
    structure = []
    if not os.path.exists(PROJECT_DIRECTORY):
        return "(empty)"

    for root, dirs, files in os.walk(PROJECT_DIRECTORY):
        relative_root = os.path.relpath(root, PROJECT_DIRECTORY)
        if relative_root == ".":
            relative_root = ""

        for name in dirs:
            structure.append(os.path.join(relative_root, name) + "/")
        for name in files:
            structure.append(os.path.join(relative_root, name))

    return "\n".join(structure) if structure else "(empty)"

async def analyze_and_plan(instruction: str):
    """
    Analyzes a user's instruction, considering the current project structure,
    and breaks it down into a series of actionable tasks using a refined prompt.
    """
    project_structure = get_project_structure()

    # The user content will be a combination of the instruction and the project structure.
    user_content = (
        f"User Request: \"{instruction}\"\n"
        f"Project Structure:\n{project_structure}"
    )

    response = await g4f.ChatCompletion.create_async(
        model=g4f.models.gpt_4o,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
    )

    try:
        tasks = json.loads(response)
        return tasks
    except (json.JSONDecodeError, TypeError):
        return [{"action": "error", "args": {"message": "Failed to parse LLM response.", "raw_response": response}}]
