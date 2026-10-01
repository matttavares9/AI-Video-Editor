from django.contrib import admin

from .models import EditDecision, Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "created_at", "export_path")
    search_fields = ("id", "status")
    readonly_fields = ("id", "source_path", "status", "analysis", "export_path", "error", "created_at", "updated_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(EditDecision)
class EditDecisionAdmin(admin.ModelAdmin):
    list_display = ("job", "start_seconds", "end_seconds", "score")
    readonly_fields = ("job", "start_seconds", "end_seconds", "score", "reason")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
