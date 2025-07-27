import g4f
import json

async def analyze_and_plan(instruction: str):
    """
    Analyzes a user's instruction and breaks it down into a series of actionable tasks.
    """
    response = await g4f.ChatCompletion.create_async(
        model=g4f.models.gpt_4o,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a task planning agent. Your job is to break down a user's request "
                    "into a series of simple, actionable tasks. Each task should be a JSON object "
                    "with an 'action' and 'args'. Supported actions are: 'create_file', 'write_to_file', "
                    "'read_file', and 'execute_command'. Respond with a JSON array of tasks."
                    "\n\n"
                    "Example Request: 'Create a flask app with a single endpoint that returns hello world'"
                    "\n\n"
                    "Example Response: "
                    '[\n'
                    '  {\n'
                    '    "action": "create_file",\n'
                    '    "args": {\n'
                    '      "filename": "app.py"\n'
                    '    }\n'
                    '  },\n'
                    '  {\n'
                    '    "action": "write_to_file",\n'
                    '    "args": {\n'
                    '      "filename": "app.py",\n'
                    '      "content": "from flask import Flask\\n\\napp = Flask(__name__)\\n\\n@app.route(\'/\')\\ndef hello_world():\\n    return \'Hello, World!\'\\n\\nif __name__ == \'__main__\':\\n    app.run(debug=True)"\n'
                    '    }\n'
                    '  }\n'
                    ']'
                )
            },
            {"role": "user", "content": instruction}
        ],
    )

    try:
        # Assuming the response is a JSON string
        tasks = json.loads(response)
        return tasks
    except (json.JSONDecodeError, TypeError):
        # Handle cases where the response is not valid JSON
        return [{"action": "error", "args": {"message": "Failed to parse LLM response.", "raw_response": response}}]
