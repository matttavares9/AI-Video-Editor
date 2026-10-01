from pydantic import BaseModel, Field


class Cut(BaseModel):
    start_seconds: float = Field(ge=0)
    end_seconds: float = Field(gt=0)
    score: float = 0
    reason: str = ""


class JobResponse(BaseModel):
    id: str
    status: str
    source_path: str
    analysis: dict | None = None
    export_path: str | None = None
    error: str | None = None
    cuts: list[Cut] = []


class AnalyzeRequest(BaseModel):
    min_clip_seconds: float = Field(default=4, gt=0)
    max_total_duration_seconds: float = Field(default=8, gt=0)
    blur_threshold: float = Field(default=5, gt=0, le=1000)


class CompileRequest(BaseModel):
    job_ids: list[str] = Field(min_length=1)
    min_clip_seconds: float = Field(default=1, gt=0)
    max_total_duration_seconds: float = Field(default=8, gt=0)
    blur_threshold: float = Field(default=5, gt=0, le=1000)
    output_name: str = Field(default="edited-video.mp4", pattern=r"^[A-Za-z0-9_.-]+$")


class CompilationResponse(BaseModel):
    output_path: str
    rendered_job_ids: list[str]
    skipped_job_ids: list[str]
    frames_written: int


class ExportRequest(BaseModel):
    output_name: str = Field(default="edited.mp4", pattern=r"^[A-Za-z0-9_.-]+$")
    cuts: list[Cut] | None = None
