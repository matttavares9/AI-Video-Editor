from django.shortcuts import render

from .models import Job


def dashboard(request):
    """Operator-facing, read-only view of the exact jobs managed by FastAPI."""
    return render(request, "review/dashboard.html", {"jobs": Job.objects.all()[:25]})
