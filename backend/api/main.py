from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import sys
sys.path.append(r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend")
from services.boss_agent_service import run_boss
from dotenv import load_dotenv
import os
import time
from pathlib import Path
import threading
import queue

# LOAD ENVIRONMENT VARIABLES ON SERVER START
load_dotenv()
app = FastAPI(
    title="Boss Agent API",
    version="1.0"
)

OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "agents" / "data_agent" / "outputs"
OUTPUTS_DIR = OUTPUTS_DIR.resolve()


class LogHub:
    def __init__(self) -> None:
        self._queue: "queue.Queue[str]" = queue.Queue()
        self._lock = threading.Lock()
        self._active = False
        self._active_event = threading.Event()

    def start_session(self) -> None:
        with self._lock:
            self._active = True
            self._active_event.set()
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    break

    def end_session(self) -> None:
        with self._lock:
            self._active = False
            self._active_event.clear()

    def is_active(self) -> bool:
        with self._lock:
            return self._active

    def wait_for_active(self, timeout: float) -> bool:
        return self._active_event.wait(timeout=timeout)

    def enqueue_line(self, line: str) -> None:
        self._queue.put(line)

    def get_line(self, timeout: float) -> str | None:
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def has_pending(self) -> bool:
        return not self._queue.empty()


class TeeStdout:
    def __init__(self, original, hub: LogHub) -> None:
        self._original = original
        self._hub = hub
        self._buffer = ""

    def write(self, data: str) -> int:
        written = self._original.write(data)
        self._original.flush()
        if not data:
            return written
        self._buffer += data
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            self._hub.enqueue_line(line.replace("\r", ""))
        return written

    def flush(self) -> None:
        self._original.flush()
        if self._buffer:
            self._hub.enqueue_line(self._buffer.replace("\r", ""))
            self._buffer = ""


LOG_HUB = LogHub()

# ======================
# REQUEST MODEL
# ======================

class ChatRequest(BaseModel):
    query: str


# ======================
# HEALTH CHECK
# ======================

@app.get("/")
def health():
    return {"status": "Boss Agent API Running"}


# ======================
# MAIN CHAT ENDPOINT
# ======================

@app.post("/chat")
def chat(req: ChatRequest):

    LOG_HUB.start_session()
    original_stdout = sys.stdout
    sys.stdout = TeeStdout(original_stdout, LOG_HUB)

    try:
        request_start = time.time()
        response = run_boss(req.query)

        if isinstance(sys.stdout, TeeStdout):
            sys.stdout.flush()
    finally:
        sys.stdout = original_stdout
        LOG_HUB.end_session()

    summary = response if isinstance(response, str) else str(response)

    artifacts = []
    if OUTPUTS_DIR.exists() and OUTPUTS_DIR.is_dir():
        for file_path in OUTPUTS_DIR.iterdir():
            if not file_path.is_file():
                continue
            if file_path.name == ".gitkeep":
                continue
            try:
                if file_path.stat().st_mtime >= request_start:
                    artifacts.append(
                        {
                            "filename": file_path.name,
                            "filetype": file_path.suffix.lower(),
                        }
                    )
            except OSError:
                continue

    artifacts.sort(key=lambda x: x["filename"])
    agent = "data_agent" if artifacts else "research_agent"

    return {
        "summary": summary,
        "agent": agent,
        "artifacts": artifacts,
        "response": response,
    }


@app.get("/outputs/{filename}")
def get_output_file(filename: str):
    candidate = (OUTPUTS_DIR / filename).resolve()
    if OUTPUTS_DIR not in candidate.parents:
        raise HTTPException(status_code=404, detail="File not found")
    if not candidate.exists() or not candidate.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(candidate),
        filename=candidate.name,
    )


@app.get("/logs/stream")
def stream_logs():
    def event_stream():
        while not LOG_HUB.is_active() and not LOG_HUB.has_pending():
            if LOG_HUB.wait_for_active(timeout=1.0):
                break
            yield ": waiting\n\n"

        while LOG_HUB.is_active() or LOG_HUB.has_pending():
            line = LOG_HUB.get_line(timeout=0.5)
            if line is None:
                continue
            yield f"data: {line}\n\n"

        yield "event: end\ndata: done\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
