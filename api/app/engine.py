import json
import os
import subprocess
import uuid
from pathlib import Path


DATA_DIR = Path(os.getenv("DATA_DIR", "./data")).resolve()
ENGINE_BIN = os.getenv("VIDEO_ENGINE_BIN", "./build/video_engine")


class EngineError(RuntimeError):
    pass


def run_engine(command: str, payload: dict) -> dict:
    work = DATA_DIR / "engine-jobs"
    work.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex
    job_path, result_path = work / f"{token}.job.json", work / f"{token}.result.json"
    job_path.write_text(json.dumps(payload), encoding="utf-8")
    process = subprocess.run(
        [ENGINE_BIN, command, "--job", str(job_path), "--output", str(result_path)],
        text=True, capture_output=True, timeout=180, check=False,
    )
    if process.returncode != 0:
        raise EngineError(process.stderr.strip() or "Video engine failed")
    if not result_path.is_file():
        raise EngineError("Video engine did not create a result JSON file")
    return json.loads(result_path.read_text(encoding="utf-8"))
