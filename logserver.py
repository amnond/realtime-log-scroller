import time
import os
import asyncio
from typing import List, AsyncGenerator, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.responses import StreamingResponse, FileResponse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Configuration ---
MONITORED_PATHS: List[str] = ["logs"]  # The folders to watch
# Create a simple logs folder and file for testing
if not os.path.exists("logs"):
    os.makedirs("logs")
if not os.path.exists("logs/app.log"):
    with open("logs/app.log", "w") as f:
        f.write("Initial log entry.\n")
# ---------------------

DEMO_FILE = os.path.join(os.path.dirname(__file__), "logviewer.html")

class LogMonitor(FileSystemEventHandler):
    """
    Handles file system events (modifications) and queues the new log lines.
    """
    def __init__(self, monitored_paths: List[str]):
        super().__init__()
        self.monitored_paths = monitored_paths
        # This Queue will hold the new log lines detected by the watchdog
        self.log_queue: asyncio.Queue[str] = asyncio.Queue()
        # Dictionary to store the last read position (size in bytes) of each file
        self.last_read_pos = {}

        # Initial scan to populate the file size
        for path in self.monitored_paths:
            for root, _, files in os.walk(path):
                for name in files:
                    filepath = os.path.join(root, name)
                    try:
                        self.last_read_pos[filepath] = os.path.getsize(filepath)
                    except OSError:
                        # File might be gone or inaccessible
                        pass
    
    def on_modified(self, event):
        """Called when a file or directory is modified."""
        if event.is_directory:
            return

        filepath = event.src_path

        # Check if the file is being monitored
        if not any(filepath.startswith(p) for p in self.monitored_paths):
            return

        print(f"File modified: {filepath}")
        self.read_new_lines(filepath)

    def read_new_lines(self, filepath: str):
        """Reads and queues new lines added to the file since the last check."""
        
        # Get the previous size, defaulting to 0 if not tracked
        last_size = self.last_read_pos.get(filepath, 0)
        
        try:
            current_size = os.path.getsize(filepath)
            
            if current_size > last_size:
                # File has grown, read the new data
                with open(filepath, 'r', encoding='utf-8') as f:
                    f.seek(last_size) # Start reading from where we left off
                    new_content = f.read()
                
                new_lines = new_content.splitlines()
                for line in new_lines:
                    if line: # Only queue non-empty lines
                        full_log = f"[{os.path.basename(filepath)}] {line}"
                        # Put the log line into the async queue
                        self.log_queue.put_nowait(full_log) 
                
                # Update the last read position
                self.last_read_pos[filepath] = current_size
            
            elif current_size < last_size:
                # File was truncated (e.g., log rotation). Start reading from the beginning.
                print(f"File truncated: {filepath}. Resetting read position.")
                self.last_read_pos[filepath] = 0 # Reset size
                # You might choose to read the whole file or just the new content here. 
                # For simplicity, we just reset and wait for the next modification event.
                
        except OSError as e:
            print(f"Error reading file {filepath}: {e}")
            self.last_read_pos.pop(filepath, None) # Stop tracking if inaccessible

# --- FastAPI Application Setup ---
log_monitor = LogMonitor(MONITORED_PATHS)
# Use a runtime assignment with a type comment to avoid evaluating the
# type expression at runtime in some tooling/environments.
observer = None  # type: Optional[Observer]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to start/stop filesystem monitoring."""
    global observer
    print("Starting file system monitoring...")
    observer = Observer()
    for path in MONITORED_PATHS:
        observer.schedule(log_monitor, path, recursive=True)
    observer.start()
    try:
        yield
    finally:
        print("Stopping file system monitoring...")
        if observer is not None:
            observer.stop()
            observer.join()


app = FastAPI(lifespan=lifespan)

async def log_stream_generator() -> AsyncGenerator[str, None]:
    """
    An asynchronous generator that yields new log lines as SSE events.
    """
    while True:
        try:
            # Wait for a new log line to appear in the queue
            log_line = await asyncio.wait_for(log_monitor.log_queue.get(), timeout=5.0)
            
            # SSE format: data: <content>\n\n
            # We must end the line with \n\n to signal the end of the event
            yield f"data: {log_line}\n\n"
            
            log_monitor.log_queue.task_done()
            
        except asyncio.TimeoutError:
            # Send a keep-alive comment event to prevent connection timeout 
            # and allow the client to retry/reconnect if needed.
            yield ": keep-alive\n\n"
        except asyncio.CancelledError:
            # Client disconnected
            break
        except Exception as e:
            print(f"Stream error: {e}")
            # Wait before trying again to prevent a tight loop on errors
            await asyncio.sleep(1)


@app.get("/stream", tags=["SSE"])
async def stream_logs(request: Request):
    """
    SSE Endpoint for clients to subscribe to the log stream.
    """
    print("Client connected to log stream.")
    # Return an async streaming response for Server-Sent Events (SSE)
    return StreamingResponse(log_stream_generator(), media_type="text/event-stream")

# --- Simple HTML Client for Testing ---

@app.get("/", tags=["UI"])
async def serve_divvscroll():
    """Serve the local `divvscroll_combined_fast.html` demo file so SSE runs from same origin."""
    try:
        return FileResponse(DEMO_FILE, media_type="text/html")
    except OSError:
        fallback = """
        <!doctype html>
        <html><head><meta charset='utf-8'><title>Demo not found</title></head>
        <body><h3>divvscroll_combined_fast.html not found.</h3>
        <p>Place the demo file next to logserver.py as `divvscroll_combined_fast.html`.</p></body></html>
        """
        return HTMLResponse(content=fallback)


if __name__ == "__main__":
    # Simple runner for local testing using uvicorn.
    try:
        import uvicorn
    except Exception:
        print("Uvicorn is required to run the server. Install it with: pip install 'uvicorn[standard]'")
    else:
        print("Starting FastAPI app with Uvicorn on http://127.0.0.1:8000")
        # When using reload or workers, uvicorn requires an import string
        # (module:attribute). Compute the module name from the filename so
        # running `python logserver.py` still works with reload enabled.
        module_name = os.path.splitext(os.path.basename(__file__))[0]
        import_str = f"{module_name}:app"
        uvicorn.run(import_str, host="127.0.0.1", port=8000, reload=True)
    