from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("confirm-admin", views.confirm, name="confirm"),
    path("admin_panel", views.admin_panel, name="admin_panel"),
    path("upload", views.upload, name="upload"),
    path("upload_custom", views.upload_custom, name="upload_custom"),
    path("upload_sounds", views.upload_sounds, name="upload_sounds"),
]