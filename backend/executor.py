import os
import aiofiles

PROJECT_DIRECTORY = "project_files"

async def create_file(filename: str):
    """Creates an empty file."""
    filepath = os.path.join(PROJECT_DIRECTORY, filename)
    try:
        async with aiofiles.open(filepath, 'w') as f:
            await f.write('')
        return {"status": "success", "message": f"File '{filename}' created."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def write_to_file(filename: str, content: str):
    """Writes content to a file."""
    filepath = os.path.join(PROJECT_DIRECTORY, filename)
    try:
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(content)
        return {"status": "success", "message": f"Content written to '{filename}'."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def read_file(filename: str):
    """Reads the content of a file."""
    filepath = os.path.join(PROJECT_DIRECTORY, filename)
    try:
        async with aiofiles.open(filepath, 'r') as f:
            content = await f.read()
        return {"status": "success", "content": content}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def execute_command(command: str):
    """Executes a shell command."""
    # This is a placeholder and should be implemented with caution.
    # For security reasons, we will not execute arbitrary commands in this example.
    return {"status": "success", "message": f"Command '{command}' executed (simulation)."}

ACTION_DISPATCHER = {
    "create_file": create_file,
    "write_to_file": write_to_file,
    "read_file": read_file,
    "execute_command": execute_command,
}

async def execute_task(task: dict):
    """Executes a single task using the dispatcher."""
    action = task.get("action")
    args = task.get("args", {})

    if action in ACTION_DISPATCHER:
        return await ACTION_DISPATCHER[action](**args)
    else:
        return {"status": "error", "message": f"Unknown action: {action}"}
