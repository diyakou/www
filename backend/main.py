from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import g4f
import asyncio
from pydantic import BaseModel
import uuid
from thinker import analyze_and_plan
from executor import execute_task

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:3000",  # React default port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FileContent(BaseModel):
    content: str

class EditRequest(BaseModel):
    content: str
    instruction: str

class AgentRequest(BaseModel):
    instruction: str

class AgentStepRequest(BaseModel):
    session_id: str
    last_task_result: dict

# In-memory storage for agent sessions
agent_sessions = {}

# Directory to manage files
PROJECT_DIRECTORY = "project_files"

if not os.path.exists(PROJECT_DIRECTORY):
    os.makedirs(PROJECT_DIRECTORY)

@app.get("/files")
async def list_files():
    """Lists all files in the project directory."""
    files = []
    for entry in os.scandir(PROJECT_DIRECTORY):
        files.append(entry.name)
    return {"files": files}

@app.get("/files/{filename}")
async def get_file(filename: str):
    """Reads the content of a specific file."""
    filepath = os.path.join(PROJECT_DIRECTORY, filename)
    if not os.path.exists(filepath):
        return {"error": "File not found"}
    async with aiofiles.open(filepath, mode='r') as f:
        content = await f.read()
    return {"content": content}

@app.post("/files/{filename}")
async def save_file(filename: str, file_content: FileContent):
    """Saves content to a file."""
    filepath = os.path.join(PROJECT_DIRECTORY, filename)
    async with aiofiles.open(filepath, mode='w') as f:
        await f.write(file_content.content)
    return {"message": f"File '{filename}' saved successfully."}

@app.post("/edit")
async def edit_code(request: EditRequest):
    """Edits code based on a natural language instruction."""
    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_4o,
            messages=[
                {"role": "user", "content": f"Here is a code snippet:\n```\n{request.content}\n```\n\nPlease apply this instruction: {request.instruction}"}
            ],
        )
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}

@app.post("/agent/start")
async def agent_start(request: AgentRequest):
    """Starts a new agent session and returns the first task."""
    session_id = str(uuid.uuid4())
    agent_sessions[session_id] = {"history": []}

    # Get the first task
    first_task = await analyze_and_plan(request.instruction, [])

    # We assume the AI returns a list, so we take the first element
    task_to_execute = first_task[0] if first_task else {"action": "complete", "args": {}}

    # Store the initial instruction in the history
    if task_to_execute.get("action") != "complete":
        task_to_execute["initial_instruction"] = request.instruction

    result = await execute_task(task_to_execute)

    agent_sessions[session_id]["history"].append({"task": task_to_execute, "result": result})

    return {"session_id": session_id, "task": task_to_execute, "result": result}


@app.post("/agent/step")
async def agent_step(request: AgentStepRequest):
    """Executes the next step in an agent session."""
    session_id = request.session_id
    if session_id not in agent_sessions:
        return {"error": "Invalid session ID"}

    history = agent_sessions[session_id]["history"]

    # Get the next task based on history
    next_task_list = await analyze_and_plan(None, history) # Instruction is now in history

    task_to_execute = next_task_list[0] if next_task_list else {"action": "complete", "args": {}}

    if task_to_execute.get("action") == "complete":
        return {"task": task_to_execute, "result": {"status": "success", "message": "Plan completed."}}

    result = await execute_task(task_to_execute)

    history.append({"task": task_to_execute, "result": result})

    return {"task": task_to_execute, "result": result}

@app.get("/")
def read_root():
    return {"message": "CursorLite API is running!"}
