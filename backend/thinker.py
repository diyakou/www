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

MAX_RETRIES = 2

async def analyze_and_plan(instruction: str, history: list):
    """
    Analyzes the user's instruction and history to determine the single next step.
    Includes a retry mechanism to ensure valid JSON output.
    """
    project_structure = get_project_structure()

    formatted_history = "\n".join([
        f"Task: {item['task']['action']}({json.dumps(item['task']['args'])}) -> Result: {item['result']['status']} - {item['result'].get('message', '')}"
        for item in history
    ])
    if not formatted_history:
        formatted_history = "(No tasks executed yet)"

    if instruction is None and history:
        instruction = history[0]['task'].get('initial_instruction', 'Could not find original instruction.')

    user_content = (
        f"Initial User Request: \"{instruction}\"\n\n"
        f"Current Project Structure:\n{project_structure}\n\n"
        f"Execution History:\n{formatted_history}\n\n"
        "Based on the above, what is the single next task to perform? Respond with a single JSON object."
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]

    for attempt in range(MAX_RETRIES):
        try:
            response = await g4f.ChatCompletion.create_async(
                model=g4f.models.gpt_4o,
                messages=messages,
            )

            # The model might return a single task object or a list with one task
            task = json.loads(response)
            if isinstance(task, list):
                return task
            return [task] # Always return a list

        except (json.JSONDecodeError, TypeError):
            # If parsing fails, add a message to the history and retry
            error_message = f"Invalid JSON response on attempt {attempt + 1}. Please provide only a single, valid JSON object."
            messages.append({"role": "assistant", "content": response}) # Add the invalid response to context
            messages.append({"role": "user", "content": error_message}) # Add the correction request

    # If all retries fail
    return [{"action": "error", "args": {"message": f"Failed to get a valid JSON response after {MAX_RETRIES} attempts."}}]
