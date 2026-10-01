from django.db import models


class Job(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    source_path = models.CharField(max_length=2048)
    status = models.CharField(max_length=32)
    analysis = models.JSONField(null=True)
    export_path = models.CharField(max_length=2048, null=True)
    error = models.CharField(max_length=2048, null=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        managed = False
        db_table = "jobs"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.id} ({self.status})"


class EditDecision(models.Model):
    job = models.ForeignKey(Job, db_column="job_id", on_delete=models.DO_NOTHING, related_name="decisions")
    start_seconds = models.FloatField()
    end_seconds = models.FloatField()
    score = models.FloatField()
    reason = models.CharField(max_length=1024)

    class Meta:
        managed = False
        db_table = "edit_decisions"
