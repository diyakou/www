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

async def analyze_and_plan(instruction: str, history: list):
    """
    Analyzes the user's instruction and history to determine the single next step.
    """
    project_structure = get_project_structure()

    # Format the history for the prompt
    formatted_history = "\n".join([
        f"Task: {item['task']['action']}({item['task']['args']}) -> Result: {item['result']['status']} - {item['result'].get('message', '')}"
        for item in history
    ])
    if not formatted_history:
        formatted_history = "(No tasks executed yet)"

    # If instruction is None, it means we are in a subsequent step.
    # The initial instruction should be in the history.
    if instruction is None and history:
        instruction = history[0]['task'].get('initial_instruction', 'Could not find original instruction.')


    user_content = (
        f"Initial User Request: \"{instruction}\"\n\n"
        f"Current Project Structure:\n{project_structure}\n\n"
        f"Execution History:\n{formatted_history}\n\n"
        "Based on the above, what is the single next task to perform?"
    )

    response = await g4f.ChatCompletion.create_async(
        model=g4f.models.gpt_4o,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
    )

    try:
        # The model might return a single task object or a list with one task
        task = json.loads(response)
        if isinstance(task, list):
            return task
        return [task]
    except (json.JSONDecodeError, TypeError):
        return [{"action": "error", "args": {"message": "Failed to parse LLM response.", "raw_response": response}}]
