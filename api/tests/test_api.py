import os
import tempfile
from pathlib import Path
from unittest.mock import patch

os.environ["DATABASE_URL"] = "sqlite:///./test_video_editor.db"
os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="video-editor-tests-")

from fastapi.testclient import TestClient
from api.app.db import Base, engine
from api.app.main import app


client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def test_upload_analyze_status_and_export():
    response = client.post("/jobs", files={"file": ("sample.mp4", b"not-a-real-video", "video/mp4")})
    assert response.status_code == 201
    job_id = response.json()["id"]

    analysis = {
        "status": "ok", "analysis": {"duration_seconds": 12},
        "cuts": [{"start_seconds": 1, "end_seconds": 6, "score": 80, "reason": "sharp"}],
    }
    with patch("api.app.main.run_engine", return_value=analysis):
        response = client.post(f"/jobs/{job_id}/analyze", json={"min_clip_seconds": 2, "max_total_duration_seconds": 10})
    assert response.status_code == 200
    assert response.json()["status"] == "analyzed"
    assert len(response.json()["cuts"]) == 1

    with patch("api.app.main.run_engine", return_value={"status": "ok"}):
        response = client.post(f"/jobs/{job_id}/export", json={"output_name": "final.mp4"})
    assert response.status_code == 200
    assert response.json()["status"] == "exported"


def test_rejects_non_video_upload():
    response = client.post("/jobs", files={"file": ("notes.txt", b"no", "text/plain")})
    assert response.status_code == 415
