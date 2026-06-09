import asyncio
import os
import sys
import threading
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

COMMAND_ORDER_PATH = Path("/workspaces/astrobiome_ai/astrobiome_ai/command_order.md")
CREW_WORKING_DIR = "/workspaces/astrobiome_ai/astrobiome_ai"
CREW_SRC_PATH = "/workspaces/astrobiome_ai/astrobiome_ai/src"

app = FastAPI(title="Astrobiome AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serialize crew runs — crewai is synchronous and os.chdir is process-wide
_crew_lock = threading.Lock()

state: dict = {
    "status": "idle",
    "last_input": None,
    "error": None,
}


class AnalyzeRequest(BaseModel):
    sector: str
    telemetry_data: str
    vision_data: str
    colony_context: str


def _run_crew_sync(inputs: dict) -> None:
    if CREW_SRC_PATH not in sys.path:
        sys.path.insert(0, CREW_SRC_PATH)

    original_cwd = os.getcwd()
    with _crew_lock:
        try:
            # crew task uses output_file='command_order.md' (relative path)
            os.chdir(CREW_WORKING_DIR)
            from astrobiome_ai.crew import AstrobiomeAi
            AstrobiomeAi().crew().kickoff(inputs=inputs)
            state["status"] = "completed"
            state["error"] = None
        except Exception as exc:
            state["status"] = "error"
            state["error"] = str(exc)
        finally:
            os.chdir(original_cwd)


async def _crew_background(inputs: dict) -> None:
    await asyncio.to_thread(_run_crew_sync, inputs)


@app.post("/analyze")
async def analyze(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    inputs = request.model_dump()
    state["last_input"] = inputs
    state["status"] = "processing"
    state["error"] = None
    background_tasks.add_task(_crew_background, inputs)
    return {"status": "processing", "message": "Crew iniciado"}


@app.get("/status")
async def get_status():
    command_order = None
    if COMMAND_ORDER_PATH.exists():
        command_order = COMMAND_ORDER_PATH.read_text(encoding="utf-8")

    return {
        "status": state["status"],
        "last_sensor_data": state["last_input"],
        "command_order": command_order,
        "error": state["error"],
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
