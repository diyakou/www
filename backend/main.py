from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import g4f
import asyncio
from pydantic import BaseModel
from thinker import analyze_and_plan

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

@app.post("/agent/execute")
async def agent_execute(request: AgentRequest):
    """Receives a high-level instruction and uses the Thinker agent to break it down into tasks."""
    tasks = await analyze_and_plan(request.instruction)
    return {"tasks": tasks}

@app.get("/")
def read_root():
    return {"message": "CursorLite API is running!"}
