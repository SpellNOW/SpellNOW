from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    # Homepage
    path("", views.index, name="index"),
    path("contact", views.contact, name="contact"),
    path("contactus", views.contactus, name="contactus"),
    path("contactrender", views.contactrender, name="contactrender"),

    # Authorization pages
    path("login", views.login, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout, name="logout"),

    # Dashboard
    path("admin_panel", views.admin_panel, name="admin_panel"),

    # Libraries
    path("word_library", views.word_library, name="word_library"),
    path("tag_library", views.tag_library, name="tag_library"),
    path("root_library", views.root_library, name="root_library"),

    # Word Changes
    path("update_words", views.update_words, name="update_words"),

    # Tag Changes
    path("delete_tag/<str:id>", views.delete_tag, name="delete_tag"),

    # Root Changes
    path("update_root", views.update_root, name="update_root"),
    path("delete_root/<str:id>", views.delete_root, name="delete_root"),

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

    # Error
    path("error_404", views.error_404, name="error_404"),

    # Profile
    path("profile", views.profile, name="profile"),

    # Change Details

    path("changedetails", views.changedetails, name="changedetails"),
    path("changenotifs", views.changenotifs, name="changenotifs"),
    path("changepassword", views.changepassword, name="changepassword"),
    path("informvalidation", views.informvalidation, name="informvalidation"),
    path("validatemail/<int:userit>-<int:lockit1>-<int:lockit2>", views.validatemail, name="validatemail"),


    # -------------DO NOT USE BELOW THIS LINE----------------- #
    # Subscribe
    path("subscribe", views.subscribe, name="subscribe"),

    # Payment
    path("payment/<str:sessionid>", views.payment, name="payment"),
]