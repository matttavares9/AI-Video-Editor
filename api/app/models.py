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


class ExportRequest(BaseModel):
    output_name: str = Field(default="edited.mp4", pattern=r"^[A-Za-z0-9_.-]+$")
    cuts: list[Cut] | None = None
