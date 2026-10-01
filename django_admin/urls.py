from django.contrib import admin
from django.urls import path

from django_admin.review.views import dashboard

urlpatterns = [path("", dashboard, name="dashboard"), path("admin/", admin.site.urls)]
