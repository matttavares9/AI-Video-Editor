"""MCP adapter for the same REST tools exposed by the FastAPI service."""
import os
from pathlib import Path
from typing import Literal

import httpx
from mcp.server.fastmcp import FastMCP


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
mcp = FastMCP("AI Video Editor")


@mcp.tool()
def get_job_status(job_id: str) -> dict:
    """Read an editor job's analysis, cuts, status, or export location."""
    response = httpx.get(f"{API_BASE_URL}/jobs/{job_id}", timeout=30)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def analyze_video(
    job_id: str,
    min_clip_seconds: float = 4,
    max_total_duration_seconds: float = 8,
    blur_threshold: float = 40,
) -> dict:
    """Analyze a job. Lower blur_threshold allows more blur; increase max_total_duration_seconds for a longer edit."""
    response = httpx.post(f"{API_BASE_URL}/jobs/{job_id}/analyze", json={
        "min_clip_seconds": min_clip_seconds,
        "max_total_duration_seconds": max_total_duration_seconds,
        "blur_threshold": blur_threshold,
    }, timeout=190)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def adjust_edit(
    job_id: str,
    blur_tolerance: Literal["more", "default", "less"] = "default",
    clip_length: Literal["shorter", "default", "longer"] = "default",
) -> dict:
    """Re-cut a job from a plain-language preference.

    Use blur_tolerance="more" for requests such as "allow a bit more blur";
    use "less" for a stricter edit. Use clip_length="longer" or "shorter"
    when the user asks to change the automatic edit duration.
    """
    thresholds = {"more": 30, "default": 40, "less": 50}
    lengths = {"shorter": 6, "default": 8, "longer": 10}
    return analyze_video(
        job_id,
        max_total_duration_seconds=lengths[clip_length],
        blur_threshold=thresholds[blur_tolerance],
    )


@mcp.tool()
def render_video(job_id: str, output_name: str = "edited.mp4") -> dict:
    """Render the approved cut list to an MP4 export."""
    response = httpx.post(f"{API_BASE_URL}/jobs/{job_id}/export", json={"output_name": output_name}, timeout=190)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def upload_video(local_path: str) -> dict:
    """Upload a local video file to the REST service and return its job ID."""
    path = Path(local_path).expanduser().resolve()
    if not path.is_file():
        raise ValueError(f"Video does not exist: {path}")
    with path.open("rb") as stream:
        response = httpx.post(f"{API_BASE_URL}/jobs", files={"file": (path.name, stream, "video/mp4")}, timeout=190)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    mcp.run()
