# Automated Video Trimmer (C++/OpenCV)

**Keep the continuous clear main shot between blurry sections.**

Matthew Tavares's original `Clip.cpp` algorithm is the editing core. It checks
Laplacian variance at half-second intervals, skips blurry footage and clear
sections that are too brief, then keeps the first sustained clear shot until
blur returns. The default threshold is 40 and the minimum clear-shot duration
is four seconds. It does not rank isolated sharp frames or split the main shot
into arbitrary highlights.

`Clip.cpp`, `Clip.h`, and `VideoCompiler.cpp` were restored from the original
codebase at commit `d2b20e2`, with portability and boundary fixes described in
[docs/original-algorithm.md](docs/original-algorithm.md). Both the desktop
program and the JSON engine use this same `Clip` class. Python, FastAPI, SQL,
Django, Flask, MCP, Docker, CI/CD, and AWS are supporting layers around it.

## Original desktop workflow

After building with CMake, run `./build/VideoTrimmer`. Create or load a text
file whose first line is the clips directory and remaining lines are filenames.
The original Display / Edit / Render workflow exports `Test.avi` in the working
directory. Optional face-first selection uses a Haar cascade supplied through
`FACE_CASCADE_PATH`; without it, selection uses blur boundaries only.

## What it does

1. **Upload** a video to `POST /jobs`.
2. **Analyze** it with a headless C++/OpenCV executable. The engine accepts a
   JSON job specification and writes JSON analysis—no prompts, windows, or
   hardcoded file paths.
3. **Validate** the C++-selected cut against the requested minimum duration
   and maximum total duration. The Python service does not select replacement
   footage.
4. **Inspect status** at `GET /jobs/{job_id}`. Jobs and approved cut decisions
   are persisted in SQLite locally and can use Postgres in deployment.
5. **Export** an MP4 with `POST /jobs/{job_id}/export`.

## Architecture

```mermaid
flowchart LR
  U[Client / MCP client] --> API[FastAPI REST service]
  API --> DB[(SQLite locally / Postgres on AWS RDS)]
  API --> E[C++ OpenCV engine]
  E --> A[JSON analysis]
  A --> D[Persisted edit decisions]
  D --> E
  M[MCP server] --> API
  F[Flask demo] --> API
  J[Django review/admin] --> DB
```

The same diagram is available in [docs/architecture.md](docs/architecture.md).

## Quick start

### Prerequisites

- Python 3.12+
- CMake 3.20+
- C++17 compiler
- OpenCV development package
- `nlohmann-json` development package

macOS example:

```bash
brew install cmake opencv nlohmann-json
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cmake -S . -B build
cmake --build build --parallel
export VIDEO_ENGINE_BIN="$PWD/build/video_engine"
uvicorn api.app.main:app --reload
```

Then open `http://127.0.0.1:8000/docs` for interactive API documentation.

### Example API flow

```bash
# 1. Upload
curl -F "file=@sample.mp4" http://127.0.0.1:8000/jobs

# 2. Analyze (replace JOB_ID)
curl -X POST http://127.0.0.1:8000/jobs/JOB_ID/analyze \
  -H 'content-type: application/json' \
  -d '{"min_clip_seconds":4,"max_total_duration_seconds":8}'

# 3. Inspect the saved cut list
curl http://127.0.0.1:8000/jobs/JOB_ID

# 4. Render the approved decisions
curl -X POST http://127.0.0.1:8000/jobs/JOB_ID/export \
  -H 'content-type: application/json' \
  -d '{"output_name":"highlight.mp4"}'
```

## Headless C++ engine

The engine is intentionally usable without Python:

```bash
./build/video_engine analyze --job job.json --output analysis.json
./build/video_engine render --job render.json --output export.json
```

`job.json` example:

```json
{
  "input_path": "/absolute/or/relative/path/to/input.mp4",
  "min_clip_seconds": 4,
  "max_total_duration_seconds": 8
}
```

The engine calls `Clip::Create`, which uses `Clip::FindNotBlurry`. It writes
source metadata, the sampled blur measurements, and the selected main shot to
JSON. `render.json` adds `output_path` and the accepted `cuts`. Optional
`face_cascade_path` enables the original face-first adjustment within that shot.

A clear section shorter than the minimum produces an empty cut list, not an
invented highlight. For footage with a roughly three-second clear section,
explicitly use `"min_clip_seconds": 2`. The default remains four seconds.
If the selected shot exceeds the maximum, the original centered trim with a
random target length is retained. Sampling remains the original half-second
cadence; `sample_interval_seconds` is no longer a selection setting.

## MCP

Run the REST API first, then expose it to Claude Desktop or Claude Code:

```bash
export API_BASE_URL=http://127.0.0.1:8000
python -m mcp_server.server
```

Available tools: `upload_video`, `analyze_video`, `adjust_edit`,
`get_job_status`, and `render_video`. Tell Codex “allow a bit more blur” with
“make it longer,” and it can call `adjust_edit` with `blur_tolerance="more"`
and `clip_length="longer"`. MCP is a thin adapter over the REST API, so there
is no second editing implementation to keep in sync.

## Django, Flask, and Docker

```bash
docker build -t ai-video-editor .
docker run --rm -p 8000:8000 -v "$PWD/data:/data" ai-video-editor
```

For the complete local stack—FastAPI, PostgreSQL, Django review/admin, and the
small Flask dashboard—run:

```bash
docker compose up --build
```

- FastAPI docs: `http://127.0.0.1:8000/docs`
- Django review/admin: `http://127.0.0.1:8001/`
- Flask demo: `http://127.0.0.1:8002/`

Django's models are intentionally read-only views of the FastAPI SQL tables;
there is one job record and one source of editing decisions.

## AWS and CI/CD

For AWS deployment, follow [aws/elastic-beanstalk/README.md](aws/elastic-beanstalk/README.md).
Use RDS PostgreSQL for jobs and decisions and S3 for original videos and
exports; local container storage is not durable across deploys. The
GitHub Actions CI workflow tests the native core, Python API, Django, Flask,
MCP package, and Docker image on every push and pull request. The separate AWS
workflow publishes an immutable image to ECR and rolls the configured ECS
service when `main` changes; configure its documented GitHub environment
variables and OIDC role before enabling production deployment.

The Elastic Beanstalk nginx configuration accepts uploads up to 100 MB. For
larger production files, use direct-to-S3 multipart uploads instead of routing
the media through the API server.

## Quality checks

```bash
pytest api/tests -q
cmake -S . -B build && cmake --build build --parallel
ctest --test-dir build --output-on-failure
docker build -t ai-video-editor .
```

GitHub Actions runs these checks on every push and pull request.

## Delivery plan

- **Sprint 1 — reliable editing core:** engine JSON contract, API job lifecycle,
  SQLite persistence, and tests.
- **Sprint 2 — delivery surfaces:** Django review/admin, Flask demo, MCP,
  Docker Compose, AWS deployment, and durable media storage.

Suggested GitHub issues are in [docs/backlog.md](docs/backlog.md).

## Important limitations

- This is an editing assistant, not a replacement for professional NLE tools.
- OpenCV export writes video frames only; preserving/remixing audio is the next
  production milestone and should use FFmpeg.
- Selection uses the original blur state machine, not semantic understanding
  of the action. Half-second sampling gives approximate blur boundaries;
  scene or speech features must remain optional additions to this core.

## License

See [LICENSE](LICENSE).
