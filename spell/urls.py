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
    path("categories", views.categories, name="categories"),
    path("make_tag", views.make_tag, name="make_tag"),
    path("ins_words_tag", views.ins_words_tag, name="ins_words_tag"),
    path("del_words_tag", views.del_words_tag, name="del_words_tag"),
    path("chooser", views.chooser, name="chooser"),
    path("delete_words", views.delete_words, name="delete_words"),
    path("delete_tag/<str:id>", views.delete_tag, name="delete_tag")
]