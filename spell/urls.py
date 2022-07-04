from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    # Homepage
    path("", views.index, name="index"),

    # Authorization pages
    path("login", views.login, name="login"),
    path("register", views.register, name="register"),

    # Dashboard
    path("admin_panel", views.admin_panel, name="admin_panel"),

    # Libraries
    path("word_library", views.word_library, name="word_library"),
    path("tag_library", views.tag_library, name="tag_library"),

    # Word Changes
    path("update_words", views.update_words, name="update_words"),

    # Tag Changes
    path("delete_tag/<str:id>", views.delete_tag, name="delete_tag"),

    # Import
    path("word_import", views.word_import, name="word_import"),
    path("upload_sounds", views.upload_sounds, name="upload_sounds"),

    # Activities

    # Spelling
    path("start", views.start, name="start"),
    path("spell", views.spell, name="spell"),
    path("finish", views.finish, name="finish"),

    # Reports
    path("reports", views.reports, name="reports"),
    path("report/<int:id>", views.report, name="report"),
]