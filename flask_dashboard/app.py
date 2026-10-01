"""A deliberately small Flask client of the FastAPI editing service."""
import os

import httpx
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


@app.get("/health")
def health():
    return {"status": "ok", "service": "flask-dashboard"}


@app.get("/")
def index():
    return render_template_string("""
    <!doctype html><title>Video Editor Demo</title>
    <h1>Video Editor Flask Demo</h1>
    <p>This small dashboard is a FastAPI client; it contains no editing logic.</p>
    <p>Use <code>/jobs/&lt;job-id&gt;</code> to inspect an API job.</p>
    """)


@app.get("/jobs/<job_id>")
def job(job_id: str):
    response = httpx.get(f"{API_BASE_URL}/jobs/{job_id}", timeout=15)
    return jsonify(response.json()), response.status_code
