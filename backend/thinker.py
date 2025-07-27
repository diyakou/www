import g4f
import json
import os

PROJECT_DIRECTORY = "project_files"

def get_project_structure():
    """Returns a string representing the project's file and directory structure."""
    structure = []
    for root, dirs, files in os.walk(PROJECT_DIRECTORY):
        # Prune the root path to be relative to the project directory
        relative_root = os.path.relpath(root, PROJECT_DIRECTORY)
        if relative_root == ".":
            relative_root = ""

        for name in dirs:
            structure.append(os.path.join(relative_root, name) + "/")
        for name in files:
            structure.append(os.path.join(relative_root, name))

    return "\n".join(structure)

async def analyze_and_plan(instruction: str):
    """
    Analyzes a user's instruction, considering the current project structure,
    and breaks it down into a series of actionable tasks.
    """
    project_structure = get_project_structure()

    system_prompt = (
        "You are a task planning agent. Your job is to break down a user's request "
        "into a series of simple, actionable tasks. Each task should be a JSON object "
        "with an 'action' and 'args'. Supported actions are: 'create_file', 'write_to_file', "
        "'read_file', and 'execute_command'. Respond with a JSON array of tasks."
        "\n\n"
        "Here is the current project structure:\n"
        f"```\n{project_structure}\n```\n\n"
        "Analyze the user's request based on this structure and provide a plan."
    )

    response = await g4f.ChatCompletion.create_async(
        model=g4f.models.gpt_4o,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": instruction}
        ],
    )

    try:
        tasks = json.loads(response)
        return tasks
    except (json.JSONDecodeError, TypeError):
        return [{"action": "error", "args": {"message": "Failed to parse LLM response.", "raw_response": response}}]
