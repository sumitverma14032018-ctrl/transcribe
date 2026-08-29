import asyncio
import json
import os
import logging
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from extractor import extract_audio
from transcriber import transcribe_audio

# Configure global logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Shared state for progress tracking
tasks = {}

class TaskLogHandler(logging.Handler):
    def __init__(self, task_id):
        super().__init__()
        self.task_id = task_id

    def emit(self, record):
        log_entry = self.format(record)
        if self.task_id in tasks:
            if "logs" not in tasks[self.task_id]:
                tasks[self.task_id]["logs"] = []
            tasks[self.task_id]["logs"].append(log_entry)

async def run_transcription_task(task_id, url=None, path=None):
    # Setup task-specific logger
    task_logger = logging.getLogger(f"task_{task_id}")
    handler = TaskLogHandler(task_id)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    task_logger.addHandler(handler)
    task_logger.propagate = True # Allow it to go to global logger too
    
    target = url if url else path
    task_logger.info(f"Starting task {task_id} for: {target}")
    tasks[task_id] = {"status": "Starting", "progress": 0, "logs": []}
    
    try:
        if path:
            # Step 1: Validate Local Path
            task_logger.info(f"Step 1: Validating Local Path: {path}")
            if not os.path.exists(path):
                raise FileNotFoundError(f"Local file not found: {path}")
            
            audio_file = path
            title = os.path.basename(path)
            tasks[task_id]["status"] = "Local file validated"
            tasks[task_id]["progress"] = 20
        else:
            # Step 1: Extraction (YouTube)
            task_logger.info("Step 1: Extracting Audio from YouTube")
            tasks[task_id]["status"] = "Extracting Audio..."
            tasks[task_id]["progress"] = 10
            
            audio_info = await asyncio.to_thread(extract_audio, url)
            audio_file = audio_info['path']
            title = audio_info['title']
            task_logger.info(f"Audio extracted: {title} ({audio_file})")

        tasks[task_id]["status"] = f"Transcribing: {title}..."
        tasks[task_id]["progress"] = 40
        
        # Step 2: Transcription
        task_logger.info("Step 2: Running Whisper Transcription (Incremental)")
        
        output_dir = "transcriptions"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        output_file = os.path.join(output_dir, f"{base_name}.txt")
        
        # We pass output_file to transcribe_audio for incremental saving
        result = await asyncio.to_thread(transcribe_audio, audio_file, output_file=output_file)
        
        # Step 3: Finalize results
        task_logger.info(f"Task completed successfully. Saved to {output_file}")
        tasks[task_id]["status"] = "Completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["result"] = result['text']
        tasks[task_id]["filename"] = f"{base_name}.txt"
        
    except Exception as e:
        task_logger.error(f"Task failed: {str(e)}")
        tasks[task_id]["status"] = f"Error: {str(e)}"
        tasks[task_id]["progress"] = 0
    finally:
        task_logger.removeHandler(handler)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/transcribe")
async def transcribe(background_tasks: BackgroundTasks, url: str = None, path: str = None):
    if not url and not path:
        return {"error": "Must provide either url or path"}
    
    seed = url if url else path
    task_id = str(hash(seed + str(asyncio.get_event_loop().time())))
    background_tasks.add_task(run_transcription_task, task_id, url=url, path=path)
    return {"task_id": task_id}

@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    return tasks.get(task_id, {"status": "Not Found", "progress": 0})

@app.get("/api/events/{task_id}")
async def events(task_id: str):
    async def event_generator():
        last_log_count = 0
        last_status = None
        last_progress = None
        
        while True:
            task = tasks.get(task_id)
            if not task:
                yield f"data: {json.dumps({'status': 'Initializing...'})}\n\n"
            else:
                current_logs = task.get("logs", [])
                new_logs = current_logs[last_log_count:]
                
                if new_logs or task["status"] != last_status or task["progress"] != last_progress:
                    # Only send new logs to save bandwidth
                    update = {
                        "status": task["status"],
                        "progress": task["progress"],
                        "new_logs": new_logs
                    }
                    if task["status"] == "Completed":
                        update["result"] = task.get("result")
                    
                    yield f"data: {json.dumps(update)}\n\n"
                    last_log_count = len(current_logs)
                    last_status = task["status"]
                    last_progress = task["progress"]
                
                if task["status"] == "Completed" or task["status"].startswith("Error"):
                    break
            
            await asyncio.sleep(0.5)
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

if os.path.exists("ui"):
    app.mount("/", StaticFiles(directory="ui", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
